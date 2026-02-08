from copy import deepcopy

from core.general import Config
from core.types.ai import ToolClassSetupObject


class ITool:
    name = 'Base Tool'

    commands: list[ToolClassSetupObject] = []

    config = Config

    @classmethod
    def get_commands(cls):
        return deepcopy(cls.commands)