from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import List

from textual import containers, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.validation import Function
from textual.widget import Widget
from textual.widgets import (
    DataTable,
    Footer,
    Input,
    Label,
    SelectionList,
)
from textual.widgets.selection_list import Selection

sql = sqlite3.connect("db.db", autocommit=True)
cursor = sql.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS Worklogs (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    task_name TEXT NOT NULL,
    duration TEXT NOT NULL
    )""")

MONTHS_VIEW = "months"
DATES_VIEW = "dates"
TASK_VIEW = "tasks"
WORKLOG_VIEW = "worklogs"


class GeneralError(Exception):
    """Base class for all errors."""


class NewWorklogScreen(Screen):
    CSS_PATH = "css/new-worklog-screen.tcss"
    BINDINGS = [Binding("escape", "close_screen", "close_screen")]

    def __init__(
        self,
        date: str = "",
        task: str = "",
        duration: str = "",
        worklog_id: int | None = None,
    ):
        self.date_value = date
        self.task_value = task
        self.duration_value = duration
        self.worklog_id = worklog_id
        super().__init__()

    @on(Input.Submitted)
    def action_on_submitt(self, message: Input.Submitted) -> None:
        if message.input.id == "duration-input":
            date = self.get_widget_by_id("date-input", Input).value
            task_name = self.get_widget_by_id("task-input", Input).value
            duration = self.get_widget_by_id("duration-input", Input).value
            if len(date) == 0 or len(task_name) == 0 or len(duration) == 0:
                self.focus_next()
            else:
                self.dismiss(WorklogDto(self.worklog_id, date, task_name, duration))
        else:
            self.focus_next()

    def action_close_screen(self) -> None:
        self.dismiss()

    def compose(self) -> ComposeResult:
        container = Container(id="new-worklog-pop-up")
        container.border_title = (
            "Update worklog" if self.date_value else "Create new worklog"
        )
        with container:
            with containers.HorizontalGroup():
                yield Label("Date    ", classes="input-desc", id="one")
                self._date = Input(
                    placeholder="YYYY-MM-DD",
                    classes="input-field",
                    id="date-input",
                    validators=[Function(validate_date)],
                    value=self.date_value,
                )
                yield self._date
            with containers.HorizontalGroup():
                yield Label("Task    ", classes="input-desc")
                self._task_field = Input(
                    classes="input-field", id="task-input", value=self.task_value
                )
                yield self._task_field
            with containers.HorizontalGroup():
                yield Label("Duration", classes="input-desc")
                self._duration = Input(
                    placeholder="2H30M",
                    classes="input-field",
                    id="duration-input",
                    value=self.duration_value,
                )
                yield self._duration
        yield Footer()


class WorklogDto:
    def __init__(self, id: int | None, date: str, task: str, duration: str):
        self.id = id
        self.date = date
        self.task = task
        self.duration = duration


class WorklogScreen(Screen):
    CSS_PATH = "css/worklogscreen.tcss"
    BINDINGS = [
        ("r", "refresh", "[R]efresh"),
        ("1", "change_focus('months')", ""),
        ("2", "change_focus('dates')", ""),
        ("3", "change_focus('tasks')", ""),
        ("4", "change_focus('worklogs')", ""),
        ("n", "create_new_worklog_screen", "[N]ew worklog"),
        ("c", "choose_current", "Choose [C]current"),
        ("a", "choose_all", "Choose [A]ll"),
        ("d", "delete_worklog", "[D]elete worklog"),
        # debug
        # ("t", "update_worklogs", "update_worlogs"),
        # ("y", "update_tasks", "update_tasks"),
        # ("u", "update_dates", "update_dates"),
        # ("i", "update_months", "update_months"),
    ]

    class UpdateMonths(Message):
        """event"""

    class UpdateDates(Message):
        """event"""

    class UpdateTasks(Message):
        """event"""

    class UpdateWorklogs(Message):
        """event"""

    def compose(self) -> ComposeResult:
        with containers.HorizontalGroup():
            with containers.VerticalGroup(id="left-bar"):
                with Container(classes="months-container"):
                    self._months = SelectionList[str](id=MONTHS_VIEW)
                    self._months.border_title = "[press 1] Months"
                    yield self._months
                with Container(classes="dates-container"):
                    self._dates = SelectionList[str](id=DATES_VIEW)
                    self._dates.border_title = "[press 2] Dates"
                    yield self._dates
                with Container(classes="task-container"):
                    self._tasks = SelectionList[str](id=TASK_VIEW)
                    self._tasks.border_title = "[press 3] Tasks"
                    yield self._tasks
            with Container(classes="worklog-container"):
                self._worklogs = DataTable(id=WORKLOG_VIEW)
                self._worklogs.border_title = "[press 4] Worklogs"
                # self._worklogs.show_header = False
                self._worklogs.cursor_type = "row"
                self._worklogs.add_columns(*["date", "task", "duration"])
                yield self._worklogs
        yield Footer()

    def action_change_focus(self, widget_name: str):
        widget = self.query_one(f"#{widget_name}", Widget)
        self.set_focus(widget)
        return

    def action_refresh(self):
        self._months.clear_options()
        self._dates.clear_options()
        self._tasks.clear_options()
        self._worklogs.clear(False)
        self.post_message(self.UpdateMonths())

    def if_options_empty(self, selection_list: SelectionList) -> None:
        if len(selection_list.options) == 0:
            selection_list.add_option(Selection("empty", "empty", False, id="empty"))
        else:
            selection_list.highlighted = 0

    @work(exclusive=True)
    @on(UpdateMonths)
    async def action_update_months(self) -> None:
        years_list = self.get_years_from_db()
        months_list = self.get_months_from_db(years_list)

        self._months.clear_options()
        self._months.add_options(
            [
                Selection(month, month, True, id=month)
                for month in months_list
                if month is not None
            ]
        )
        self._months.highlighted = 0
        self.post_message(self.UpdateDates())

    @work(exclusive=True)
    @on(UpdateWorklogs)
    async def action_update_worklogs(self):
        dates: SelectionList = self._dates
        tasks: SelectionList = self._tasks
        worklogs: DataTable = self._worklogs
        worklogs.clear(False)

        worklogs_by_id = {
            worklog.id: (worklog.date, worklog.task, worklog.duration)
            for worklog in self.get_worklogs_from_db(dates.selected, tasks.selected)
        }
        for id, row in worklogs_by_id.items():
            worklogs.add_row(*row, key=id)

    @work(exclusive=True)
    @on(UpdateTasks)
    async def action_update_tasks(self):
        new_tasks = self.get_tasks_from_db(self._dates.selected)
        self._tasks.clear_options()
        self._tasks.add_options(
            [
                Selection(task, task, True, id=task)
                for task in new_tasks
                if task is not None
            ]
        )
        self.if_options_empty(self._tasks)
        self.post_message(self.UpdateWorklogs())

    @work(exclusive=True)
    @on(UpdateDates)
    async def action_update_dates(self) -> None:
        new_dates = self.get_dates_from_db(
            self.get_years_from_db(), self._months.selected
        )
        self._dates.clear_options()
        self._dates.add_options(
            [
                Selection(date, date, True, id=date)
                for date in new_dates
                if date is not None
            ]
        )
        self.if_options_empty(self._dates)
        self.post_message(self.UpdateTasks())

    def action_create_new_worklog_screen(self) -> None:
        def new_worklog_result(result: WorklogDto | None) -> None:
            if result:
                data = [(result.date, result.task, result.duration)]
                cursor.execute(
                    "INSERT INTO Worklogs(date, task_name, duration) VALUES (?, ?, ?)",
                    *data,
                )
                self.post_message(self.UpdateMonths())
            else:
                return

        self.app.push_screen(NewWorklogScreen(), new_worklog_result)

    @on(DataTable.RowSelected)
    def action_create_update_worklog_screen(self):
        def update_worklog(result: WorklogDto | None) -> None:
            if result:
                data = [(result.date, result.task, result.duration, result.id)]
                cursor.execute(
                    "update Worklogs set date = ?, task_name = ?, duration = ? where id = ?",
                    *data,
                )

        table = self._worklogs
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row_data = self._worklogs.get_row(row_key)
        self.app.push_screen(
            NewWorklogScreen(
                row_data[0], row_data[1], row_data[2], worklog_id=int(row_key.value)
            ),
            update_worklog,
        )
        pass

    def action_choose_current(self) -> None:
        if self.focused.id == self._tasks.id:
            self.choose_current(self._tasks)
            self.post_message(self.UpdateWorklogs())
        elif self.focused.id == self._dates.id:
            self.choose_current(self._dates)
            self.post_message(self.UpdateTasks())
        elif self.focused.id == self._months.id:
            self.choose_current(self._months)
            self.post_message(self.UpdateDates())

    def action_choose_all(self) -> None:
        if self.focused.id == self._tasks.id:
            self._tasks.select_all()
            self.post_message(self.UpdateWorklogs())
        elif self.focused.id == self._dates.id:
            self._dates.select_all()
            self.post_message(self.UpdateTasks())
        elif self.focused.id == self._months.id:
            self._months.select_all()
            self.post_message(self.UpdateDates())

    def get_worklogs_from_db(
        self, dates: List[str], tasks: List[str]
    ) -> List[WorklogDto]:
        list_as_string = ",".join("'" + x + "'" for x in dates)
        tasks_as_string = ",".join("'" + x + "'" for x in tasks)
        cursor.execute(
            f"SELECT w.id, w.date, w.task_name, w.duration FROM Worklogs w WHERE w.date in ({list_as_string}) and w.task_name in ({tasks_as_string}) order by w.date, w.task_name"
        )
        all_data = cursor.fetchall()
        return [WorklogDto(x[0], x[1], x[2], x[3]) for x in all_data]

    def get_years_from_db(self) -> List[str]:
        cursor.execute("SELECT distinct strftime('%Y',w.date) FROM Worklogs w")
        return [x[0] for x in cursor.fetchall()]

    def get_months_from_db(self, years: List[str]) -> List[str]:
        list_as_string = ",".join("'" + x + "'" for x in years)
        cursor.execute(
            f"SELECT DISTINCT strftime('%m',w.date) FROM Worklogs w WHERE strftime('%Y', w.date) in ({list_as_string}) order by strftime('%m',w.date)"
        )
        return [x[0] for x in cursor.fetchall()]

    def get_dates_from_db(self, years: List[str], months: List[str]) -> List[str]:
        years_as_string = ",".join("'" + x + "'" for x in years)
        months_as_string = ",".join("'" + x + "'" for x in months)
        cursor.execute(
            f"SELECT DISTINCT w.date FROM Worklogs w WHERE strftime('%Y', w.date) in ({years_as_string}) and strftime('%m', w.date) in ({months_as_string}) order by w.date"
        )
        return [x[0] for x in cursor.fetchall()]

    def get_tasks_from_db(self, dates: List[str]):
        dates_as_string = ",".join("'" + x + "'" for x in dates)
        cursor.execute(
            f"SELECT DISTINCT w.task_name FROM Worklogs w WHERE date in ({dates_as_string})"
        )
        return [x[0] for x in cursor.fetchall()]

    def on_mount(self) -> None:
        self.action_refresh()

    @on(SelectionList.SelectionToggled)
    async def update_worklogs_based_on_selection(
        self, message: SelectionList.SelectionToggled
    ) -> None:
        id = message.selection_list.id
        print(f"event from id {id}")

        if MONTHS_VIEW == id:
            self.post_message(self.UpdateDates())
        elif DATES_VIEW == id:
            self.post_message(self.UpdateTasks())
        elif TASK_VIEW == id:
            self.post_message(self.UpdateWorklogs())

    def choose_current(self, selection_list: SelectionList[str]):
        if selection_list.highlighted is None:
            return
        index: int = selection_list.highlighted
        selection_list.deselect_all()
        selection_list.select(selection_list.get_option_at_index(index))

    def action_delete_worklog(self):
        if self.focused.id == self._worklogs.id:
            table = self._worklogs
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            cursor.execute(f"DELETE FROM Worklogs WHERE id = {row_key.value}")
            table.remove_row(row_key)


def validate_date(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y-%m-%d"):
            raise ValueError
        return True
    except ValueError:
        return False
