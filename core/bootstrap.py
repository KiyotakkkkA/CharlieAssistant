from core.commands import SkillsInfoCommand
from core.general.agent.Assistant import Assistant

from core.general.agent.tools import (
    SystemManagementTool,
    DockerTool,
    MIREAScheduleTool,
    TelegramTool,
    WebSearchTool,
    RulesHelperTool
)


assistant = (
    Assistant()
    .with_tools([
        SystemManagementTool,
        DockerTool,
        MIREAScheduleTool,
        TelegramTool,
        WebSearchTool,
        RulesHelperTool
    ])
    .with_commands({
        "skills": SkillsInfoCommand(),
    })
    .with_provider('ollama')
    .with_model('gpt-oss:20b')
)

__all__ = [
    "assistant",
]