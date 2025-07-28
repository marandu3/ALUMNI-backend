
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()
#Load environment variables from .env file
DATABASE_URL = os.getenv("DATABASE_URL")

uri = DATABASE_URL

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

#creating a database
db = client['ALUMNI']

#creating a collection\\\\]
user_collection = db['alumni']
news_collection = db['news']
payment_collection = db['payment']

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)