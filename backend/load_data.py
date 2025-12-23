import json
import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection (using your existing connection)
MONGO_URL = "mongodb+srv://RIL_sys:M(>$s8!p@rootcause-db.wayefpy.mongodb.net/?appName=rootcause-db"
client = MongoClient(MONGO_URL)
db = client["fivewhy_db"]
collection = db["equipment_data"]

print("✅ Connected to MongoDB")

try:
    # Load JSON data
    with open("equipment_100_domain_enriched.json", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} records from JSON file")
    
    transformed_data = []
    
    for item in data:
        transformed_item = {
            # ---------------- BASIC INFO ----------------
            "equipment_id": item.get("Equipment_ID", ""),
            "equipment_type": item.get("Equipment_Type", ""),
            
            # ---------------- CORE RCA ----------------
            "issue": item.get("Issue_Description", ""),
            "root_cause": item.get("Root_Cause", ""),
            
            # ---------------- 5-WHY ----------------
            "why1": item.get("Why_1", ""),
            "why2": item.get("Why_2", ""),
            "why3": item.get("Why_3", ""),
            "why4": item.get("Why_4", ""),
            "why5": item.get("Why_5", ""),
            
            # ---------------- ACTION ----------------
            "solution": item.get("Corrective_Action", ""),
            
            # ---------------- META ----------------
            "department": item.get("Department", ""),
            "severity": item.get("Severity", "High", "Critical"),
            "date_reported": item.get("Date_Reported", datetime.now().strftime("%Y-%m-%d")),
            
            # ---------------- DOMAIN FEATURES ----------------
            "shift_time": item.get("shift_time", "day"),
            "machine_age_bucket": item.get("machine_age_bucket", "mid"),
            "maintenance_gap_days": item.get("maintenance_gap_days", "moderate"),
            "failure_frequency": item.get("failure_frequency", "medium"),
            
            # ---------------- ADDITIONAL FIELDS (for defaults) ----------------
            "environment": "clean",  # Default value
            "operating_load": "normal",  # Default value
            "recent_maintenance": "yes",  # Default value
            "source": item.get("Source", "")  # Keep source for reference
        }
        
        transformed_data.append(transformed_item)
    
    # ---------------- RESET COLLECTION ----------------
    print("Clearing existing data...")
    collection.delete_many({})
    print("Inserting new data...")
    
    # Insert in batches to avoid timeout
    batch_size = 50
    for i in range(0, len(transformed_data), batch_size):
        batch = transformed_data[i:i + batch_size]
        collection.insert_many(batch)
        print(f"Inserted batch {i//batch_size + 1} ({len(batch)} records)")
    
    print(f"✅ Data inserted successfully! {len(transformed_data)} records loaded.")
    
    # Show some stats
    print(f"\n📊 Database Statistics:")
    print(f"Total records: {collection.count_documents({})}")
    print(f"Unique root causes: {len(collection.distinct('root_cause'))}")
    print(f"Unique equipment types: {len(collection.distinct('equipment_type'))}")
    
    # Show a sample record
    sample = collection.find_one()
    if sample:
        print(f"\n📋 Sample Record:")
        print(f"Equipment ID: {sample.get('equipment_id')}")
        print(f"Equipment Type: {sample.get('equipment_type')}")
        print(f"Issue: {sample.get('issue')[:80]}...")
        print(f"Root Cause: {sample.get('root_cause')}")
        print(f"Department: {sample.get('department')}")
        print(f"Severity: {sample.get('severity')}")
        
except FileNotFoundError:
    print(f"❌ Error: 'equipment_100_domain_enriched.json' file not found!")
    print("Please make sure the JSON file is in the same directory as this script.")
    print(f"Current directory files: {[f for f in os.listdir('.') if f.endswith('.json')]}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")