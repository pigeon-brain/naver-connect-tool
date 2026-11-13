"""Language selection shared by the advanced Tk windows."""

import re
from tkinter import ttk

from advanced_strings import TRANSLATIONS


LANGUAGES = ("한국어", "English", "日本語")


class Language:
    def __init__(self, parent, busy):
        self.index = 0
        self.busy = busy
        self.bindings = []
        bar = ttk.Frame(parent)
        bar.pack(fill="x", padx=16, pady=(8, 0))
        self.label = ttk.Label(bar)
        self.label.pack(side="left", padx=(0, 8))
        self.bind(lambda: self.label.configure(text=self.text("언어")))
        self.widget(ttk.Label(bar), "실제 기기 작업").pack(side="right")
        self.selector = ttk.Combobox(bar, state="readonly", values=LANGUAGES, width=10)
        self.selector.pack(side="left")
        self.selector.current(self.index)
        self.selector.bind("<<ComboboxSelected>>", self.change)

    def change(self, event=None):
        index = self.selector.current()
        if self.busy() or index < 0:
            self.selector.current(self.index)
            return
        self.index = index
        for update in self.bindings:
            update()

    def sync(self):
        self.selector.state(["disabled"] if self.busy() else ["!disabled", "readonly"])

    def bind(self, update):
        self.bindings.append(update)
        update()

    def widget(self, widget, source):
        self.bind(lambda: widget.configure(text=self.text(source)))
        return widget

    def text(self, source, **values):
        translation = TRANSLATIONS.get(source)
        if translation is not None and self.index:
            source = translation[self.index - 1]
        return source.format(**values) if values else source

    def setup_line(self, line):
        # The backend emits these messages as strings for the original log.
        if line in TRANSLATIONS:
            return self.text(line)
        counts = re.fullmatch(r"ADB 기기 ([0-9]+)대, 무선 연결 주소 ([0-9]+)개", line)
        if counts:
            return self.text(
                "ADB 기기 {devices}대, 무선 연결 주소 {addresses}개",
                devices=counts[1], addresses=counts[2],
            )
        if line.startswith("로그 저장 위치 "):
            return self.text("로그 저장 위치 {path}", path=line[len("로그 저장 위치 "):])
        for prefix in ("실패", "예기치 않은 오류", "로그 저장 실패"):
            marker = prefix + " ("
            if line.startswith(marker) and line.endswith(")"):
                return self.text(prefix + " ({detail})", detail=self.setup_line(line[len(marker):-1]))
        for app in ("진단 앱", "콘솔 앱"):
            if line.startswith(app + " "):
                action, separator, detail = line[len(app) + 1:].partition(". ")
                source = "{app} " + action
                if source in TRANSLATIONS:
                    text = self.text(source, app=self.text(app))
                    return text + (". " + self.text(detail) if separator else "")
        return line

    def check_detail(self, source):
        space = re.fullmatch(r"여유 ([0-9.]+)GB\. 35GB 이상이 필요합니다\.", source)
        if space:
            return self.text("여유 {space}GB. 35GB 이상이 필요합니다.", space=space[1])
        return self.text(source)
