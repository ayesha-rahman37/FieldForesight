from fastapi import APIRouter

router = APIRouter()

CROPS = [
    {"id": 1, "name": "Rice", "type": "cereal"},
    {"id": 2, "name": "Wheat", "type": "cereal"},
]

@router.get("/crops")
def get_crops():
    return CROPS