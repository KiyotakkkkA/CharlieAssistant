import asyncio
from datetime import datetime
from typing import Optional

from openai.types.responses import ResponseInputParam
from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Footer, Header, Input

from core.general.agent.Assistant import Assistant
from core.ui.components.general import ASCIIDrawer
from core.ui.components.modal import ConfirmDeleteDialogModal, RenameDialogModal
from core.ui.components.sidebar import DialogSidebar
from core.types.chat import ChatDialog, ChatEntry

from core.ui.components.chat import ChatBubble
from core.ui.css import APPLICATION_THEME


def _now_hhmm() -> str:
    return datetime.now().strftime("%H:%M")


class CharlieChatApp(App):
    CSS = APPLICATION_THEME.create()
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        ("ctrl+b", "toggle_sidebar", "Диалоги"),
        ("ctrl+n", "new_dialog", "Новый диалог"),
        ("ctrl+e", "rename_dialog", "Переименовать"),
        ("ctrl+d", "delete_dialog", "Удалить"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(
        self,
        *,
        assistant: Assistant,
    ) -> None:
        super().__init__()
        self.assistant = assistant
        self._dialogs: dict[str, ChatDialog] = {}
        self._active_dialog_id: Optional[str] = None
        self._dialog_counter: int = 0
        self._busy: bool = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="root"):
            self._sidebar = DialogSidebar(id="sidebar")
            yield self._sidebar

            with Container(id="chat_area"):
                self._chat_scroll = VerticalScroll(id="chat_scroll")
                yield self._chat_scroll
                with Container(id="composer"):
                    self._input = Input(
                        placeholder="Напишите сообщение и нажмите Enter… (Ctrl+C — выход)",
                        id="chat_input",
                    )
                    yield self._input
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Чарли"
        self.sub_title = "ИИ Ассистент"
        dialog = self._create_dialog(title="Диалог 1", make_active=True)
        self._seed_dialog(dialog_id=dialog["id"])
        self._input.focus()

    def _seed_dialog(self, dialog_id: str) -> None:
        self._add_banner(dialog_id)
        self._add_hint(dialog_id)
        self._render_active_dialog()

    def _add_banner(self, dialog_id: str) -> None:
        banner = ASCIIDrawer(text="Charlie CLI : ALPHA", fill_background=False)
        if not banner.content().plain.strip():
            return

        entry = self._store_entry(
            dialog_id,
            ChatEntry(
                role="system",
                title=None,
                timestamp=None,
                content=banner.content(),
                bordered=False,
                render_mode="markup",
            ),
        )

        if dialog_id == self._active_dialog_id:
            self._chat_scroll.mount(self._build_bubble(entry))

    def _add_hint(self, dialog_id: str) -> None:
        entry = self._store_entry(
            dialog_id,
            ChatEntry(
                role="system",
                title=None,
                timestamp=None,
                content="Начните диалог: введите текст снизу и нажмите **Enter**.",
                bordered=True,
                render_mode="markdown",
            ),
        )

        if dialog_id == self._active_dialog_id:
            self._chat_scroll.mount(self._build_bubble(entry))

    def _create_dialog(self, *, title: Optional[str] = None, make_active: bool = False) -> ChatDialog:
        self._dialog_counter += 1
        dialog_id = f"dialog-{self._dialog_counter}"
        dialog_title = title or f"Диалог {self._dialog_counter}"
        dialog: ChatDialog = {"id": dialog_id, "title": dialog_title, "messages": []}
        self._dialogs[dialog_id] = dialog

        self._sidebar.add_dialog(dialog_id=dialog_id, title=dialog_title)

        if make_active:
            self._set_active_dialog(dialog_id)
        return dialog

    def _set_active_dialog(self, dialog_id: str) -> None:
        if dialog_id == self._active_dialog_id:
            return
        self._active_dialog_id = dialog_id

        self._sidebar.set_active(dialog_id=dialog_id)

        self._render_active_dialog()

    def _render_active_dialog(self) -> None:
        if not self._active_dialog_id:
            return

        self._clear_chat_scroll()
        for entry in self._dialogs[self._active_dialog_id]["messages"]:
            self._chat_scroll.mount(self._build_bubble(entry))
        self._chat_scroll.scroll_end(animate=False)

    def _clear_chat_scroll(self) -> None:
        for child in list(self._chat_scroll.children):
            child.remove()

    def _store_entry(self, dialog_id: str, entry: ChatEntry) -> ChatEntry:
        self._dialogs[dialog_id]["messages"].append(entry)
        return entry

    def _build_bubble(self, entry: ChatEntry) -> ChatBubble:
        classes = ["bubble"]
        if entry["role"] == "user":
            classes.append("bubble_user")
        elif entry["role"] == "assistant":
            classes.append("bubble_ai")

        return ChatBubble(
            role=entry["role"],
            title=entry["title"],
            timestamp=entry["timestamp"],
            content=entry["content"],
            show_tool_calls=entry["role"] == "assistant",
            render_mode=entry["render_mode"],
            classes=" ".join(classes),
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = (event.value or "").strip()
        if not text or self._busy:
            self._input.value = ""
            return

        self._busy = True
        self._input.disabled = True

        dialog_id = self._ensure_active_dialog()
        self._append_user(dialog_id, text)
        self._input.value = ""

        ai_bubble, ai_entry = self._append_ai_placeholder(dialog_id)
        await self._stream_ai_reply(dialog_id=dialog_id, user_text=text, bubble=ai_bubble, entry=ai_entry)

        self._busy = False
        self._input.disabled = False
        self._input.focus()

    def _append_user(self, dialog_id: str, content: str) -> None:
        entry = self._store_entry(
            dialog_id,
            ChatEntry(
                role="user",
                title="Вы",
                timestamp=_now_hhmm(),
                content=content,
                bordered=True,
                render_mode="markdown",
            ),
        )

        if dialog_id == self._active_dialog_id:
            bubble = self._build_bubble(entry)
            self._chat_scroll.mount(bubble)
            self._chat_scroll.scroll_end(animate=True)

    def _append_ai_placeholder(self, dialog_id: str) -> tuple[ChatBubble, ChatEntry]:
        entry = self._store_entry(
            dialog_id,
            ChatEntry(
                role="assistant",
                title=self.assistant.provider.model_name,
                timestamp=_now_hhmm(),
                content="",
                bordered=True,
                render_mode="markdown",
            ),
        )

        bubble = self._build_bubble(entry)
        if dialog_id == self._active_dialog_id:
            self._chat_scroll.mount(bubble)
            self._chat_scroll.scroll_end(animate=False)

        return bubble, entry

    async def _stream_ai_reply(self, *, dialog_id: str, user_text: str, bubble: ChatBubble, entry: ChatEntry) -> None:
        accumulated = ""

        tool_events: list[dict] = []

        def update_tools_view() -> None:
            if not tool_events:
                return

            used = [ev for ev in tool_events if ev.get("type") == "tool_result"]
            if not used:
                return

            total_ms = 0
            tools_view = Text()
            tools_view.append("Использованные инструменты", style="bold yellow")

            for ev in used:
                name = ev.get("name") or ""
                ms = int(ev.get("duration_ms") or 0)
                total_ms += ms
                tools_view.append("\n• ", style="dim")
                tools_view.append(name, style="cyan")
                tools_view.append(f" — {ms} ms", style="dim")

            tools_view.append("\n\nИтого: ", style="dim")
            tools_view.append(f"{total_ms} ms", style="bold")
            self.call_from_thread(bubble.set_tool_renderable, tools_view)

        def on_tool_event(ev: dict) -> None:
            tool_events.append(ev)
            update_tools_view()

        messages = self._build_llm_messages(dialog_id)

        def run_sync_stream() -> str:
            nonlocal accumulated
            for chunk in self.assistant.chat_completion(messages=messages, user_text=user_text):
                tool_ev = chunk.get("tool_event")
                if isinstance(tool_ev, dict) and tool_ev:
                    on_tool_event(tool_ev)

                content_chunk_data = chunk.get("ai_content_part") or ""
                if not content_chunk_data:
                    continue
                accumulated += content_chunk_data
                entry["content"] += content_chunk_data
                self.call_from_thread(bubble.append_text, content_chunk_data)
                self.call_from_thread(self._chat_scroll.scroll_end, animate=False)
            return accumulated
            
        try:
            await asyncio.to_thread(run_sync_stream)
        except Exception as exc:
            error_text = f"\n\n**Ошибка:** {type(exc).__name__}: {exc}"
            entry["content"] += error_text
            bubble.append_text(error_text)

    def _build_llm_messages(self, dialog_id: str) -> ResponseInputParam:
        dialog = self._dialogs.get(dialog_id)
        if not dialog:
            return []

        messages: ResponseInputParam = []
        for entry in dialog["messages"]:
            role = entry.get("role")
            if role not in {"user", "assistant"}:
                continue
            content = entry.get("content", "")
            if isinstance(content, Text):
                content_str = content.plain
            else:
                content_str = str(content or "")
            if role == "assistant" and not content_str.strip():
                continue
            if role == "user":
                messages.append({"role": "user", "content": content_str})
            else:
                messages.append({"role": "assistant", "content": content_str})

        return messages

    def _ensure_active_dialog(self) -> str:
        if self._active_dialog_id is None:
            dialog = self._create_dialog(title="Диалог", make_active=True)
            self._seed_dialog(dialog_id=dialog["id"])
        return self._active_dialog_id or ""

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar", Container)
        sidebar.toggle_class("collapsed")

    def action_new_dialog(self) -> None:
        dialog = self._create_dialog()
        self._seed_dialog(dialog_id=dialog["id"])

    def on_dialog_sidebar_dialog_selected(self, event: DialogSidebar.DialogSelected) -> None:
        self._set_active_dialog(event.dialog_id)

    def action_rename_dialog(self) -> None:
        if self._busy:
            return
        dialog_id = self._active_dialog_id
        if not dialog_id or dialog_id not in self._dialogs:
            return
        current_title = self._dialogs[dialog_id]["title"]

        def _done(result: Optional[str]) -> None:
            if not result:
                return
            self._rename_dialog(dialog_id, result)

        self.push_screen(RenameDialogModal(current_title=current_title), _done)

    def _rename_dialog(self, dialog_id: str, title: str) -> None:
        self._dialogs[dialog_id]["title"] = title
        self._sidebar.rename_dialog(dialog_id=dialog_id, title=title)

    def action_delete_dialog(self) -> None:
        if self._busy:
            return
        dialog_id = self._active_dialog_id
        if not dialog_id or dialog_id not in self._dialogs:
            return
        title = self._dialogs[dialog_id]["title"]

        def _done(confirmed: bool | None) -> None:
            if confirmed is True:
                self._delete_dialog(dialog_id)

        self.push_screen(ConfirmDeleteDialogModal(title=title), _done)

    def _delete_dialog(self, dialog_id: str) -> None:
        if dialog_id not in self._dialogs:
            return
        del self._dialogs[dialog_id]
        self._sidebar.remove_dialog(dialog_id=dialog_id)

        next_id = next(iter(self._dialogs.keys()), None)
        if next_id is None:
            dialog = self._create_dialog(title="Диалог 1", make_active=True)
            self._seed_dialog(dialog_id=dialog["id"])
        else:
            self._set_active_dialog(next_id)