from core.interfaces import ITool

from core.types.ai import ToolClassSetupObject
from core.general.agent.services import WebSearchService
from core.general.agent.ToolBuilder import ToolBuilder


class WebSearchTool(ITool):
    name = 'Web Search Tools Pack'
    
    @staticmethod
    def setup_web_search_tool() -> ToolClassSetupObject:
        return {
            "name": "web_search_tool",
            "handler": WebSearchTool.web_search_handler,
            "tool": ToolBuilder()
                .set_name("web_search_tool")
                .set_description(
                    "Tool that performs web searches. "
                    "Use this to find information on the web and fetch relevant data."
                )
                .add_property("query", "string", description="The search query to perform")
                .add_requirements(['query'])
        }

    @staticmethod
    def setup_web_fetch_tool() -> ToolClassSetupObject:
        return {
            "name": "web_fetch_tool",
            "handler": WebSearchTool.web_fetch_handler,
            "tool": ToolBuilder()
                .set_name("web_fetch_tool")
                .set_description(
                    "Tool that fetches the content of a web page. "
                    "Use this to retrieve the content of a specific URL."
                )
                .add_property("url", "string", description="The URL of the web page to fetch")
                .add_requirements(['url'])
        }
    
    @staticmethod
    def web_search_handler(query: str):
        return WebSearchService.web_search(query)

    @staticmethod
    def web_fetch_handler(url: str):
        return WebSearchService.web_fetch(url)


WebSearchTool.commands = [
    WebSearchTool.setup_web_search_tool(),
    WebSearchTool.setup_web_fetch_tool()
]
