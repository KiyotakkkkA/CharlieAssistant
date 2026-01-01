from dataclasses import dataclass
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import ListItem, ListView, Static


class DialogSidebar(Container):

    @dataclass
    class DialogSelected(Message):
        dialog_id: str

    def compose(self) -> ComposeResult:
        yield Static("Список диалогов", id="sidebar_title")
        self._dialog_list = ListView(id="dialog_list")
        yield self._dialog_list

    @property
    def dialog_list(self) -> ListView:
        return self._dialog_list

    def add_dialog(self, *, dialog_id: str, title: str) -> None:
        self._dialog_list.append(ListItem(Static(title), id=dialog_id))

    def rename_dialog(self, *, dialog_id: str, title: str) -> None:
        item = self._find_item(dialog_id)
        if not item:
            return
        label = item.query_one(Static)
        label.update(title)

    def remove_dialog(self, *, dialog_id: str) -> None:
        item = self._find_item(dialog_id)
        if not item:
            return
        item.remove()

    def set_active(self, *, dialog_id: str) -> None:
        for index, child in enumerate(self._dialog_list.children):
            if isinstance(child, ListItem) and child.id == dialog_id:
                self._dialog_list.index = index
                break

    def get_active_id(self) -> Optional[str]:
        index = self._dialog_list.index
        if index is None:
            return None
        try:
            item = self._dialog_list.children[index]
        except Exception:
            return None
        if isinstance(item, ListItem):
            return item.id
        return None

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id:
            self.post_message(self.DialogSelected(event.item.id))

    def _find_item(self, dialog_id: str) -> Optional[ListItem]:
        for child in self._dialog_list.children:
            if isinstance(child, ListItem) and child.id == dialog_id:
                return child
        return None
