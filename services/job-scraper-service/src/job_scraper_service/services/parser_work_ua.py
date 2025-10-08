import re
import requests
import gzip
import brotli
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

BASE = "https://www.work.ua"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
}


def _decode_response(response: requests.Response) -> str:
    encoding = (response.headers.get("Content-Encoding") or "").lower()
    raw = response.content
    try:
        if "br" in encoding:
            return brotli.decompress(raw).decode("utf-8", errors="ignore")
        if "gzip" in encoding:
            return gzip.decompress(raw).decode("utf-8", errors="ignore")
        return response.text
    except Exception:
        return response.text


def fetch_job_description(job_url: str, desc_limit: Optional[int] = None) -> str:
    """
    Загружает и обрезает описание вакансии.
    Args:
        job_url: ссылка на вакансию
        desc_limit: максимальная длина описания (в символах)
    """
    try:
        response = requests.get(job_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        desc_div = soup.find("div", class_="card-body") or soup.find("div", class_="job-description")
        if not desc_div:
            return ""
        text = desc_div.get_text("\n", strip=True)
        if desc_limit and len(text) > desc_limit:
            text = text[:desc_limit].rsplit(" ", 1)[0] + "..."
        return text
    except Exception as e:
        print(f"Ошибка при получении описания {job_url}: {e}")
        return ""


def parse_workua(query: str, pages: int = 1, desc_limit: Optional[int] = None) -> List[Dict]:
    """
    Парсит вакансии с work.ua
    Args:
        query: поисковый запрос
        pages: количество страниц для парсинга
        desc_limit: максимальная длина описания вакансии (None — без обрезки)
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    results: List[Dict] = []

    query_part = quote_plus(query)
    base_search = f"{BASE}/en/jobs-{query_part}/"

    for p in range(pages):
        page_num = p + 1
        url = base_search if page_num == 1 else f"{base_search}?page={page_num}"
        try:
            resp = session.get(url, timeout=15)
        except requests.RequestException as e:
            print(f"[work.ua] network error for page {page_num}: {e}")
            continue

        html = _decode_response(resp)
        soup = BeautifulSoup(html, "html.parser")
        h2_tags = soup.find_all("h2")

        if not h2_tags:
            break

        for h2 in h2_tags:
            a = h2.find("a", href=True)
            if not a or not re.search(r"(vacanc|vacancy|vacancies|jobs|job)", a["href"]):
                continue
            link = urljoin(BASE, a["href"])
            title = a.get_text(strip=True)

            company, location, salary, date, snippet = None, None, None, None, None
            parent = h2.parent
            candidates = []
            for _ in range(3):
                if parent is None:
                    break
                candidates.extend(parent.find_all(["p", "div", "span", "a"], recursive=False))
                parent = parent.parent
            if not candidates:
                sibs = [sib for sib in h2.next_siblings if hasattr(sib, "get_text")][:6]
                candidates = sibs

            for c in candidates:
                text = c.get_text(" ", strip=True)
                if not text:
                    continue
                if re.search(r"\b(годин|години|днів|день|тому|ago|day|days)\b", text, flags=re.I) and not date:
                    date = text
                    continue
                if re.search(r"\bгрн\b|₴|UAH|\$\s?\d|€\s?\d", text) and not salary:
                    salary = text
                    continue
                if not company and len(text.split()) <= 6 and not re.search(r"\d", text):
                    if not re.search(r"повна|часткова|дистанц|remote|full-time|part-time", text, flags=re.I):
                        company = text
                        continue
                if not location and re.search(r"[,•]|Київ|Дистанц|Remote|Робота віддалено|м\.", text, flags=re.I):
                    location = text
                    continue
                if not snippet:
                    snippet = text

            description = fetch_job_description(link, desc_limit)

            results.append({
                "title": title,
                "company": company or "-",
                "location": location or "-",
                "salary": salary or "-",
                "link": link,
                "description": description or "-",
            })

    return results
