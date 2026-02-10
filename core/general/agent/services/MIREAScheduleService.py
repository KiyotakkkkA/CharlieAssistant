import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.request import Request, urlopen

from icalendar import Calendar
from dateutil.rrule import rrulestr
from dateutil import tz

from core.stores import CacheStore
from core.general.Config import Config


WEEKDAYS_RU = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "воскресенье",
}


class MIREAScheduleService:
    def __init__(self) -> None:
        self._cache = CacheStore()
        self._local_tz = tz.gettz(Config.ASSISTANT_TIMEZONE)

    def fetch_schedule(self, *, url: str, ttl_seconds: int, target_date: str | None = None) -> dict[str, Any]:
        key = self._build_cache_key(url=url, target_date=target_date)
        cached = self._cache.get_valid(key, ttl_seconds)
        if cached is not None:
            return cached

        try:
            html = self._fetch_html(url)
            ical_content = self._extract_ical_from_html(html)
            grouped = self._parse_schedule(ical_content, target_date=target_date)
            self._cache.set_with_ttl(key, grouped, ttl_seconds)
            return grouped
        except Exception as e:
            cached = self._cache.get_valid(key, ttl_seconds)
            if cached is not None:
                return cached
            return {"error": "schedule_fetch_failed with exception: " + str(e)}

    def _build_cache_key(self, *, url: str, target_date: str | None) -> str:
        return f"mirea_schedule::{url}::{target_date or 'all'}"

    def _fetch_html(self, url: str) -> str:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")

    def _extract_ical_from_html(self, html_content: str) -> str:
        match = re.search(r"<script id=\"__NEXT_DATA__\".*?>(.*?)</script>", html_content, re.DOTALL)
        if not match:
            raise ValueError("next_data_not_found")
        data = json.loads(match.group(1))
        return data["props"]["pageProps"]["scheduleLoadInfo"][0]["iCalContent"]

    def _parse_schedule(self, ical_content: str, target_date: str | None = None) -> dict[str, Any]:
        if target_date:
            start_dt = datetime.strptime(target_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=1)
        else:
            start_dt = datetime.now()
            end_dt = start_dt + timedelta(days=180)

        events = self._parse_ical_events(ical_content, start_dt, end_dt)
        grouped = self._group_events_by_day(events)

        if target_date and target_date in grouped:
            return {target_date: grouped[target_date]}
        return grouped

    def _parse_ical_events(self, ical_content: str, start_date: datetime, end_date: datetime) -> list[dict[str, Any]]:
        ical_content = ical_content.replace("\\r\\n", "\r\n").replace("\\n", "\n")
        cal = Calendar.from_ical(ical_content)
        events = []
        start_cmp = self._to_utc(self._as_datetime(start_date))
        end_cmp = self._to_utc(self._as_datetime(end_date))

        for component in cal.walk("VEVENT"):
            if "SUMMARY" in component and "неделя" in str(component.get("SUMMARY", "")):
                continue

            event_data = {
                "summary": str(component.get("SUMMARY", "")).replace("\r\n", "").replace("\n", " "),
                "start": component.get("DTSTART").dt if "DTSTART" in component else None,
                "end": component.get("DTEND").dt if "DTEND" in component else None,
                "location": str(component.get("LOCATION", "")).strip(),
                "description": str(component.get("DESCRIPTION", "")).replace("\r\n", "\n"),
                "uid": str(component.get("UID", "")),
                "categories": str(component.get("CATEGORIES", "")),
            }

            if not event_data["start"]:
                continue

            if "RRULE" in component:
                rrule_str = component["RRULE"].to_ical().decode("utf-8")
                dtstart = event_data["start"]

                if hasattr(dtstart, "tzinfo") and dtstart.tzinfo:
                    dtstart_utc = dtstart.astimezone(tz.UTC)
                    rrule_str = self._normalize_rrule_until(rrule_str, dtstart_utc)
                    dtstart_line = dtstart_utc.strftime("%Y%m%dT%H%M%SZ")
                    rrule = rrulestr(f"DTSTART:{dtstart_line}\nRRULE:{rrule_str}", dtstart=dtstart_utc)
                else:
                    rrule = rrulestr(
                        f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}\nRRULE:{rrule_str}",
                        dtstart=dtstart.replace(tzinfo=tz.gettz("Europe/Moscow")),
                    )

                for occurrence in rrule:
                    occ_cmp = self._to_utc(self._as_datetime(occurrence))
                    if occ_cmp > end_cmp:
                        break
                    if occ_cmp >= start_cmp:
                        if "EXDATE" in component:
                            exdates = component.get("EXDATE")
                            if not isinstance(exdates, list):
                                exdates = [exdates]
                            skip = False
                            for exdate_list in exdates:
                                for exdate in exdate_list.dts:
                                    exdate_dt = exdate.dt
                                    if hasattr(exdate_dt, "date") and occurrence.date() == exdate_dt.date():
                                        skip = True
                                        break
                                if skip:
                                    break
                            if skip:
                                continue

                        event_copy = event_data.copy()
                        event_copy["start"] = occurrence
                        if event_data["end"]:
                            duration = self._calc_duration(event_data["start"], event_data["end"])
                            event_copy["end"] = occurrence + duration
                        events.append(event_copy)
            else:
                event_start_cmp = self._to_utc(self._as_datetime(event_data["start"]))
                if start_cmp <= event_start_cmp <= end_cmp:
                    events.append(event_data)

        return events

    def _normalize_rrule_until(self, rrule_str: str, dtstart_utc: datetime) -> str:
        match = re.search(r"UNTIL=([0-9TZ]+)", rrule_str)
        if not match:
            return rrule_str
        raw_until = match.group(1)
        if raw_until.endswith("Z"):
            return rrule_str
        if len(raw_until) == 8:
            until_dt = datetime.strptime(raw_until, "%Y%m%d").replace(tzinfo=tz.UTC)
        else:
            until_dt = datetime.strptime(raw_until, "%Y%m%dT%H%M%S").replace(tzinfo=dtstart_utc.tzinfo)
            until_dt = until_dt.astimezone(tz.UTC)
        until_str = until_dt.strftime("%Y%m%dT%H%M%SZ")
        return re.sub(r"UNTIL=[0-9TZ]+", f"UNTIL={until_str}", rrule_str)

    def _as_datetime(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
            return datetime(value.year, value.month, value.day)
        return datetime.now(timezone.utc)

    def _ensure_aware(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=tz.gettz("Europe/Moscow"))
        return dt

    def _to_utc(self, dt: datetime) -> datetime:
        return self._ensure_aware(dt).astimezone(timezone.utc)

    def _to_local(self, dt: datetime) -> datetime:
        return self._ensure_aware(dt).astimezone(self._local_tz)

    def _calc_duration(self, start: Any, end: Any) -> timedelta:
        start_dt = self._as_datetime(start)
        end_dt = self._as_datetime(end)
        if start_dt.tzinfo or end_dt.tzinfo:
            return self._to_utc(end_dt) - self._to_utc(start_dt)
        return end_dt - start_dt

    def _group_events_by_day(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        grouped: dict[str, Any] = {}

        for event in events:
            if not event["start"]:
                continue

            start_local = self._to_local(self._as_datetime(event["start"]))
            end_local = self._to_local(self._as_datetime(event["end"])) if event.get("end") else None

            date_key = start_local.strftime("%Y-%m-%d")
            weekday_num = start_local.weekday()
            weekday_ru = WEEKDAYS_RU[weekday_num]

            if date_key not in grouped:
                grouped[date_key] = {
                    "weekday": weekday_ru,
                    "lessons": [],
                }

            summary = event["summary"]
            subject = summary.replace("ЛК ", "").replace("ПР ", "").strip()
            lesson_type = "ЛК" if "ЛК " in summary else "ПР" if "ПР " in summary else event["categories"]

            teacher = ""
            if event["description"]:
                desc_lines = event["description"].split("\n")
                for line in desc_lines:
                    if "Преподаватель:" in line:
                        teacher = line.replace("Преподаватель:", "").strip()
                        break

            start_time = start_local.strftime("%H:%M")
            end_time = end_local.strftime("%H:%M") if end_local else ""
            time_str = f"{start_time} - {end_time}" if end_time else start_time

            grouped[date_key]["lessons"].append(
                {
                    "time": time_str,
                    "subject": subject,
                    "type": lesson_type,
                    "teacher": teacher,
                    "location": event["location"],
                    "uid": event["uid"],
                }
            )

        for date_key in grouped:
            grouped[date_key]["lessons"].sort(key=lambda x: x["time"])

        return grouped
