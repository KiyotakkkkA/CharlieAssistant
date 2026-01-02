from typing import Dict, List, Protocol, TypedDict, Callable, NotRequired


class ToolFunctionParamsObject(TypedDict):
    type: str
    properties: Dict[str, Dict]
    required: list[str]


class ToolFunctionObject(TypedDict):
    name: str
    description: str
    parameters: ToolFunctionParamsObject


class ToolObject(TypedDict):
    type: str
    function: ToolFunctionObject


class ToolClassSetupObject(TypedDict):
    name: str
    handler: Callable
    tool: ToolObject


class ToolClassProtocol(Protocol):
    name: str

    @staticmethod
    def get_commands() -> List[ToolClassSetupObject]: ...
