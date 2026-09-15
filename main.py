from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

URLS = {
    "Emergency": "https://wrha.mb.ca/wait-times/emergency/",
    "Urgent Care": "https://wrha.mb.ca/wait-times/urgent-care/"
}

# Mimic a complete desktop browser request to bypass bot blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

@app.get("/")
def root():
    return {"status": "WRHA Wait Times API is running"}

@app.get("/api/waittimes")
@app.get("/api/waittimes/")
def get_wait_times():
    results = {"Emergency": [], "Urgent Care": []}

    session = requests.Session()
    session.headers.update(HEADERS)

    for category, url in URLS.items():
        try:
            resp = session.get(url, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Extract rows from any table element present
                for tr in soup.find_all('tr'):
                    # Collect non-empty text from cells
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th']) if td.get_text(strip=True)]

                    if len(cells) >= 4:
                        facility = cells[0]

                        # Filter out table header rows
                        if any(h in facility.lower() for h in ["facility", "hospital", "location", "department", "urgent care"]):
                            continue

                        waiting = cells[1]
                        treating = cells[2]
                        wait_str = cells[3]

                        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", wait_str)
                        hours = float(match.group(1)) if match else None

                        results[category].append({
                            "facility": facility,
                            "waiting": waiting,
                            "treating": treating,
                            "waitTime": wait_str,
                            "hours": hours
                        })
        except Exception as e:
            print(f"Error fetching {category}: {e}")

    return results
