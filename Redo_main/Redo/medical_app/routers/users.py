from fastapi import APIRouter, HTTPException, Depends
from medical_app.models import UserSignup, UserLogin, UserCreate, Token
from medical_app.database import db
from medical_app.auth import hash_password, verify_password, create_access_token
from medical_app.dependencies import role_required
from datetime import timedelta
from medical_app.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/users", tags=["Users"])
users_collection = db["users"]

@router.post("/signup", response_model=Token)
def signup(user: UserSignup):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pwd = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_pwd
    user_dict["role"] = "patient"
    users_collection.insert_one(user_dict)
    access_token = create_access_token(
        {"sub": user.username, "role": "patient"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        {"sub": db_user["username"], "role": db_user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create", response_model=Token, dependencies=[Depends(role_required("admin"))])
def create_user(user: UserCreate):
    if user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=400, detail="Role must be admin or doctor")
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pwd = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_pwd
    users_collection.insert_one(user_dict)
    access_token = create_access_token(
        {"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
