from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import ListItem, ListView, Static

from core.interfaces import ICommand


@dataclass(frozen=True)
class _CommandRow:
	name: str
	description: str


class CommandPalette(Container):
	class CommandChosen(Message):
		def __init__(self, name: str) -> None:
			super().__init__()
			self.name = name

	def __init__(
		self,
		*,
		commands: Optional[Dict[str, ICommand]] = None,
		id: Optional[str] = None,
		classes: Optional[str] = None,
	) -> None:
		super().__init__(id=id, classes=classes)
		self._commands: Dict[str, ICommand] = dict(commands or {})
		self._rows: List[_CommandRow] = []
		self._filter: str = ""

		self._list = ListView(id="command_palette_list")

	def compose(self) -> ComposeResult:
		yield self._list

	def set_commands(self, commands: Dict[str, ICommand]) -> None:
		self._commands = dict(commands or {})
		self.update_filter(self._filter)

	def open(self, filter_text: str = "") -> None:
		self.remove_class("hidden")
		self.update_filter(filter_text)

	def close(self) -> None:
		self.add_class("hidden")

	@property
	def is_open(self) -> bool:
		return not self.has_class("hidden")

	def update_filter(self, filter_text: str) -> None:
		self._filter = (filter_text or "").strip()
		self._rows = self._build_rows(self._filter)
		self._render_rows(self._rows)

	def move_selection(self, delta: int) -> None:
		if not self.is_open:
			return
		if delta < 0:
			self._list.action_cursor_up()
		elif delta > 0:
			self._list.action_cursor_down()

	def choose_selected(self) -> Optional[str]:
		if not self.is_open:
			return None
		if not self._rows:
			return None

		index = self._list.index
		if index is None:
			index = 0
		index = max(0, min(index, len(self._rows) - 1))
		name = self._rows[index].name
		self.post_message(self.CommandChosen(name))
		return name

	def _build_rows(self, filter_text: str) -> List[_CommandRow]:
		items: List[Tuple[str, ICommand]] = sorted(self._commands.items(), key=lambda kv: kv[0].lower())
		if filter_text:
			ft = filter_text.lower()
			items = [(k, v) for k, v in items if k.lower().startswith(ft)]

		rows: List[_CommandRow] = []
		for name, cmd in items:
			desc = getattr(cmd, "description", "") or ""
			rows.append(_CommandRow(name=name, description=desc))
		return rows

	def _render_rows(self, rows: List[_CommandRow]) -> None:
		self._list.clear()
		for row in rows:
			label = Static(f"@{row.name}  {row.description}".rstrip(), classes="command_palette_item")
			self._list.append(ListItem(label))

		if rows:
			self._list.index = 0
