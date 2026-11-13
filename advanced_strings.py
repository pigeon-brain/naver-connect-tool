"""English and Japanese translations keyed by the original Korean text."""

TRANSLATIONS = {
    "실제 기기 작업": ("Device operations", "実機の操作"),
    "안내": ("Info", "情報"),
    "언어": (
        "Language",
        "言語",
    ),
    "백업 · 언락 · OS": (
        "Backup · Unlock · OS",
        "バックアップ・ロック解除・OS",
    ),
    "연결 · 앱 설치": (
        "Connect · Install apps",
        "接続・アプリのインストール",
    ),
    "준비 상태": (
        "Readiness",
        "準備状況",
    ),
    "항목": (
        "Item",
        "項目",
    ),
    "상태": (
        "Status",
        "状態",
    ),
    "필요한 조치": (
        "Required action",
        "必要な対応",
    ),
    "항목을 선택하면 필요한 조치가 표시됩니다.": (
        "Select an item to see what to do.",
        "項目を選ぶと必要な対応が表示されます。",
    ),
    "검사 결과는 로그 폴더의 preflight-latest.json에 저장됩니다. 실패한 항목을 수정한 뒤 다시 검사하세요.": (
        "Results are saved to preflight-latest.json in the logs folder. Fix any failed checks and run the check again.",
        "結果はログフォルダーの preflight-latest.json に保存されます。失敗した項目を修正して再確認してください。",
    ),
    "네이버 커넥트 도구": (
        "Naver Connect Tool",
        "NAVER Connect ツール",
    ),
    "백업 폴더": (
        "Backup folder",
        "バックアップフォルダー",
    ),
    "기기 시리얼": (
        "Device serial",
        "端末のシリアル番号",
    ),
    "LineageOS 이미지": (
        "LineageOS image",
        "LineageOS イメージ",
    ),
    "순정 vbmeta_a": (
        "Stock vbmeta_a",
        "純正 vbmeta_a",
    ),
    "선택": (
        "Browse",
        "参照",
    ),
    "언락 후 OS 설치 포함 — 사용자 데이터 삭제": (
        "Install OS after unlocking (erases user data)",
        "ロック解除後に OS をインストール（ユーザーデータを消去）",
    ),
    "설정 검사": (
        "Check setup",
        "設定を確認",
    ),
    "백업부터 순서대로 실행": (
        "Run from backup",
        "バックアップから順に実行",
    ),
    "기존 백업 검증": (
        "Verify existing backup",
        "既存のバックアップを検証",
    ),
    "기존 백업으로 언락부터 진행": (
        "Unlock using existing backup",
        "既存のバックアップでロック解除から実行",
    ),
    "Fastboot 진입": (
        "Enter Fastboot",
        "Fastboot に移行",
    ),
    "현재 Fastboot에서 OS 설치": (
        "Install OS in current Fastboot session",
        "現在の Fastboot 接続で OS をインストール",
    ),
    "대기 중": (
        "Idle",
        "待機中",
    ),
    "MT6768/6769 커넥트 전용. 통합 백업·언락·OS 경로는 모의 검증 단계이며 실제 복원은 미검증.": (
        "For MT6768/6769 Connect only. The combined backup, unlock, and OS workflow has been tested in simulation. Restoring a real device is unverified.",
        "MT6768/6769 搭載の Connect 専用です。バックアップ・ロック解除・OS の一連の手順は模擬環境で検証済みです。実機での復元は未検証です。",
    ),
    "작업 진행 중": (
        "Operation in progress",
        "処理中",
    ),
    "현재 작업이 끝난 뒤 창을 닫아주세요.": (
        "Close the window after the current operation finishes.",
        "現在の処理が完了してからウィンドウを閉じてください。",
    ),
    "검사 실패: {detail}": (
        "Check failed: {detail}",
        "確認に失敗しました: {detail}",
    ),
    "덮어쓰지 않도록 새 폴더를 지정하세요.": (
        "Choose a new folder to avoid overwriting the existing backup.",
        "既存のバックアップを上書きしないよう、新しいフォルダーを指定してください。",
    ),
    "본인 소유의 네이버 커넥트 한 대만 연결했는지 확인하세요. 백업 검증 실패 시 쓰기는 중지됩니다.": (
        "Connect only one Naver Connect device that you own. Writing stops if backup verification fails.",
        "ご自身の NAVER Connect を1台だけ接続してください。バックアップの検証に失敗すると書き込みを中止します。",
    ),
    "OS 설치는 사용자 데이터를 삭제합니다. 선택한 백업이 이 기기의 순정 백업이어야 합니다.": (
        "Installing the OS erases user data. Select a stock backup from this device.",
        "OS のインストールはユーザーデータを消去します。この端末の純正バックアップを選択してください。",
    ),
    "작업 확인": (
        "Confirm operation",
        "処理の確認",
    ),
    "준비 상태 탭의 필요한 항목을 해결한 뒤 다시 실행하세요. 기기 작업은 시작하지 않았습니다.": (
        "Resolve the items in the Readiness tab and try again. No device operation has started.",
        "「準備状況」タブの必要な項目に対応してから再実行してください。端末の処理は開始していません。",
    ),
    "실행: {filename}": (
        "Running: {filename}",
        "実行中: {filename}",
    ),
    "{filename} 실패. 후속 단계는 실행하지 않았습니다. 로그와 현재 기기 상태를 확인하세요. 부분 백업을 삭제하거나 무조건 다시 쓰지 마세요.": (
        "{filename} failed. The remaining steps were skipped. Check the log and device state. Keep partial backups and verify the device state before writing again.",
        "{filename} に失敗しました。後続の手順は実行していません。ログと端末の状態を確認してください。途中までのバックアップは保持し、端末の状態を確認してから再度書き込んでください。",
    ),
    "요청한 단계 완료. OS를 설치했다면 초기 설정 완료 후 연결 · 앱 설치 탭을 사용하세요.": (
        "Requested steps complete. If you installed the OS, finish Android setup before using the Connect · Install apps tab.",
        "指定した手順が完了しました。OS をインストールした場合は初期設定を済ませてから「接続・アプリのインストール」タブを使用してください。",
    ),
    "정상": (
        "OK",
        "正常",
    ),
    "필요": (
        "Action needed",
        "要対応",
    ),
    "연결 도구 대기 중. USB와 전원을 분리한 뒤 USB → 전원 순서로 연결하세요.": (
        "Connection tool waiting. Disconnect USB and power, then reconnect USB first and power second.",
        "接続ツールは待機中です。USB と電源を取り外し、USB、電源の順に接続してください。",
    ),
    "네이버 커넥트 설정": (
        "Naver Connect Setup",
        "NAVER Connect の設定",
    ),
    "페어링 IP:포트": (
        "Pairing IP:port",
        "ペアリング用 IP:ポート",
    ),
    "페어링 코드": (
        "Pairing code",
        "ペアリングコード",
    ),
    "연결 IP:포트": (
        "Connection IP:port",
        "接続用 IP:ポート",
    ),
    "ADB 기기": (
        "ADB device",
        "ADB 端末",
    ),
    "진단 APK": (
        "Diagnostics APK",
        "診断 APK",
    ),
    "콘솔 APK": (
        "Console APK",
        "コンソール APK",
    ),
    "APK SHA-256 매니페스트": (
        "APK SHA-256 manifest",
        "APK SHA-256 マニフェスト",
    ),
    "파일 선택": (
        "Browse files",
        "ファイルを選択",
    ),
    "무선 페어링 및 연결": (
        "Pair and connect wirelessly",
        "ワイヤレスでペアリング・接続",
    ),
    "ADB 기기 검색": (
        "Find ADB devices",
        "ADB 端末を検索",
    ),
    "음소거": (
        "Mute",
        "ミュート",
    ),
    "음소거 및 앱 설치": (
        "Mute and install apps",
        "ミュートしてアプリをインストール",
    ),
    "지원 파일": (
        "Supported files",
        "対応ファイル",
    ),
    "페어링 주소가 비어 있습니다. 기기의 페어링 화면을 열고 ADB 기기 검색을 누르세요.": (
        "Enter the pairing address or open the pairing screen on the device and select Find ADB devices.",
        "ペアリングアドレスを入力するか、端末のペアリング画面を開いて「ADB 端末を検索」を選択してください。",
    ),
    "페어링 또는 연결 주소를 입력하거나 ADB 기기 검색을 누르세요.": (
        "Enter a pairing or connection address, or select Find ADB devices.",
        "ペアリング用または接続用のアドレスを入力するか、「ADB 端末を検索」を選択してください。",
    ),
    "기기의 페어링 화면에 표시된 6자리 코드를 입력하세요.": (
        "Enter the six-digit code shown on the device's pairing screen.",
        "端末のペアリング画面に表示された6桁のコードを入力してください。",
    ),
    "무선 ADB 요청 완료": (
        "Wireless ADB request complete",
        "ワイヤレス ADB のリクエストが完了しました",
    ),
    "ADB 기기 {devices}대, 무선 연결 주소 {addresses}개": (
        "ADB devices: {devices}, wireless addresses: {addresses}",
        "ADB 端末 {devices} 台、ワイヤレス接続先 {addresses} 件",
    ),
    "APK 매니페스트": (
        "APK manifest",
        "APK マニフェスト",
    ),
    "{fields} 항목을 입력하거나 선택하세요.": (
        "Enter or select these fields: {fields}.",
        "次の項目を入力または選択してください: {fields}。",
    ),
    "로그 저장 위치 {path}": (
        "Log file: {path}",
        "ログの保存先: {path}",
    ),
    "실패 ({detail})": (
        "Failed ({detail})",
        "失敗（{detail}）",
    ),
    "예기치 않은 오류 ({detail})": (
        "Unexpected error ({detail})",
        "予期しないエラー（{detail}）",
    ),
    "작업 중단. 진행 로그의 마지막 항목을 확인하세요.": (
        "Operation stopped. Check the last entry in the log.",
        "処理を中断しました。ログの最後の項目を確認してください。",
    ),
    "작업 완료": (
        "Operation complete",
        "処理が完了しました",
    ),
    "로그 저장 실패 ({detail})": (
        "Could not save log ({detail})",
        "ログの保存に失敗しました（{detail}）",
    ),
    "로그 폴더의 쓰기 권한과 PC 저장 공간을 확인하세요.": (
        "Check log folder write permissions and available disk space.",
        "ログフォルダーの書き込み権限と PC の空き容量を確認してください。",
    ),
    "진단 앱": (
        "Diagnostics app",
        "診断アプリ",
    ),
    "콘솔 앱": (
        "Console app",
        "コンソールアプリ",
    ),
    "{app} SHA-256 불일치": (
        "{app}: SHA-256 mismatch",
        "{app} の SHA-256 が一致しません",
    ),
    "{app} SHA-256 확인 완료": (
        "{app}: SHA-256 verified",
        "{app} の SHA-256 を確認しました",
    ),
    "{app} 설치 중": (
        "Installing {app}",
        "{app} をインストール中",
    ),
    "{app} 설치 실패": (
        "Could not install {app}",
        "{app} のインストールに失敗しました",
    ),
    "{app} 설치 확인 실패": (
        "Could not verify {app} installation",
        "{app} のインストールを確認できませんでした",
    ),
    "{app} 설치 확인 완료": (
        "{app} installation verified",
        "{app} のインストールを確認しました",
    ),
    "콘솔 앱 실행 확인 완료": (
        "Console app launch verified",
        "コンソールアプリの起動を確認しました",
    ),
    "ADB 실행 파일이 없습니다. Android Platform-Tools를 설치하고 PATH에 추가하세요.": (
        "ADB was not found. Install Android Platform-Tools and add it to PATH.",
        "ADB が見つかりません。Android Platform-Tools をインストールし、PATH に追加してください。",
    ),
    "ADB 인증이 필요합니다. 기기 화면을 잠금 해제하고 USB 디버깅을 허용하거나 무선 페어링을 다시 하세요.": (
        "ADB authorization is required. Unlock the device screen and allow USB debugging, or pair wirelessly again.",
        "ADB の認証が必要です。端末の画面ロックを解除して USB デバッグを許可するか、ワイヤレスペアリングをやり直してください。",
    ),
    "ADB 기기가 오프라인입니다. 디버깅 연결을 끊었다가 다시 연결하고 기기를 검색하세요.": (
        "The ADB device is offline. Reconnect debugging and search for the device again.",
        "ADB 端末はオフラインです。デバッグ接続をやり直して端末を再検索してください。",
    ),
    "무선 ADB 연결을 확인할 수 없습니다. PC와 기기를 같은 네트워크에 연결하고 무선 디버깅 화면의 현재 IP와 연결 포트를 확인하세요.": (
        "Wireless ADB connection could not be verified. Connect the PC and device to the same network and check the current IP and connection port on the Wireless debugging screen.",
        "ワイヤレス ADB 接続を確認できません。PC と端末を同じネットワークに接続し、「ワイヤレス デバッグ」画面の現在の IP と接続ポートを確認してください。",
    ),
    "선택한 ADB 기기가 보이지 않습니다. 디버깅을 켜고 다시 검색하세요. USB 연결이면 데이터 케이블과 Windows ADB 드라이버를 확인하세요.": (
        "The selected ADB device is unavailable. Enable debugging and search again. For USB connections, check the data cable and Windows ADB driver.",
        "選択した ADB 端末が見つかりません。デバッグを有効にして再検索してください。USB 接続の場合はデータケーブルと Windows の ADB ドライバーを確認してください。",
    ),
    "기기 저장 공간이 부족합니다. 공간을 확보한 뒤 설치를 다시 실행하세요.": (
        "The device has insufficient storage. Free up space and retry the installation.",
        "端末の空き容量が不足しています。容量を確保してからインストールをやり直してください。",
    ),
    "설치된 앱 버전이 더 높습니다. 같거나 더 높은 버전의 APK와 해당 매니페스트를 선택하세요.": (
        "The installed app has a newer version. Select an APK of the same or newer version and its manifest.",
        "インストール済みのアプリのほうが新しいバージョンです。同じか新しいバージョンの APK と対応するマニフェストを選択してください。",
    ),
    "설치된 앱과 APK의 서명이 다릅니다. 기존 앱과 같은 키로 서명된 APK를 선택하세요.": (
        "The installed app and APK have different signatures. Choose an APK signed with the same key as the installed app.",
        "インストール済みのアプリと APK の署名が異なります。同じ鍵で署名された APK を選択してください。",
    ),
    "APK가 이 Android 버전 또는 기기 CPU와 호환되지 않습니다. 이 기기용 APK를 선택하세요.": (
        "The APK is incompatible with this Android version or device CPU. Choose an APK for this device.",
        "APK はこの Android バージョンまたは端末の CPU に対応していません。この端末用の APK を選択してください。",
    ),
    "Android에서 앱 설치를 차단했습니다. 기기의 설치 제한 또는 확인 화면을 확인하세요.": (
        "Android blocked app installation. Check installation restrictions or confirmation prompts on the device.",
        "Android がアプリのインストールをブロックしました。端末のインストール制限や確認画面を確認してください。",
    ),
    "Android가 APK를 읽을 수 없습니다. 해당 앱의 빌드 파일과 매니페스트를 다시 선택하세요.": (
        "Android could not read the APK. Select the app build and manifest again.",
        "Android が APK を読み取れません。アプリのビルドファイルとマニフェストを選択し直してください。",
    ),
    "USB ADB 권한을 확인할 수 없습니다. USB 디버깅 권한과 Windows ADB 드라이버 상태를 확인하세요.": (
        "USB ADB permissions could not be verified. Check USB debugging permissions and the Windows ADB driver.",
        "USB ADB の権限を確認できません。USB デバッグの許可と Windows の ADB ドライバーを確認してください。",
    ),
    "무선 페어링에 실패했습니다. 기기에 새 페어링 코드를 표시하고 해당 화면의 IP와 포트로 다시 시도하세요.": (
        "Wireless pairing failed. Generate a new pairing code on the device and retry with the IP and port shown on that screen.",
        "ワイヤレスペアリングに失敗しました。端末で新しいペアリングコードを表示し、その画面の IP とポートで再試行してください。",
    ),
    "무선 ADB 연결에 실패했습니다. 무선 디버깅 기본 화면의 IP와 연결 포트를 확인하세요.": (
        "Wireless ADB connection failed. Check the IP and connection port on the main Wireless debugging screen.",
        "ワイヤレス ADB 接続に失敗しました。「ワイヤレス デバッグ」のメイン画面の IP と接続ポートを確認してください。",
    ),
    "앱 설치에 실패했습니다. 기기 화면의 설치 메시지를 확인하세요.": (
        "App installation failed. Check the installation message on the device.",
        "アプリのインストールに失敗しました。端末のインストールメッセージを確認してください。",
    ),
    "ADB 요청에 실패했습니다. 기기의 디버깅 연결을 확인하고 다시 검색하세요.": (
        "ADB request failed. Check the device's debugging connection and search again.",
        "ADB のリクエストに失敗しました。端末のデバッグ接続を確認して再検索してください。",
    ),
    "ADB 응답 시간 초과. 기기 화면의 확인 요청이나 USB·무선 연결을 확인하세요.": (
        "ADB timed out. Check the device for prompts and check its USB or wireless connection.",
        "ADB の応答がタイムアウトしました。端末の確認画面と USB またはワイヤレス接続を確認してください。",
    ),
    "ADB를 실행할 수 없습니다. Android Platform-Tools의 설치와 실행 권한을 확인하세요.": (
        "Could not run ADB. Check that Android Platform-Tools is installed and can be executed.",
        "ADB を実行できません。Android Platform-Tools のインストールと実行権限を確認してください。",
    ),
    "IP 주소와 포트를 확인하세요.": (
        "Check the IP address and port.",
        "IP アドレスとポートを確認してください。",
    ),
    "IP 주소 형식이 올바르지 않습니다.": (
        "The IP address format is invalid.",
        "IP アドレスの形式が正しくありません。",
    ),
    "페어링 IP와 포트가 비어 있습니다. 기기의 페어링 화면을 열고 ADB 기기 검색을 누르세요.": (
        "The pairing IP and port are missing. Open the device's pairing screen and select Find ADB devices.",
        "ペアリング用の IP とポートが未入力です。端末のペアリング画面を開き、「ADB 端末を検索」を選択してください。",
    ),
    "페어링 또는 연결 IP와 포트를 입력하세요. ADB 기기 검색으로 찾을 수 있습니다.": (
        "Enter the pairing or connection IP and port. Find ADB devices can look them up.",
        "ペアリング用または接続用の IP とポートを入力してください。「ADB 端末を検索」でも確認できます。",
    ),
    "6자리 페어링 코드를 입력하세요.": (
        "Enter the six-digit pairing code.",
        "6桁のペアリングコードを入力してください。",
    ),
    "무선 주소 자동 검색 실패. 기기의 무선 디버깅 화면에서 IP와 포트를 확인하세요.": (
        "Could not discover wireless addresses. Check the IP and port on the device's Wireless debugging screen.",
        "ワイヤレス接続先を自動検出できません。端末の「ワイヤレス デバッグ」画面で IP とポートを確認してください。",
    ),
    "사용 가능한 ADB 기기가 없습니다. 개발자 옵션의 디버깅 설정을 확인하세요.": (
        "No ADB devices are available. Check debugging settings under Developer options.",
        "利用できる ADB 端末がありません。開発者向けオプションのデバッグ設定を確認してください。",
    ),
    "APK 매니페스트에 진단 앱과 콘솔 앱의 패키지가 필요합니다.": (
        "The APK manifest must include the diagnostics and console app packages.",
        "APK マニフェストには診断アプリとコンソールアプリのパッケージが必要です。",
    ),
    "두 앱의 APK를 지정하세요.": (
        "Select both app APKs.",
        "両方のアプリの APK を指定してください。",
    ),
    "매니페스트의 SHA-256 형식이 올바르지 않습니다.": (
        "The manifest contains an invalid SHA-256 value.",
        "マニフェストの SHA-256 の形式が正しくありません。",
    ),
    "Android 미디어 음소거 상태를 읽을 수 없습니다.": (
        "Could not read Android media mute state.",
        "Android のメディア音量のミュート状態を取得できません。",
    ),
    "APK 파일을 선택하세요.": (
        "Select an APK file.",
        "APK ファイルを選択してください。",
    ),
    "기기 시리얼 형식이 올바르지 않습니다.": (
        "The device serial format is invalid.",
        "端末のシリアル番号の形式が正しくありません。",
    ),
    "ADB 기기 형식이 올바르지 않습니다.": (
        "The ADB device format is invalid.",
        "ADB 端末の指定形式が正しくありません。",
    ),
    "네이버 커넥트 모델을 확인할 수 없습니다.": (
        "Could not verify the Naver Connect model.",
        "NAVER Connect のモデルを確認できません。",
    ),
    "연결된 Android 기기의 시리얼이 일치하지 않습니다.": (
        "The connected Android device serial does not match.",
        "接続した Android 端末のシリアル番号が一致しません。",
    ),
    "Android 부팅이 완료되지 않았습니다.": (
        "Android is still starting.",
        "Android の起動が完了していません。",
    ),
    "기기 시리얼 및 Android 부팅 확인 완료": (
        "Device serial and Android startup verified",
        "端末のシリアル番号と Android の起動を確認しました",
    ),
    "Android 미디어 음소거를 확인할 수 없습니다.": (
        "Could not verify that Android media is muted.",
        "Android のメディア音量がミュートになっていることを確認できません。",
    ),
    "Android 미디어 음소거 확인 완료": (
        "Android media mute verified",
        "Android のメディア音量のミュートを確認しました",
    ),
    "방해 금지 모드를 확인할 수 없습니다.": (
        "Could not verify Do Not Disturb mode.",
        "サイレント モードを確認できません。",
    ),
    "방해 금지 모드 확인 완료": (
        "Do Not Disturb mode verified",
        "サイレント モードを確認しました",
    ),
    "시스템 효과음 끄기를 확인할 수 없습니다.": (
        "Could not verify that system sounds are off.",
        "システム効果音がオフになっていることを確認できません。",
    ),
    "터치 및 잠금 효과음 끄기 확인 완료": (
        "Touch and lock sounds are off",
        "タッチ音とロック音がオフになっていることを確認しました",
    ),
    "콘솔 앱 실행을 확인할 수 없습니다.": (
        "Could not verify that the console app started.",
        "コンソールアプリの起動を確認できません。",
    ),
    "Android Platform-Tools를 설치하고 PATH 또는 .android_sdk/platform-tools에 두세요.": (
        "Install Android Platform-Tools and make it available on PATH or in .android_sdk/platform-tools.",
        "Android Platform-Tools をインストールし、PATH に追加するか .android_sdk/platform-tools に配置してください。",
    ),
    "백업 폴더를 선택하세요.": (
        "Choose a backup folder.",
        "バックアップフォルダーを選択してください。",
    ),
    "새 백업 폴더": (
        "New backup folder",
        "新しいバックアップフォルダー",
    ),
    "아직 없는 폴더 이름을 입력하세요. 기존 백업은 덮어쓰지 않습니다.": (
        "Enter the name of a new folder. Existing backups are kept.",
        "新しいフォルダー名を入力してください。既存のバックアップは保持されます。",
    ),
    "백업 저장 공간": (
        "Backup disk space",
        "バックアップ先の空き容量",
    ),
    "여유 {space}GB. 35GB 이상이 필요합니다.": (
        "{space} GB available. At least 35 GB is required.",
        "空き容量は {space} GB です。35 GB 以上必要です。",
    ),
    "백업 쓰기 권한": (
        "Backup write permissions",
        "バックアップ先の書き込み権限",
    ),
    "NAS라면 탐색기에서 공유 폴더에 먼저 로그인하세요.": (
        "For a NAS, sign in to the shared folder in File Explorer first.",
        "NAS の場合は先にエクスプローラーから共有フォルダーにログインしてください。",
    ),
    "백업 저장소": (
        "Backup storage",
        "バックアップ先",
    ),
    "드라이브/공유 경로를 열 수 없습니다. NAS 로그인과 연결을 확인하세요.": (
        "Could not open the drive or share. Check the NAS sign-in and connection.",
        "ドライブまたは共有フォルダーを開けません。NAS のログイン状態と接続を確認してください。",
    ),
    "백업 완료 기록": (
        "Backup completion record",
        "バックアップ完了記録",
    ),
    "session-status.json의 완료 상태를 확인합니다.": (
        "Checks the completion status in session-status.json.",
        "session-status.json の完了状態を確認します。",
    ),
    "USER·BOOT 백업 파일": (
        "USER and BOOT backup files",
        "USER・BOOT バックアップファイル",
    ),
    "파일 존재·크기 검사입니다. 실제 실행 전 SHA-256도 대조합니다.": (
        "Checks file existence and size. SHA-256 is checked before running the operation.",
        "ファイルの有無とサイズを確認します。処理の実行前に SHA-256 も確認します。",
    ),
    "백업 기기 식별 정보": (
        "Backup device identity",
        "バックアップの端末識別情報",
    ),
    "CID·GPT·Preloader 기록이 필요합니다. 없으면 이 버전의 언락은 실행하지 않습니다.": (
        "CID, GPT, and Preloader records are required to unlock in this version.",
        "このバージョンでロック解除するには、CID・GPT・Preloader の記録が必要です。",
    ),
    "순정 백업": (
        "Stock backup",
        "純正バックアップ",
    ),
    "완료된 백업 폴더와 session-status.json을 선택하세요.": (
        "Select a completed backup folder containing session-status.json.",
        "session-status.json が入った完了済みのバックアップフォルダーを選択してください。",
    ),
    "대상 시리얼": (
        "Target serial",
        "対象のシリアル番号",
    ),
    "기기 라벨 또는 실제 Fastboot에서 확인한 시리얼을 입력하세요.": (
        "Enter the serial shown on the device label or in Fastboot.",
        "端末のラベルまたは Fastboot で確認したシリアル番号を入力してください。",
    ),
    "기존 mtk-venv로 실행하거나 PyUSB를 설치하세요.": (
        "Run from the existing mtk-venv or install PyUSB.",
        "既存の mtk-venv から実行するか、PyUSB をインストールしてください。",
    ),
    "검증된 mtkclient를 준비하거나 CONNECT_MTK_REPO 경로를 지정하세요.": (
        "Set up a verified mtkclient or specify its path with CONNECT_MTK_REPO.",
        "検証済みの mtkclient を用意するか、CONNECT_MTK_REPO にパスを指定してください。",
    ),
    "검증한 버전과 해시가 일치해야 합니다.": (
        "The hash must match the verified version.",
        "検証済みバージョンのハッシュと一致する必要があります。",
    ),
    "현재 Fastboot 연결": (
        "Current Fastboot connection",
        "現在の Fastboot 接続",
    ),
    "선택한 기기 한 대를 Fastboot로 연결하세요. Android 앱 설치는 연결 · 앱 설치 탭을 사용하세요.": (
        "Connect the selected device in Fastboot. To install Android apps, use the Connect · Install apps tab.",
        "選択した端末を1台だけ Fastboot で接続してください。Android アプリのインストールは「接続・アプリのインストール」タブを使用してください。",
    ),
    "Fastboot 조회에 실패했습니다. USB와 해당 모드 드라이버를 확인하세요.": (
        "The Fastboot query failed. Check USB and the driver for this mode.",
        "Fastboot の照会に失敗しました。USB と該当モードのドライバーを確認してください。",
    ),
    "GSI 이미지": (
        "GSI image",
        "GSI イメージ",
    ),
    "검증된 LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img를 선택하세요. 실행 전 SHA-256을 확인합니다.": (
        "Select the verified LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img. SHA-256 is checked before running.",
        "検証済みの LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img を選択してください。実行前に SHA-256 を確認します。",
    ),
    "같은 기기에서 백업한 8MiB vbmeta_a를 선택하세요.": (
        "Select the 8 MiB vbmeta_a backed up from the same device.",
        "同じ端末からバックアップした 8 MiB の vbmeta_a を選択してください。",
    ),
    "WinUSB 등록을 확인했습니다.": (
        "WinUSB registration verified.",
        "WinUSB の登録を確認しました。",
    ),
    "해당 모드의 WinUSB 드라이버를 먼저 설치하세요. 연결 이력이 없으면 확인되지 않을 수 있습니다.": (
        "Install the WinUSB driver for this mode first. A prior connection may be required for detection.",
        "先にこのモードの WinUSB ドライバーをインストールしてください。接続履歴がない場合は検出できないことがあります。",
    ),
    "USB 드라이버 조회": (
        "USB driver query",
        "USB ドライバーの照会",
    ),
    "Windows 장치 조회에 실패했습니다. 관리자 권한으로 다시 실행하세요.": (
        "The Windows device query failed. Run again as administrator.",
        "Windows のデバイス照会に失敗しました。管理者として再実行してください。",
    ),
}
