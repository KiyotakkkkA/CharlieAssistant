from openai import OpenAI, Stream
from openai.types.responses import ResponseInputParam, ResponseStreamEvent

from typing import Any, Generator, cast

from core.general import Config
from core.exeptions import NoClientError
from core.types.ai import OpenRouterAIResponseChunk
from core.providers.BaseAIProvider import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self, config: Config):
        super().__init__(
            api_key=config.OPENAI_API_KEY,
            api_base=config.OPENAI_API_BASE
        )

    def provider_setup(self):
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
        )
    
    def generate_response(self, messages: ResponseInputParam, **kwargs) -> Generator[OpenRouterAIResponseChunk, None, None]:
        if not self.client:
            raise NoClientError("OpenAIProvider")

        def _get_field(obj: Any, key: str) -> Any:
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        for event in self.client.responses.create(
            model=self.model_name,
            input=messages,
            **kwargs,
        ):
            data = cast(ResponseStreamEvent, event)
            event_type = _get_field(data, "type") or ""

            chunk: OpenRouterAIResponseChunk = {
                "event": data,
                "event_type": str(event_type),
            }

            if event_type == "response.output_text.delta":
                delta = _get_field(data, "delta")
                if isinstance(delta, str) and delta:
                    chunk["ai_content_part"] = delta

            elif event_type == "response.output_item.added":
                item = _get_field(data, "item")
                item_type = _get_field(item, "type")
                if item_type == "function_call":
                    output_index = _get_field(data, "output_index")
                    if isinstance(output_index, int):
                        chunk["tool_call_index"] = output_index

                    tool_call: dict[str, Any] = {
                        "type": "function_call",
                        "id": _get_field(item, "id") or "",
                        "call_id": _get_field(item, "call_id") or "",
                        "name": _get_field(item, "name") or "",
                        "arguments": _get_field(item, "arguments") or "",
                    }
                    chunk["tool_call"] = cast(Any, tool_call)
                    if tool_call.get("id"):
                        chunk["tool_call_id"] = cast(str, tool_call["id"])

            elif event_type == "response.function_call_arguments.delta":
                delta = _get_field(data, "delta")
                if isinstance(delta, str) and delta:
                    chunk["tool_call_arguments_delta"] = delta

                output_index = _get_field(data, "output_index")
                if isinstance(output_index, int):
                    chunk["tool_call_index"] = output_index

                item_id = _get_field(data, "item_id")
                if isinstance(item_id, str) and item_id:
                    chunk["tool_call_id"] = item_id

            elif event_type == "response.function_call_arguments.done":
                arguments = _get_field(data, "arguments")
                if isinstance(arguments, str):
                    chunk["tool_call_arguments"] = arguments

                output_index = _get_field(data, "output_index")
                if isinstance(output_index, int):
                    chunk["tool_call_index"] = output_index

                item_id = _get_field(data, "item_id")
                if isinstance(item_id, str) and item_id:
                    chunk["tool_call_id"] = item_id

            elif event_type == "response.output_item.done":
                item = _get_field(data, "item")
                item_type = _get_field(item, "type")
                if item_type == "function_call":
                    output_index = _get_field(data, "output_index")
                    if isinstance(output_index, int):
                        chunk["tool_call_index"] = output_index

                    tool_call: dict[str, Any] = {
                        "type": "function_call",
                        "id": _get_field(item, "id") or "",
                        "call_id": _get_field(item, "call_id") or "",
                        "name": _get_field(item, "name") or "",
                        "arguments": _get_field(item, "arguments") or "",
                    }
                    chunk["tool_call"] = cast(Any, tool_call)
                    if tool_call.get("id"):
                        chunk["tool_call_id"] = cast(str, tool_call["id"])

            yield chunk
        

        
