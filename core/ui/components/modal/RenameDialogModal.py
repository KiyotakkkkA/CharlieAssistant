from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


class RenameDialogModal(ModalScreen[Optional[str]]):
    def __init__(self, *, current_title: str) -> None:
        super().__init__()
        self._current_title = current_title

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Переименовать диалог", id="modal_title")
            self._input = Input(value=self._current_title, id="rename_input")
            yield self._input
            with Horizontal(id="modal_actions"):
                yield Button("Отмена", id="cancel", variant="default")
                yield Button("ОК", id="ok", variant="success")

    def on_mount(self) -> None:
        self._input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        value = (event.value or "").strip()
        self.dismiss(value if value else None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            value = (self._input.value or "").strip()
            self.dismiss(value if value else None)
        else:
            self.dismiss(None)
