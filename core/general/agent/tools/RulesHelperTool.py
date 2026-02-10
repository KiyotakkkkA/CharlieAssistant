from core.interfaces import ITool

from core.types.ai import ToolClassSetupObject
from core.general.agent.services import RulesHelperService
from core.general.agent.ToolBuilder import ToolBuilder


class RulesHelperTool(ITool):
    name = "RulesHelper Tool Pack"

    @staticmethod
    def setup_get_docs_design_rules_tool() -> ToolClassSetupObject:
        return {
            "name": "get_docs_gost_design_rules_tool",
            "handler": RulesHelperTool.get_docs_gost_design_rules_handler,
            "tool": ToolBuilder()
                .set_name("get_docs_gost_design_rules_tool")
                .set_description("Returns design rules from GOST 7.32 – 2017;")
        }

    @staticmethod
    def get_docs_gost_design_rules_handler(**kwargs) -> str:
        return RulesHelperService.get_docs_gost_design_rules()

    @staticmethod
    def setup_get_charlie_tools_guide_tool() -> ToolClassSetupObject:
        return {
            "name": "get_charlie_tools_guide_tool",
            "handler": RulesHelperTool.get_charlie_tools_guide_handler,
            "tool": ToolBuilder()
                .set_name("get_charlie_tools_guide_tool")
                .set_description("Returns the internal tools guide for Charlie assistant")
        }

    @staticmethod
    def get_charlie_tools_guide_handler(**kwargs) -> str:
        return RulesHelperService.get_charlie_tools_guide()

RulesHelperTool.commands = [
    RulesHelperTool.setup_get_docs_design_rules_tool(),
    RulesHelperTool.setup_get_charlie_tools_guide_tool(),
]