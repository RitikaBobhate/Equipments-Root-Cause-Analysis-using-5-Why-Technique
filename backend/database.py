from pymongo import MongoClient

MONGO_URL = "mongodb+srv://RIL_sys:M(>$s8!p@rootcause-db.wayefpy.mongodb.net/?appName=rootcause-db"

client = MongoClient(MONGO_URL)
db = client["fivewhy_db"]
collection = db["equipment_data"]
