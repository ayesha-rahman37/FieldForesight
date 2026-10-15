from app.data.district_coordinates import DISTRICT_COORDINATES

BBOX_SIZE = .05

def get_region_bbox(region:str):

    if region not in DISTRICT_COORDINATES:
        raise ValueError(f"District '{region}' not found in coordinates list")

    lat,lon = DISTRICT_COORDINATES[region]

    min_lat = lat - BBOX_SIZE
    max_lat = lat + BBOX_SIZE
    min_lon = lon - BBOX_SIZE
    max_lon = lon + BBOX_SIZE

    return min_lon, min_lat, max_lon, max_lat