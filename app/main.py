from urllib.parse import urlencode
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
import requests



app = FastAPI()

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/login")
async def login():
    url = "https://www.strava.com/oauth/authorize?"
    parameters = {
        "client_id" : CLIENT_ID,
        "redirect_uri" : "http://127.0.0.1:8000/dashboard",
        "response_type" : "code",
        "approval_prompt" :"auto",
        "scope" :"read_all"
    }
    query = urlencode(query=parameters)
    final_url = f"{url}{query}"
    print(final_url)
    return RedirectResponse(final_url)

@app.get("/dashboard")
async def dashboard(code : str):
    params = {
        "client_id" : CLIENT_ID,
        "client_secret" : CLIENT_SECRET,
        "code" : code,
        "grant_type": "authorization_code"
    }
    url = "https://www.strava.com/oauth/token"
    token_response = requests.post(url, params=params)
    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data["access_token"]
    return RedirectResponse("http://127.0.0.1:5500/dashboard.html")
