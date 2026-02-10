from typing import Literal, Optional, cast

from rich.text import Text

from openai.types.responses import ResponseInputParam, ResponseInputItemParam

from core.types.chat import ChatDialog, ChatEntry


class DialogStore:
    def __init__(self) -> None:
        self._dialogs: dict[str, ChatDialog] = {}
        self._active_dialog_id: Optional[str] = None
        self._dialog_counter: int = 0

    @property
    def active_dialog_id(self) -> Optional[str]:
        return self._active_dialog_id

    def create_dialog(self, *, title: Optional[str] = None, make_active: bool = False) -> ChatDialog:
        self._dialog_counter += 1
        dialog_id = f"dialog-{self._dialog_counter}"
        dialog_title = title or f"Диалог {self._dialog_counter}"
        dialog: ChatDialog = {"id": dialog_id, "title": dialog_title, "messages": []}
        self._dialogs[dialog_id] = dialog

        if make_active:
            self.set_active(dialog_id)
        return dialog

    def set_active(self, dialog_id: str) -> None:
        if dialog_id == self._active_dialog_id:
            return
        if dialog_id not in self._dialogs:
            return
        self._active_dialog_id = dialog_id

    def get_dialog(self, dialog_id: str) -> Optional[ChatDialog]:
        return self._dialogs.get(dialog_id)

    def list_entries(self, dialog_id: str) -> list[ChatEntry]:
        dialog = self._dialogs.get(dialog_id)
        if not dialog:
            return []
        return dialog["messages"]

    def append_entry(
        self,
        dialog_id: str,
        entry: ChatEntry,
        *,
        build_to_llm: bool | None = None,
        build_to_ui: bool | None = None,
    ) -> ChatEntry:
        if dialog_id not in self._dialogs:
            return entry

        if build_to_llm is not None:
            entry["build_to_llm"] = bool(build_to_llm)
        else:
            entry["build_to_llm"] = bool(entry.get("build_to_llm", False))

        if build_to_ui is not None:
            entry["build_to_ui"] = bool(build_to_ui)
        else:
            entry["build_to_ui"] = bool(entry.get("build_to_ui", False))

        self._dialogs[dialog_id]["messages"].append(entry)
        return entry

    def make_entry(
        self,
        *,
        role: str,
        content: str | Text,
        title: str | None = None,
        timestamp: str | None = None,
        bordered: bool = True,
        render_mode: Literal["markdown", "markup"] = "markdown",
        build_to_llm: bool = False,
        build_to_ui: bool = False,
    ) -> ChatEntry:
        return ChatEntry(
            role=role,
            title=title,
            timestamp=timestamp,
            content=content,
            bordered=bordered,
            render_mode=render_mode,
            build_to_llm=build_to_llm,
            build_to_ui=build_to_ui,
        )

    def ensure_active(self, *, title: str = "Диалог") -> str:
        if self._active_dialog_id is None:
            dialog = self.create_dialog(title=title, make_active=True)
            return dialog["id"]
        return self._active_dialog_id

    def rename_dialog(self, dialog_id: str, title: str) -> None:
        if dialog_id not in self._dialogs:
            return
        self._dialogs[dialog_id]["title"] = title

    def delete_dialog(self, dialog_id: str) -> Optional[str]:
        if dialog_id not in self._dialogs:
            return self._active_dialog_id
        del self._dialogs[dialog_id]

        if self._active_dialog_id == dialog_id:
            self._active_dialog_id = next(iter(self._dialogs.keys()), None)
        return self._active_dialog_id

    def build_llm_messages(self, dialog_id: str) -> ResponseInputParam:
        dialog = self._dialogs.get(dialog_id)
        if not dialog or not dialog.get("messages"):
            return []

        messages: list[ResponseInputItemParam] = []
        for entry in dialog["messages"]:
            role = entry.get("role")
            if not entry.get("build_to_llm", False):
                continue
            if role not in {"user", "assistant", "system"}:
                continue
            content = entry.get("content", "")
            if isinstance(content, Text):
                content_str = content.plain
            else:
                content_str = str(content or "")
            if role == "assistant" and not content_str.strip():
                continue
            messages.append(cast(ResponseInputItemParam, {"role": role, "content": content_str}))

        return messages
