from typing import Literal, TypedDict, Optional

from rich.text import Text


class ChatEntry(TypedDict):
    role: str
    title: str | None
    content: str | Text
    timestamp: str | None
    bordered: bool
    render_mode: Literal["markdown", "markup"]


class ChatDialog(TypedDict):
    id: str
    title: str
    messages: list[ChatEntry]