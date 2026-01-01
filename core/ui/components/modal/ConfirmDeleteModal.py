from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmDeleteDialogModal(ModalScreen[bool]):
    def __init__(self, *, title: str) -> None:
        super().__init__()
        self._title = title

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Удалить диалог?", id="modal_title")
            yield Static(f"Вы уверены, что хотите удалить: {self._title}", id="modal_message")
            with Horizontal(id="modal_actions"):
                yield Button("Отмена", id="cancel", variant="default")
                yield Button("Удалить", id="delete", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "delete")
