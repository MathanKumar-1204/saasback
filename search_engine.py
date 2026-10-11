import re
import base64
import urllib.parse
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

SKIP_DOMAINS = [
    "wikipedia", "bing.com", "microsoft", "youtube", "facebook", "pdf", "scribd", 
    "gov", "ibef", "indiapost", "britannica", "geeksforgeeks", "just a moment", 
    "cloudflare", "amazon", "ebay", "flipkart", "twitter", "instagram", "yahoo", "google"
]

def find_company_urls(industry, product, count=8):
    """
    Module 1: Dedicated Search Engine.
    Executes live web search queries to discover top 5 to 10 company website URLs.
    """
    ind_str = industry.strip() if industry else "Software"
    prod_str = product.strip() if product else "Enterprise Solutions"

    search_queries = [
        f"{ind_str} {prod_str} company official website",
        f"top {ind_str} companies for {prod_str}",
        f"{prod_str} manufacturer enterprise portal"
    ]

    discovered_urls = []

    for query in search_queries:
        if len(discovered_urls) >= count:
            break
            
        bing_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": USER_AGENT}
        
        try:
            resp = requests.get(bing_url, headers=headers, timeout=6)
            soup = BeautifulSoup(resp.text, "html.parser")
            
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "u=a1" in href:
                    b64_part = href.split("u=a1")[1].split("&")[0]
                    b64_part += "=" * (-len(b64_part) % 4)
                    try:
                        real_url = base64.b64decode(b64_part).decode("utf-8", errors="ignore")
                        if real_url.startswith("http") and not any(skip in real_url.lower() for skip in SKIP_DOMAINS):
                            if real_url not in discovered_urls:
                                discovered_urls.append(real_url)
                    except Exception:
                        pass
        except Exception as e:
            print(f"--> [SEARCH ENGINE ERROR] {query}: {e}", flush=True)

    print(f"--> [SEARCH ENGINE] Discovered {len(discovered_urls)} live company URLs for '{ind_str} - {prod_str}': {discovered_urls[:5]}", flush=True)
    return discovered_urls[:count]
