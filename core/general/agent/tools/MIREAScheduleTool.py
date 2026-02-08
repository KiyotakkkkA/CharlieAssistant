import re
from datetime import datetime
from typing import Any, Dict

from core.general.agent.ToolBuilder import ToolBuilder
from core.general.agent.services import MIREAScheduleService
from core.interfaces import ITool
from core.types.ai import ToolClassSetupObject


class MIREAScheduleTool(ITool):
    name = "MIREA Schedule Tools Pack"
    CACHE_TTL = "6h"

    @staticmethod
    def _parse_ttl(ttl: str) -> int:
        value = (ttl or "").strip().lower()
        if not value:
            return 0
        total = 0
        for count, unit in re.findall(r"(\d+)([smhdw])", value):
            n = int(count)
            if unit == "s":
                total += n
            elif unit == "m":
                total += n * 60
            elif unit == "h":
                total += n * 3600
            elif unit == "d":
                total += n * 86400
            elif unit == "w":
                total += n * 604800
        return total

    @staticmethod
    def setup_get_schedule_tool() -> ToolClassSetupObject:
        return {
            "name": "mirea_schedule_tool",
            "handler": MIREAScheduleTool.get_schedule_handler,
            "tool": ToolBuilder()
                .set_name("mirea_schedule_tool")
                .set_description("Fetch and parse RTU MIREA schedule")
                .add_property("target_date", "string", description="Optional date YYYY-MM-DD, if not provided - today is used")
        }

    @staticmethod
    def get_schedule_handler(target_date: str | None = None, **kwargs) -> Dict[str, Any]:
        ttl_seconds = MIREAScheduleTool._parse_ttl(MIREAScheduleTool.CACHE_TTL)
        service = MIREAScheduleService()
        date_value = target_date if target_date else datetime.now().strftime("%Y-%m-%d")
        target_url = f"https://schedule-of.mirea.ru/?date={date_value}&s=1_778"
        return service.fetch_schedule(url=target_url, target_date=date_value, ttl_seconds=ttl_seconds)


MIREAScheduleTool.commands = [
    MIREAScheduleTool.setup_get_schedule_tool(),
]
