import os
import sys
import platform
from datetime import datetime

from telethon import events
from PIL import Image, ImageDraw, ImageFont

info = {"name": "About", "description": "Баннер с версией и инфой"}
commands = [{"cmd": ".about", "desc": "О боте"}]

_DIR = os.path.dirname(os.path.abspath(__file__))
_BANNER = os.path.join(_DIR, "banner.png")
_OUT = os.path.join(_DIR, "_about_out.png")

_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def _font(size):
    for p in _FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _stamp(ver):
    img = Image.open(_BANNER).convert("RGBA")
    d = ImageDraw.Draw(img)
    fs = max(10, int(img.height * 0.022))
    font = _font(fs)
    text = f"v{ver}"
    bb = d.textbbox((0, 0), text, font=font)
    y = img.height - (bb[3] - bb[1]) - 6 - bb[1]
    d.text((7, y + 1), text, font=font, fill=(0, 0, 0, 100))
    d.text((6, y), text, font=font, fill=(0, 0, 0, 255))
    img.convert("RGB").save(_OUT, "PNG")
    return _OUT


def _uptime(start_ts):
    s = int(datetime.now().timestamp() - start_ts)
    d, r = divmod(s, 86400)
    h, r = divmod(r, 3600)
    m, sec = divmod(r, 60)
    parts = []
    if d: parts.append(f"{d}д")
    if h: parts.append(f"{h}ч")
    if m: parts.append(f"{m}м")
    parts.append(f"{sec}с")
    return " ".join(parts)


def setup(client):
    client.registry["about"] = {"info": info, "commands": commands}
    start_ts = datetime.now().timestamp()
    prefix = (client.config.get("app") or {}).get("prefix", ".")
    cmd = f"{prefix}about"

    @client.on(events.NewMessage(outgoing=True))
    async def _(event):
        if (event.raw_text or "").strip() != cmd:
            return

        ver = (client.config.get("app") or {}).get("version", "?")

        try:
            me = await client.get_me()
            hoster = f"{me.first_name or ''} {me.last_name or ''}".strip() or f"ID:{me.id}"
            tag = f"@{me.username}" if me.username else f"ID:{me.id}"
        except Exception:
            hoster, tag = "неизвестно", "—"

        cap = (
            f"**Userbyte** — `v{ver}`\n\n"
            f"👤 **Хостер:** {hoster} ({tag})\n"
            f"🐍 **Python:** {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n"
            f"📦 **Модулей:** {len(client.registry)}\n"
            f"⏱ **Uptime:** {_uptime(start_ts)}\n"
            f"💻 **OS:** {platform.system()} {platform.release()}"
        )

        file = None
        if os.path.exists(_BANNER):
            try:
                file = _stamp(ver)
            except Exception as e:
                cap += f"\n\n⚠️ `{e}`"
        else:
            cap += "\n\n⚠️ `banner.png` не найден."

        if file:
            await event.reply(cap, file=file, parse_mode="md")
        else:
            await event.reply(cap, parse_mode="md")
