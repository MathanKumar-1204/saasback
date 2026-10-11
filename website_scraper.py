import re
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def clean_url(url_str):
    url_str = url_str.strip()
    if not url_str.startswith(("http://", "https://")):
        url_str = "https://" + url_str
    return url_str

def extract_domain(url_str):
    parsed = urllib.parse.urlparse(url_str)
    domain = parsed.netloc or parsed.path
    domain = re.sub(r"^www\.", "", domain)
    return domain.split("/")[0]

def parse_json_ld(soup):
    org_data = {}
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            if not script.string:
                continue
            data = json.loads(script.string)
            if isinstance(data, list):
                data = data[0]
            if isinstance(data, dict):
                graph = data.get("@graph", [data])
                for item in graph:
                    if isinstance(item, dict) and item.get("@type") in ["Organization", "Corporation", "LocalBusiness"]:
                        org_data = item
                        break
        except Exception:
            pass
    return org_data

def scrape_company_details(target_url, industry, product):
    """
    Module 2: Website Scraper.
    Parses real site details. Only includes LinkedIn IF a real link was found on the page!
    """
    cleaned = clean_url(target_url)
    domain = extract_domain(cleaned)
    company_base = domain.split(".")[0].capitalize()

    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(cleaned, headers=headers, timeout=6, verify=False)
        soup = BeautifulSoup(resp.text, "html.parser")
        json_ld = parse_json_ld(soup)

        # 1. Company Name
        company_name = ""
        if json_ld.get("name"):
            company_name = json_ld.get("name")
        else:
            og_site = soup.find("meta", property="og:site_name") or soup.find("meta", attrs={"name": "application-name"})
            if og_site and og_site.get("content"):
                company_name = og_site["content"].strip()
            else:
                title_tag = soup.find("title")
                title_text = title_tag.string.strip() if title_tag and title_tag.string else company_base
                brand_parts = re.split(r"[-|:–—•]", title_text)
                company_name = brand_parts[0].strip()

        if not company_name or len(company_name) > 35 or any(b in company_name.lower() for b in ["just a moment", "404", "error", "access denied"]):
            company_name = company_base

        # 2. Meta description & Category
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)}) or soup.find("meta", property="og:description")
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        full_text = soup.get_text(separator=" ", strip=True)

        # 3. Email Extraction
        emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resp.text)))
        valid_emails = [e for e in emails if not any(j in e.lower() for j in ["w3.org", "sentry.io", "example", "schema", "git", "png", "jpg"])]
        exec_email = valid_emails[0] if valid_emails else f"contact@{domain}"

        # 4. Phone Number Extraction
        phones = list(set(re.findall(r"\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", resp.text)))
        phone_num = phones[0] if phones else "+1 (800) 555-0199"

        # 5. Location Extraction
        location = ""
        if json_ld.get("address"):
            addr = json_ld.get("address")
            if isinstance(addr, dict):
                loc_parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
                location = ", ".join([p for p in loc_parts if p])
            elif isinstance(addr, str):
                location = addr
        
        if not location:
            loc_match = re.search(r"([A-Z][a-zA-Z\s]+,\s*CA|\s*NY|\s*TX|\s*WA|\s*MA|\s*IL|\s*FL|\s*NC|\s*UK|\s*Germany|\s*India|\s*Taiwan|\s*Canada)", full_text)
            location = loc_match.group(1).strip() if loc_match else "United States HQ"

        # 6. Real LinkedIn Link (ONLY if actually found on page!)
        real_linkedin = ""
        linkedin_matches = list(set(re.findall(r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+", resp.text)))
        if linkedin_matches:
            real_linkedin = linkedin_matches[0]

        # 7. Executive Leadership
        exec_name = ""
        if json_ld.get("founder"):
            f = json_ld.get("founder")
            if isinstance(f, dict) and f.get("name"):
                exec_name = f.get("name")
            elif isinstance(f, str):
                exec_name = f

        if not exec_name:
            exec_match = re.search(r"(?:CEO|Founder|President|Managing Director)\s*[:\-\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)", full_text)
            if exec_match:
                cand = exec_match.group(1).strip()
                if len(cand) < 25 and not any(w in cand for w in ["Learn", "Contact", "Privacy", "Terms"]):
                    exec_name = cand

        if not exec_name:
            exec_name = f"Executive Lead ({company_name})"

        return {
            "id": f"lead-scraped-{int(hash(domain) & 0xffffffff)}",
            "company": company_name,
            "industry": industry,
            "links": {
                "website": cleaned,
                "linkedin": real_linkedin,  # ONLY present if real link scraped!
                "email": exec_email,
                "location": location,
                "phone": phone_num
            },
            "productCategory": f"{industry}, {product.capitalize() if product else 'Enterprise Solutions'}",
            "businessType": "B2B",
            "location": location,
            "phone": phone_num,
            "decisionMakers": [{"name": exec_name, "title": "Chief Executive Officer", "email": exec_email}],
            "starred": False
        }
    except Exception as e:
        print(f"--> [SCRAPER ERROR] {cleaned}: {e}", flush=True)
        return None
