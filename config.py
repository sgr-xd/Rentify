import os
from dotenv import load_dotenv
class Config:
    load_dotenv()
    SECRET_KEY = os.urandom(24)
    mongo_uri = os.environ.get('MONGO_URI')
    if mongo_uri is None:
        raise ValueError("No MONGODB_URI environment variable set")
    MONGO_DBNAME = 'rentify_db' 
    
    