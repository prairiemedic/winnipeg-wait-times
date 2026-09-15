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

@app.get("/api/waittimes")
def get_waittimes():
    results = {"Emergency": [], "Urgent Care": []}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    urls = {
        "Emergency": "https://wrha.mb.ca/wait-times/emergency/",
        "Urgent Care": "https://wrha.mb.ca/wait-times/urgent-care/"
    }

    for category, url in urls.items():
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tr in soup.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th']) if td.get_text(strip=True)]
                if len(cells) >= 4 and not any(h in cells[0].lower() for h in ["facility", "hospital"]):
                    results[category].append({
                        "facility": cells[0],
                        "waiting": cells[1],
                        "treating": cells[2],
                        "waitTime": cells[3]
                    })
        except Exception as e:
            print(f"Error: {e}")

    return results
