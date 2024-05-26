import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    SECRET_KEY = os.urandom(24)
    MONGO_URI = os.environ.get('MONGO_URI')
    if MONGO_URI is None:
        raise ValueError("No MONGO_URI environment variable set")
    MONGO_DBNAME = 'rentify_db'
