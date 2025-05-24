from database.config import user_collection

#this function is used to increment the id of a user
def increment_user_id():
    # Find the user with the maximum id
    max_user = user_collection.find_one(sort=[("id", -1)], projection={"id": 1})
    
    # If no users exist, start with id 1
    if not max_user:
        return 1
    
    # Increment the maximum id by 1
    return max_user["id"] + 1
# This function can be used when creating a new user to ensure unique IDs
# Example usage:
# new_user_id = increment_user_id()
# print(new_user_id)  # This will print the next available user ID
# Note: Ensure that the user_collection is properly defined and connected to your MongoDB instance.
# Ensure that the user_collection is properly defined and connected to your MongoDB instance.
