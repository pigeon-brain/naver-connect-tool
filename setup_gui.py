"""네이버 커넥트 Android 설정 화면."""

import ipaddress
import json
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from advanced_i18n import Language
from connect import BASE, digest_file


PACKAGES = {
    "local.son.connectdiagnostics": "진단 앱",
    "local.son.connectconsole": "콘솔 앱",
}
ADB_LOCAL = BASE / ".android_sdk/platform-tools/adb.exe"
LOG_DIRECTORY = Path.home() / "ConnectSetup" / "logs"


def adb_executable():
    if ADB_LOCAL.is_file():
        return str(ADB_LOCAL)
    executable = shutil.which("adb")
    if executable:
        return executable
    raise RuntimeError("ADB 실행 파일이 없습니다. Android Platform-Tools를 설치하고 PATH에 추가하세요.")


def adb_error(output, command):
    output = output.lower()
    rules = (
        (("unauthorized", "authentication failed"), "ADB 인증이 필요합니다. 기기 화면을 잠금 해제하고 USB 디버깅을 허용하거나 무선 페어링을 다시 하세요."),
        (("offline",), "ADB 기기가 오프라인입니다. 디버깅 연결을 끊었다가 다시 연결하고 기기를 검색하세요."),
        (("connection refused", "10061", "failed to connect", "no route to host"), "무선 ADB 연결을 확인할 수 없습니다. PC와 기기를 같은 네트워크에 연결하고 무선 디버깅 화면의 현재 IP와 연결 포트를 확인하세요."),
        (("no devices", "not found"), "선택한 ADB 기기가 보이지 않습니다. 디버깅을 켜고 다시 검색하세요. USB 연결이면 데이터 케이블과 Windows ADB 드라이버를 확인하세요."),
        (("install_failed_insufficient_storage", "no space left"), "기기 저장 공간이 부족합니다. 공간을 확보한 뒤 설치를 다시 실행하세요."),
        (("install_failed_version_downgrade",), "설치된 앱 버전이 더 높습니다. 같거나 더 높은 버전의 APK와 해당 매니페스트를 선택하세요."),
        (("install_failed_update_incompatible", "install_parse_failed_inconsistent_certificates", "signatures do not match"), "설치된 앱과 APK의 서명이 다릅니다. 기존 앱과 같은 키로 서명된 APK를 선택하세요."),
        (("install_failed_older_sdk", "install_failed_no_matching_abis"), "APK가 이 Android 버전 또는 기기 CPU와 호환되지 않습니다. 이 기기용 APK를 선택하세요."),
        (("install_failed_user_restricted", "install_failed_verification_failure"), "Android에서 앱 설치를 차단했습니다. 기기의 설치 제한 또는 확인 화면을 확인하세요."),
        (("install_failed_invalid_apk", "install_parse_failed"), "Android가 APK를 읽을 수 없습니다. 해당 앱의 빌드 파일과 매니페스트를 다시 선택하세요."),
        (("no permissions", "driver"), "USB ADB 권한을 확인할 수 없습니다. USB 디버깅 권한과 Windows ADB 드라이버 상태를 확인하세요."),
    )
    for tokens, message in rules:
        if any(token in output for token in tokens):
            return message
    return {
        "pair": "무선 페어링에 실패했습니다. 기기에 새 페어링 코드를 표시하고 해당 화면의 IP와 포트로 다시 시도하세요.",
        "connect": "무선 ADB 연결에 실패했습니다. 무선 디버깅 기본 화면의 IP와 연결 포트를 확인하세요.",
        "install": "앱 설치에 실패했습니다. 기기 화면의 설치 메시지를 확인하세요.",
    }.get(command, "ADB 요청에 실패했습니다. 기기의 디버깅 연결을 확인하고 다시 검색하세요.")


