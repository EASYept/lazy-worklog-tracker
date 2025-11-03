from sqlite3 import Error
import types
from typing import List, Tuple
from dependency_injector.containers import DeclarativeContainer
from dependency_injector import providers

from abstract.interfaces import WorklogsRepository
from lazy_worklog_tracker.app import WorklogTracker
from lazy_worklog_tracker.plugin_loader import load_plugins


def find_repository(plugins: List[Tuple[str, type]]) -> WorklogsRepository:
    for name, cls in plugins:
        if WorklogsRepository in types.get_original_bases(cls):
            return cls()

    raise Error


class Container(DeclarativeContainer):
    plugins = providers.List(*load_plugins("src/plugins"))
    repo = providers.Singleton(find_repository, plugins)
    app = providers.Singleton(WorklogTracker, repo)

