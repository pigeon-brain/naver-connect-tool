"""네이버 커넥트 백업 및 Fastboot 도구."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


BASE = Path(__file__).resolve().parent
FASTBOOT_LOCAL = BASE / ".android_sdk/platform-tools/fastboot.exe"
LIBUSB_LOCAL = Path(os.environ.get("CONNECT_MTK_REPO", str(BASE / "vendor/mtkclient"))) / "mtkclient/Windows/libusb-1.0.dll"
MANIFEST = "sha256-manifest.json"
SESSION = "session-status.json"
STOCK_FILES = {"boot1.bin", "boot2.bin", "user.bin"}
USB_MODES = {
    "VID_0E8D&PID_2000": "Preloader",
    "VID_0E8D&PID_0003": "Boot ROM",
    "VID_0E8D&PID_201C": "부트로더 Fastboot",
    "VID_18D1&PID_4EE0": "Fastbootd",
}
FASTBOOT_VARIABLES = (
    "product", "unlocked", "secure", "current-slot", "is-userspace",
    "snapshot-update-status", "is-logical:system_a", "partition-size:system_a",
    "partition-size:super",
)


def progress(message):
    print(message, flush=True)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest_file(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    return size, digest.hexdigest()


def safe_file(root, name):
    parts = name.split("/")
    if any(part in ("", ".", "..") or ":" in part or "\\" in part
           or part.rstrip(" .") != part for part in parts):
        raise ValueError(f"잘못된 기록 경로 ({name})")
    path = root
    for part in parts:
        path /= part
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError(f"링크는 검증 대상에 포함할 수 없습니다 ({name})")
    if not path.is_file():
        raise ValueError(f"백업 파일을 찾을 수 없습니다 ({name})")
    return path


def inventory_names(root):
    names = set()
    for folder, directories, files in os.walk(root):
        folder = Path(folder)
        for name in directories:
            path = folder / name
            if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
                raise ValueError(f"링크는 백업에 포함할 수 없습니다 ({name})")
        for name in files:
            relative = (folder / name).relative_to(root).as_posix()
            if relative != MANIFEST:
                safe_file(root, relative)
                names.add(relative)
    return names


def parse_records(records):
    if not isinstance(records, list) or not records:
        raise ValueError("파일 기록이 비어 있습니다.")
    result = {}
    folded = set()
    for entry in records:
        if not isinstance(entry, dict):
            raise ValueError("파일 기록 형식이 잘못되었습니다.")
        name, size, digest = (entry.get(key) for key in ("path", "bytes", "sha256"))
        if (not isinstance(name, str) or name.casefold() in folded
                or type(size) is not int or size < 0 or not isinstance(digest, str)
                or re.fullmatch(r"[a-fA-F0-9]{64}", digest) is None):
            raise ValueError("파일 기록의 경로, 크기 또는 SHA-256이 잘못되었습니다.")
        folded.add(name.casefold())
        result[name] = (size, digest.lower())
    return result


def load_stock_records(root):
    session = read_json(safe_file(root, SESSION))
    if (not isinstance(session, dict) or session.get("complete") is not True
            or session.get("stage") != "dump-files-verified" or session.get("hwcode") != 0x707):
        raise ValueError("완료된 네이버 커넥트 순정 덤프 기록을 확인할 수 없습니다.")
    entries = parse_records(session.get("files"))
    sizes = session.get("sizes")
    if (set(entries) != STOCK_FILES or not isinstance(sizes, dict)
            or any(size <= 0 or sizes.get(Path(name).stem) != size
                   for name, (size, _) in entries.items())):
        raise ValueError("순정 덤프의 boot1, boot2, user 크기 기록이 일치하지 않습니다.")
    return entries


def verify_entries(root, entries):
    for name, expected in sorted(entries.items()):
        if digest_file(safe_file(root, name)) != expected:
            raise ValueError(f"백업 크기 또는 SHA-256 불일치 ({name})")
        progress(f"검증 완료 ({name})")


def verify_backup(root):
    if not root.is_dir():
        raise ValueError("백업 폴더를 찾을 수 없습니다.")
    if (root / MANIFEST).exists():
        entries = parse_records(read_json(safe_file(root, MANIFEST)))
        if set(entries) != inventory_names(root):
            raise ValueError("매니페스트와 폴더의 파일 목록이 일치하지 않습니다.")
        if SESSION in entries:
            stock = load_stock_records(root)
            if any(entries.get(name) != record for name, record in stock.items()):
                raise ValueError("매니페스트와 순정 덤프의 파일 기록이 일치하지 않습니다.")
    else:
        entries = load_stock_records(root)
    verify_entries(root, entries)
    progress(f"백업 무결성 확인 완료 ({len(entries)}개 파일)")
    return entries


def save_manifest(root, entries):
    records = [
        {"path": name, "bytes": size, "sha256": digest}
        for name, (size, digest) in sorted(entries.items())
    ]
    with (root / MANIFEST).open("x", encoding="utf-8") as output:
        json.dump(records, output, ensure_ascii=False, indent=2)
        output.write("\n")


def copy_backup(source, destination):
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if destination.exists() or destination.is_relative_to(source):
        raise ValueError("백업 원본 밖에 아직 없는 대상 폴더를 지정하세요.")
    entries = verify_backup(source)
    if (source / MANIFEST).exists():
        metadata = {}
    else:
        metadata = {SESSION: digest_file(safe_file(source, SESSION))}
        if load_stock_records(source) != entries:
            raise ValueError("검증 도중 순정 덤프 기록이 변경되었습니다.")
    copied = entries | metadata
    with tempfile.TemporaryDirectory(prefix=".connect-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "backup"
        staged.mkdir()
        for name in sorted(copied):
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe_file(source, name), target)
            progress(f"복사 완료 ({name})")
        save_manifest(staged, copied)
        verify_backup(staged)
        staged.rename(destination)
    progress("백업 사본 저장 완료")


def fastboot_path(explicit):
    if explicit:
        return str(Path(explicit).resolve(strict=True))
    executable = shutil.which("fastboot")
    if executable:
        return executable
    if FASTBOOT_LOCAL.is_file():
        return str(FASTBOOT_LOCAL)
    raise ValueError("Android Platform-Tools를 설치하거나 --fastboot로 실행 파일을 지정하세요.")


def run(command, timeout=6):
    return subprocess.run(
        command, capture_output=True, encoding="utf-8", errors="replace", timeout=timeout,
    )


def list_fastboot(executable):
    result = run([executable, "devices"])
    if result.returncode:
        raise RuntimeError("Fastboot 기기 목록 조회 실패")
    return [match.group(1) for match in re.finditer(
        r"^(\S+)[ \t]+fastboot[ \t]*$", result.stdout, re.MULTILINE,
    )]


def getvar(executable, serial, name):
    result = run([executable, "-s", serial, "getvar", name])
    if result.returncode:
        return None
    matches = re.findall(
        rf"^(?:\(bootloader\)[ \t]*)?{re.escape(name)}:[ \t]*([^\r\n]+)$",
        result.stdout + "\n" + result.stderr, re.MULTILINE,
    )
    return matches[0].strip() if len(matches) == 1 else None


def report_fastboot(executable, serial, *, mode_only=False):
    if list_fastboot(executable).count(serial) != 1:
        raise RuntimeError("지정한 Fastboot 기기 한 대를 확인할 수 없습니다.")
    mode = getvar(executable, serial, "is-userspace")
    if mode_only and mode not in ("yes", "no"):
        raise RuntimeError("Fastboot 연결은 확인했으나 모드 조회에 실패했습니다.")
    if mode in ("yes", "no"):
        progress("Fastbootd 확인 완료" if mode == "yes" else "부트로더 Fastboot 확인 완료")
    if not mode_only:
        values = {
            name: getvar(executable, serial, name)
            for name in FASTBOOT_VARIABLES if name != "is-userspace"
        }
        print(json.dumps({"is-userspace": mode, **values}, indent=2, ensure_ascii=False))


def usb_status():
    if sys.platform != "win32":
        raise ValueError("USB 드라이버 조회는 Windows에서 지원합니다.")
    patterns = "|".join(USB_MODES)
    script = (
        "[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
        f"Get-PnpDevice -PresentOnly -ErrorAction Stop | Where-Object InstanceId -Match '{patterns}' | "
        "ForEach-Object { "
        "$service = Get-PnpDeviceProperty -InstanceId $_.InstanceId "
        "-KeyName DEVPKEY_Device_Service -ErrorAction SilentlyContinue; "
        "[pscustomobject]@{ Id=$_.InstanceId; Name=$_.FriendlyName; "
        "Status=$_.Status; Driver=$service.Data } } | ConvertTo-Json -Compress"
    )
    result = run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], timeout=25)
    if result.returncode:
        raise RuntimeError("Windows USB 상태 조회 실패")
    if not result.stdout.strip():
        progress("지원 USB 모드 연결 안 됨")
        return
    rows = json.loads(result.stdout)
    for row in rows if isinstance(rows, list) else [rows]:
        mode = next(label for token, label in USB_MODES.items() if token in row["Id"].upper())
        progress(f"{mode} / {row['Status']} / {row['Driver'] or '드라이버 서비스 확인 불가'}")


def wait_reply(endpoint, usb_core, timeout, *, ignore_ready=False):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            answer = bytes(endpoint.read(endpoint.wMaxPacketSize, timeout=250))
        except usb_core.USBTimeoutError:
            continue
        if ignore_ready and answer == b"READY":
            continue
        return answer
    raise TimeoutError("Preloader 응답 시간 초과")


def request_fastboot(device, usb_core, usb_util):
    try:
        try:
            config = device.get_active_configuration()
        except usb_core.USBError as exc:
            if exc.strerror != "Configuration not set":
                raise
            device.set_configuration()
            config = device.get_active_configuration()
        interface = config[(0, 0)]
        usb_util.claim_interface(device, interface.bInterfaceNumber)
        incoming = next((ep for ep in interface if ep.bEndpointAddress & 0x80), None)
        outgoing = next((ep for ep in interface if not ep.bEndpointAddress & 0x80), None)
        if incoming is None or outgoing is None:
            raise RuntimeError("Preloader USB 엔드포인트 확인 실패")
        progress("Preloader 연결 완료")
        coding = bytes.fromhex("00100e00000008")
        if device.ctrl_transfer(0x21, 0x20, 0, 0, coding, timeout=1000) != len(coding):
            raise RuntimeError("Preloader 직렬 설정 실패")
        device.ctrl_transfer(0x21, 0x22, 2, 0, b"", timeout=1000)
        progress("Preloader 직렬 설정 완료")
        if wait_reply(incoming, usb_core, 5) != b"READY":
            raise RuntimeError("Preloader READY 응답을 확인할 수 없습니다.")
        progress("Preloader READY 확인 완료")
        if outgoing.write(b"FASTBOOT", timeout=1000) != 8:
            raise RuntimeError("Fastboot 모드 요청 전송 실패")
        if wait_reply(incoming, usb_core, 5, ignore_ready=True) != b"TOOBTSAF":
            raise RuntimeError("Fastboot 모드 응답을 확인할 수 없습니다.")
        progress("Preloader 모드 전환 응답 확인 완료")
        try:
            outgoing.write(b"DISCONNECT", timeout=1000)
        except usb_core.USBError:
            progress("Preloader 연결이 종료되었습니다. Fastboot 연결을 확인합니다.")
    finally:
        try:
            usb_util.dispose_resources(device)
        except usb_core.USBError:
            pass


def enter_fastboot(executable, serial, libusb, timeout):
    import usb.backend.libusb1
    import usb.core
    import usb.util

    if list_fastboot(executable):
        raise RuntimeError("연결된 Fastboot 기기를 분리한 뒤 시도하세요.")
    dll = libusb or (LIBUSB_LOCAL if LIBUSB_LOCAL.is_file() else None)
    backend = (usb.backend.libusb1.get_backend(find_library=lambda _: str(dll.resolve(strict=True)))
               if dll else usb.backend.libusb1.get_backend())
    if backend is None:
        raise RuntimeError("libusb를 찾을 수 없습니다. --libusb로 DLL을 지정하세요.")
    progress(f"네이버 커넥트 Preloader 연결 대기 중 ({timeout}초, 취소 Ctrl+C)")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        devices = list(usb.core.find(
            find_all=True, idVendor=0x0E8D, idProduct=0x2000, backend=backend,
        ))
        if len(devices) > 1:
            raise RuntimeError("Preloader 기기가 여러 대 감지되었습니다.")
        if devices:
            request_fastboot(devices[0], usb.core, usb.util)
            break
        time.sleep(0.05)
    else:
        raise TimeoutError("Preloader 연결 시간 초과")
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        detected = list_fastboot(executable)
        if detected:
            if detected != [serial]:
                raise RuntimeError("연결된 Fastboot 기기가 지정한 시리얼과 일치하지 않습니다.")
            report_fastboot(executable, serial, mode_only=True)
            return
        time.sleep(0.5)
    raise TimeoutError("Fastboot 재연결 시간 초과. USB 드라이버 상태를 확인하세요.")


def serial_argument(value):
    if re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value) is None:
        raise argparse.ArgumentTypeError("시리얼 형식이 잘못되었습니다.")
    return value


def input_path(label):
    return input(label).strip().strip('"')


def menu():
    while True:
        print(
            "\n네이버 커넥트\n"
            "1. USB 드라이버 상태\n"
            "2. Fastboot 기기 목록\n"
            "3. Fastboot 상태 조회\n"
            "4. Preloader에서 Fastboot 진입\n"
            "5. 기존 백업 검증\n"
            "6. 백업 사본 저장\n"
            "7. SHA-256 매니페스트 생성\n"
            "0. 종료\n"
            "기기에서 새 순정 덤프 읽기 및 잠금 해제는 지원하지 않습니다."
        )
        try:
            choice = input("번호 입력 > ").strip()
            if choice == "0":
                return 0
            if choice in ("1", "2"):
                command = ["usb-status" if choice == "1" else "fastboot-list"]
            elif choice in ("3", "4"):
                serial = input("Fastboot 시리얼 > ").strip()
                if choice == "4":
                    print("다른 MediaTek 기기를 분리하고 지정한 네이버 커넥트만 연결하세요.")
                    if input("계속하려면 예 입력 > ").strip() != "예":
                        continue
                action = "fastboot-status" if choice == "3" else "enter-fastboot"
                command = [action, "--serial", serial]
            elif choice in ("5", "7"):
                folder = input_path("백업 폴더 > ")
                if not folder:
                    continue
                command = ["verify" if choice == "5" else "manifest", folder]
            elif choice == "6":
                source = input_path("원본 폴더 > ")
                destination = input_path("저장할 새 폴더 > ")
                if not source or not destination:
                    continue
                command = ["backup-copy", source, destination]
            else:
                print("목록에서 번호를 선택하세요.")
                continue
            try:
                main(command)
            except SystemExit:
                pass
        except (EOFError, KeyboardInterrupt):
            return 130


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastboot", type=Path, help="fastboot 실행 파일")
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("menu", help="대화형 메뉴 실행")
    commands.add_parser("usb-status", help="Windows USB 모드와 드라이버 서비스 조회")
    commands.add_parser("fastboot-list", help="Fastboot 시리얼 조회")
    status = commands.add_parser("fastboot-status", help="Fastboot 변수와 잠금 상태 조회")
    status.add_argument("--serial", required=True, type=serial_argument)
    enter = commands.add_parser("enter-fastboot", help="네이버 커넥트를 Preloader에서 Fastboot로 전환")
    enter.add_argument("--serial", required=True, type=serial_argument)
    enter.add_argument("--libusb", type=Path, help="libusb-1.0 DLL")
    enter.add_argument("--timeout", type=int, default=43200, help="Preloader 연결 대기 시간(초, 기본 43200)")
    verify = commands.add_parser("verify", help="기존 순정 덤프 또는 매니페스트 검증")
    verify.add_argument("folder", type=Path)
    backup = commands.add_parser("backup-copy", help="기존 백업을 검증하고 사본 저장")
    backup.add_argument("source", type=Path)
    backup.add_argument("destination", type=Path)
    manifest = commands.add_parser("manifest", help="로컬 백업 폴더의 SHA-256 매니페스트 생성")
    manifest.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "menu":
            return menu()
        if args.action == "usb-status":
            usb_status()
        elif args.action == "verify":
            verify_backup(args.folder)
        elif args.action == "backup-copy":
            copy_backup(args.source, args.destination)
        elif args.action == "manifest":
            if (args.folder / MANIFEST).exists():
                raise ValueError("이미 매니페스트가 있습니다.")
            stock = {}
            if (args.folder / SESSION).exists():
                stock = verify_backup(args.folder)
            entries = {}
            for name in sorted(inventory_names(args.folder)):
                if name in stock:
                    entries[name] = stock[name]
                else:
                    entries[name] = digest_file(safe_file(args.folder, name))
                progress(f"SHA-256 계산 완료 ({name})")
            if not entries:
                raise ValueError("백업 파일이 없습니다.")
            save_manifest(args.folder, entries)
            progress("매니페스트 저장 완료")
        else:
            executable = fastboot_path(args.fastboot)
            if args.action == "fastboot-list":
                progress("\n".join(list_fastboot(executable)) or "Fastboot 연결 안 됨")
            elif args.action == "fastboot-status":
                report_fastboot(executable, args.serial)
            else:
                if not 1 <= args.timeout <= 43200:
                    raise ValueError("연결 대기 시간은 1~43200초로 지정하세요.")
                enter_fastboot(executable, args.serial, args.libusb, args.timeout)
    except ModuleNotFoundError as exc:
        print(f"필요한 모듈을 찾을 수 없습니다 ({exc.name}). PyUSB를 설치하세요.", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"실패 ({exc})", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("중단됨", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
