import asyncio
import aiohttp
from typing import Dict, Any


class TelegramService:
    @staticmethod
    async def send_message(bot_token:str, user_id: str, message: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        try:
            if not bot_token or not user_id:
                return {"success": False, "error": "missing_config", "message": "Telegram config is incomplete"}

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": user_id, "text": message, "parse_mode": parse_mode}

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=timeout) as resp:
                    data = await resp.json()
                    if resp.status == 200 and data.get('ok'):
                        return {"success": True, "message": "sent", "message_id": data.get('result', {}).get('message_id')}
                    else:
                        err = data.get('description', 'unknown')
                        return {"success": False, "error": err, "message": "failed"}

        except asyncio.TimeoutError:
            return {"success": False, "error": "timeout", "message": "request timeout"}
        except Exception as e:
            return {"success": False, "error": "unexpected_error", "message": str(e)}
