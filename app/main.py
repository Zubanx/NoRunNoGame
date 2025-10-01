from urllib.parse import urlencode
from typing import Annotated, List
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timedelta, timezone


access_token =""
user_data = {}

class User(BaseModel):
    first_name : str
    last_name : str
    city : str

class Activity(BaseModel):
    name: str
    type: str
    sport_type: str
    start_date_local: datetime
    elapsed_time: int
    description: str
    distance: float
    trainer: int
    commute: int


    

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
async def read_root():
    return FileResponse("static/login.html")

#Used to redirect to the Strava auth page to get code
@app.get("/login")
async def login():
    url = "https://www.strava.com/oauth/authorize?"
    parameters = {
        "client_id" : CLIENT_ID,
        "redirect_uri" : "http://127.0.0.1:8000/dashboard",
        "response_type" : "code",
        "approval_prompt" :"force",
        "scope" :"activity:read_all,activity:write"
    }
    query = urlencode(query=parameters)
    final_url = f"{url}{query}"
    print(final_url)
    return RedirectResponse(final_url)

#Exchanges code for access token
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
        "redirect_uri": "http://127.0.0.1:8000/dashboard" 
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

# Used to display user on dashboard
@app.get("/user")
async def get_user():
    global user_data
    if not user_data:
        return {"error": "No user data available"}
    return user_data


# Creates activity for testing purposes
# @app.post("/activities")
# async def create_activity():
#     activity = {
#     "name": "Morning Hill Run",
#     "type": "Run",
#     "sport_type": "Run",
#     "start_date_local": "2025-09-30T06:15:00",
#     "elapsed_time": 2847,
#     "description": "Beautiful sunrise run through the park. Felt strong on the hills today!",
#     "distance": 8420.5,
#     "trainer": 0,
#     "commute": 0
# }
#     url = "https://www.strava.com/api/v3/activities"
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     activity_response = requests.post(url, json=activity, headers=headers)
#     if activity_response.status_code == 201:
#         return {"message": "Activity created successfully", "data": activity_response.json()}
#     else:
#         return {
#             "error": f"Creating activity failed: {activity_response.text}",
#             "status_code": activity_response.status_code
#         }

#Get all weekly miles
@app.get("/activities")
async def get_weekly_miles():

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    url = "https://www.strava.com/api/v3/athlete/activities"
    params = {
        "before" : now.timestamp(),
        "after" : week_ago.timestamp(),
        "per_page" : 5
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    activity_request = requests.get(url, params=params, headers=headers)
    if activity_request.status_code == 200:
        activities = activity_request.json()
        print("!!!!!!")
        print(activities)
        total_miles = sum(
            activity.get('distance', 0) 
            for activity in activities 
            if activity.get('type') == 'Run'
        )
        print(f"Total miles: {total_miles}")
        return total_miles
    else:
        return {"error:" f"Failed to fetch miles ran: {activity_request.text}"}
    
