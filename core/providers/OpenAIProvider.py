from openai import OpenAI, Stream
from openai.types.responses import ResponseInputParam, ResponseStreamEvent

from typing import Any, Generator, cast

from core.general import Config
from core.exeptions import NoClientError
from core.types.ai import OpenRouterAIResponseChunk
from core.providers.BaseAIProvider import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        super().__init__(
            api_key=Config.OPENAI_API_KEY,
            api_base=Config.OPENAI_API_BASE
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

    def add_assistant_message(self, messages: list[dict[str, Any]], *, content: str, tool_calls: list[dict[str, Any]]) -> None:
        if content.strip():
            messages.append({"role": "assistant", "content": content})

    def add_tool_call_message(self, messages: list[dict[str, Any]], *, tool_call: dict[str, Any]) -> None:
        tool_name = str((tool_call.get("name") or "")).strip()
        raw_args = tool_call.get("arguments") or "{}"
        call_id = str((tool_call.get("call_id") or tool_call.get("id") or "")).strip()

        messages.append(
            {
                "type": "function_call",
                "id": tool_call.get("id") or "",
                "call_id": tool_call.get("call_id") or call_id,
                "name": tool_name,
                "arguments": raw_args,
            }
        )

    def add_tool_result_message(
        self,
        messages: list[dict[str, Any]],
        *,
        tool_name: str,
        tool_call: dict[str, Any],
        output: str,
    ) -> None:
        call_id = str((tool_call.get("call_id") or tool_call.get("id") or "")).strip()
        messages.append({"type": "function_call_output", "call_id": call_id, "output": output})
        

        
