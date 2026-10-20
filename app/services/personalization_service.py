from sqlalchemy.orm import Session

from app.models.user_preference import UserPreference
from app.schemas.personalization import PreferenceResponse


def save_preference(
    user_id: int,
    crop: str,
    region: str,
    db: Session,
) -> bool:
    preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )

    if preference:
        preference.last_crop = crop
        preference.last_region = region
    else:
        db.add(
            UserPreference(
                user_id=user_id,
                last_crop=crop,
                last_region=region,
            )
        )

    db.commit()
    return True


def get_user_references(
    user_id: int,
    db: Session,
) -> PreferenceResponse:
    preference = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )

    if not preference:
        return PreferenceResponse(
            user_id=user_id,
            last_crop=None,
            last_region=None,
        )

    return PreferenceResponse(
        user_id=user_id,
        last_crop=preference.last_crop,
        last_region=preference.last_region,
    )