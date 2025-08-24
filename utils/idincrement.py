from database.config import user_collection, news_collection

def increment_user_id():
    max_user = user_collection.find_one(sort=[("id", -1)], projection={"id": 1})
    if not max_user:
        return 1
    return max_user["id"] + 1

def increment_news_id():
    max_news = news_collection.find_one(sort=[("id", -1)], projection={"id": 1})
    if not max_news:
        return 1
    return max_news["id"] + 1
