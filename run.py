import requests
import xml.etree.ElementTree as ET
from datetime import datetime

RSS_URL = "https://www.lennyspodcast.com/feed"

print("Fetching RSS...")
res = requests.get(RSS_URL)
res.raise_for_status()

root = ET.fromstring(res.content)
channel = root.find("channel")
items = channel.findall("item")

latest = items[0]
title = latest.find("title").text
link = latest.find("link").text
pub = latest.find("pubDate").text

html = f"""
<html>
<head>
  <meta charset="utf-8">
  <title>Podcast Radar</title>
</head>
<body>
  <h1>🎧 Podcast Radar</h1>
  <p>Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>

  <h2>Latest from Lenny's Podcast</h2>
  <p><strong>{title}</strong></p>
  <p><a href="{link}" target="_blank">Listen</a></p>
  <p>{pub}</p>
</body>
</html>
"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated docs/index.html")

