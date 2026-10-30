"""Fetch top news headlines from a public RSS feed (e.g., BBC News)."""
import urllib.request
import xml.etree.ElementTree as ET

RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"


def get_news(limit=5):
    """Fetches top headlines from the RSS feed."""
    try:
        req = urllib.request.Request(
            RSS_URL,
            headers={"User-Agent": "MamboAssistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        items = root.findall(".//item")

        headlines = []
        for item in items[:limit]:
            title = item.find("title")
            if title is not None and title.text:
                headlines.append(title.text.strip())

        return headlines if headlines else ["No news headlines available."]
    except Exception as e:
        return [f"Could not load news: {e}"]