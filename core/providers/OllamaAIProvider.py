import json
from typing import Any, Generator

from ollama import Client, ChatResponse
from openai.types.responses import ResponseInputParam

from core.general import Config
from core.exeptions import NoClientError
from core.types.ai import OllamaAIResponseChunk
from core.providers.BaseAIProvider import BaseAIProvider


class OllamaAIProvider(BaseAIProvider):
    REQUIRES_API_KEY = False
    REQUIRES_API_BASE = False

    def __init__(self):
        super().__init__(
            api_key=Config.OLLAMA_API_KEY,
            api_base=Config.OLLAMA_API_BASE
        )

    def provider_setup(self):
        headers: dict[str, str] | None = None
        if self.api_key:
            headers = {"Authorization": f"Bearer {self.api_key}"}

        self.client = Client(host=self.api_base, headers=headers)

    @staticmethod
    def _coerce_messages(messages: ResponseInputParam) -> list[dict[str, Any]]:
        coerced: list[dict[str, Any]] = []
        for msg in list(messages):
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            if role not in {"system", "user", "assistant", "tool"}:
                continue

            content = msg.get("content")
            content_str = content if isinstance(content, str) else str(content or "")

            if role == "tool":
                tool_name = msg.get("tool_name") or msg.get("name")
                if isinstance(tool_name, str) and tool_name:
                    coerced.append({"role": "tool", "tool_name": tool_name, "content": content_str})  # type: ignore[typeddict-item]
                else:
                    coerced.append({"role": "tool", "content": content_str})
            elif role == "assistant":
                out: dict[str, Any] = {"role": "assistant", "content": content_str}
                thinking = msg.get("thinking")
                if isinstance(thinking, str) and thinking:
                    out["thinking"] = thinking
                tool_calls = msg.get("tool_calls")
                if isinstance(tool_calls, list):
                    out["tool_calls"] = tool_calls
                coerced.append(out)
            else:
                coerced.append({"role": str(role), "content": content_str})

        return coerced

    @staticmethod
    def _get_field(obj: Any, key: str) -> Any:
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)

    def generate_response(self, messages: ResponseInputParam, **kwargs) -> Generator[OllamaAIResponseChunk, None, None]:
        if not self.client:
            raise NoClientError("OllamaAIProvider")

        stream = bool(kwargs.get("stream", True))
        tools = kwargs.get("tools")

        allowed_passthrough = {"format", "options", "keep_alive", "think"}
        call_kwargs: dict[str, Any] = {k: v for k, v in kwargs.items() if k in allowed_passthrough}
        if tools is not None:
            call_kwargs["tools"] = tools
        call_kwargs["stream"] = stream

        ollama_messages = self._coerce_messages(messages)

        if not stream:
            data: ChatResponse = self.client.chat(
                model=self.model_name,
                messages=ollama_messages,
                **call_kwargs,
            )

            msg = self._get_field(data, "message") or {}
            text = self._get_field(msg, "content") or ""
            if not isinstance(text, str):
                text = str(text)

            yield OllamaAIResponseChunk(event=data, event_type="ollama.chat.done", ai_content_part=text)

            tool_calls = self._get_field(msg, "tool_calls")
            if isinstance(tool_calls, list):
                for i, tc in enumerate(tool_calls):
                    fn = self._get_field(tc, "function") or {}
                    fn_name = self._get_field(fn, "name") or ""
                    fn_args = self._get_field(fn, "arguments")
                    if isinstance(fn_args, str):
                        args_str = fn_args
                    else:
                        try:
                            args_str = json.dumps(fn_args or {}, ensure_ascii=False)
                        except Exception:
                            args_str = str(fn_args or "")

                    idx = self._get_field(fn, "index")
                    tool_idx = int(idx) if isinstance(idx, int) else i

                    yield OllamaAIResponseChunk(
                        event=data,
                        event_type="ollama.tool_call",
                        tool_call_index=tool_idx,
                        tool_call={
                            "type": "function_call",
                            "id": "",
                            "call_id": "",
                            "name": str(fn_name),
                            "arguments": args_str,
                        },
                    )

            return

        for part in self.client.chat(
            model=self.model_name,
            messages=ollama_messages,
            **call_kwargs,
        ):
            msg = self._get_field(part, "message") or {}

            delta = self._get_field(msg, "content") or ""
            if isinstance(delta, str) and delta:
                yield OllamaAIResponseChunk(event=part, event_type="ollama.chat.delta", ai_content_part=delta)

            tool_calls = self._get_field(msg, "tool_calls")
            if isinstance(tool_calls, list) and tool_calls:
                for i, tc in enumerate(tool_calls):
                    fn = self._get_field(tc, "function") or {}
                    fn_name = self._get_field(fn, "name") or ""
                    fn_args = self._get_field(fn, "arguments")

                    if isinstance(fn_args, str):
                        args_str = fn_args
                    else:
                        try:
                            args_str = json.dumps(fn_args or {}, ensure_ascii=False)
                        except Exception:
                            args_str = str(fn_args or "")

                    idx = self._get_field(fn, "index")
                    tool_idx = int(idx) if isinstance(idx, int) else i

                    yield OllamaAIResponseChunk(
                        event=part,
                        event_type="ollama.tool_call",
                        tool_call_index=tool_idx,
                        tool_call={
                            "type": "function_call",
                            "id": "",
                            "call_id": "",
                            "name": str(fn_name),
                            "arguments": args_str,
                        },
                    )

            if self._get_field(part, "done") is True:
                yield OllamaAIResponseChunk(event=part, event_type="ollama.chat.done")

    def add_assistant_message(self, messages: list[dict[str, Any]], *, content: str, tool_calls: list[dict[str, Any]]) -> None:
        if not content.strip() and not tool_calls:
            return

        msg: dict[str, Any] = {"role": "assistant", "content": content}

        if tool_calls:
            calls_payload: list[dict[str, Any]] = []
            for idx, tc in enumerate(tool_calls):
                tool_name = str((tc.get("name") or "")).strip()
                raw_args = tc.get("arguments") or "{}"

                args_dict: dict[str, Any]
                try:
                    parsed = json.loads(raw_args) if isinstance(raw_args, str) and raw_args.strip() else {}
                    args_dict = parsed if isinstance(parsed, dict) else {}
                except Exception:
                    args_dict = {}

                call_index = tc.get("index")
                if isinstance(call_index, int):
                    idx = call_index

                calls_payload.append(
                    {
                        "type": "function",
                        "function": {"index": idx, "name": tool_name, "arguments": args_dict},
                    }
                )

            msg["tool_calls"] = calls_payload

        messages.append(msg)

    def add_tool_result_message(
        self,
        messages: list[dict[str, Any]],
        *,
        tool_name: str,
        tool_call: dict[str, Any],
        output: str,
    ) -> None:
        messages.append({"role": "tool", "tool_name": tool_name, "content": output})
