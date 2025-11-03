from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable


@dataclass
class WorklogEntity:
    id: int | None
    date: str
    task: str
    duration: str


class WorklogsRepository:
    "interface for plugin storage"

    @abstractmethod
    def get_years(self) -> Iterable[str]:
        return []

    @abstractmethod
    def get_months(self, years: Iterable[str]) -> Iterable[str]:
        return []

    @abstractmethod
    def get_dates(
        self, years: Iterable[str], months: Iterable[str] | None
    ) -> Iterable[str]:
        return []

    @abstractmethod
    def get_tasks(self, dates: Iterable[str]) -> Iterable[str]:
        return []

    @abstractmethod
    def get_worklogs(
        self, dates: Iterable[str], tasks: Iterable[str]
    ) -> Iterable[WorklogEntity]:
        return []

    def save(self, entity: WorklogEntity) -> WorklogEntity:
        return entity

    def update(self, entity: WorklogEntity) -> WorklogEntity:
        return entity

    def delete(self, id: int) -> int:
        return 0


class Plugin:
    @abstractmethod
    def on_save(self, entity: WorklogEntity):
        pass
