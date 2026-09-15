from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direct WRHA REST API endpoints
ENDPOINTS = {
    "Emergency": "https://wrha.mb.ca/wp-json/wrha/v1/wait-times/emergency",
    "Urgent Care": "https://wrha.mb.ca/wp-json/wrha/v1/wait-times/urgent-care"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

@app.get("/")
def root():
    return {"status": "WRHA Wait Times API is running"}

@app.get("/api/waittimes")
def get_wait_times():
    results = {"Emergency": [], "Urgent Care": []}
    session = requests.Session()
    session.headers.update(HEADERS)

    for category, url in ENDPOINTS.items():
        try:
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data:
                    results[category].append({
                        "facility": item.get("name", item.get("facility", "")),
                        "waiting": str(item.get("waiting", 0)),
                        "treating": str(item.get("treating", 0)),
                        "waitTime": item.get("wait_time", item.get("waitTime", "N/A")),
                        "hours": item.get("hours", None)
                    })
        except Exception as e:
            print(f"Error fetching {category}: {e}")

    return results
