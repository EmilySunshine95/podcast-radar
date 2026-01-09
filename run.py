import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ✅ 多个候选 RSS（按优先级尝试）
RSS_CANDIDATES = [
    "https://www.lennysnewsletter.com/feed/podcast",   # Substack 常见 podcast feed
    "https://www.lennyspodcast.com/feed",              # 你之前那个（有时会 522，留作备用）
    "https://www.lennysnewsletter.com/feed",           # 文章 feed（至少能证明抓取通）
]

def fetch(url: str, retries: int = 3, backoff: float = 2.0) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0 (PodcastRadarBot/1.0; +https://github.com/EmilySunshine95/podcast-radar)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        "Referer": "https://www.lennysnewsletter.com/",
    }
    last_err = None
    for i in range(retries):
        try:
            print(f"Fetching RSS: {url} (attempt {i+1}/{retries})")
            res = requests.get(url, headers=headers, timeout=25, allow_redirects=True)
            res.raise_for_status()
            return res.content
        except Exception as e:
            last_err = e
            time.sleep(backoff * (i + 1))
    raise last_err

def pick_first_working_feed() -> tuple[str, bytes]:
    errs = []
    for u in RSS_CANDIDATES:
        try:
            return u, fetch(u)
        except Exception as e:
            errs.append(f"{u} -> {repr(e)}")
            print("Failed:", errs[-1])
    raise RuntimeError("All RSS candidates failed:\n" + "\n".join(errs))

feed_url, xml_bytes = pick_first_working_feed()
print("Using feed:", feed_url)

root = ET.fromstring(xml_bytes)
channel = root.find("channel")
if channel is None:
    raise RuntimeError("Invalid RSS: missing <channel>")

items = channel.findall("item")
if not items:
    raise RuntimeError("No <item> found in RSS")

latest = items[0]
title = (latest.findtext("title") or "").strip()
link = (latest.findtext("link") or "").strip()
pub = (latest.findtext("pubDate") or "").strip()

html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Podcast Radar</title>
</head>
<body>
  <h1>Podcast Radar</h1>
  <p>✅ GitHub Pages is live.</p>
  <p><b>Feed used:</b> {feed_url}</p>
  <p>Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>

  <h2>Latest item</h2>
  <p><b>{title}</b></p>
  <p><a href="{link}">{link}</a></p>
  <p>{pub}</p>
</body>
</html>
"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated docs/index.html")
