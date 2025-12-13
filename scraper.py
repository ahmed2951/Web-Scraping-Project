import argparse
import json
import sys
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

DEFAULT_URL = "https://www.zamaleksc.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ZamalekScraper/1.0)"}


def absolutize(base, link):
    if not link:
        return None
    return urljoin(base, link)


def parse_date(text):
    if not text:
        return None
    try:
        dt = dateparser.parse(text, fuzzy=True)
        return dt.isoformat()
    except Exception:
        return text.strip()


def extract_from_element(el, base_url):
    # title
    title = None
    link = None
    for tag in ("h1", "h2", "h3", "a", "strong"):
        t = el.find(tag)
        if t:
            if t.name == "a":
                link = t.get("href") or t.get("data-href")
                title = (t.get_text() or t.get("title"))
            else:
                # if there's an anchor inside header
                a = t.find("a")
                if a:
                    link = a.get("href") or a.get("data-href")
                    title = a.get_text()
                else:
                    title = t.get_text()
            if title:
                title = title.strip()
                break

    # fallback: any anchor in element
    if not title:
        a = el.find("a")
        if a:
            title = (a.get_text() or a.get("title") or "").strip()
            link = link or a.get("href")

    # summary
    summary = None
    p = el.find("p")
    if p:
        summary = p.get_text().strip()

    # date
    date_text = None
    time_tag = el.find("time")
    if time_tag:
        date_text = time_tag.get("datetime") or time_tag.get_text()
    else:
        # common date classes
        for cls in ("date", "time", "post-date", "meta-date"):
            d = el.find(class_=lambda c: c and cls in c)
            if d:
                date_text = d.get_text()
                break

    # image
    img = el.find("img")
    img_src = img.get("src") if img else None

    return {
        "title": title,
        "link": absolutize(base_url, link) if link else None,
        "summary": summary,
        "date": parse_date(date_text),
        "image": absolutize(base_url, img_src) if img_src else None,
    }


def find_news(soup, base_url):
    candidates = []

    # try common containers
    selectors = [
        "article",
        ".news-item",
        ".item",
        ".post",
        ".blog-post",
        ".article",
        ".news",
        ".newsList li",
        ".news_list li",
        ".recent-news",
        ".post-item",
    ]

    for sel in selectors:
        els = soup.select(sel)
        if els:
            for el in els:
                item = extract_from_element(el, base_url)
                if item.get("title") or item.get("link"):
                    candidates.append(item)
            if candidates:
                break

    # fallback: any top-level link blocks
    if not candidates:
        for a in soup.select("a")[:60]:
            text = a.get_text().strip()
            href = a.get("href")
            if text and href and len(text) > 10:
                candidates.append({
                    "title": text,
                    "link": absolutize(base_url, href),
                    "summary": None,
                    "date": None,
                    "image": None,
                })

    # deduplicate by link or title
    seen = set()
    out = []
    for c in candidates:
        key = c.get("link") or c.get("title")
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(c)

    return out


def scrape(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.content, "lxml")
    base_url = "{}://{}".format(urlparse(url).scheme, urlparse(url).netloc)

    # try main news lists
    news = find_news(soup, base_url)

    return news


def main():
    parser = argparse.ArgumentParser(description="Simple scraper for zamaleksc.com")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL to scrape")
    parser.add_argument("--output", default="zamalek_news.json", help="Output JSON file")
    parser.add_argument("--limit", type=int, default=20, help="Maximum items to save")
    args = parser.parse_args()

    items = scrape(args.url)
    if not items:
        print("No items found.")
    else:
        items = items[: args.limit]
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(items)} items to {args.output}")


if __name__ == "__main__":
    main()
