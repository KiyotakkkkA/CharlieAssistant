import json

import time

from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Type, cast

from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolUnionParam

from core.general import Config
from core.providers import OpenAIProvider
from core.types.ai import AIChunk, AIRequest, ToolClassProtocol, ToolObject
from core.general.agent.tools import (
    SystemManagementTool,
)

class Assistant:
    def __init__(self) -> None:
        self.config = Config()
        self.provider = OpenAIProvider(self.config).set_model('mistralai/devstral-2512:free')

        self.request_params: AIRequest = {
            "stream": True,
        }

        self.tools: List[ToolObject] = []
        self._tool_handlers: Dict[str, Callable[..., Any]] = {}
        self.tools_classes: List[Type[ToolClassProtocol]] = [
            SystemManagementTool,
        ]

        self.load_tools()
    
    def chat_completion(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam] | None = None,
        user_text: str = "",
        max_tool_iterations: int = 6,
        on_tool_event: Optional[Callable[[dict], None]] = None,
        **kwargs,
    ) -> Generator[AIChunk, None, None]:

        base_messages: List[ChatCompletionMessageParam] = list(messages) if messages is not None else [
            {"role": "user", "content": user_text}
        ]

        def _emit(event: dict) -> None:
            if on_tool_event is not None:
                on_tool_event(event)

        for _iteration in range(max_tool_iterations):
            tool_calls_acc: Dict[int, dict] = {}
            assistant_content_parts: List[str] = []

            for chunk in self.provider.chat_completion(
                messages=base_messages,
                tools=cast(Iterable[ChatCompletionToolUnionParam], self.tools),
                **self.request_params,
                **kwargs,
            ):
                yield chunk

                delta = chunk["content"].choices[0].delta
                if delta.content:
                    assistant_content_parts.append(delta.content)

                if getattr(delta, "tool_calls", None):
                    for tc in (delta.tool_calls or []):
                        idx = tc.index
                        current = tool_calls_acc.get(idx)
                        if current is None:
                            current = {
                                "id": getattr(tc, "id", None),
                                "type": getattr(tc, "type", "function"),
                                "function": {
                                    "name": getattr(tc.function, "name", ""),
                                    "arguments": "",
                                },
                            }
                            tool_calls_acc[idx] = current

                        if getattr(tc, "id", None):
                            current["id"] = tc.id
                        if getattr(tc, "type", None):
                            current["type"] = tc.type
                        if tc.function and getattr(tc.function, "name", None):
                            current["function"]["name"] = tc.function.name
                        if tc.function and getattr(tc.function, "arguments", None):
                            current["function"]["arguments"] += tc.function.arguments

            tool_calls = [tool_calls_acc[i] for i in sorted(tool_calls_acc.keys())]
            assistant_content = "".join(assistant_content_parts)

            assistant_message: ChatCompletionMessageParam = {
                "role": "assistant",
                "content": assistant_content,
            }
            if tool_calls:
                assistant_message["tool_calls"] = tool_calls  # type: ignore[typeddict-item]
            base_messages.append(assistant_message)

            if not tool_calls:
                break

            for tc in tool_calls:
                fn = (tc.get("function") or {})
                tool_name = (fn.get("name") or "").strip()
                tool_call_id = (tc.get("id") or "").strip()
                raw_args = fn.get("arguments") or "{}"

                _emit({"type": "tool_call", "name": tool_name, "arguments": raw_args, "id": tool_call_id})

                args: dict
                try:
                    parsed = json.loads(raw_args) if isinstance(raw_args, str) and raw_args.strip() else {}
                    args = parsed if isinstance(parsed, dict) else {}
                except Exception:
                    args = {}

                result_obj: Any
                duration_ms = 0
                handler = self._tool_handlers.get(tool_name)
                if handler is None:
                    result_obj = {"error": f"Unknown tool: {tool_name}"}
                else:
                    t0 = time.perf_counter()
                    try:
                        result_obj = handler(**args)
                    except Exception as exc:
                        result_obj = {"error": f"{type(exc).__name__}: {exc}"}

                    duration_ms = int((time.perf_counter() - t0) * 1000)

                _emit({"type": "tool_result", "name": tool_name, "result": result_obj, "id": tool_call_id, "duration_ms": duration_ms})

                try:
                    tool_content = json.dumps(result_obj, ensure_ascii=False)
                except Exception:
                    tool_content = str(result_obj)

                tool_message: ChatCompletionMessageParam = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_content,
                }
                base_messages.append(tool_message)
    
    def load_tools(self) -> None:
        for tool_class in self.tools_classes:
            tool_object = tool_class.get_commands()

            for tool in tool_object:
                tool_name = tool["tool"]["function"]["name"]
                self._tool_handlers[tool_name] = tool["handler"]
                self.tools.append({
                    "type": tool['tool']['type'],
                    "function": tool['tool']['function'],
                })