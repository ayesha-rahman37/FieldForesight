from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.session import UserSession
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
)
from app.services.security import hash_password, verify_password
from app.services.auth_service import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(
            (User.username == data.username)
            | (User.email == data.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )

    farmer_role = (
        db.query(Role)
        .filter(Role.name == "farmer")
        .first()
    )

    if not farmer_role:
        raise HTTPException(
            status_code=500,
            detail="Farmer role not found"
        )

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role_id=farmer_role.id,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.username == data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    # Generate a secure session token
    session_token = secrets.token_urlsafe(32)

    # Session expires after 24 hours
    expires_at = datetime.utcnow() + timedelta(hours=24)

    new_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at,
    )

    db.add(new_session)
    db.commit()

    return {
        "access_token": session_token,
        "token_type": "bearer",
    }
@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user