from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from models import User
from database import get_db

auth_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Request models with validation
from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    shop_name: str
    shop_address: str
    phone_number: str = Field(pattern=r'^\d{11}$', description="Phone number must be exactly 11 digits")
    email: EmailStr
    password: str = Field(min_length=8, max_length=12)

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

# Signup route
@auth_router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if username or email already exists
    if db.query(User).filter((User.username == request.username) | (User.email == request.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")
    if db.query(User).filter(User.phone_number == request.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone number already exists")

    # Hash password and save user
    hashed_password = pwd_context.hash(request.password)
    new_user = User(
        username=request.username,
        shop_name=request.shop_name,
        shop_address=request.shop_address,
        phone_number=request.phone_number,
        email=request.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# Login route
@auth_router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Find user by username or email
    user = db.query(User).filter((User.username == request.username_or_email) | (User.email == request.username_or_email)).first()
    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username/email or password")
    return {"message": f"Welcome, {user.username}!"}
