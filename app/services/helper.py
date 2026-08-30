import os
from datetime import datetime, timedelta
from pathlib import Path
import rasterio
from rasterio.transform import from_bounds
import numpy as np
from dotenv import load_dotenv

from sentinelhub import (
    SHConfig, BBox, CRS, SentinelHubRequest,
    DataCollection, MimeType, bbox_to_dimensions, MosaickingOrder
)

from app.data.district_bbox import get_region_bbox

# .env load (root folder)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- Sentinel Hub Config (Copernicus Data Space Ecosystem) ---
config = SHConfig()
config.sh_client_id = os.getenv("SENTINELHUB_CLIENT_ID")
config.sh_client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")

# Copernicus Data Space endpoints — default sentinelhub library points elsewhere
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# Data collection registered against Copernicus Data Space endpoint
DATA_COLLECTION_S2L2A = DataCollection.SENTINEL2_L2A.define_from(
    "s2l2a_cdse", service_url=config.sh_base_url
)

EVALSCRIPT_NDVI_BANDS = """
//VERSION=3
function setup() {
    return {
        input: ["B04", "B08"],
        output: { bands: 2, sampleType: "FLOAT32" }
    };
}
function evaluatePixel(sample) {
    return [sample.B04, sample.B08];
}
"""


def fetch_ndvi_for_region(region: str) -> float:
    bbox_coords = get_region_bbox(region)
    bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=10)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)

    request = SentinelHubRequest(
        evalscript=EVALSCRIPT_NDVI_BANDS,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DATA_COLLECTION_S2L2A,
                time_interval=(str(start_date), str(end_date)),
                mosaicking_order=MosaickingOrder.LEAST_CC
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=size,
        config=config
    )

    data = request.get_data()[0]
    red = data[:, :, 0].astype(float)
    nir = data[:, :, 1].astype(float)

    denom = red + nir
    denom[denom == 0] = 1e-6
    ndvi = (nir - red) / denom
    avg_ndvi = float(np.nanmean(ndvi))

    save_raw_bands(red, nir, bbox_coords, region)

    return round(avg_ndvi, 3)



def save_raw_bands(red, nir, bbox_coords, region_name):
    output_dir = "satellite_output/satellite_cache"
    os.makedirs(output_dir, exist_ok=True)

    transform = from_bounds(*bbox_coords, red.shape[1], red.shape[0])
    output_path = f"{output_dir}/{region_name}_bands.tif"

    with rasterio.open(
        output_path, 'w', driver='GTiff',
        height=red.shape[0], width=red.shape[1],
        count=2, dtype='float32', crs='EPSG:4326', transform=transform
    ) as dst:
        dst.write(red.astype('float32'), 1)   # band 1 = Red
        dst.write(nir.astype('float32'), 2)   # band 2 = NIR

def classify_vegetation(ndvi_value: float) -> str:
    if ndvi_value > 0.5:
        return "Healthy"
    elif ndvi_value > 0.2:
        return "Moderate"
    else:
        return "Poor"

