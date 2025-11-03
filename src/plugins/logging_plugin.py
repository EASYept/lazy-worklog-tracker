from abstract.interfaces import Plugin, WorklogEntity


class PluginImpl(Plugin):
    def on_save(self, entity: WorklogEntity):
        print("I'M HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
