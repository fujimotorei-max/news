# src/search_news.py
import os
import requests
from typing import List, Dict, Optional
import re
from datetime import datetime, timedelta

API_KEY = os.environ["GOOGLE_SEARCH_API_KEY"]
CX = os.environ["GOOGLE_SEARCH_CX"]

# 信頼ソース
TRUSTED_DOMAINS = [
    "www.nhk.or.jp",
    "www3.nhk.or.jp",
    "www.nikkei.com",
    "www.asahi.com",
    "www.yomiuri.co.jp",
    "mainichi.jp",
    "www.sankei.com",
    "www.jiji.com",
    "www.kyodo.co.jp",
    "jp.reuters.com",
    "www.bloomberg.co.jp",
    "www.kantei.go.jp",
    "www.mhlw.go.jp",
    "www.mof.go.jp",
    "www.boj.or.jp",
    "www.soumu.go.jp",
    "www.meti.go.jp",
    "www.cas.go.jp",
    "www8.cao.go.jp",
]

# 除外
BLOCKED_DOMAINS = [
    "prtimes.jp",
]


# -----------------------------
# ドメインフィルタ
# -----------------------------
def _domain_ok(link: str,
               allow_domains: Optional[List[str]],
               block_domains: Optional[List[str]]) -> bool:

    if block_domains:
        for d in block_domains:
            if d in link:
                return False

    if allow_domains:
        return any(d in link for d in allow_domains)

    return True


# -----------------------------
# 記事日付判定（n日以内）
# -----------------------------
def _is_recent(snippet: str, days: int = 7) -> bool:
    if not snippet:
        return False

    today = datetime.now().date()

    # 年あり日付
    m = re.search(r"(20\d{2})[年/-](\d{1,2})[月/-](\d{1,2})", snippet)
    if m:
        y, mth, d = map(int, m.groups())
        try:
            article_date = datetime(y, mth, d).date()
            return today - article_date <= timedelta(days=days)
        except:
            return False

    # 年なし日付（3月26日 / 03/26）
    m = re.search(r"(\d{1,2})[月/-](\d{1,2})", snippet)
    if m:
        mth, d = map(int, m.groups())
        try:
            article_date = datetime(today.year, mth, d).date()
            return today - article_date <= timedelta(days=days)
        except:
            return False

    return False


# -----------------------------
# Google検索
# -----------------------------
def search(query: str,
           num: int = 10,
           date_restrict: str = "d2",
           allow_domains: Optional[List[str]] = None,
           block_domains: Optional[List[str]] = None,
           days: int = 7) -> List[Dict]:
    """
    date_restrict:
      d1=過去1日, d2=過去2日, d7=過去7日
      （Googleのクロール日基準）

    days:
      記事公開日ベースでのフィルタ日数
      Daily=2, Weekly=7
    """

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "hl": "ja",
        "gl": "jp",
        "num": num,
        "dateRestrict": date_restrict,
    }

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    results: List[Dict] = []
    items = data.get("items", []) or []

    for item in items:
        link = item.get("link", "") or ""
        if not link:
            continue

        # ドメインフィルタ
        if not _domain_ok(link, allow_domains, block_domains):
            continue

        snippet = item.get("snippet", "")

        # 日付フィルタ
        if not _is_recent(snippet, days):
            continue

        results.append({
            "title": item.get("title"),
            "snippet": snippet,
            "link": link,
            "source": item.get("displayLink"),
        })

    return results
