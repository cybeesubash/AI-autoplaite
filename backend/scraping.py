# ============================================================
# scraping.py  –  Multi-Engine BeautifulSoup Web Scraper
# Engines: Google, DuckDuckGo, Bing (public search results)
# ============================================================

import os
import sys
import re
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.web_search import contains_pii

# ── Common Headers Pool ──────────────────────────────────────
HEADERS_CHROME = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

HEADERS_FIREFOX = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
        "Gecko/20100101 Firefox/125.0"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ── 1. Google Search Scraper ─────────────────────────────────
def scrape_google(query: str, max_results: int = 8) -> list:
    """
    Scrape Google search results using BeautifulSoup.
    Returns list of {title, snippet, url, domain, source_engine}.
    """
    results = []
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}&hl=en&num=10"

    try:
        resp = requests.get(url, headers=HEADERS_CHROME, timeout=6)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")

        # Each result block — Google wraps in <div class="g"> or <div jscontroller>
        blocks = soup.select("div.g, div[data-sokoban-container]")
        for block in blocks:
            if len(results) >= max_results:
                break

            # Title
            title_tag = block.find("h3")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # URL
            a_tag = block.find("a", href=True)
            if not a_tag:
                continue
            href = a_tag["href"]
            if href.startswith("/url?"):
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                href = parsed.get("q", [href])[0]
            if not href.startswith("http"):
                continue

            # Snippet — try multiple Google class patterns
            snippet = ""
            for sel in [
                "[data-sncf]", ".VwiC3b", ".IsZvec", ".aCOpRe",
                "div[style*='-webkit-line-clamp']", ".s3v9rd"
            ]:
                el = block.select_one(sel)
                if el:
                    snippet = el.get_text(separator=" ", strip=True)
                    break
            if not snippet:
                # fallback: grab all <span> text in block
                spans = block.find_all("span")
                for sp in spans:
                    t = sp.get_text(strip=True)
                    if len(t) > 40:
                        snippet = t[:300]
                        break

            if contains_pii(title) or contains_pii(snippet):
                continue

            domain = urllib.parse.urlparse(href).netloc
            results.append({
                "title": title,
                "snippet": snippet[:300],
                "url": href,
                "domain": domain,
                "source_engine": "Google"
            })

    except Exception as e:
        print(f"[Scraper:Google] {e}")

    return results


# ── 2. DuckDuckGo HTML Scraper ───────────────────────────────
def scrape_duckduckgo(query: str, max_results: int = 8) -> list:
    """
    Scrape DuckDuckGo HTML search using BeautifulSoup.
    """
    results = []
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    try:
        resp = requests.get(url, headers=HEADERS_FIREFOX, timeout=6)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        nodes = soup.find_all("div", class_="result__body")

        for node in nodes:
            if len(results) >= max_results:
                break

            title_tag = node.find("a", class_="result__a")
            snippet_tag = node.find("a", class_="result__snippet")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            href = title_tag.get("href", "#")

            # Resolve DDG redirect
            if "/l/?" in href or "uddg=" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                href = parsed.get("uddg", [href])[0]

            if not href.startswith("http"):
                continue
            if contains_pii(title) or contains_pii(snippet):
                continue

            domain = urllib.parse.urlparse(href).netloc
            results.append({
                "title": title,
                "snippet": snippet[:300],
                "url": href,
                "domain": domain,
                "source_engine": "DuckDuckGo"
            })

    except Exception as e:
        print(f"[Scraper:DuckDuckGo] {e}")

    return results


