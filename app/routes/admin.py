from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.role import Role
from app.services.auth_service import get_current_admin
from app.schemas.admin import UserStatusUpdate, UserRoleUpdate

router = APIRouter()


@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role_id": user.role_id,
            "is_active": user.is_active,
        }
        for user in users
    ]


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_admin.id and not data.is_active:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own admin account",
        )

    user.is_active = data.is_active
    db.commit()
    db.refresh(user)

    return {
        "message": "User status updated successfully",
        "user_id": user.id,
        "is_active": user.is_active,
    }


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own admin role",
        )

    role = db.query(Role).filter(Role.name == data.role_name).first()

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found",
        )

    user.role_id = role.id
    db.commit()
    db.refresh(user)

    return {
        "message": "User role updated successfully",
        "user_id": user.id,
        "role": role.name,
    }