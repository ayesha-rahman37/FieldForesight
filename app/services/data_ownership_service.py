"""
Data-ownership service.

get_user_data  — queries real User, PredictionHistory, and UserPreference
                 tables instead of returning hardcoded mock values.

delete_data    — accepts a DeleteRequest object (not a plain str) and
                 performs a real DB delete/soft-delete depending on
                 data_type, then returns True/False for the route to
                 translate into a DeleteResponse.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.prediction_history import PredictionHistory
from app.models.user_preference import UserPreference
from app.schemas.data_ownership_schema import (
    UserData,
    UserProfileData,
    PredictionHistoryItem,
    DeleteRequest,
)


def get_user_data(user_id: int, db: Session) -> UserData:
    # ── Profile ───────────────────────────────────────────────────────────────
    user = db.query(User).filter(User.id == user_id).first()

    pref = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )

    if user:
        profile = UserProfileData(
            name=user.username,
            phone="",           # phone column not on User model yet
            region=pref.last_region if (pref and pref.last_region) else "",
        )
    else:
        profile = UserProfileData(name="Unknown", phone="", region="")

    # ── Prediction history ────────────────────────────────────────────────────
    history_rows = (
        db.query(PredictionHistory)
        .filter(
            (PredictionHistory.user_id == user_id) | (PredictionHistory.user_id == None)
        )
        .order_by(PredictionHistory.created_at.desc())
        .limit(20)
        .all()
    )

    prediction_history = [
        PredictionHistoryItem(
            prediction_id=str(row.id),
            date=row.created_at.strftime("%Y-%m-%d") if row.created_at else "",
            crop=row.crop,
            region=row.region,
            yield_predicted=f"{row.predicted_yield:.2f} ton/hectare",
        )
        for row in history_rows
    ]

    # ── Saved preferences ─────────────────────────────────────────────────────
    saved_preference = {
        "last_crop":   pref.last_crop   if pref else None,
        "last_region": pref.last_region if pref else None,
    }

    return UserData(
        profile=profile,
        prediction_history=prediction_history,
        saved_preference=saved_preference,
    )


def delete_data(request: DeleteRequest, user_id: int, db: Session) -> bool:
    """
    Deletes user data by data_type.

    Supported data_type values:
      "predictions" / "prediction_history" — hard-delete PredictionHistory rows for user_id
      "preferences"                        — hard-delete UserPreference row for user_id
      "profile"                            — clear saved profile preferences for user_id
      "all"                                — all of the above

    Returns True on success, False if nothing was found to delete.
    """
    data_type = request.data_type.strip().lower()
    deleted_any = False

    if data_type in ("predictions", "prediction_history", "all"):
        rows = (
            db.query(PredictionHistory)
            .filter(PredictionHistory.user_id == user_id)
            .all()
        )
        for row in rows:
            db.delete(row)
        if rows:
            deleted_any = True

    if data_type in ("preferences", "all"):
        pref = (
            db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .first()
        )
        if pref:
            db.delete(pref)
            deleted_any = True

    if data_type in ("profile", "all"):
        pref = (
            db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .first()
        )
        if pref:
            pref.last_crop = None
            pref.last_region = None
            deleted_any = True

    if deleted_any:
        db.commit()

    return deleted_any