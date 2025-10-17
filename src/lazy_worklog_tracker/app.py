from __future__ import annotations

from textual.app import App

from abstract.interfaces import WorklogsRepository
from lazy_worklog_tracker.worklogscreen import WorklogScreen


class WorklogTracker(App):
    def __init__(self, repository: WorklogsRepository):
        self._screen = WorklogScreen(repository=repository)
        super().__init__()

    BINDINGS = []

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_ready(self) -> None:
        self.push_screen(self._screen)