def adb(executable, *args, timeout=20, pairing_code=None):
    try:
        result = subprocess.run(
            [executable, *args], capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, input=pairing_code,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("ADB 응답 시간 초과. 기기 화면의 확인 요청이나 USB·무선 연결을 확인하세요.") from None
    except OSError:
        raise RuntimeError("ADB를 실행할 수 없습니다. Android Platform-Tools의 설치와 실행 권한을 확인하세요.") from None
    if result.returncode:
        command = args[2] if args[0] == "-s" else args[0]
        raise RuntimeError(adb_error(result.stdout + "\n" + result.stderr, command))
    return result.stdout.strip()


def endpoint(value):
    address, separator, port = value.rpartition(":")
    if not separator or not port.isdecimal() or not 1 <= int(port) <= 65535:
        raise ValueError("IP 주소와 포트를 확인하세요.")
    try:
        ip = ipaddress.ip_address(address.strip("[]"))
    except ValueError:
        raise ValueError("IP 주소 형식이 올바르지 않습니다.") from None
    return f"[{ip}]:{port}" if ip.version == 6 else f"{ip}:{port}"


def connect_wifi(address, pairing_address, code):
    if code and not pairing_address:
        raise ValueError("페어링 IP와 포트가 비어 있습니다. 기기의 페어링 화면을 열고 ADB 기기 검색을 누르세요.")
    if not pairing_address and not address:
        raise ValueError("페어링 또는 연결 IP와 포트를 입력하세요. ADB 기기 검색으로 찾을 수 있습니다.")
    address = endpoint(address) if address else ""
    executable = adb_executable()
    if pairing_address or code:
        if not re.fullmatch(r"[0-9]{6}", code):
            raise ValueError("6자리 페어링 코드를 입력하세요.")
        response = adb(executable, "pair", endpoint(pairing_address), pairing_code=code + "\n")
        if "Successfully paired" not in response:
            raise RuntimeError(adb_error(response, "pair"))
    if address:
        response = adb(executable, "connect", address)
        if response not in (f"connected to {address}", f"already connected to {address}"):
            raise RuntimeError(adb_error(response, "connect"))


def discover(emit=None):
    executable = adb_executable()
    try:
        services = adb(executable, "mdns", "services")
    except RuntimeError:
        services = ""
        if emit is not None:
            emit("무선 주소 자동 검색 실패. 기기의 무선 디버깅 화면에서 IP와 포트를 확인하세요.")
    addresses = []
    for line in services.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[1].rstrip(".") == "_adb-tls-connect._tcp":
            try:
                addresses.append(endpoint(fields[2]))
            except ValueError:
                continue
    devices = adb(executable, "devices")
    rows = [line.split() for line in devices.splitlines()]
    transports = [
        fields[0] for fields in rows if len(fields) == 2 and fields[1] == "device"
    ]
    if emit is not None:
        for state in ("unauthorized", "offline", "no permissions"):
            if any(len(fields) >= 2 and " ".join(fields[1:]).startswith(state) for fields in rows):
                emit(adb_error(state, "devices"))
        if not addresses and not transports:
            emit("사용 가능한 ADB 기기가 없습니다. 개발자 옵션의 디버깅 설정을 확인하세요.")
    return list(dict.fromkeys(addresses)), transports


def validate_apks(paths, manifest, emit):
    expected = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if not isinstance(expected, dict) or set(expected) != set(PACKAGES):
        raise ValueError("APK 매니페스트에 진단 앱과 콘솔 앱의 패키지가 필요합니다.")
    if set(paths) != set(PACKAGES):
        raise ValueError("두 앱의 APK를 지정하세요.")
    for package, path in paths.items():
        digest = expected[package]
        if not isinstance(digest, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", digest):
            raise ValueError("매니페스트의 SHA-256 형식이 올바르지 않습니다.")
        if path.suffix.lower() != ".apk" or digest_file(path)[1] != digest.lower():
            raise ValueError(f"{PACKAGES[package]} SHA-256 불일치")
        emit(f"{PACKAGES[package]} SHA-256 확인 완료")


def music_muted(report):
    section = re.search(
        r"(?m)^\s*-?\s*STREAM_MUSIC\s*:\s*$([\s\S]*?)(?=^\s*-?\s*STREAM_[A-Z_]+\s*:|\Z)",
        report,
    )
    if section:
        states = re.findall(r"(?mi)^\s*Muted:\s*(true|false)\s*$", section[1])
        if len(states) == 1:
            return states[0].lower() == "true"
    raise RuntimeError("Android 미디어 음소거 상태를 읽을 수 없습니다.")


def configure(transport, serial, paths, manifest, emit):
    if paths is None:
        configure_device(transport, serial, None, emit)
        return
    with tempfile.TemporaryDirectory(prefix="connect-apks-") as folder:
        staged = {}
        for index, (package, path) in enumerate(paths.items()):
            if path.suffix.lower() != ".apk":
                raise ValueError("APK 파일을 선택하세요.")
            staged[package] = Path(folder) / f"app-{index}.apk"
            shutil.copyfile(path, staged[package])
        validate_apks(staged, manifest, emit)
        configure_device(transport, serial, staged, emit)


def configure_device(transport, serial, paths, emit):
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", serial):
        raise ValueError("기기 시리얼 형식이 올바르지 않습니다.")
    if not re.fullmatch(r"[A-Za-z0-9_.:\[\]%-]{1,255}", transport) or transport.startswith("-"):
        raise ValueError("ADB 기기 형식이 올바르지 않습니다.")
    executable = adb_executable()

    def device(*args, timeout=20):
        return adb(executable, "-s", transport, *args, timeout=timeout)

    def verify_device():
        state = device("get-state")
        if state != "device":
            raise RuntimeError(adb_error(state, "get-state"))
        if device("shell", "getprop", "ro.product.model") != "Npay_connect":
            raise RuntimeError("네이버 커넥트 모델을 확인할 수 없습니다.")
        if device("shell", "getprop", "ro.serialno") != serial:
            raise RuntimeError("연결된 Android 기기의 시리얼이 일치하지 않습니다.")
        if device("shell", "getprop", "sys.boot_completed") != "1":
            raise RuntimeError("Android 부팅이 완료되지 않았습니다.")

    verify_device()
    emit("기기 시리얼 및 Android 부팅 확인 완료")
    if not music_muted(device("shell", "dumpsys", "audio")):
        verify_device()
        device("shell", "input", "keyevent", "164")
        if not music_muted(device("shell", "dumpsys", "audio")):
            raise RuntimeError("Android 미디어 음소거를 확인할 수 없습니다.")
    emit("Android 미디어 음소거 확인 완료")
    if device("shell", "settings", "get", "global", "zen_mode") != "2":
        verify_device()
        device("shell", "cmd", "notification", "set_dnd", "none")
        if device("shell", "settings", "get", "global", "zen_mode") != "2":
            raise RuntimeError("방해 금지 모드를 확인할 수 없습니다.")
    emit("방해 금지 모드 확인 완료")
    for setting in ("sound_effects_enabled", "lockscreen_sounds_enabled"):
        if device("shell", "settings", "get", "system", setting) != "0":
            verify_device()
            device("shell", "settings", "put", "system", setting, "0")
            if device("shell", "settings", "get", "system", setting) != "0":
                raise RuntimeError("시스템 효과음 끄기를 확인할 수 없습니다.")
    emit("터치 및 잠금 효과음 끄기 확인 완료")
    if paths is None:
        return
    for package, path in paths.items():
        verify_device()
        emit(f"{PACKAGES[package]} 설치 중")
        try:
            result = device("install", "-r", str(path), timeout=180)
            if "Success" not in result.splitlines():
                raise RuntimeError(adb_error(result, "install"))
        except RuntimeError as exc:
            raise RuntimeError(f"{PACKAGES[package]} 설치 실패. {exc}") from None
        installed = device("shell", "pm", "path", package)
        if not any(line.startswith("package:") for line in installed.splitlines()):
            raise RuntimeError(f"{PACKAGES[package]} 설치 확인 실패")
        emit(f"{PACKAGES[package]} 설치 확인 완료")
    verify_device()
    result = device("shell", "am", "start", "-W", "-n", "local.son.connectconsole/.MainActivity")
    if "Status: ok" not in result.splitlines():
        raise RuntimeError("콘솔 앱 실행을 확인할 수 없습니다.")
    emit("콘솔 앱 실행 확인 완료")


class SetupWindow:
    def __init__(self, root, parent=None, language=None):
        self.root = root
        self.active = False
        self.language = language or Language(root, lambda: self.active)
        if parent is None:
            self.language.bind(lambda: root.title(self.language.text("네이버 커넥트 설정")))
        root.minsize(700, 570)
        body = ttk.Frame(parent or root, padding=16)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(13, weight=1)
        self.messages = queue.Queue()
        self.buttons = []
        self.fields = []
        self.variables = {}
        fields = (
            ("pair", "페어링 IP:포트"), ("code", "페어링 코드"),
            ("connect", "연결 IP:포트"), ("transport", "ADB 기기"),
            ("serial", "기기 시리얼"), ("diagnostics", "진단 APK"),
            ("console", "콘솔 APK"), ("manifest", "APK SHA-256 매니페스트"),
        )
        for row, (key, label) in enumerate(fields):
            variable = self.variables[key] = tk.StringVar()
            self.language.widget(ttk.Label(body), label).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 12))
            if key in ("connect", "transport"):
                field = ttk.Combobox(body, textvariable=variable)
                setattr(self, key, field)
            else:
                field = ttk.Entry(body, textvariable=variable, show="*" if key == "code" else "")
            field.grid(row=row, column=1, sticky="ew", pady=4)
            self.fields.append(field)
            if key in ("diagnostics", "console", "manifest"):
                extension = "*.json" if key == "manifest" else "*.apk"
                button = self.language.widget(
                    ttk.Button(body, command=lambda var=variable, ext=extension: self.choose(var, ext)),
                    "파일 선택",
                )
                button.grid(row=row, column=2, padx=(8, 0))
                self.buttons.append(button)
        for row, text, callback in (
            (8, "무선 페어링 및 연결", self.pair), (9, "ADB 기기 검색", self.refresh),
            (10, "음소거", lambda: self.apply(False)), (11, "음소거 및 앱 설치", lambda: self.apply(True)),
        ):
            button = self.language.widget(ttk.Button(body, command=callback), text)
            button.grid(row=row, column=0, columnspan=3, sticky="ew", pady=3)
            self.buttons.append(button)
        self.status = tk.StringVar()
        self.status_message = ""
        self.missing_fields = []
        self.language.bind(self.translate_status)
        ttk.Label(body, textvariable=self.status, wraplength=630).grid(
            row=12, column=0, columnspan=3, sticky="w", pady=6)
        self.output = tk.Text(body, height=9, wrap="word", state="disabled")
        self.output.grid(row=13, column=0, columnspan=3, sticky="nsew")
        if parent is None:
            root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(75, self.drain)

    def set_status(self, source):
        self.status_message = source
        self.missing_fields = []
        self.translate_status()

    def translate_status(self):
        if self.missing_fields:
            fields = ", ".join(self.language.text(label) for label in self.missing_fields)
            self.status.set(self.language.text("{fields} 항목을 입력하거나 선택하세요.", fields=fields))
        else:
            self.status.set(self.language.text(self.status_message))

    def close(self):
        if self.active:
            messagebox.showwarning(
                self.language.text("작업 진행 중"),
                self.language.text("현재 작업이 끝난 뒤 창을 닫아주세요."),
                parent=self.root,
            )
            return
        self.root.destroy()

    def choose(self, variable, extension):
        selected = filedialog.askopenfilename(
            parent=self.root, title=self.language.text("파일 선택"),
            filetypes=[(self.language.text("지원 파일"), extension)],
        )
        if selected:
            variable.set(selected)

    def values(self):
        return {key: value.get().strip() for key, value in self.variables.items()}

    def pair(self):
        data = self.values()
        try:
            if data["code"] and not data["pair"]:
                raise ValueError("페어링 주소가 비어 있습니다. 기기의 페어링 화면을 열고 ADB 기기 검색을 누르세요.")
            if not data["pair"] and not data["connect"]:
                raise ValueError("페어링 또는 연결 주소를 입력하거나 ADB 기기 검색을 누르세요.")
            if data["pair"] and not re.fullmatch(r"[0-9]{6}", data["code"]):
                raise ValueError("기기의 페어링 화면에 표시된 6자리 코드를 입력하세요.")
            for key in ("pair", "connect"):
                if data[key]:
                    endpoint(data[key])
        except ValueError as exc:
            self.set_status(str(exc))
            return
        self.variables["code"].set("")

        def work(emit):
            connect_wifi(data["connect"], data["pair"], data["code"])
            emit("무선 ADB 요청 완료")
            self.messages.put(("devices", discover(emit)))

        self.start(work)

    def refresh(self):
        def work(emit):
            addresses, transports = discover(emit)
            self.messages.put(("devices", (addresses, transports)))
            executable = adb_executable()
            identities = [(t, adb(executable, "-s", t, "shell", "getprop", "ro.serialno")) for t in transports]
            if identities and len({serial for _, serial in identities}) == 1:
                self.messages.put(("identity", identities[0]))
            try:
                services = adb(executable, "mdns", "services")
            except RuntimeError:
                services = ""
            pairings = [line.split()[2] for line in services.splitlines() if len(line.split()) == 3 and line.split()[1].rstrip(".") == "_adb-tls-pairing._tcp"]
            if len(pairings) == 1:
                self.messages.put(("pairing", pairings[0]))
            if len(addresses) == 1:
                self.messages.put(("connection", addresses[0]))
            emit(f"ADB 기기 {len(transports)}대, 무선 연결 주소 {len(addresses)}개")

        self.start(work)

    def apply(self, install):
        data = self.values()
        required = {
            "transport": "ADB 기기", "serial": "기기 시리얼",
        }
        if install:
            required.update(diagnostics="진단 APK", console="콘솔 APK", manifest="APK 매니페스트")
        missing = [label for key, label in required.items() if not data[key]]
        if missing:
            self.missing_fields = missing
            self.translate_status()
            return

        def work(emit):
            paths, manifest = None, None
            if install:
                paths = dict(zip(PACKAGES, (Path(data["diagnostics"]), Path(data["console"]))))
                manifest = Path(data["manifest"])
            configure(data["transport"], data["serial"], paths, manifest, emit)

        self.start(work)

    def start(self, work):
        if self.active:
            return
        self.active = True
        self.language.sync()
        self.set_status("작업 진행 중")
        for widget in self.buttons + self.fields:
            widget.state(["disabled"])

        def run_work():
            try:
                LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
                path = LOG_DIRECTORY / datetime.now().strftime("%Y%m%d-%H%M%S-%f.log")
                with path.open("x", encoding="utf-8") as log:
                    def emit(line):
                        print(line, file=log, flush=True)
                        self.messages.put(("line", line))

                    self.messages.put(("line", f"로그 저장 위치 {path}"))
                    try:
                        work(emit)
                    except (ValueError, OSError, RuntimeError) as exc:
                        emit(f"실패 ({exc})")
                        self.messages.put(("status", "작업 중단. 진행 로그의 마지막 항목을 확인하세요."))
                    except Exception as exc:
                        emit(f"예기치 않은 오류 ({type(exc).__name__})")
                        self.messages.put(("status", "작업 중단. 진행 로그의 마지막 항목을 확인하세요."))
                    else:
                        self.messages.put(("status", "작업 완료"))
            except OSError as exc:
                self.messages.put(("line", f"로그 저장 실패 ({exc})"))
                self.messages.put(("status", "로그 폴더의 쓰기 권한과 PC 저장 공간을 확인하세요."))
            finally:
                self.messages.put(("idle", None))

        threading.Thread(target=run_work, daemon=True).start()

    def drain(self):
        while not self.messages.empty():
            kind, value = self.messages.get_nowait()
            if kind == "devices":
                addresses, transports = value
                self.connect.configure(values=addresses)
                self.transport.configure(values=transports)
                if len(transports) == 1:
                    self.variables["transport"].set(transports[0])
            elif kind == "identity":
                transport, serial = value
                self.variables["transport"].set(transport)
                self.variables["serial"].set(serial)
            elif kind == "pairing":
                self.variables["pair"].set(value)
            elif kind == "connection":
                self.variables["connect"].set(value)
            elif kind == "idle":
                self.active = False
                self.language.sync()
                for widget in self.buttons + self.fields:
                    widget.state(["!disabled"])
            elif kind == "status":
                self.set_status(value)
            else:
                self.output.configure(state="normal")
                self.output.insert("end", self.language.setup_line(value) + "\n")
                self.output.see("end")
                self.output.configure(state="disabled")
        self.root.after(75, self.drain)


def main():
    root = tk.Tk()
    SetupWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
