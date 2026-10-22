from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.role import Role
from app.models.session import UserSession
from app.models.user import User

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def _utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    session = (
        db.query(UserSession)
        .filter(UserSession.session_token == token)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
        )

    if session.expires_at < _utcnow_naive():
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Session has expired",
        )

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    return user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_optional),
    db: Session = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    token = credentials.credentials

    session = (
        db.query(UserSession)
        .filter(UserSession.session_token == token)
        .first()
    )

    if not session:
        return None

    if session.expires_at < _utcnow_naive():
        db.delete(session)
        db.commit()
        return None

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        return None

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if not role or role.name != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )
    return current_user
