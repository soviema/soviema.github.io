"""Build feed.xml and index.html for Cahiers du Soviéma from show.toml and episodes.toml.

    python3 build_feed.py

Standard library only (Python 3.11+). The audio files are assets of the GitHub release named in
show.toml (`audio_base`); the episode art and the show cover sit in art/ and are served by GitHub Pages.
"""
import html
import tomllib
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня",
          "июля", "августа", "сентября", "октября", "ноября", "декабря"]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def cdata(text: str) -> str:
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def flag(value: bool) -> str:
    return "true" if value else "false"


def load() -> tuple[dict, list[dict]]:
    show = tomllib.loads((ROOT / "show.toml").read_text(encoding="utf-8"))
    episodes = tomllib.loads((ROOT / "episodes.toml").read_text(encoding="utf-8"))["episode"]
    episodes.sort(key=lambda e: parsedate_to_datetime(e["published"]), reverse=True)
    for e in episodes:
        e["audio_url"] = show["audio_base"] + e["audio"]
        e["image_url"] = show["site"] + e["image"]
    return show, episodes


def feed(show: dict, episodes: list[dict]) -> str:
    site, email = show["site"], show["owner_email"]
    cover = site + show["image"]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"'
        ' xmlns:podcast="https://podcastindex.org/namespace/1.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        f"<title>{esc(show['title'])}</title>",
        f"<link>{esc(site)}</link>",
        f"<description>{cdata(show['description'])}</description>",
        f"<language>{esc(show['language'])}</language>",
        f"<copyright>{esc(show['copyright'])}</copyright>",
        f"<lastBuildDate>{format_datetime(datetime.now(timezone.utc), usegmt=True)}</lastBuildDate>",
        "<generator>build_feed.py</generator>",
        f'<atom:link href="{esc(show["feed"])}" rel="self" type="application/rss+xml"/>',
        f"<image><url>{esc(cover)}</url><title>{esc(show['title'])}</title><link>{esc(site)}</link></image>",
        f"<itunes:author>{esc(show['author'])}</itunes:author>",
        f"<itunes:summary>{cdata(show['description'])}</itunes:summary>",
        f"<itunes:owner><itunes:name>{esc(show['owner_name'])}</itunes:name>"
        f"<itunes:email>{esc(email)}</itunes:email></itunes:owner>",
        f'<itunes:image href="{esc(cover)}"/>',
        f'<itunes:category text="{esc(show["category"])}">'
        f'<itunes:category text="{esc(show["subcategory"])}"/></itunes:category>',
        f"<itunes:explicit>{flag(show['explicit'])}</itunes:explicit>",
        f"<itunes:type>{esc(show['type'])}</itunes:type>",
        f"<podcast:guid>{esc(show['guid'])}</podcast:guid>",
        f'<podcast:locked owner="{esc(email)}">{"yes" if show["locked"] else "no"}</podcast:locked>',
    ]
    for e in episodes:
        lines += [
            "<item>",
            f"<title>{esc(e['title'])}</title>",
            f"<description>{cdata(e['description'])}</description>",
            f"<link>{esc(site)}#{esc(e['key'])}</link>",
            f'<guid isPermaLink="false">{esc(e["guid"])}</guid>',
            f"<pubDate>{esc(e['published'])}</pubDate>",
            f'<enclosure url="{esc(e["audio_url"])}" length="{e["length"]}" type="{esc(e["mime"])}"/>',
            f"<itunes:duration>{esc(e['duration'])}</itunes:duration>",
            f'<itunes:image href="{esc(e["image_url"])}"/>',
            f"<itunes:explicit>{flag(e['explicit'])}</itunes:explicit>",
        ]
        if "number" in e:
            lines.append(f"<itunes:episode>{e['number']}</itunes:episode>")
        lines += [
            f"<itunes:season>{e['season']}</itunes:season>",
            f"<itunes:episodeType>{esc(e['type'])}</itunes:episodeType>",
            "</item>",
        ]
    lines += ["</channel>", "</rss>", ""]
    return "\n".join(lines)


def page(show: dict, episodes: list[dict]) -> str:
    items = []
    for e in episodes:
        d = parsedate_to_datetime(e["published"])
        h, m, _ = (int(x) for x in e["duration"].split(":"))
        length = f"{h} ч {m:02d} мин" if h else f"{m} мин"
        items.append(
            f'<li id="{esc(e["key"])}"><img src="{esc(e["image"])}" alt="" loading="lazy">'
            f"<div><h2>{esc(e['title'])}</h2>"
            f'<p class="meta">{d.day} {MONTHS[d.month - 1]} {d.year} · {length}</p>'
            f"{e['description']}"
            f'<p><a href="{esc(e["audio_url"])}">Аудиофайл, {e["length"] / 1e6:.0f} МБ</a></p></div></li>')
    links = " · ".join(f'<a href="{esc(url)}">{esc(name)}</a>' for name, url in show["links"].items())
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(show['title'])}</title>
<link rel="alternate" type="application/rss+xml" title="{esc(show['title'])}" href="{esc(show['feed'])}">
<style>
:root {{ --bg: #faf8f5; --fg: #1d1b19; --muted: #6b655e; --line: #e2ddd6; --link: #8a2b1d; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg: #161514; --fg: #ece8e2; --muted: #a39d95; --line: #2e2b28; --link: #e0876f; }} }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 17px/1.5 Georgia, "Times New Roman", serif; }}
main {{ max-width: 720px; margin: 0 auto; padding: 24px 16px 48px; }}
header {{ display: flex; gap: 20px; align-items: center; margin-bottom: 32px; }}
header img {{ width: 140px; height: 140px; object-fit: cover; border-radius: 6px; flex: none; }}
h1 {{ margin: 0 0 6px; font-size: 30px; line-height: 1.15; }}
h2 {{ margin: 0 0 4px; font-size: 19px; line-height: 1.3; }}
a {{ color: var(--link); }}
.meta {{ margin: 0 0 8px; color: var(--muted); font-size: 15px; }}
ul {{ list-style: none; margin: 0; padding: 0; }}
li {{ display: flex; gap: 16px; padding: 20px 0; border-top: 1px solid var(--line); }}
li img {{ width: 88px; height: 88px; object-fit: cover; border-radius: 4px; flex: none; }}
li p {{ margin: 0 0 8px; }}
@media (max-width: 480px) {{ header {{ flex-direction: column; align-items: flex-start; }} li img {{ width: 64px; height: 64px; }} }}
</style>
</head>
<body>
<main>
<header><img src="{esc(show['image'])}" alt="Обложка подкаста">
<div><h1>{esc(show['title'])}</h1><p class="meta">{esc(show['description'])}</p>
<p>{links} · <a href="{esc(show['feed'])}">RSS</a></p></div></header>
<ul>
{chr(10).join(items)}
</ul>
</main>
</body>
</html>
"""


def main() -> None:
    show, episodes = load()
    (ROOT / "feed.xml").write_text(feed(show, episodes), encoding="utf-8")
    (ROOT / "index.html").write_text(page(show, episodes), encoding="utf-8")
    print(f"feed.xml and index.html: {len(episodes)} episodes")


if __name__ == "__main__":
    main()
