from core.commands import SkillsInfoCommand
from core.general.agent.Assistant import Assistant

from core.general.agent.tools import (
    SystemManagementTool,
    DockerTool,
    MIREAScheduleTool,
    TelegramTool,
    WebSearchTool
)


assistant = (
    Assistant()
    .with_provider('ollama')
    .with_model('gpt-oss:20b')
    .with_tools([
        SystemManagementTool,
        DockerTool,
        MIREAScheduleTool,
        TelegramTool,
        WebSearchTool
    ])
    .with_commands({
        "skills": SkillsInfoCommand(),
    })
)

__all__ = [
    "assistant",
]