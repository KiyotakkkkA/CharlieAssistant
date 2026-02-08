import asyncio
import json
from datetime import datetime
from typing import Optional
import inspect

from openai import APIStatusError
from openai.types.responses import ResponseInputParam
from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Footer, Header, Input
from textual import events

from core.general.agent.Assistant import Assistant
from core.ui.components.general import ASCIIDrawer
from core.ui.components.modal import ConfirmDeleteDialogModal, RenameDialogModal
from core.ui.components.sidebar import DialogSidebar
from core.types.chat import ChatEntry, ChatDialog
from core.stores import DialogStore

from core.ui.components.chat import ChatBubble
from core.ui.components.chat.CommandPalette import CommandPalette
from core.ui.css import APPLICATION_THEME

from core.prompts.MainSystemPrompt import SYSTEM_PROMPT_BASE


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
        self._system_prompt = SYSTEM_PROMPT_BASE.format(assistant_name="Чарли")
        self._store = DialogStore()
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
                    self._command_palette = CommandPalette(
                        commands=self.assistant.commands,
                        id="command_palette",
                        classes="hidden",
                    )
                    yield self._command_palette
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

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "chat_input":
            return

        value = event.value or ""
        cmd_token = self._extract_command_token(value)
        if cmd_token is None:
            if self._command_palette.is_open:
                self._command_palette.close()
            return

        self._command_palette.open(cmd_token)

    def on_key(self, event: events.Key) -> None:
        if not getattr(self, "_command_palette", None):
            return

        if not self._command_palette.is_open:
            return

        key = event.key
        if key in {"up", "down", "escape", "enter", "tab"}:
            event.prevent_default()
            event.stop()

        if key == "up":
            self._command_palette.move_selection(-1)
        elif key == "down":
            self._command_palette.move_selection(1)
        elif key == "escape":
            self._command_palette.close()
        elif key in {"enter", "tab"}:
            chosen = self._command_palette.choose_selected()
            if chosen:
                self._input.value = f"@{chosen} "
                self._input.cursor_position = len(self._input.value)
                self._command_palette.close()

    def _seed_dialog(self, dialog_id: str) -> None:
        self._add_banner(dialog_id)
        self._add_hint(dialog_id)
        self._add_system_prompt(dialog_id)
        self._render_active_dialog()

    def _add_system_prompt(self, dialog_id: str) -> None:
        entry = self._store.append_entry(
            dialog_id,
            self._store.make_entry(
                role="system",
                title="System Prompt",
                timestamp=None,
                content=self._system_prompt,
                bordered=False,
                build_to_llm=True,
                build_to_ui=False,
            ),
        )
        self._mount_entry(dialog_id, entry, animate=False)

    def _add_banner(self, dialog_id: str) -> None:
        banner = ASCIIDrawer(text="Charlie CLI : ALPHA", fill_background=False)
        if not banner.content().plain.strip():
            return

        entry = self._store_entry(
            dialog_id,
            self._store.make_entry(
                role="system",
                title=None,
                timestamp=None,
                content=banner.content(),
                bordered=False,
                render_mode="markup",
                build_to_llm=False,
                build_to_ui=True,
            ),
        )
        self._mount_entry(dialog_id, entry, animate=False)

    def _add_hint(self, dialog_id: str) -> None:
        entry = self._store_entry(
            dialog_id,
            self._store.make_entry(
                role="system",
                title=None,
                timestamp=None,
                content="Начните диалог: введите текст снизу и нажмите **Enter**.",
                build_to_llm=False,
                build_to_ui=True,
            ),
        )
        self._mount_entry(dialog_id, entry, animate=False)

    def _create_dialog(self, *, title: Optional[str] = None, make_active: bool = False) -> ChatDialog:
        dialog = self._store.create_dialog(title=title, make_active=make_active)
        self._sidebar.add_dialog(dialog_id=dialog["id"], title=dialog["title"])
        if make_active:
            self._set_active_dialog(dialog["id"])
        return dialog

    def _set_active_dialog(self, dialog_id: str) -> None:
        self._store.set_active(dialog_id)
        self._sidebar.set_active(dialog_id=dialog_id)
        self._render_active_dialog()

    def _render_active_dialog(self) -> None:
        active_id = self._store.active_dialog_id
        if not active_id:
            return

        self._clear_chat_scroll()
        for entry in self._store.list_entries(active_id):
            if not entry.get("build_to_ui", True):
                continue
            self._chat_scroll.mount(self._build_bubble(entry))
        self._chat_scroll.scroll_end(animate=False)

    def _clear_chat_scroll(self) -> None:
        for child in list(self._chat_scroll.children):
            child.remove()

    def _store_entry(
        self,
        dialog_id: str,
        entry: ChatEntry,
        build_to_llm: bool | None = None,
        build_to_ui: bool | None = None,
    ) -> ChatEntry:
        return self._store.append_entry(
            dialog_id,
            entry,
            build_to_llm=build_to_llm,
            build_to_ui=build_to_ui,
        )

    def _should_mount_entry(self, dialog_id: str, entry: ChatEntry) -> bool:
        if dialog_id != self._store.active_dialog_id:
            return False
        return bool(entry.get("build_to_ui", True))

    def _mount_entry(self, dialog_id: str, entry: ChatEntry, *, animate: bool = False) -> None:
        if not self._should_mount_entry(dialog_id, entry):
            return
        bubble = self._build_bubble(entry)
        self._chat_scroll.mount(bubble)
        self._chat_scroll.scroll_end(animate=animate)

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
        self._input.value = ""
        await self._handle_submitted_text((event.value or "").strip())

    def send_as_user(self, message: str) -> None:
        text = (message or "").strip()
        if not text:
            return
        self.run_worker(self._handle_submitted_text(text), exclusive=True)

    def apply_theme_css(self, css: str) -> None:
        self.__class__.CSS = css
        app_path = inspect.getfile(self.__class__)
        read_from = (app_path, f"{self.__class__.__name__}.CSS")
        self.stylesheet.add_source(css, read_from=read_from, is_default_css=False)
        self.refresh_css(animate=False)
        self.refresh(layout=True)

    async def _handle_submitted_text(self, text: str) -> None:
        text = (text or "").strip()
        if not text or self._busy:
            return

        if text.startswith("@"):
            dialog_id = self._ensure_active_dialog()
            handled = self._try_run_command(dialog_id=dialog_id, text=text)
            if handled:
                self._input.focus()
                return

        self._busy = True
        self._input.disabled = True

        dialog_id = self._ensure_active_dialog()
        self._append_user(dialog_id, text)

        ai_bubble, ai_entry = self._append_ai_placeholder(dialog_id)
        await self._stream_ai_reply(dialog_id=dialog_id, user_text=text, bubble=ai_bubble, entry=ai_entry)

        self._busy = False
        self._input.disabled = False
        self._input.focus()

    def _extract_command_token(self, value: str) -> str | None:
        raw = value or ""
        if not raw.startswith("@"):
            return None
        after = raw[1:]
        if not after:
            return ""
        if " " in after:
            return None
        return after.strip()

    def _append_system(self, dialog_id: str, content: str | Text) -> None:
        entry = self._store_entry(
            dialog_id,
            self._store.make_entry(
                role="system",
                title="Команда",
                timestamp=_now_hhmm(),
                content=content,
                render_mode="markdown" if isinstance(content, str) else "markup",
                build_to_llm=False,
                build_to_ui=True,
            ),
        )
        self._mount_entry(dialog_id, entry, animate=False)

    def _try_run_command(self, *, dialog_id: str, text: str) -> bool:
        raw = (text or "").strip()
        if not raw.startswith("@"):
            return False

        payload = raw[1:].strip()
        if not payload:
            self._append_system(dialog_id, "Укажите команду после **@**.")
            return True

        parts = payload.split(maxsplit=1)
        name = parts[0].strip()
        args = parts[1] if len(parts) > 1 else ""

        cmd = (self.assistant.commands or {}).get(name)
        if cmd is None:
            self._append_system(dialog_id, f"Неизвестная команда: **@{name}**")
            return True

        try:
            out = cmd.execute(app=self, assistant=self.assistant, dialog_id=dialog_id, args=args)
        except Exception as exc:
            self._append_system(dialog_id, f"Ошибка команды **@{name}**: {type(exc).__name__}: {exc}")
            return True

        if out is not None and (str(out).strip() if isinstance(out, str) else True):
            self._append_system(dialog_id, out)

        return True

    def _append_user(self, dialog_id: str, content: str) -> None:
        entry = self._store_entry(
            dialog_id,
            self._store.make_entry(
                role="user",
                title="Вы",
                timestamp=_now_hhmm(),
                content=content,
                build_to_llm=True,
                build_to_ui=True,
            ),
            True,
        )
        self._mount_entry(dialog_id, entry, animate=True)

    def _append_ai_placeholder(self, dialog_id: str) -> tuple[ChatBubble, ChatEntry]:
        entry = self._store_entry(
            dialog_id,
            self._store.make_entry(
                role="assistant",
                title=self.assistant.provider.model_name,
                timestamp=_now_hhmm(),
                content="",
                build_to_llm=True,
                build_to_ui=True,
            ),
            True,
        )

        bubble = self._build_bubble(entry)
        if self._should_mount_entry(dialog_id, entry):
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

        messages = self._store.build_llm_messages(dialog_id)

        def run_sync_stream() -> str:
            nonlocal accumulated
            for chunk in self.assistant.generate_response(messages=messages, user_text=user_text):
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
            if isinstance(exc, APIStatusError):
                http_error_content = json.loads(exc.response.content.decode('utf-8'))
                error_text = f"\n\n**Ошибка:** {http_error_content['error']['message']}"
            else:
                error_text = f"\n\n**Ошибка:** {type(exc).__name__}: {exc}"

            entry["content"] += error_text
            bubble.append_text(error_text)

    def _ensure_active_dialog(self) -> str:
        active_id = self._store.active_dialog_id
        if active_id is None:
            dialog = self._create_dialog(title="Диалог", make_active=True)
            self._seed_dialog(dialog_id=dialog["id"])
            return dialog["id"]
        return active_id

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
        dialog_id = self._store.active_dialog_id
        dialog = self._store.get_dialog(dialog_id or "")
        if not dialog_id or not dialog:
            return
        current_title = dialog["title"]

        def _done(result: Optional[str]) -> None:
            if not result:
                return
            self._rename_dialog(dialog_id, result)

        self.push_screen(RenameDialogModal(current_title=current_title), _done)

    def _rename_dialog(self, dialog_id: str, title: str) -> None:
        self._store.rename_dialog(dialog_id, title)
        self._sidebar.rename_dialog(dialog_id=dialog_id, title=title)

    def action_delete_dialog(self) -> None:
        if self._busy:
            return
        dialog_id = self._store.active_dialog_id
        if not dialog_id:
            return
        dialog = self._store.get_dialog(dialog_id)
        if not dialog:
            return
        title = dialog["title"]

        def _done(confirmed: bool | None) -> None:
            if confirmed is True:
                self._delete_dialog(dialog_id)

        self.push_screen(ConfirmDeleteDialogModal(title=title), _done)

    def _delete_dialog(self, dialog_id: str) -> None:
        next_id = self._store.delete_dialog(dialog_id)
        self._sidebar.remove_dialog(dialog_id=dialog_id)

        if next_id is None:
            dialog = self._create_dialog(title="Диалог 1", make_active=True)
            self._seed_dialog(dialog_id=dialog["id"])
        else:
            self._set_active_dialog(next_id)