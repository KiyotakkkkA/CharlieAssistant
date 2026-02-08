from core.commands import ThemeChangeCommand, SkillsInfoCommand
from core.general.agent.Assistant import Assistant


assistant = (
    Assistant()
    .with_provider('ollama')
    .with_model('gpt-oss:20b')
    .with_commands({
        "theme_change": ThemeChangeCommand(),
        "skills": SkillsInfoCommand(),
    })
)

__all__ = [
    "assistant",
]