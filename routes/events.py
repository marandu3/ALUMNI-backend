from fastapi import APIRouter, HTTPException, Depends
from models.events import EventCreate, EventUpdate, EventInResponse, EventRegistration
from database.config import events_collection
from routes.user import get_current_user, role_required
from models.token import TokenData
from utils.idincrement import generate_event_id
from datetime import datetime
from typing import List

router = APIRouter()

# Create new event (admin only)
@router.post("/events", response_model=EventInResponse)
async def create_event(event: EventCreate, current_user: TokenData = Depends(role_required("admin"))):
    event_dict = event.model_dump()
    event_dict["id"] = generate_event_id()
    event_dict["created_by"] = current_user.username
    event_dict["created_at"] = datetime.utcnow()
    event_dict["status"] = "upcoming"
    event_dict["registrations"] = []

    result = events_collection.insert_one(event_dict)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create event")
    
    created_event = events_collection.find_one({"_id": result.inserted_id}, {"_id": 0})
    return EventInResponse(**created_event)

# Get all upcoming events (public)
@router.get("/events")
async def get_events():
    events = events_collection.find({"status": "upcoming"}, {"_id": 0}).sort("event_date", 1)
    events_list = [EventInResponse(**event) for event in events]
    return events_list

# Get all events (admin only)
@router.get("/admin/events")
async def get_all_events(current_user: TokenData = Depends(role_required("admin"))):
    events = events_collection.find({}, {"_id": 0}).sort("event_date", -1)
    events_list = [EventInResponse(**event) for event in events]
    return events_list

# Get event by ID
@router.get("/events/{event_id}")
async def get_event_by_id(event_id: str):
    event = events_collection.find_one({"id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventInResponse(**event)

# Update event (admin only)
@router.put("/events/{event_id}", response_model=EventInResponse)
async def update_event(event_id: str, event: EventUpdate, current_user: TokenData = Depends(role_required("admin"))):
    event_dict = event.model_dump(exclude_unset=True)
    event_dict["updated_at"] = datetime.utcnow()
    
    updated_event = events_collection.find_one_and_update(
        {"id": event_id},
        {"$set": event_dict},
        return_document=True
    )
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return EventInResponse(**updated_event)

# Delete event (admin only)
@router.delete("/events/{event_id}")
async def delete_event(event_id: str, current_user: TokenData = Depends(role_required("admin"))):
    result = events_collection.delete_one({"id": event_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}

# Register for event
@router.post("/events/{event_id}/register")
async def register_for_event(event_id: str, registration: EventRegistration, current_user: TokenData = Depends(get_current_user)):
    event = events_collection.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user is already registered
    if any(reg["user_id"] == current_user.username for reg in event.get("registrations", [])):
        raise HTTPException(status_code=400, detail="Already registered for this event")
    
    # Check if event is full
    if len(event.get("registrations", [])) >= event.get("max_participants", 0) and event.get("max_participants", 0) > 0:
        raise HTTPException(status_code=400, detail="Event is full")
    
    registration_data = {
        "user_id": current_user.username,
        "registration_date": datetime.utcnow(),
        "additional_info": registration.additional_info
    }
    
    result = events_collection.update_one(
        {"id": event_id},
        {"$push": {"registrations": registration_data}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to register for event")
    
    return {"message": "Successfully registered for event"}

# Unregister from event
@router.delete("/events/{event_id}/unregister")
async def unregister_from_event(event_id: str, current_user: TokenData = Depends(get_current_user)):
    result = events_collection.update_one(
        {"id": event_id},
        {"$pull": {"registrations": {"user_id": current_user.username}}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Not registered for this event")
    
    return {"message": "Successfully unregistered from event"}

# Get user's registered events
@router.get("/my-events")
async def get_my_events(current_user: TokenData = Depends(get_current_user)):
    events = events_collection.find(
        {"registrations.user_id": current_user.username},
        {"_id": 0}
    ).sort("event_date", 1)
    
    events_list = [EventInResponse(**event) for event in events]
    return events_list 