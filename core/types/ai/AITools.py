from typing import Dict, TypedDict, Callable, NotRequired


class ToolFunctionParamsObject(TypedDict):
    type: str
    properties: Dict[str, Dict]


class ToolFunctionObject(TypedDict):
    name: str
    description: str
    parameters: ToolFunctionParamsObject
    required: list[str]


class ToolObject(TypedDict):
    type: str
    requires_confirmation: NotRequired[bool]
    humanized_description: NotRequired[str]
    function: ToolFunctionObject


class ToolClassSetupObject(TypedDict):
    name: str
    handler: Callable
    tool: ToolObject