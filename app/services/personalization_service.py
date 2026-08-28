from sqlalchemy.orm import Session

from app.models.user_preference import UserPreference
from app.schemas.personalization import SaveResponse, PreferenceResponse


def save_preference(user_id:int,crop:str,region:str,db:Session) -> bool:
    user = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if user:
        user.last_crop = crop
        user.last_region = region
    else:
        new_pref = UserPreference(user_id=user_id, last_crop=crop, last_region=region)
        db.add(new_pref)

    db.commit()
    return True

def get_user_references(user_id,db:Session):
    user = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    if not user:
        return PreferenceResponse(user_id=user_id,last_crop=None,last_region=None)
    return PreferenceResponse(
        user_id=user.user_id,
        last_crop=user.last_crop,
        last_region=user.last_region
    )