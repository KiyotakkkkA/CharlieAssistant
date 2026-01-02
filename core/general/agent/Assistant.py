import json

import time

from typing import Any, Callable, Dict, Generator, List, Type, cast

from openai.types.responses import ResponseInputParam 

from core.general import Config
from core.providers import OpenAIProvider
from core.types.ai import (
    OpenRouterAIResponseChunk,
    AIRequest,
    ToolClassProtocol,
    ToolObject,
    FlatToolObject,
    AllowedAIToolTypes,
    AIProviders
)
from core.general.agent.tools import (
    SystemManagementTool,
    DockerTool
)
from core.types.ai.AIAssistant import AllowedAIProviders

class Assistant:
    def __init__(self) -> None:
        self.config = Config()

        self.current_provider = {
            'generation_fn': lambda: 'NotImplemented'
        }

        self.providers: AIProviders = {
            'openrouter': ("OpenAIProvider", OpenAIProvider, self._openrouter_generate_response, 'flat'),
        }

        self.request_params: AIRequest = {
            "stream": True,
        }

        self.tools: List[ToolObject | FlatToolObject] = []

        self.tools_classes: List[Type[ToolClassProtocol]] = [
            SystemManagementTool,
            DockerTool
        ]
        self._tool_handlers: Dict[str, Callable[..., Any]] = {}
    
    def with_provider(self, provider_id: AllowedAIProviders):
        selected_provider_meta = self.providers[provider_id]
        self.current_provider = {
            'generation_fn': selected_provider_meta[2]
        }
        self.provider = selected_provider_meta[1](self.config) # type: ignore

        if provider_id == 'openrouter':
            self.tools = [
                {
                    'type': 'web_search_preview'
                }
            ]

        self.load_tools(selected_provider_meta[3])

        return self
    
    def with_model(self, model_name):
        self.provider.set_model(model_name)
        return self
    
    def generate_response(self) -> Any:
        return self.current_provider['generation_fn']
        
    def _openrouter_generate_response(
        self,
        *,
        messages: ResponseInputParam | None = None,
        user_text: str = "",
        **kwargs,
    ) -> Generator[OpenRouterAIResponseChunk, None, None]:

        base_messages: ResponseInputParam = list(messages) if messages is not None else [
            {"role": "user", "content": user_text}
        ]

        def _emit(ev: dict) -> None:
            yield_chunk: OpenRouterAIResponseChunk = {
                "event": ev,
                "event_type": str(ev.get("type") or "tool_event"),
                "tool_event": ev,
            }
            nonlocal_yields.append(yield_chunk)

        nonlocal_yields: List[OpenRouterAIResponseChunk] = []

        while True:
            assistant_content_parts: List[str] = []
            tool_calls_acc: Dict[int, Dict[str, Any]] = {}

            request_kwargs: dict[str, Any] = {
                **self.request_params,
                **kwargs,
            }
            request_kwargs["tools"] = self.tools

            for chunk in self.provider.generate_response(
                messages=base_messages,
                **request_kwargs,
            ):
                if nonlocal_yields:
                    for y in nonlocal_yields:
                        yield y
                    nonlocal_yields.clear()

                yield chunk

                if chunk.get("ai_content_part"):
                    assistant_content_parts.append(str(chunk.get("ai_content_part") or ""))

                tool_call = chunk.get("tool_call")
                tool_call_index = chunk.get("tool_call_index")

                if isinstance(tool_call_index, int) and isinstance(tool_call, dict):
                    current = tool_calls_acc.get(tool_call_index)
                    if current is None:
                        current = {
                            "type": tool_call.get("type") or "function_call",
                            "id": tool_call.get("id") or "",
                            "call_id": tool_call.get("call_id") or "",
                            "name": tool_call.get("name") or "",
                            "arguments": tool_call.get("arguments") or "",
                        }
                        tool_calls_acc[tool_call_index] = current
                    else:
                        for k in ("type", "id", "call_id", "name", "arguments"):
                            v = tool_call.get(k)
                            if isinstance(v, str) and v:
                                current[k] = v

                delta = chunk.get("tool_call_arguments_delta")
                if isinstance(delta, str) and delta:
                    idx = chunk.get("tool_call_index")
                    if isinstance(idx, int):
                        current = tool_calls_acc.get(idx)
                        if current is None:
                            current = {
                                "type": "function_call",
                                "id": chunk.get("tool_call_id") or "",
                                "call_id": "",
                                "name": "",
                                "arguments": "",
                            }
                            tool_calls_acc[idx] = current
                        current["arguments"] = (current.get("arguments") or "") + delta

                done_args = chunk.get("tool_call_arguments")
                if isinstance(done_args, str):
                    idx = chunk.get("tool_call_index")
                    if isinstance(idx, int):
                        current = tool_calls_acc.get(idx)
                        if current is None:
                            current = {
                                "type": "function_call",
                                "id": chunk.get("tool_call_id") or "",
                                "call_id": "",
                                "name": "",
                                "arguments": done_args,
                            }
                            tool_calls_acc[idx] = current
                        else:
                            current["arguments"] = done_args

            if nonlocal_yields:
                for y in nonlocal_yields:
                    yield y
                nonlocal_yields.clear()

            tool_calls = [tool_calls_acc[i] for i in sorted(tool_calls_acc.keys())]
            assistant_content = "".join(assistant_content_parts)

            if assistant_content.strip():
                base_messages.append({"role": "assistant", "content": assistant_content})

            if not tool_calls:
                break

            for tc in tool_calls:
                tool_name = (tc.get("name") or "").strip()
                tool_call_id = (tc.get("call_id") or tc.get("id") or "").strip()
                raw_args = tc.get("arguments") or "{}"

                base_messages.append(
                    {
                        "type": "function_call",
                        "id": tc.get("id") or "",
                        "call_id": tc.get("call_id") or tool_call_id,
                        "name": tool_name,
                        "arguments": raw_args,
                    }
                )

                args: dict
                try:
                    parsed = json.loads(raw_args) if isinstance(raw_args, str) and raw_args.strip() else {}
                    args = parsed if isinstance(parsed, dict) else {}
                except Exception:
                    args = {}

                _emit({"type": "tool_call", "name": tool_name, "arguments": raw_args, "id": tool_call_id})

                handler = self._tool_handlers.get(tool_name)
                result_obj: Any
                duration_ms = 0
                if handler is None:
                    result_obj = {"error": f"Unknown tool: {tool_name}"}
                else:
                    t0 = time.perf_counter()
                    try:
                        result_obj = handler(**args)
                    except Exception as exc:
                        result_obj = {"error": f"{type(exc).__name__}: {exc}"}
                    duration_ms = int((time.perf_counter() - t0) * 1000)

                _emit(
                    {
                        "type": "tool_result",
                        "name": tool_name,
                        "result": result_obj,
                        "id": tool_call_id,
                        "duration_ms": duration_ms,
                    }
                )

                try:
                    tool_output = json.dumps(result_obj, ensure_ascii=False)
                except Exception:
                    tool_output = str(result_obj)

                base_messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call_id,
                        "output": tool_output,
                    }
                )
    
    def load_tools(self, mode: AllowedAIToolTypes) -> None:
        for tool_class in self.tools_classes:
            tool_object = tool_class.get_commands()

            for tool in tool_object:
                tool_def = tool['tool'].build_flat() if mode == 'flat' else tool['tool'].build()
                handler = tool.get("handler")

                tool_name = ""
                if isinstance(tool_def.get("function"), dict):
                    tool_name = str((tool_def.get("function") or {}).get("name") or "")
                elif isinstance(tool_def.get("name"), str):
                    tool_name = cast(str, tool_def.get("name") or "")

                if tool_name:
                    if callable(handler):
                        self._tool_handlers[tool_name] = cast(Callable[..., Any], handler)
                    self.tools.append(tool_def)