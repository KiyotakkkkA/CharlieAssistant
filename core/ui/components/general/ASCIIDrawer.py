from typing import Iterable, Sequence

from rich.style import Style
from rich.text import Text

from core.static.ASCII_LETTERS import LETTERS, RUS_LETTERS, NUMBERS_LETTERS, SPECIAL_LETTERS

ASCII_HEIGHT = 6

GLYPHS = {}
GLYPHS.update(RUS_LETTERS)
GLYPHS.update(LETTERS)
GLYPHS.update(NUMBERS_LETTERS)
GLYPHS.update(SPECIAL_LETTERS)


class ASCIIDrawer:
    def __init__(self, font: str = "standard", gradient: Sequence[str] | None = None, text: str = 'Hello World', fill_background: bool = False) -> None:
        self.font = font
        self.gradient = tuple(gradient) if gradient else ("#f97316", "#f59e0b", "#fb923c")
        self.text = text

        self.rendered = self.render_text(self.text, gradient=self.gradient, fill_background=fill_background)

    def content(self) -> Text:
        return self.rendered

    def render_text(
        self,
        text: str,
        *,
        gradient: Sequence[str] | None = None,
        fill_background: bool = False,
    ) -> Text:

        clean_text = (text or "").strip()
        if not clean_text:
            return Text("")

        ascii_text = self._render_ascii(clean_text)
        colors = tuple(gradient) if gradient else self.gradient
        return self._to_rich_text(ascii_text, colors, fill_background=fill_background)

    def _render_ascii(self, text: str) -> str:
        lines = ["" for _ in range(ASCII_HEIGHT)]
        for raw_char in text:
            char = (raw_char or " ").lower()
            glyph = GLYPHS.get(char) or GLYPHS.get("?")
            if glyph is None:
                glyph = LETTERS[" "]
            for i in range(ASCII_HEIGHT):
                lines[i] += glyph[i] + " "
        return "\n".join(line.rstrip() for line in lines).rstrip("\n")

    def _to_rich_text(self, ascii_text: str, colors: Sequence[str], *, fill_background: bool) -> Text:
        lines = ascii_text.splitlines()
        max_width = max((len(line) for line in lines), default=0)
        palette = self._build_palette(max_width, colors)
        out = Text()
        for line_index, line in enumerate(lines):
            for x, ch in enumerate(line):
                if ch.isspace() or x >= len(palette):
                    out.append(ch)
                    continue
                color = palette[x]
                style = Style(color=color, bgcolor=color if fill_background else None)
                out.append(ch, style=style)

            if line_index != len(lines) - 1:
                out.append("\n")

        return out

    def _build_palette(self, length: int, colors: Sequence[str]) -> list[str]:
        if length <= 0:
            return []
        if len(colors) == 1:
            return [colors[0]] * length

        segments = len(colors) - 1
        palette: list[str] = []
        for index in range(length):
            position = index / max(length - 1, 1)
            segment_index = min(int(position * segments), segments - 1)
            start_color = colors[segment_index]
            end_color = colors[segment_index + 1]
            local_t = (position * segments) - segment_index
            palette.append(self._lerp_hex(start_color, end_color, local_t))
        return palette

    def _lerp_hex(self, start: str, end: str, t: float) -> str:
        sr, sg, sb = self._hex_to_rgb(start)
        er, eg, eb = self._hex_to_rgb(end)
        rr = int(sr + (er - sr) * t)
        rg = int(sg + (eg - sg) * t)
        rb = int(sb + (eb - sb) * t)
        return self._rgb_to_hex((rr, rg, rb))

    def _hex_to_rgb(self, value: str) -> tuple[int, ...]:
        value = value.lstrip("#")
        if len(value) != 6:
            return (255, 255, 255)
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: Iterable[int]) -> str:
        r, g, b = (max(0, min(255, int(c))) for c in rgb)
        return f"#{r:02x}{g:02x}{b:02x}"
