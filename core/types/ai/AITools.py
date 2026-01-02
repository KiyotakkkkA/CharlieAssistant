from typing import Dict, List, Protocol, TypedDict, Callable, NotRequired, TYPE_CHECKING

if TYPE_CHECKING:
    from core.general.agent.ToolBuilder import ToolBuilder


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


class FlatToolObject(TypedDict, total=False):
    type: str
    name: str
    description: str
    parameters: ToolFunctionParamsObject
    strict: NotRequired[bool]


class ToolClassSetupObject(TypedDict):
    name: str
    handler: Callable
    tool: "ToolBuilder"


class ToolClassProtocol(Protocol):
    name: str

    @staticmethod
    def get_commands() -> List[ToolClassSetupObject]: ...
