from typing import Literal, Optional

from rich.markdown import Markdown
from rich.text import Text

from textual.app import ComposeResult
from textual.widgets import Static


class ChatBubble(Static):
    def __init__(
        self,
        *,
        role: str,
        title: str | None,
        timestamp: str | None,
        content: str | Text = "",
        bordered: bool,
        render_mode: Literal["markdown", "markup"] = "markdown",
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.role = role
        self._title = title
        self._timestamp = timestamp
        self._content = content
        self._render_mode = render_mode

        self._title_widget = Static()
        self._content_widget = Static()

    def compose(self) -> ComposeResult:
        yield self._title_widget
        yield self._content_widget

    def on_mount(self) -> None:
        self._sync()

    def append_text(self, text: str) -> None:
        if not text:
            return
        if isinstance(self._content, Text):
            self._content.append(text)
        else:
            self._content += text
        self._sync_content()

    def set_text(self, text: str) -> None:
        self._content = text
        self._sync_content()

    def _sync(self) -> None:
        self._sync_title()
        self._sync_content()

    def _sync_title(self) -> None:
        title = Text()
        if self._title is not None:
            title.append(self._title)
        if self._timestamp is not None:
            title.append("  ", style="dim")
            title.append("•", style="dim")
            title.append(f"  {self._timestamp}", style="dim")
        self._title_widget.update(title)
        self._title_widget.add_class("bubble_title")

    def _sync_content(self) -> None:
        if isinstance(self._content, Text):
            self._content_widget.update(self._content)
            self._content_widget.add_class("bubble_content")
            return

        if self._render_mode == "markup":
            self._content_widget.update(Text.from_markup(self._content or ""))
        else:
            self._content_widget.update(Markdown(self._content or ""))
        self._content_widget.add_class("bubble_content")