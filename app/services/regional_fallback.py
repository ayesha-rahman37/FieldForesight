from functools import lru_cache
from pathlib import Path

import pandas as pd
from prophet import Prophet

from app.services.adjustment_rules import apply_adjustments
from app.services.feature_engineering import prepare_yield_features


BASE_DIR = Path(__file__).resolve().parents[1]
FALLBACK_MODEL_DIR = BASE_DIR / "data" / "models"

FALLBACK_MODEL_VERSION = "fallback-prophet-bbs-regional-v1"

# Source-based national yield series.
# Rice values are from FAOSTAT annual crop-yield data.
# Wheat values use the annual Bangladesh wheat-yield series
# available from FAO/USDA-derived agricultural statistics.
NATIONAL_YIELD_DATA = {
    "Rice": {
        2015: 4.5518,
        2016: 4.5863,
        2017: 4.6619,
        2018: 4.7257,
        2019: 4.7402,
        2020: 4.8088,
        2021: 4.8187,
        2022: 4.8912,
        2023: 5.0348,
    },

    # Bangladesh national wheat yield series.
    # Source: FAS/PSD agricultural statistics.

    "Wheat": {
    2015: 3.07,
    2016: 3.09,
    2017: 3.12,
    2018: 3.44,
    2019: 3.53,
    2020: 3.52,
    2021: 3.44,
    2022: 3.55,
    2023: 3.55,
    2024: 3.55,
    },
}


# Regional calibration based on BBS 2022/23 yield-rate data.
#
# Regional factor =
#     district yield / Bangladesh national yield
#
# Rice national benchmark = 3.3 MT/ha
# Wheat national benchmark = 3.4 MT/ha
REGIONAL_FACTORS = {
    ("Rice", "Dhaka"): 4.1 / 3.3,
    ("Rice", "Rangpur"): 3.5 / 3.3,
    ("Wheat", "Dhaka"): 3.0 / 3.4,
    ("Wheat", "Rangpur"): 3.1 / 3.4,
}


RECENT_YEARS_COUNT = 3
RECENT_YEAR_WEIGHT_MULTIPLIER = 3


def _apply_recent_weighting(
    df: pd.DataFrame
) -> pd.DataFrame:

    if df.empty:
        return df.copy()

    max_year = int(df["year"].max())

    cutoff_year = (
        max_year
        - RECENT_YEARS_COUNT
        + 1
    )

    recent_rows = df[
        df["year"] >= cutoff_year
    ]

    older_rows = df[
        df["year"] < cutoff_year
    ]

    if recent_rows.empty:
        return (
            df
            .sort_values("ds")
            .reset_index(drop=True)
        )

    weighted_df = pd.concat(
        [
            older_rows,
            *(
                [recent_rows]
                * RECENT_YEAR_WEIGHT_MULTIPLIER
            )
        ],
        ignore_index=True
    )

    return (
        weighted_df
        .sort_values("ds")
        .reset_index(drop=True)
    )


def _get_national_dataframe(
    crop: str
) -> pd.DataFrame:

    crop_key = crop.strip().title()

    if crop_key not in NATIONAL_YIELD_DATA:
        raise FileNotFoundError(
            f"No fallback yield dataset is available for {crop}."
        )

    rows = [
        {
            "year": year,
            "rainfall": 0.0,
            "yield": value
        }
        for year, value
        in NATIONAL_YIELD_DATA[crop_key].items()
    ]

    return pd.DataFrame(rows)


def get_regional_factor(
    crop: str,
    region: str
) -> float:

    key = (
        crop.strip().title(),
        region.strip().title()
    )

    factor = REGIONAL_FACTORS.get(key)

    if factor is None:
        raise FileNotFoundError(
            f"No regional calibration is available for "
            f"{crop} in {region}."
        )

    return float(factor)


@lru_cache(maxsize=8)
def _load_fallback_model(
    crop: str
):

    national_data = _get_national_dataframe(
        crop
    )

    features = prepare_yield_features(
        national_data[
            [
                "year",
                "rainfall",
                "yield"
            ]
        ]
    )

    if len(features) < 2:
        raise ValueError(
            f"Not enough fallback records available "
            f"for {crop}."
        )

    weighted_data = _apply_recent_weighting(
        features
    )

    model = Prophet(
        yearly_seasonality=False
    )

    model.fit(
        weighted_data[
            [
                "ds",
                "y"
            ]
        ]
    )

    FALLBACK_MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return model


def get_fallback_prediction(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single"
):

    factor = get_regional_factor(
        crop,
        region
    )

    model = _load_fallback_model(
        crop
    )

    future = model.make_future_dataframe(
        periods=1,
        freq="YS"
    )

    forecast = model.predict(
        future
    )

    latest = forecast.iloc[-1]

    base_yield = (
        float(latest["yhat"])
        * factor
    )

    lower = (
        float(latest["yhat_lower"])
        * factor
    )

    upper = (
        float(latest["yhat_upper"])
        * factor
    )

    adjusted_yield = apply_adjustments(
        base_yield,
        variety,
        cropping_type
    )

    adjusted_lower = apply_adjustments(
        lower,
        variety,
        cropping_type
    )

    adjusted_upper = apply_adjustments(
        upper,
        variety,
        cropping_type
    )

    return {
        "predicted_yield": adjusted_yield,
        "lower_bound": adjusted_lower,
        "upper_bound": adjusted_upper,
        "message": (
            f"Regionalized fallback forecast generated "
            f"for {crop} in {region} using national "
            f"crop yield trends and BBS regional calibration."
        ),
        "model_version": FALLBACK_MODEL_VERSION,
        "cache_hit": False
    }


def get_regional_historical_data(
    crop: str,
    region: str
):

    factor = get_regional_factor(
        crop,
        region
    )

    national_data = _get_national_dataframe(
        crop
    )

    return {
        "years": [
            int(year)
            for year in national_data["year"]
        ],
        "rainfall": [
            None
            for _ in national_data["year"]
        ],
        "yield": [
            round(
                float(value) * factor,
                4
            )
            for value
            in national_data["yield"]
        ],
        "source_type": (
            "regionalized_national_fallback"
        )
    }