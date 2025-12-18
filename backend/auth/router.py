from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from auth.hashing import Hash
from auth.jwt_handler import signJWT
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["Auth"])

class UserSignup(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/auth/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.email == user.email).first()
    if user_exists:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    new_user = User(email=user.email, password_hash=Hash.bcrypt(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@router.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_found = db.query(User).filter(User.email == user.email).first()
    if not user_found:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not Hash.verify(user.password, user_found.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return signJWT(str(user_found.id))
