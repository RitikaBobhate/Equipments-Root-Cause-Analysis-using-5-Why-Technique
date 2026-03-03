from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from pymongo import MongoClient
from pydantic import BaseModel


SECRET_KEY = "test-secret-key-123" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# FIXED: Use pbkdf2_sha256 instead of bcrypt
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()


MONGO_URL = "mongodb+srv://RIL_sys:M(>$s8!p@rootcause-db.wayefpy.mongodb.net/fivewhy_db?retryWrites=true&w=majority&ssl=true&tls=true&tlsAllowInvalidCertificates=true"
client = MongoClient(MONGO_URL)
db = client["fivewhy_db"]
users_collection = db["users"]


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials = Depends(security)):
    """Get current user from token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": payload.get("role")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")