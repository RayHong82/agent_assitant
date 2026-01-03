import requests
from bs4 import BeautifulSoup


def fetch_and_summarize(url: str) -> dict:
    """Fetch url (simple) and return title and first paragraphs."""
    headers = {"User-Agent": "PropertyAgentAssistant/1.0 (+https://example.com)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    # grab first few paragraphs
    paras = [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip()]
    summary = "\n\n".join(paras[:3])
    return {"url": url, "title": title, "summary": summary}
