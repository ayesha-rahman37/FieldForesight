from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.data.district_coordinates import normalize_region_name
from app.database import get_db
from app.models.role import Role
from app.models.session import UserSession
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import get_current_user, security
from app.services.security import hash_password, verify_password

router = APIRouter()


def _utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.post("/register", response_model=TokenResponse)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == data.username) | (User.email == data.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered",
        )

    try:
        farmer_role = db.query(Role).filter(Role.name == "farmer").first()
        if not farmer_role:
            farmer_role = Role(name="farmer")
            admin_role = Role(name="admin")
            db.add_all([admin_role, farmer_role])
            db.flush()

        new_user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role_id=farmer_role.id,
            is_active=True,
        )
        db.add(new_user)
        db.flush()

        if data.region:
            pref = UserPreference(
                user_id=new_user.id,
                last_crop="Rice",
                last_region=normalize_region_name(data.region),
            )
            db.add(pref)

        session_token = secrets.token_urlsafe(32)
        expires_at = _utcnow_naive() + timedelta(hours=24)

        new_session = UserSession(
            user_id=new_user.id,
            session_token=session_token,
            expires_at=expires_at,
        )
        db.add(new_session)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {exc}") from exc

    return {
        "access_token": session_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter((User.username == data.username) | (User.email == data.username))
        .first()
    )

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    session_token = secrets.token_urlsafe(32)
    expires_at = _utcnow_naive() + timedelta(hours=24)

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
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    (
        db.query(UserSession)
        .filter(
            UserSession.user_id == current_user.id,
            UserSession.session_token == credentials.credentials,
        )
        .delete()
    )
    db.commit()
    return {"message": "Logged out successfully"}
