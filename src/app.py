from __future__ import annotations
from sqlite3 import Error
import types

from textual.app import App

from abstract.interfaces import WorklogsRepository
from lazy_worklog_tracker.worklogscreen import WorklogScreen
from plugin_loader import load_plugins


class WorklogTracker(App):
    def __init__(self, repository: WorklogsRepository):
        self._screen = WorklogScreen(repository=repository)
        super().__init__()

    BINDINGS = []

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_ready(self) -> None:
        self.push_screen(self._screen)


def find_repository(plugins) -> WorklogsRepository:
    for name, cls in plugins:
        if WorklogsRepository in types.get_original_bases(cls):
            return cls()

    raise Error


if __name__ == "__main__":
    plugins = load_plugins("D:/WaveAccess/Repository/lazy-worklog-tracker/src/plugins")
    repo: WorklogsRepository = find_repository(plugins)
    app = WorklogTracker(repo)
    app.run()
