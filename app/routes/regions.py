from fastapi import APIRouter

router = APIRouter()

REGIONS = [
    {"id": 1, "name": "Dhaka"},
    {"id": 2, "name": "Rangpur"},
]

@router.get("/regions")
def get_regions():
    return REGIONS