from functools import lru_cache
from math import sqrt
from pathlib import Path

import pandas as pd

from app.services.adjustment_rules import apply_adjustments


BASE_DIR = Path(__file__).resolve().parents[1]

FALLBACK_MODEL_DIR = (
    BASE_DIR / "data" / "models"
)

FALLBACK_MODEL_VERSION = (
    "fallback-regional-trend-v2"
)


# Source-based Bangladesh national crop-yield series.
# Rice: FAOSTAT annual crop-yield series.
# Wheat: Bangladesh wheat-yield annual series from FAS/PSD data.
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


# 2022/23 district-to-national calibration.
#
# Regional factor =
# district yield / Bangladesh benchmark yield
#
# These factors are used only when a local crop-region
# historical model is unavailable.

REGIONAL_FACTORS = {

    ("Rice", "Dhaka"):
        4.1 / 3.3,

    ("Rice", "Rangpur"):
        3.5 / 3.3,

    ("Wheat", "Dhaka"):
        3.0 / 3.4,

    ("Wheat", "Rangpur"):
        3.1 / 3.4,
}


RECENT_YEARS_COUNT = 3
RECENT_YEAR_WEIGHT = 3.0


def _get_national_dataframe(
    crop: str
) -> pd.DataFrame:

    crop_key = crop.strip().title()

    values = NATIONAL_YIELD_DATA.get(
        crop_key
    )

    if not values:

        raise FileNotFoundError(
            f"No fallback yield dataset is available "
            f"for {crop}."
        )

    return pd.DataFrame(
        [
            {
                "year": int(year),
                "yield": float(value),
            }
            for year, value in values.items()
        ]
    ).sort_values(
        "year"
    ).reset_index(
        drop=True
    )


def get_regional_factor(
    crop: str,
    region: str
) -> float:

    key = (
        crop.strip().title(),
        region.strip().title(),
    )

    factor = REGIONAL_FACTORS.get(
        key
    )

    if factor is None:

        raise FileNotFoundError(
            f"No regional calibration is available "
            f"for {crop} in {region}."
        )

    return float(factor)


def _get_year_weight(
    year: int,
    latest_year: int
) -> float:

    cutoff = (
        latest_year
        - RECENT_YEARS_COUNT
        + 1
    )

    if year >= cutoff:
        return RECENT_YEAR_WEIGHT

    return 1.0


def _weighted_linear_forecast(
    data: pd.DataFrame
) -> tuple[float, float]:

    if len(data) < 2:

        raise ValueError(
            "At least two historical records are "
            "required for fallback forecasting."
        )

    latest_year = int(
        data["year"].max()
    )

    x_values = [
        float(year)
        for year in data["year"]
    ]

    y_values = [
        float(value)
        for value in data["yield"]
    ]

    weights = [
        _get_year_weight(
            int(year),
            latest_year
        )
        for year in data["year"]
    ]

    total_weight = sum(
        weights
    )

    weighted_x_mean = (
        sum(
            weight * x
            for weight, x
            in zip(
                weights,
                x_values
            )
        )
        / total_weight
    )

    weighted_y_mean = (
        sum(
            weight * y
            for weight, y
            in zip(
                weights,
                y_values
            )
        )
        / total_weight
    )

    sxx = sum(
        weight
        * (
            x - weighted_x_mean
        ) ** 2
        for weight, x
        in zip(
            weights,
            x_values
        )
    )

    if sxx == 0:

        prediction = weighted_y_mean

        residual_variance = 0.0

    else:

        sxy = sum(
            weight
            * (
                x - weighted_x_mean
            )
            * (
                y - weighted_y_mean
            )
            for weight, x, y
            in zip(
                weights,
                x_values,
                y_values
            )
        )

        slope = (
            sxy / sxx
        )

        intercept = (
            weighted_y_mean
            - slope
            * weighted_x_mean
        )

        next_year = (
            latest_year + 1
        )

        prediction = (
            intercept
            + slope * next_year
        )

        residuals = [

            y
            - (
                intercept
                + slope * x
            )

            for x, y
            in zip(
                x_values,
                y_values
            )
        ]

        residual_sum = sum(

            weight
            * residual ** 2

            for weight, residual
            in zip(
                weights,
                residuals
            )
        )

        degrees_of_freedom = max(
            total_weight - 2.0,
            1.0
        )

        residual_variance = (
            residual_sum
            / degrees_of_freedom
        )

    prediction_error = sqrt(
        max(
            residual_variance,
            0.0
        )
        * (
            1.0
            + 1.0
            / max(
                total_weight,
                1.0
            )
        )
    )

    margin = (
        1.96
        * prediction_error
    )

    return (
        max(
            prediction,
            0.0
        ),
        margin
    )


@lru_cache(maxsize=8)
def _get_fallback_forecast(
    crop: str
):

    data = _get_national_dataframe(
        crop
    )

    prediction, margin = (
        _weighted_linear_forecast(
            data
        )
    )

    lower = max(
        prediction - margin,
        0.0
    )

    upper = max(
        prediction + margin,
        lower
    )

    return (
        prediction,
        lower,
        upper
    )


def get_fallback_prediction(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single"
):

    regional_factor = (
        get_regional_factor(
            crop,
            region
        )
    )

    prediction, lower, upper = (
        _get_fallback_forecast(
            crop
        )
    )

    prediction *= regional_factor
    lower *= regional_factor
    upper *= regional_factor

    prediction = apply_adjustments(
        prediction,
        variety,
        cropping_type
    )

    lower = apply_adjustments(
        lower,
        variety,
        cropping_type
    )

    upper = apply_adjustments(
        upper,
        variety,
        cropping_type
    )

    return {

        "predicted_yield":
            prediction,

        "lower_bound":
            lower,

        "upper_bound":
            upper,

        "message": (
            f"Regionalized fallback forecast "
            f"generated for {crop} in {region} "
            f"using national yield trend and "
            f"documented regional calibration."
        ),

        "model_version":
            FALLBACK_MODEL_VERSION,

        "cache_hit":
            False,
    }


def get_regional_historical_data(
    crop: str,
    region: str
):

    regional_factor = (
        get_regional_factor(
            crop,
            region
        )
    )

    data = _get_national_dataframe(
        crop
    )

    regional_yield = [

        round(
            float(value)
            * regional_factor,
            4
        )

        for value
        in data["yield"]
    ]

    return {

        "years": [
            int(year)
            for year
            in data["year"]
        ],

        "rainfall": [
            None
            for _
            in data["year"]
        ],

        "yield":
            regional_yield,

        "source_type":
            "regionalized_national_fallback",
    }