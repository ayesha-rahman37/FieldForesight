from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.session import UserSession
from app.models.role import Role


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    session = (
        db.query(UserSession)
        .filter(UserSession.session_token == token)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    if session.expires_at < datetime.utcnow():
        db.delete(session)
        db.commit()

        raise HTTPException(
            status_code=401,
            detail="Session has expired"
        )

    user = (
        db.query(User)
        .filter(User.id == session.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    return user
def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role or role.name != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user