
import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.database import engine, SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.session import UserSession
from app.models.prediction_history import PredictionHistory
from app.models.user_preference import UserPreference
from app.models.ndvi_cache import NDVICache
from app.services.security import verify_password

from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class AdminAuthentication(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", "")).strip()
        password = str(form.get("password", ""))

        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()

            if not user or not user.is_active:
                return False

            if not verify_password(password, user.password_hash):
                return False

            role = db.query(Role).filter(Role.id == user.role_id).first()
            if not role or role.name.lower() != "admin":
                return False

            request.session.clear()
            request.session["admin_user_id"] = user.id
            return True
        finally:
            db.close()

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False

        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                request.session.clear()
                return False

            role = db.query(Role).filter(Role.id == user.role_id).first()
            if not role or role.name.lower() != "admin":
                request.session.clear()
                return False

            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True


class SecureModelView(ModelView):
    def is_accessible(self, request: Request) -> bool:
        return bool(request.session.get("admin_user_id"))

    def is_visible(self, request: Request) -> bool:
        return self.is_accessible(request)


class UserAdmin(SecureModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [
        User.id, User.username, User.email, User.role_id,
        User.is_active, User.created_at,
    ]
    column_searchable_list = [User.username, User.email]
    form_excluded_columns = [User.password_hash]
    can_create = False
    can_edit = False
    can_delete = False


class RoleAdmin(SecureModelView, model=Role):
    name = "Role"
    name_plural = "Roles"
    column_list = [Role.id, Role.name]
    can_create = False
    can_edit = False
    can_delete = False


class SessionAdmin(SecureModelView, model=UserSession):
    name = "Session"
    name_plural = "Sessions"
    column_list = [
        UserSession.id, UserSession.user_id,
        UserSession.expires_at, UserSession.created_at,
    ]
    form_excluded_columns = [UserSession.session_token]
    can_create = False
    can_edit = False
    can_delete = False


class PredictionHistoryAdmin(SecureModelView, model=PredictionHistory):
    name = "Prediction History"
    name_plural = "Prediction History"
    column_list = [
        PredictionHistory.id, PredictionHistory.user_id,
        PredictionHistory.crop, PredictionHistory.region,
        PredictionHistory.predicted_yield, PredictionHistory.created_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class UserPreferenceAdmin(SecureModelView, model=UserPreference):
    name = "User Preference"
    name_plural = "User Preferences"
    column_list = [
        UserPreference.id, UserPreference.user_id,
        UserPreference.last_crop, UserPreference.last_region,
        UserPreference.updated_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False


class NDVICacheAdmin(SecureModelView, model=NDVICache):
    name = "Satellite Cache"
    name_plural = "Satellite Cache"
    column_list = [
        NDVICache.id, NDVICache.region_name,
        NDVICache.ndvi_value, NDVICache.vegetation_status,
        NDVICache.computed_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False


def setup_sqladmin(app):
    secret = os.getenv("SQLADMIN_SECRET_KEY", "").strip()
    if len(secret) < 32:
        raise RuntimeError(
            "SQLADMIN_SECRET_KEY must be set in the project .env file "
            "and contain at least 32 characters."
        )

    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=AdminAuthentication(secret_key=secret),
        title="FieldForesight Admin",
        base_url="/admin",
    )

    for view in (
        UserAdmin,
        RoleAdmin,
        SessionAdmin,
        PredictionHistoryAdmin,
        UserPreferenceAdmin,
        NDVICacheAdmin,
    ):
        admin.add_view(view)

    return admin
