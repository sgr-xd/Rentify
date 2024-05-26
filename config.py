import os
from dotenv import load_dotenv
class Config:
    load_dotenv()
    SECRET_KEY = os.urandom(24)
    MONGODB_URI = os.getenv('MONGODB_URI')
    if MONGODB_URI is None:
        raise ValueError("No MONGODB_URI environment variable set")
    MONGO_DBNAME = 'rentify_db' 
    
    