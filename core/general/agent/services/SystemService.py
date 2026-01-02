from datetime import datetime

from typing import Any, Dict


class SystemService:    
    @staticmethod
    def get_time() -> Dict[str, Any]:
        return SystemService._collect_time_info()
    
    @staticmethod
    def _collect_time_info() -> Dict[str, Any]:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        return {
            "status": "success",
            "current_time": current_time,
            "current_date": current_date
        }