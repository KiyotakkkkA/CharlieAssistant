from __future__ import annotations

from typing import Any

from core.interfaces import ICommand
from core.ui.ThemeLoader import list_theme_ids, load_theme
from core.ui.css import build_application_css


class ThemeChangeCommand(ICommand):
    description = "Сменить тему: @theme_change <theme_id>"

    def execute(self, *, app: Any, assistant: Any, dialog_id: str, args: str):
        theme_id = (args or "").strip()
        if not theme_id:
            themes = list_theme_ids()
            if not themes:
                return "Темы не найдены в **data/themes**."
            return "Доступные темы:\n" + "\n".join([f"- **{t}**" for t in themes])

        template = load_theme(theme_id)
        css = build_application_css(template)
        app.apply_theme_css(css)
        return f"Тема применена: **{theme_id}**"
