import numpy as np
import pandas as pd

from prophet import Prophet


def calculate_mae(actual, predicted) -> float:
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)

    return float(
        np.mean(
            np.abs(actual_values - predicted_values)
        )
    )


def calculate_rmse(actual, predicted) -> float:
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)

    return float(
        np.sqrt(
            np.mean(
                (actual_values - predicted_values) ** 2
            )
        )
    )


def calculate_mape(actual, predicted) -> float:
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)

    mask = actual_values != 0

    if not np.any(mask):
        return 0.0

    return float(
        np.mean(
            np.abs(
                (
                    actual_values[mask]
                    - predicted_values[mask]
                )
                / actual_values[mask]
            )
        )
        * 100
    )


def evaluate_prophet_model(
    data: pd.DataFrame,
    weighting_function
):
    if len(data) < 4:
        return {
            "mae": None,
            "rmse": None,
            "mape": None,
            "evaluation_records": 0
        }

    split_index = max(
        2,
        int(len(data) * 0.8)
    )

    if split_index >= len(data):
        split_index = len(data) - 1

    train_data = data.iloc[:split_index].copy()
    test_data = data.iloc[split_index:].copy()

    weighted_train = weighting_function(train_data)

    model = Prophet(
        yearly_seasonality=False
    )

    model.fit(
        weighted_train[["ds", "y"]]
    )

    future = test_data[["ds"]].copy()

    forecast = model.predict(future)

    actual = test_data["y"].values
    predicted = forecast["yhat"].values

    return {
        "mae": round(
            calculate_mae(actual, predicted),
            4
        ),
        "rmse": round(
            calculate_rmse(actual, predicted),
            4
        ),
        "mape": round(
            calculate_mape(actual, predicted),
            4
        ),
        "evaluation_records": len(test_data)
    }