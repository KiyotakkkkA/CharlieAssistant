import asyncio
from typing import Dict, Any
from core.interfaces import ITool

from core.types.ai import ToolClassSetupObject
from core.general.agent.services import TelegramService
from core.general.agent.ToolBuilder import ToolBuilder

from core.general import Config


class TelegramTool(ITool):
    name = 'Telegram Tools Pack'
    
    @staticmethod
    def setup_send_telegram_message_tool() -> ToolClassSetupObject:
        return {
            "name": "send_telegram_message_tool",
            "handler": TelegramTool.send_telegram_message_handler,
            "tool": ToolBuilder()
                .set_name("send_telegram_message_tool")
                .set_description(
                    "Tool that sends a message to the user via Telegram. "
                    "Use this to notify the user about important events, send results, or communicate with them."
                )
                .add_property("message", "string", description="The message text to send to the user")
                .add_requirements(['message'])
        }
    
    @staticmethod
    def send_telegram_message_handler(message: str) -> Dict[str, Any]:
        return asyncio.run(TelegramService.send_message(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_USER_ID, message))


TelegramTool.commands = [
    TelegramTool.setup_send_telegram_message_tool()
]
