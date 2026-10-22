from sqlalchemy.orm import Session

from app.data.district_coordinates import normalize_region_name
from app.models.user_preference import UserPreference
from app.schemas.personalization import PreferenceResponse


def save_preference(user_id: int, crop: str, region: str, db: Session) -> bool:
    clean_crop = crop.strip().title() if crop else None
    clean_region = normalize_region_name(region) if region else None
    pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if pref:
        pref.last_crop = clean_crop
        pref.last_region = clean_region
    else:
        new_pref = UserPreference(
            user_id=user_id,
            last_crop=clean_crop,
            last_region=clean_region,
        )
        db.add(new_pref)

    db.commit()
    return True


def get_user_preferences(user_id: int, db: Session) -> PreferenceResponse:
    pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not pref:
        return PreferenceResponse(user_id=user_id, last_crop=None, last_region=None)
    return PreferenceResponse(
        user_id=pref.user_id,
        last_crop=pref.last_crop,
        last_region=pref.last_region,
    )
