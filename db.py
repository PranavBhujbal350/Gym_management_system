from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, date
from config import Config

_client = None
_db = None

def get_client():
    """Returns the MongoClient instance, creating it if necessary."""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client

def get_db():
    """Returns the database instance."""
    global _db
    if _db is None:
        client = get_client()
        # If DB name is part of URI, PyMongo will use it, else fallback to Config.DB_NAME
        try:
            default_db = client.get_default_database()
            _db = default_db if default_db is not None else client[Config.DB_NAME]
        except Exception:
            _db = client[Config.DB_NAME]
    return _db

def test_connection():
    """Tests connection to MongoDB. Returns (True, message) or (False, error)."""
    try:
        client = get_client()
        client.admin.command('ping')
        return True, "Successfully connected to MongoDB server."
    except Exception as e:
        return False, str(e)

# Collection helpers
def get_collection(name):
    return get_db()[name]

def users_col():
    return get_collection('users')

def members_col():
    return get_collection('members')

def trainers_col():
    return get_collection('trainers')

def plans_col():
    return get_collection('membership_plans')

def memberships_col():
    return get_collection('member_memberships')

def payments_col():
    return get_collection('payments')

def attendance_col():
    return get_collection('attendance')

def workout_plans_col():
    return get_collection('workout_plans')

def member_workouts_col():
    return get_collection('member_workouts')

# Helper utilities for BSON / ObjectId handling
def to_object_id(id_str):
    """Safely converts string or ObjectId to ObjectId."""
    if isinstance(id_str, ObjectId):
        return id_str
    if not id_str or not ObjectId.is_valid(id_str):
        return None
    return ObjectId(id_str)

def serialize_doc(doc):
    """Recursively serializes ObjectId and datetimes in document for JSON and templates."""
    if doc is None:
        return None
    res = {}
    for key, val in doc.items():
        if isinstance(val, ObjectId):
            res[key] = str(val)
        elif isinstance(val, (datetime, date)):
            res[key] = val.isoformat()
        elif isinstance(val, list):
            res[key] = [
                serialize_doc(item) if isinstance(item, dict)
                else str(item) if isinstance(item, ObjectId)
                else item.isoformat() if isinstance(item, (datetime, date))
                else item
                for item in val
            ]
        elif isinstance(val, dict):
            res[key] = serialize_doc(val)
        else:
            res[key] = val
    return res

def serialize_list(docs):
    """Serializes a cursor or list of documents."""
    return [serialize_doc(doc) for doc in docs]
