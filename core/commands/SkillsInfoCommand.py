from typing import Any

from core.interfaces import ICommand


class SkillsInfoCommand(ICommand):
    description = "Информация о всех доступных навыках"

    def execute(self, *, app: Any, assistant: Any, dialog_id: str, args: str):
        msg = (
            f"Привет!\n"
            "Подскажи, что ты умеешь?\n"
            "И какими навыками обладаешь"
        )
        self.send_as_user(app=app, message=msg)
        return None
