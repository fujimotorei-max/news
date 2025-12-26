# src/search_news.py
import os
import requests
from typing import List, Dict, Optional

API_KEY = os.environ["GOOGLE_SEARCH_API_KEY"]
CX = os.environ["GOOGLE_SEARCH_CX"]

# 「全国レベルの重要ニュース」寄せの信頼ソース
TRUSTED_DOMAINS = [
    # 国内主要メディア
    "www.nhk.or.jp",
    "www3.nhk.or.jp",
    "www.nikkei.com",
    "www.asahi.com",
    "www.yomiuri.co.jp",
    "mainichi.jp",
    "www.sankei.com",
    "www.jiji.com",
    "www.kyodo.co.jp",
    # 国際通信（日本関連が強い）
    "jp.reuters.com",
    "www.bloomberg.co.jp",
    # 政府・公的機関（制度系の一次情報）
    "www.kantei.go.jp",
    "www.mhlw.go.jp",
    "www.mof.go.jp",
    "www.boj.or.jp",
    "www.soumu.go.jp",
    "www.meti.go.jp",
    "www.cas.go.jp",
    "www8.cao.go.jp",
]

# 明確に落としたいもの（会話用でも邪魔になりがち）
BLOCKED_DOMAINS = [
    "prtimes.jp",
]

def _domain_ok(link: str, allow_domains: Optional[List[str]], block_domains: Optional[List[str]]) -> bool:
    if block_domains:
        for d in block_domains:
            if d in link:
                return False
    if allow_domains:
        return any(d in link for d in allow_domains)
    return True

def search(query: str, num: int = 10, date_restrict: str = "d2",
           allow_domains: Optional[List[str]] = None,
           block_domains: Optional[List[str]] = None) -> List[Dict]:
    """
    date_restrict:
      d1=過去1日, d2=過去2日, d7=過去7日 ... (Google CSEの仕様)
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
        # sort=date は環境によって効き方がぶれるので dateRestrict を主に使う
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
        if not _domain_ok(link, allow_domains, block_domains):
            continue

        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": link,
            "source": item.get("displayLink"),
        })
    return results
