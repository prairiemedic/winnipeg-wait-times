from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.get("/api/waittimes")
def get_waittimes():
    scraped_results = {"Emergency": [], "Urgent Care": []}

    for category, url in URLS.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Scrape every table on the page (catches both main and sub-tables)
                tables = soup.find_all('table')
                for table in tables:
                    # [1:] skips the header row [0]
                    for tr in table.find_all('tr')[1:]:
                        cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                        if len(cols) >= 4:
                            fac_name = cols[0]
                            # Ignore any lingering header text
                            if "facility" in fac_name.lower() or "department" in fac_name.lower():
                                continue

                            scraped_results[category].append({
                                "facility": cols[0],
                                "waiting": cols[1],
                                "treating": cols[2],
                                "waitTime": cols[3]
                            })
        except Exception as e:
            print(f"Error fetching {category}: {e}")

    return scraped_results
