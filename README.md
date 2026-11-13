# Naver Connect Toolkit

[한국어](README.ko.md) · [English](README.md) · [日本語](README.ja.md)

A Windows tool for Npay Connect backup, bootloader unlock, a verified LineageOS installation flow, and Android app setup. **Experimental: the combined backup-to-install workflow has not been retested end to end on hardware. Stock restoration is not implemented or verified.**

## Repository scope and release status

This repository contains the Windows backup/unlock/OS tool only. Android diagnostic sources are in the separate `naver-connect-diagnostics` repository; the dashboard/stream-deck console belongs to `naver-connect-console`. Neither app nor the RGB/IC helper is bundled here. The optional external-APK setup screen remains, but requires explicitly selected APKs and their SHA-256 manifest; it does not build the apps or start their hardware helper.

This is an experimental source release, not a complete installer. Formatting userdata occurs only in the selected OS installation workflow; there is no separate tested factory-reset/restore feature. The combined backup→unlock→OS workflow has not been retested end to end, restoration/relocking and interrupted-operation resume are not implemented, and clean-PC bootstrap is not hardware-validated. Individual device operations and offline checks do not establish complete recovery. Android speaker muting does not mute the independent payment-reader buzzer.


## Try the interface without touching a device

1. Install Python with Tkinter.
2. Double-click **Preview.cmd**.
3. Choose **한국어 / English / 日本語** in the window.

The preview uses simulated data. It blocks external process execution and does not access ADB, USB, firmware, or your backups. You can test normal progress, missing drivers, lost connections, and backup verification failures.

## Actual operation

**Connect.cmd** opens the advanced operational interface. It can modify the connected device. Read the preparation checks before starting.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
# Optional: prepare the pinned mtkclient environment for backup/unlock.
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -WithDeviceTools
```

Install Android Platform-Tools and make `adb` and `fastboot` available on PATH. Prepare WinUSB drivers for `0E8D:2000`, `0E8D:0003`, `0E8D:201C`, and `18D1:4EE0`. Fastboot requires the Android device-interface GUID. The setup script does not install drivers, request administrator rights, or run device commands.

The launchers prefer `.venv`, then the system Python launcher. `CONNECT_MTK_REPO` can point to a prepared mtkclient checkout. An included patch documents the exact local fixes used with upstream commit `118a000a83ea31c4f427fe5225abfe964546e05e`.

### Workflows

- Backup USER, BOOT1, BOOT2, RAM Preloader and GPT; check sizes, SHA-256 and GPT CRC.
- Verify device identity and stock seccfg against that backup before the supported unlock operation. Restrict the write to one approved 512-byte record and verify the full partition afterward.
- Enter Fastboot through the verified Preloader handshake, then confirm actual Fastboot responses.
- Optionally install the one explicitly hash-allowlisted LineageOS image. This formats userdata. Failures stop subsequent writes; automatic resume and relocking are not supported.
- Discover/pair wireless ADB, verify the selected Connect, mute audio, verify/install the selected console and diagnostic APKs, and launch the console.

Power/cable operations, Windows permission prompts, Android setup and debugging authorization still require the person operating the device. These are prompted at the relevant stages. A single GUI does not remove these physical requirements.

Only the tested MT6768/MT6769 Npay Connect path is intended. **TS-201 is a separate Windows device and is not supported.** Never substitute another device's Preloader, vbmeta, or backup. Keep at least 35GB available for a new backup. RPMB, separate secure elements, payment keys and server-side registration are outside backup coverage. A successful file hash check is not proof that restoration will succeed.

## Assets not distributed

No device dumps, firmware, APKs, proprietary fonts, USB driver binaries or payment material are included. Select your own authorized assets. External APK manifests are supplied by the operator and are not bundled. The accepted GSI comes from [MisterZtr/LineageOS_gsi](https://github.com/MisterZtr/LineageOS_gsi/releases/tag/v2026.01.05-lineage22.2), not an official device build.

## Verification and troubleshooting

The **Preparation** view lists missing settings and suggested fixes. Failed checks prevent device work. Logs and workflow checkpoints remain local under `logs/`; Android setup logs are under the user's `ConnectSetup/logs` directory. Do not upload them without reviewing and removing device identifiers and private paths.

```powershell
python -m unittest discover -p "test_*.py"
python scripts/check_public_tree.py
```

`verification.json` distinguishes hardware observations from offline tests. The Android mute/app-install flow was tested on the device; the integrated backup/unlock/OS rewrite was not rerun for packaging. GUI translation covers the application interface; upstream tool output can remain in its original language.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). The toolkit is distributed under [GPL-3.0](LICENSE). See [THIRD_PARTY.md](THIRD_PARTY.md) for upstream attribution. This is an independent project, not affiliated with or endorsed by Naver, Npay, or LineageOS.
