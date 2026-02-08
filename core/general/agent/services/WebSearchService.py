import json
from urllib.request import Request, urlopen

from core.general import Config


class WebSearchService:
    @staticmethod
    def web_search(request: str):
        payload = json.dumps({"query": request}).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {Config.OLLAMA_API_KEY}",
            "Content-Type": "application/json",
        }
        req = Request("https://ollama.com/api/web_search", data=payload, headers=headers, method="POST")
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        return json.loads(raw) if raw else {}

    @staticmethod
    def web_fetch(url: str):
        payload = json.dumps({"url": url}).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {Config.OLLAMA_API_KEY}",
            "Content-Type": "application/json",
        }
        req = Request("https://ollama.com/api/web_fetch", data=payload, headers=headers, method="POST")
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        return json.loads(raw) if raw else {}