from fastapi import APIRouter

router = APIRouter()

CROPS = [
    {"id": 1, "name": "ধান", "type": "cereal"},
    {"id": 2, "name": "গম", "type": "cereal"},
]

@router.get("/crops")
def get_crops():
    return CROPS