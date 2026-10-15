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


from app.models.user_preference import UserPreference


@router.post("/register", response_model=TokenResponse)
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
        # Auto-create roles if they don't exist
        farmer_role = Role(name="farmer")
        admin_role = Role(name="admin")
        db.add_all([admin_role, farmer_role])
        db.commit()
        db.refresh(farmer_role)

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

    if data.region:
        pref = UserPreference(user_id=new_user.id, last_region=data.region)
        db.add(pref)
        db.commit()

    # Generate a secure session token to auto-login
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    new_session = UserSession(
        user_id=new_user.id,
        session_token=session_token,
        expires_at=expires_at,
    )

    db.add(new_session)
    db.commit()

    return {
        "access_token": session_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            (User.username == data.username)
            | (User.email == data.username)
        )
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
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role_obj = db.query(Role).filter(Role.id == current_user.role_id).first()
    role_name = role_obj.name if role_obj else "farmer"
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role_id": current_user.role_id,
        "role": role_name,
        "is_active": current_user.is_active,
    }


@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Logged out successfully"}
