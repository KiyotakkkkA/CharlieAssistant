from __future__ import annotations

from typing import Any

from core.interfaces import ICommand


class TestMsgCommand(ICommand):
    description = "Отправить тестовое приветствие как пользователь"

    def execute(self, *, app: Any, assistant: Any, dialog_id: str, args: str):
        name = (args or "").strip() or "Чарли"
        msg = (
            f"Привет! Меня зовут {name}.\n\n"
            "Хочу проверить команды и переключение тем. "
            "Подскажи, что ты умеешь?"
        )
        self.send_as_user(app=app, message=msg)
        return None
