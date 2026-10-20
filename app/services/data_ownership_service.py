from sqlalchemy.orm import Session

from app.models.user import User
from app.models.prediction_history import PredictionHistory
from app.models.user_preference import UserPreference
from app.schemas.data_ownership_schema import (
    UserData,
    UserProfileData,
    PredictionHistoryItem,
)


def get_user_data(user_id: int, db: Session) -> UserData:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    history = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == user_id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )

    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )

    history_items = [
        PredictionHistoryItem(
            prediction_id=str(item.id),
            date=item.created_at.isoformat(),
            crop=item.crop,
            region=item.region,
            yield_predicted=f"{item.predicted_yield} ton/hectare",
        )
        for item in history
    ]

    saved_preferences = {
        "last_crop": preferences.last_crop if preferences else None,
        "last_region": preferences.last_region if preferences else None,
    }

    return UserData(
        profile=UserProfileData(
            username=user.username,
            email=user.email,
        ),
        prediction_history=history_items,
        saved_preference=saved_preferences,
    )


def delete_data(request, user_id: int, db: Session) -> bool:
    data_type = request.data_type

    if data_type == "prediction_history":
        db.query(PredictionHistory).filter(
            PredictionHistory.user_id == user_id
        ).delete(synchronize_session=False)

    elif data_type == "preferences":
        db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).delete(synchronize_session=False)

    else:
        return False

    db.commit()
    return True