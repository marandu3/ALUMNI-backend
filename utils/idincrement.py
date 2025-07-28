from database.config import user_collection, news_collection, events_collection
import uuid

#this function is used to increment the id of a user
def increment_user_id():
    # Find the user with the maximum id
    max_user = user_collection.find_one(sort=[("id", -1)], projection={"id": 1})
    
    # If no users exist, start with id 1
    if not max_user:
        return 1
    
    # Increment the maximum id by 1
    return max_user["id"] + 1

#increment_news_id function
def increment_news_id():
    # Find the news item with the maximum id
    max_news = news_collection.find_one(sort=[("id", -1)], projection={"id": 1})
    
    # If no news items exist, start with id 1
    if not max_news:
        return 1
    
    # Increment the maximum id by 1
    return max_news["id"] + 1

#generate unique event id
def generate_event_id():
    return str(uuid.uuid4())

#generate unique news id
def generate_news_id():
    return str(uuid.uuid4())