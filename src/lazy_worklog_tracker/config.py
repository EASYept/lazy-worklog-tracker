from sqlite3 import Error
import types
from typing import List, Tuple
from dependency_injector.containers import DeclarativeContainer
from dependency_injector import providers

from abstract.interfaces import Plugin, WorklogsRepository
from lazy_worklog_tracker.app import WorklogTracker
from lazy_worklog_tracker.plugin_loader import load_plugins


def find_repository(plugins: List[Tuple[str, type]]) -> WorklogsRepository:
    for name, cls in plugins:
        if WorklogsRepository in types.get_original_bases(cls):
            return cls()

    raise Error


def is_subclass_of_plugin(t: type):
    if issubclass(t, Plugin) and not t == Plugin:
        return True


def filter_plugins(plugins: List[Tuple[str, type]]):
    _plugins = filter(lambda x: is_subclass_of_plugin(x[1]), plugins)
    return list(_plugins)


def create_plugins(plugins: List[Tuple[str, type]]) -> List[Plugin]:
    m = map(lambda x: x[1](), plugins)
    return list(m)


class Container(DeclarativeContainer):
    plugins = providers.List(*load_plugins("src/plugins"))
    repo = providers.Singleton(find_repository, plugins)
    extensions = providers.List(*create_plugins(filter_plugins(plugins())))

    app = providers.Singleton(WorklogTracker, repo, extensions)