# ── 3. Bing Search Scraper ───────────────────────────────────
def scrape_bing(query: str, max_results: int = 6) -> list:
    """
    Scrape Bing search results using BeautifulSoup.
    """
    results = []
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}&setlang=en&cc=US&mkt=en-US"

    try:
        resp = requests.get(url, headers=HEADERS_CHROME, timeout=6)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("li.b_algo")

        for item in items:
            if len(results) >= max_results:
                break

            title_tag = item.find("h2")
            if not title_tag:
                continue
            a_tag = title_tag.find("a", href=True)
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            href = a_tag["href"]
            # Skip Bing internal redirect URLs
            if not href.startswith("http") or "bing.com/ck/" in href or "bing.com/search" in href:
                continue

            snippet = ""
            snippet_el = item.select_one(".b_caption p, p.b_algoSlug")
            if snippet_el:
                snippet = snippet_el.get_text(separator=" ", strip=True)

            if contains_pii(title) or contains_pii(snippet):
                continue

            domain = urllib.parse.urlparse(href).netloc
            results.append({
                "title": title,
                "snippet": snippet[:300],
                "url": href,
                "domain": domain,
                "source_engine": "Bing"
            })

    except Exception as e:
        print(f"[Scraper:Bing] {e}")

    return results


# ── 4. Full Page Content Extractor ───────────────────────────
def extract_public_page_snippet(url: str, max_chars: int = 400) -> str | None:
    """
    Safely extract meaningful public text snippet from a webpage using
    BeautifulSoup. Strips scripts, styles, nav, forms, and PII.
    """
    if not url or not url.startswith("http"):
        return None

    try:
        resp = requests.get(url, headers=HEADERS_FIREFOX, timeout=5)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noisy elements
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "form", "input", "button", "aside", "noscript"]):
            tag.decompose()

        # Try <article> first for structured content
        article = soup.find("article")
        source = article if article else soup.find("main") or soup.find("body")

        if not source:
            return None

        paragraphs = source.find_all("p")
        for p in paragraphs:
            text = re.sub(r'\s+', ' ', p.get_text()).strip()
            if len(text) > 60 and not contains_pii(text):
                return (text[:max_chars] + "…") if len(text) > max_chars else text

        # Fallback: plain text dump
        raw = re.sub(r'\s+', ' ', source.get_text()).strip()
        if len(raw) > 60 and not contains_pii(raw):
            return (raw[:max_chars] + "…") if len(raw) > max_chars else raw

    except Exception as e:
        print(f"[Scraper:PageExtract] Skipped {url}: {e}")

    return None


# ── 5. Multi-Engine Merged Search ───────────────────────────
def multi_engine_search(query: str, max_per_engine: int = 5) -> list:
    """
    Run query across Google + DuckDuckGo + Bing in sequence,
    merge results, deduplicate by URL, return ranked list.
    """
    all_results = []
    seen_urls = set()

    engines = [
        ("Google",     lambda q: scrape_google(q, max_per_engine)),
        ("DuckDuckGo", lambda q: scrape_duckduckgo(q, max_per_engine)),
        ("Bing",       lambda q: scrape_bing(q, max_per_engine)),
    ]

    for engine_name, fn in engines:
        try:
            results = fn(query)
            for r in results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)
        except Exception as e:
            print(f"[MultiEngine:{engine_name}] {e}")
        time.sleep(0.1)  # small polite delay between engines

    return all_results


# ── 6. Plate-Focused Public Search ──────────────────────────
def search_plate_number(plate: str, max_results: int = 12) -> list:
    """
    Run multi-engine public search specifically for an Indian/global
    vehicle registration number. Returns merged, deduplicated results.
    """
    clean = re.sub(r'[^A-Z0-9]', '', plate.upper().strip())
    if len(clean) < 2:
        return []

    spaced = " ".join(re.findall(r'[A-Z]+|\d+', clean))

    queries = [
        f'"{clean}" vehicle registration',
        f'"{spaced}" number plate India',
        f'"{clean}" RTO site:carinfo.app OR site:parivahan.gov.in OR site:team-bhp.com',
    ]

    all_results = []
    seen_urls = set()

    for q in queries:
        for r in multi_engine_search(q, max_per_engine=4):
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                # Mark relevance
                r["relevance_label"] = (
                    "Exact match" if clean in r["title"].upper().replace(" ", "") or
                    clean in r["snippet"].upper().replace(" ", "")
                    else "Potentially related"
                )
                all_results.append(r)
        if len(all_results) >= max_results:
            break

    return all_results[:max_results]
