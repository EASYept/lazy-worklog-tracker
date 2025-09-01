from typing import Iterable

import sqlite3

from abstract.interfaces import WorklogEntity, WorklogsRepository


class SqliteWorklogsRepository(WorklogsRepository):
    def __init__(self) -> None:
        self.sql = sqlite3.connect("db.db", autocommit=True)
        self.cursor = self.sql.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Worklogs (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            task_name TEXT NOT NULL,
            duration TEXT NOT NULL)""")
        super().__init__()

    def get_years(self) -> Iterable[str]:
        self.cursor.execute("SELECT distinct strftime('%Y',w.date) FROM Worklogs w")
        return [x[0] for x in self.cursor.fetchall()]

    def get_months(self, years: Iterable[str]) -> Iterable[str]:
        list_as_string = ",".join("'" + x + "'" for x in years)
        self.cursor.execute(
            f"SELECT DISTINCT strftime('%m',w.date) FROM Worklogs w WHERE strftime('%Y', w.date) in ({list_as_string}) order by strftime('%m',w.date)"
        )
        return [x[0] for x in self.cursor.fetchall()]

    def get_dates(
        self, years: Iterable[str], months: Iterable[str] | None
    ) -> Iterable[str]:
        years_as_string = ",".join("'" + x + "'" for x in years)
        months_as_string = ",".join("'" + x + "'" for x in months)
        self.cursor.execute(
            f"SELECT DISTINCT w.date FROM Worklogs w WHERE strftime('%Y', w.date) in ({years_as_string}) and strftime('%m', w.date) in ({months_as_string}) order by w.date"
        )
        return [x[0] for x in self.cursor.fetchall()]

    def get_tasks(self, dates: Iterable[str]) -> Iterable[str]:
        dates_as_string = ",".join("'" + x + "'" for x in dates)
        self.cursor.execute(
            f"SELECT DISTINCT w.task_name FROM Worklogs w WHERE date in ({dates_as_string})"
        )
        return [x[0] for x in self.cursor.fetchall()]

    def get_worklogs(
        self, dates: Iterable[str], tasks: Iterable[str]
    ) -> Iterable[WorklogEntity]:
        list_as_string = ",".join("'" + x + "'" for x in dates)
        tasks_as_string = ",".join("'" + x + "'" for x in tasks)
        self.cursor.execute(
            f"""select w.id, w.date, w.task_name, w.duration 
            from Worklogs w 
            where w.date in ({list_as_string}) and w.task_name in ({tasks_as_string}) 
            order by w.date, w.task_name
            """
        )
        return [WorklogEntity(x[0], x[1], x[2], x[3]) for x in self.cursor.fetchall()]

    def save(self, entity: WorklogEntity) -> int:
        data = [(entity.date, entity.task, entity.duration)]
        self.cursor.execute(
            "INSERT INTO Worklogs(date, task_name, duration) VALUES (?, ?, ?)",
            *data,
        )
        return 0

    def update(self, entity: WorklogEntity) -> int:
        data = [(entity.date, entity.task, entity.duration, entity.id)]
        self.cursor.execute(
            "update Worklogs set date = ?, task_name = ?, duration = ? where id = ?",
            *data,
        )
        return 0

    def delete(self, id: int) -> int:
        self.cursor.execute(f"DELETE FROM Worklogs WHERE id = {id}")
        return id
