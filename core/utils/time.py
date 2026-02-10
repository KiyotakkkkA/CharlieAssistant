import re


def parse_time_from_string(query: str) -> int:
        value = (query or "").strip().lower()
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

__all__ = ["parse_time_from_string"]