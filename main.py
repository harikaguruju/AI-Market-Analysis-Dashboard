from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
import os
from dotenv import load_dotenv
import time

# load env
load_dotenv()

app = FastAPI()

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# API KEY
# -------------------------------
API_KEY = "mysecret123"
api_key_header = APIKeyHeader(name="x-api-key")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# -------------------------------
# RATE LIMIT
# -------------------------------
request_log = {}
RATE_LIMIT = 5
TIME_WINDOW = 60

def check_rate_limit(client_ip):
    current_time = time.time()

    if client_ip not in request_log:
        request_log[client_ip] = []

    request_log[client_ip] = [
        t for t in request_log[client_ip]
        if current_time - t < TIME_WINDOW
    ]

    if len(request_log[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    request_log[client_ip].append(current_time)

# -------------------------------
# FETCH NEWS (simple mock)
# -------------------------------
def fetch_news(sector):
    return [
        f"{sector} sector is growing rapidly in India",
        f"Investments in {sector} are increasing",
        f"Government policies support {sector}",
        f"{sector} startups are booming",
        f"Competition in {sector} is rising"
    ]

# -------------------------------
# ROUTES
# -------------------------------
@app.get("/analyze/{sector}")
def analyze_sector(
    sector: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):

    check_rate_limit(request.client.host)

    insights = fetch_news(sector)

    report = f"""
# Market Analysis: {sector}

## Current Trends
- {insights[0]}
- {insights[1]}

## Opportunities
- Growing demand
- Strong investment flow

## Risks
- High competition
- Regulatory challenges

## Conclusion
The {sector} sector shows strong future potential.
"""

    return {
        "sector": sector,
        "report": report,
        "metrics": {
            "growth": 80,
            "risk": 60,
            "demand": 75
        }
    }

# -------------------------------
# SERVE FRONTEND (VERY IMPORTANT)
# -------------------------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")