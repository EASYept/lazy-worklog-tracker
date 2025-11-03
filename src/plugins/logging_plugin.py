from typing import Dict, List
from abstract.interfaces import Plugin, WorklogEntity


class PluginImpl(Plugin):
    ma: Dict[str, WorklogEntity] = {}
    _columns: List[str] = ["sync"]

    def columns(self) -> List[str]:
        return self._columns

    def on_save(self, entity: WorklogEntity):
        self.ma[str(entity.id)] = entity
        print("I'M HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
