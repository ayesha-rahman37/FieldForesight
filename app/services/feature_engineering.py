import pandas as pd


def prepare_yield_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data["rainfall"] = pd.to_numeric(data["rainfall"], errors="coerce")
    data["yield"] = pd.to_numeric(data["yield"], errors="coerce")

    data = data.dropna(
        subset=["year", "yield"]
    )

    if data.empty:
        return data

    data["rainfall"] = data["rainfall"].fillna(
        data["rainfall"].median()
        if not data["rainfall"].dropna().empty
        else 0.0
    )

    data = data.sort_values("year")
    data = data.drop_duplicates(
        subset=["year"],
        keep="last"
    )
    data = data.reset_index(drop=True)

    data["ds"] = pd.to_datetime(
        data["year"].astype(int).astype(str),
        format="%Y"
    )

    data["y"] = data["yield"].astype(float)

    data["year_index"] = (
        data["year"] - data["year"].min()
    )

    data["lag_yield"] = data["y"].shift(1)

    data["yield_change"] = (
        data["y"] - data["lag_yield"]
    )

    data["rolling_yield_mean"] = (
        data["y"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    data["yield_anomaly"] = (
        data["y"] - data["rolling_yield_mean"]
    )

    data["anomaly_score"] = (
        data["yield_anomaly"]
        / data["rolling_yield_mean"].replace(0, 1)
    )

    recent_cutoff = data["year"].max() - 2

    data["is_recent"] = (
        data["year"] >= recent_cutoff
    ).astype(int)

    data["lag_yield"] = data["lag_yield"].fillna(data["y"])
    data["yield_change"] = data["yield_change"].fillna(0.0)

    return data