import os

import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

DB_NAME = os.getenv("DB_NAME", "books")
db = client.get_database(DB_NAME)
books_collection = db.get_collection(DB_NAME)
