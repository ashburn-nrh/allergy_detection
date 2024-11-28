# main.py
from fastapi import FastAPI, HTTPException
from model import Profile, UpdateProfile
from fastapi.middleware.cors import CORSMiddleware
# from db import profiles_collection
from bson import ObjectId
from bson import ObjectId
from pymongo import ReturnDocument
app = FastAPI()
# db.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.test  # Replace with your MongoDB database name
profiles_collection = db.profile # Collection for profile data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Fetch Profile
@app.get("/api/profile/{uid}", response_model=Profile)
async def get_profile(uid: str):
    profile = await profiles_collection.find_one({"uid": uid})
    if profile:
        # Convert ObjectId to string for JSON serialization
        profile["_id"] = str(profile["_id"])
        return profile
    raise HTTPException(status_code=404, detail="Profile not found")

# Update Profile
@app.post("/api/profile/{uid}", response_model=Profile)
async def update_or_create_profile(uid: str, profile_data: UpdateProfile):
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    if update_data:
        # Attempt to update an existing profile
        profile = await profiles_collection.find_one_and_update(
            {"uid": uid},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if profile:
            profile["_id"] = str(profile["_id"])
            return profile

        # If profile doesn't exist, create a new one
        new_profile_data = {"uid": uid, **update_data}
        result = await profiles_collection.insert_one(new_profile_data)
        new_profile_data["_id"] = str(result.inserted_id)
        return new_profile_data

    raise HTTPException(status_code=400, detail="No data provided for update or creation")