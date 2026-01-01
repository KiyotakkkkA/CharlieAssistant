from copy import deepcopy

from core.types.ai import ToolClassSetupObject


class ITool:
    name = 'Base Tool'

    commands: list[ToolClassSetupObject] = []

    @classmethod
    def get_commands(cls):
        return cls.commands