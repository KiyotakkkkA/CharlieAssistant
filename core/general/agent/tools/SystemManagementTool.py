from typing import Dict, Any

from core.general.agent.ToolBuilder import ToolBuilder
from core.general.agent.services import SystemService
from core.interfaces import ITool
from core.types.ai import ToolClassSetupObject


class SystemManagementTool(ITool):

    name = 'System Management Tools Pack'

    @staticmethod
    def setup_get_system_time_tool() -> ToolClassSetupObject:
        return {
            "name": "get_time_tool",
            "handler": SystemManagementTool.get_time_handler,
            "tool": ToolBuilder()
                .set_name("get_time_tool")
                .set_description("Tool that retrieves the current system time")
        }
    
    @staticmethod
    def get_time_handler(**kwargs) -> Dict[str, Any]:
        return SystemService.get_time()


SystemManagementTool.commands = [
    SystemManagementTool.setup_get_system_time_tool(),
]
