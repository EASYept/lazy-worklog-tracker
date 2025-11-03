from __future__ import annotations
from typing import List

from textual.app import App

from abstract.interfaces import Plugin, WorklogsRepository
from lazy_worklog_tracker.worklogscreen import WorklogScreen


class WorklogTracker(App):
    def __init__(self, repository: WorklogsRepository, plugins=List[Plugin]):
        self._screen = WorklogScreen(repository=repository, plugins=plugins)
        super().__init__()

    BINDINGS = []

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_ready(self) -> None:
        self.push_screen(self._screen)
