from app.data.district_coordinates import DISTRICT_COORDINATES, normalize_region_name

BBOX_SIZE = 0.05


def get_region_bbox(region: str):
    canonical = normalize_region_name(region)
    coords = DISTRICT_COORDINATES.get(canonical) or DISTRICT_COORDINATES.get(region)
    if not coords:
        raise ValueError(f"District '{region}' not found in coordinates list")

    lat, lon = coords

    min_lat = lat - BBOX_SIZE
    max_lat = lat + BBOX_SIZE
    min_lon = lon - BBOX_SIZE
    max_lon = lon + BBOX_SIZE

    return min_lon, min_lat, max_lon, max_lat
