from __future__ import annotations

from textual.app import App
from lazy_worklog_tracker.worklogscreen import WorklogScreen


class WorklogTracker(App):
    BINDINGS = []

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_ready(self) -> None:
        self.push_screen(WorklogScreen())


if __name__ == "__main__":
    app = WorklogTracker()
    app.run()
