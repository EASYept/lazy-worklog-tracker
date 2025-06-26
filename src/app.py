from __future__ import annotations
from asyncio import sleep
from typing import Iterable, List

from textual.widget import Widget

import httpx
from httpx import DigestAuth
import sqlite3
from textual import on, work, containers
from textual.app import App, ComposeResult
from textual.widgets import (
    DataTable,
    Input,
    Markdown,
    ListItem,
    ListView,
    Digits,
    Label,
    Footer,
)
from textual.containers import Container

from lazy_worklog_tracker.worklogscreen import NewWorklogScreen, WorklogScreen


class WorklogTracker(App):
    BINDINGS = []

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_ready(self) -> None:
        self.push_screen(WorklogScreen())


if __name__ == "__main__":
    app = WorklogTracker()
    app.run()
