from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from rich.text import Text


CommandOutput = str | Text | None


class ICommand(ABC):
    description: str = ""

    @abstractmethod
    def execute(self, *, app: Any, assistant: Any, dialog_id: str, args: str) -> CommandOutput:
        raise NotImplementedError

    def send_as_user(self, *, app: Any, message: str) -> None:
        fn = getattr(app, "send_as_user", None)
        if callable(fn):
            fn(message)
            return

        input_widget = getattr(app, "_input", None)
        if input_widget is not None:
            try:
                input_widget.value = message
            except Exception:
                pass
