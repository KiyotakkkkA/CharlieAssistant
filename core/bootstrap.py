from core.commands import ThemeChangeCommand, TestMsgCommand
from core.general.agent.Assistant import Assistant


assistant = (
    Assistant()
    .with_provider('ollama')
    .with_model('gpt-oss:20b')
    .with_commands({
        "theme_change": ThemeChangeCommand(),
        "test_msg": TestMsgCommand(),
    })
)

__all__ = [
    "assistant",
]