from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json



class Item(BaseModel):
    name: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/dronedata")
async def root(request: Request):
    # response = await request.json()
    with open("waypoint_mission.json", "r") as f:
        data = json.load(f)
    print(type(data))
    print(data)
    return json.dumps(data)