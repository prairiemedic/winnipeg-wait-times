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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.get("/")
def root():
    return {"status": "WRHA Wait Times API is running"}

@app.get("/api/waittimes")
@app.get("/api/waittimes/")
def get_wait_times():
    results = {"Emergency": [], "Urgent Care": []}

    for category, url in URLS.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    for tr in table.find_all('tr'):
                        cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]

                        # Verify row has valid columns and skip table header rows
                        if len(cols) >= 4 and not any(h in cols[0].lower() for h in ["facility", "location", "hospital"]):
                            match = re.search(r"([0-9]+(?:\.[0-9]+)?)", cols[3])
                            hours = float(match.group(1)) if match else None

                            results[category].append({
                                "facility": cols[0],
                                "waiting": cols[1],
                                "treating": cols[2],
                                "waitTime": cols[3],
                                "hours": hours
                            })
        except Exception as e:
            print(f"Error fetching {category}: {e}")

    return results
