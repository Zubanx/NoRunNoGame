from urllib.parse import urlencode
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


access_token =""
user_data = {}

class User(BaseModel):
    first_name : str
    last_name : str
    city : str

    

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
async def read_root():
    return FileResponse("static/login.html")

@app.get("/login")
async def login():
    url = "https://www.strava.com/oauth/authorize?"
    parameters = {
        "client_id" : CLIENT_ID,
        "redirect_uri" : "http://127.0.0.1:8000/dashboard",
        "response_type" : "code",
        "approval_prompt" :"force",
        "scope" :"read"
    }
    query = urlencode(query=parameters)
    final_url = f"{url}{query}"
    print(final_url)
    return RedirectResponse(final_url)

@app.get("/dashboard")
def dashboard(code: str):
    global access_token, user_data
    
    print(f"=== TOKEN EXCHANGE WITH REDIRECT_URI ===")
    print(f"Code received: {code}")
    
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:8000/dashboard"  # ADD THIS LINE
    }
    
    url = "https://www.strava.com/oauth/token"
    
    print(f"Request params: {params}")
    
    try:
        token_response = requests.post(url, data=params)
        
        print(f"Response status: {token_response.status_code}")
        print(f"Response body: {token_response.text}")
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data["access_token"]
            user_data = token_data["athlete"]
            print(f"SUCCESS: Token obtained: {access_token}")
            return RedirectResponse("/static/dashboard.html")
        else:
            return {"error": f"Token exchange failed: {token_response.text}"}
            
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

@app.get("/user")
async def get_user():
    global user_data
    if not user_data:
        return {"error": "No user data available"}
    return user_data
    