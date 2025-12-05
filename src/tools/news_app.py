
import os, asyncio, json
import openai
import requests, feedparser, pytz
from datetime import datetime, timedelta
from typing import Annotated
from textwrap import dedent
from src.toolbox.toolbox import register_tool_decorator


INTERESTS = dedent("""
* Artificial Intelligence
* Computer Programming Innovations
* Robotics
* New Investments in Tech Companies
* Space Travel
* Climate Change and Mitigations
* Computer Games
""") 


NEWS_PROMPT = dedent("""
Bitte extrahiere die Top {TOP} der relevantesten Nachrichten auf Basis meiner Interessen, absteigend sortiert basierend auf den Interessen:

Interessen: 
{INTERESTS}

Newsfeed:
{NEWSFEED}

Die Nachrichten sind bereits auf die letzten 24 Stunden gefiltert. Bitte erstelle eine Bullet Point Liste auf Deutsch wie in folgendem Beispiel:

* [Zusammenfassung von Titel und Summary der Nachricht](Hyperlink-Adresse auf den Artikel)
* [Zusammenfassung von Titel und Summary der Nachricht](Hyperlink-Adresse auf den Artikel)
* ...

Bitte verzichte auf Überschrift oder Einleitung und fasse die Nachrichten kurz und prägnant zusammen.
""").replace("{INTERESTS}", INTERESTS)


class NewsReaderApp:

    def __init__(self):
        self.tz = pytz.timezone("Europe/Berlin")
        pass
    
    
    def _convert_to_datetime(self, published_parsed):
        dt = datetime(*published_parsed[:6])
        if published_parsed.tm_zone:
            tz = pytz.timezone(published_parsed.tm_zone)
            dt = tz.localize(dt)
        else:
            dt = self.tz.localize(dt)
        return dt


    def _feed_to_dict(self, feed):
        news_dict = {
            "title": feed.feed.title,
            "link": feed.feed.link,
            "entries": []
        }
        for entry in feed.entries:
            news_entry = {
                "title": entry.title,
                "link": entry.link,
                "published": str(self._convert_to_datetime(entry.published_parsed)),
                "summary": entry.summary
            }
            news_dict["entries"].append(news_entry)
        return news_dict


    def _filter(self, feed_dict, time_delta):
        filtered_entries = []
        for entry in feed_dict["entries"]:
            entry_time = datetime.strptime(entry["published"], "%Y-%m-%d %H:%M:%S%z")
            if entry_time > datetime.now(self.tz) - time_delta:
                filtered_entries.append(entry)
        feed_dict["entries"] = filtered_entries
        return feed_dict

    
    async def get_news(self, url, top=3):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        # Try fetching via requests with browser-like headers; fall back to feedparser fetching.
        try:
            response = await asyncio.to_thread(
                requests.get, url, headers=headers, timeout=(5, 10)
            )
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except Exception:
            # Fallback: let feedparser fetch directly (supports passing headers).
            feed = feedparser.parse(url, request_headers=headers)
        feed = self._feed_to_dict(feed)
        feed = self._filter(feed, timedelta(hours=13))

        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # model = "gpt-4o"
        model = "gpt-4o-mini"

        prompt = NEWS_PROMPT.replace("{NEWSFEED}", str(feed)).replace("{TOP}", str(top))
    
        ai_response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Du bist ein Newsanalyst und bereitest Nachrichten für deinen User auf."},
                {"role": "user", "content": prompt}
                ],
            max_tokens=5000
        )

        return ai_response.choices[0].message.content
    
    
    async def condense_news(self, news, top=10):
        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # model = "gpt-4o"
        model = "gpt-4o-mini"
        
        prompt = NEWS_PROMPT.replace("{NEWSFEED}", str(news)).replace("{TOP}", str(top))
    
        ai_response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Du bist ein Newsanalyst und bereitest Nachrichten für deinen User auf."},
                {"role": "user", "content": prompt}
                ],
            max_tokens=5000
        )
        
        return ai_response.choices[0].message.content


@register_tool_decorator
async def get_news() -> Annotated[str, "Generates relevant news based on the user's interests."]:
    """
    Generate relevant news based on the user's interests.
    """
    news_channel_rsss = dict({
        "techcrunch": "https://techcrunch.com/feed/",
        # "theverge": "https://www.theverge.com/rss/google/index.xml",
        "wired.com": "https://www.wired.com/feed/rss",
        "reuters": "https://news.google.com/rss/search?q=site%3Areuters.com&hl=en-US&gl=US&ceid=US%3Aen",
        "heise": "https://www.heise.de/rss/heise.rdf",
        "spiegel": "https://www.spiegel.de/schlagzeilen/tops/index.rss",
        "macrumors": "https://feeds.macrumors.com/MacRumors-All",
    })
    
    async def fetch_news(feedname, feed):
        return feedname, await news_reader.get_news(feed, top=3)

    news_reader = NewsReaderApp()
    tasks = [fetch_news(feedname, feed) for feedname, feed in news_channel_rsss.items()]
    results = await asyncio.gather(*tasks)
    news = {feedname: result for feedname, result in results}
    
    condensed_news = await news_reader.condense_news(str(news), top=12)
    result = dict()
    result["news"] = condensed_news
    result["system-instruction"] = dedent("""Bitte erstelle auf Basis der gegebenen News eine Bullet Point Liste auf Deutsch wie in folgendem Beispiel:
* [Zusammenfassung von Titel und Summary der Nachricht](Hyperlink-Adresse auf den Artikel)
* [Zusammenfassung von Titel und Summary der Nachricht](Hyperlink-Adresse auf den Artikel)
* ...""")
    return json.dumps(result)




# if __name__ == "__main__":
#     news = asyncio.run(get_news())
#     print(news)
