from datetime import datetime
from auth import users_collection, get_password_hash

# Delete old user if exists
users_collection.delete_one({"username": "testuser"})

# Create new user with new hashing
new_user = {
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "hashed_password": get_password_hash("password123"),
    "role": "user",
    "created_at": datetime.now().isoformat()
}

users_collection.insert_one(new_user)
print("✅ New test user created!")
exit()