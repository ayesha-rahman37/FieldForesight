import datetime
import math
import numpy as np
import pandas as pd
from models import Variety
from schemas import ForecastPoint, ForecastResponse


def run_prophet_or_fallback_forecast(variety: Variety, metric_type: str = "yield_index", days: int = 30) -> ForecastResponse:
    today = datetime.date.today()
    yield_potential = variety.yield_potential_ton_ha or 6.0

    try:
        from prophet import Prophet

        history_days = 90
        dates = [today - datetime.timedelta(days=i) for i in range(history_days, 0, -1)]
        base_val = yield_potential if metric_type == "yield_index" else 25.0

        df_list = []
        for i, d in enumerate(dates):
            seasonal = math.sin(i / 10.0) * (base_val * 0.15)
            noise = np.random.normal(0, base_val * 0.03)
            val = max(1.0, base_val + seasonal + noise)
            df_list.append({"ds": d.strftime("%Y-%m-%d"), "y": val})

        df = pd.DataFrame(df_list)
        df['ds'] = pd.to_datetime(df['ds'])

        m = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
        m.fit(df)

        future = m.make_future_dataframe(periods=days)
        forecast = m.predict(future)

        future_forecast = forecast.tail(days)
        points = []
        for _, row in future_forecast.iterrows():
            points.append(
                ForecastPoint(
                    ds=row['ds'].strftime("%Y-%m-%d"),
                    yhat=round(float(row['yhat']), 2),
                    yhat_lower=round(float(row['yhat_lower']), 2),
                    yhat_upper=round(float(row['yhat_upper']), 2)
                )
            )

        return ForecastResponse(
            variety_id=variety.id,
            metric_type=metric_type,
            points=points
        )

    except Exception:
        points = []
        base_val = yield_potential if metric_type == "yield_index" else 30.0

        for day_offset in range(1, days + 1):
            future_date = today + datetime.timedelta(days=day_offset)
            date_str = future_date.strftime("%Y-%m-%d")

            phase = (day_offset / 30.0) * math.pi
            growth_trend = math.sin(phase) * 0.8
            yhat = round(base_val + growth_trend, 2)
            yhat_lower = round(yhat - 0.45, 2)
            yhat_upper = round(yhat + 0.45, 2)

            points.append(
                ForecastPoint(
                    ds=date_str,
                    yhat=max(yhat, 0.5),
                    yhat_lower=max(yhat_lower, 0.2),
                    yhat_upper=yhat_upper
                )
            )

        return ForecastResponse(
            variety_id=variety.id,
            metric_type=metric_type,
            points=points
        )
