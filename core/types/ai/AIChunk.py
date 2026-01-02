from typing import Any, NotRequired, TypedDict, TypeAlias

from openai.types.responses import ResponseStreamEvent
from ollama import ChatResponse


class FunctionCallItem(TypedDict, total=False):
    type: str
    id: str
    call_id: str
    name: str
    arguments: str


class OpenRouterAIResponseChunk(TypedDict, total=False):
    event: ResponseStreamEvent | Any
    event_type: str

    ai_content_part: NotRequired[str]

    tool_call: NotRequired[FunctionCallItem]
    tool_call_index: NotRequired[int]
    tool_call_id: NotRequired[str]
    tool_call_arguments_delta: NotRequired[str]
    tool_call_arguments: NotRequired[str]

    tool_event: NotRequired[dict]


class OllamaAIResponseChunk(TypedDict, total=False):
    event: ChatResponse | Any
    event_type: str

    ai_content_part: NotRequired[str]

    tool_call: NotRequired[FunctionCallItem]
    tool_call_index: NotRequired[int]

    tool_event: NotRequired[dict]


AIResponseChunk: TypeAlias = OpenRouterAIResponseChunk | OllamaAIResponseChunk