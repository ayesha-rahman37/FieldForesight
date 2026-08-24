from app.schemas.data_ownership_schema import UserData, UserProfileData, PredictionHistoryItem


def get_user_data(user_id: int) -> UserData:
    mock_profile = UserProfileData(
        name="Karim Mia",
        phone="01755545454",
        region="Rangpur"
    )
    mock_history = [
        PredictionHistoryItem(
            prediction_id="pred_1",
            date="2026-03-01",
            crop="Rice",
            region="Rangpur",
            yield_predicted="4.2 ton/hectare"
        )
    ]
    mock_preferences = {"last_crop": "Rice", "last_region": "Rangpur"}

    return UserData(
        profile = mock_profile,
        prediction_history= mock_history,
        saved_preference= mock_preferences
    )


def delete_data(request:str, user_id:int):
    print(f"Deleting {request} for user{user_id}")
    return True