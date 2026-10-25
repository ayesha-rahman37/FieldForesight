"""
Data-ownership service.

get_user_data  — queries real User, Role, PredictionHistory, and UserPreference tables.
delete_data    — deletes user data by data_type ("prediction_history" / "predictions",
                 "preferences", "profile", or "all").
"""

from sqlalchemy.orm import Session

from app.models.advisory_history import AdvisoryHistory
from app.models.explainability_cache import ExplainabilityCache
from app.models.prediction_history import PredictionHistory
from app.models.role import Role
from app.models.session import UserSession
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.data_ownership_schema import (
    DeleteRequest,
    PredictionHistoryItem,
    UserData,
    UserProfileData,
)


def get_user_data(user_id: int | None, db: Session) -> UserData:
    user = db.query(User).filter(User.id == user_id).first() if user_id is not None else None
    pref = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
        if user_id is not None
        else None
    )

    role_name = "farmer"
    if user and user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            role_name = role.name

    if user:
        profile = UserProfileData(
            name=user.username,
            username=user.username,
            email=user.email,
            role=role_name,
            phone=user.email,
            region=pref.last_region if (pref and pref.last_region) else "",
            created_at=user.created_at.strftime("%Y-%m-%d") if user.created_at else "",
        )
    else:
        profile = UserProfileData(
            name="Guest Farmer",
            username="guest",
            email="",
            role="guest",
            phone="",
            region=pref.last_region if (pref and pref.last_region) else "",
            created_at="",
        )

    if user_id is not None:
        history_filter = PredictionHistory.user_id == user_id
    else:
        history_filter = PredictionHistory.user_id.is_(None)

    total_predictions = db.query(PredictionHistory).filter(history_filter).count()

    history_rows = (
        db.query(PredictionHistory)
        .filter(history_filter)
        .order_by(PredictionHistory.created_at.desc())
        .limit(50)
        .all()
    )

    prediction_history = [
        PredictionHistoryItem(
            prediction_id=str(row.id),
            date=row.created_at.strftime("%Y-%m-%d %H:%M") if row.created_at else "",
            crop=row.crop,
            region=row.region,
            variety=row.variety or "HYV",
            yield_predicted=f"{row.predicted_yield:.2f} ton/ha",
            lower_bound=row.lower_bound,
            upper_bound=row.upper_bound,
        )
        for row in history_rows
    ]

    saved_preference = {}
    preferences_count = 0
    if pref and (pref.last_crop or pref.last_region):
        saved_preference = {
            "last_crop": pref.last_crop,
            "last_region": pref.last_region,
            "updated_at": pref.updated_at.strftime("%Y-%m-%d") if pref.updated_at else "",
        }
        preferences_count = 1

    return UserData(
        profile=profile,
        prediction_history=prediction_history,
        prediction_count=total_predictions,
        saved_preference=saved_preference,
        preferences_count=preferences_count,
    )


def delete_data(request: DeleteRequest, user_id: int | None, db: Session) -> bool:
    """
    Deletes user data by data_type:
      "prediction_history" / "predictions" — delete PredictionHistory rows & explainability caches
      "preferences"                        — delete UserPreference row for user_id
      "profile"                            — delete entire User account, sessions, preferences, and predictions
      "all"                                — all of the above
    """
    data_type = request.data_type.strip().lower()
    deleted_any = False

    if data_type in ("predictions", "prediction_history", "all"):
        if user_id is not None:
            history_filter = PredictionHistory.user_id == user_id
        else:
            history_filter = PredictionHistory.user_id.is_(None)

        rows = db.query(PredictionHistory).filter(history_filter).all()
        if rows:
            pred_ids = [r.id for r in rows]
            db.query(ExplainabilityCache).filter(ExplainabilityCache.prediction_id.in_(pred_ids)).delete(synchronize_session=False)
            db.query(AdvisoryHistory).filter(AdvisoryHistory.prediction_id.in_(pred_ids)).delete(synchronize_session=False)
            db.query(PredictionHistory).filter(PredictionHistory.id.in_(pred_ids)).delete(synchronize_session=False)
            deleted_any = True

    if data_type in ("preferences", "all") and user_id is not None:
        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if pref:
            db.delete(pref)
            deleted_any = True

    elif data_type == "profile" and user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # 1. Clean up user's predictions, caches, and advisories
            user_preds = db.query(PredictionHistory.id).filter(PredictionHistory.user_id == user_id).all()
            if user_preds:
                pred_ids = [p[0] for p in user_preds]
                db.query(ExplainabilityCache).filter(ExplainabilityCache.prediction_id.in_(pred_ids)).delete(synchronize_session=False)
                db.query(AdvisoryHistory).filter(AdvisoryHistory.prediction_id.in_(pred_ids)).delete(synchronize_session=False)
                db.query(PredictionHistory).filter(PredictionHistory.id.in_(pred_ids)).delete(synchronize_session=False)

            db.query(AdvisoryHistory).filter(AdvisoryHistory.user_id == user_id).delete(synchronize_session=False)
            db.query(UserPreference).filter(UserPreference.user_id == user_id).delete(synchronize_session=False)
            db.query(UserSession).filter(UserSession.user_id == user_id).delete(synchronize_session=False)
            db.delete(user)
            deleted_any = True

    if deleted_any:
        db.commit()

    return deleted_any
