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

                # Target every row in all tables
                for tr in soup.find_all('tr'):
                    # Gather text from cells, filtering empty strings
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th']) if td.get_text(strip=True)]

                    # A valid data row has at least Facility, Waiting, Treating, and Wait Time
                    if len(cells) >= 4:
                        facility = cells[0]

                        # Skip header rows
                        if any(h in facility.lower() for h in ["facility", "hospital", "department", "urgent care", "location"]):
                            continue

                        waiting = cells[1]
                        treating = cells[2]
                        wait_str = cells[3]

                        # Extract numeric hours for visual styling logic in frontend
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
