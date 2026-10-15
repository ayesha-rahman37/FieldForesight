from fastapi import APIRouter

router = APIRouter()

CROPS = [
    {"id": 1, "name": "Rice", "type": "cereal"},
    {"id": 2, "name": "Wheat", "type": "cereal"},
    {"id": 3, "name": "Maize", "type": "cereal"},
    {"id": 4, "name": "Potato", "type": "tuber"},
    {"id": 5, "name": "Jute", "type": "fiber"},
    {"id": 6, "name": "Mustard", "type": "oilseed"},
]


@router.get("/crops")
def get_crops():
    return CROPS