from sqladmin import ModelView
from models import Variety, RiskThreshold, AdvisoryHistory, ForecastData

class VarietyAdmin(ModelView, model=Variety):
    column_list = [
        Variety.id,
        Variety.name,
        Variety.name_bangla,
        Variety.crop_type,
        Variety.optimal_temp_min,
        Variety.optimal_temp_max,
        Variety.max_temp_threshold,
        Variety.pest_susceptibility,
        Variety.yield_potential_ton_ha
    ]
    column_searchable_list = [Variety.name, Variety.name_bangla, Variety.crop_type]
    icon = "fa-solid fa-wheat-awn"

class RiskThresholdAdmin(ModelView, model=RiskThreshold):
    column_list = [
        RiskThreshold.id,
        RiskThreshold.variety_id,
        RiskThreshold.metric_name,
        RiskThreshold.low_max,
        RiskThreshold.medium_max,
        RiskThreshold.high_max,
        RiskThreshold.critical_min
    ]
    icon = "fa-solid fa-triangle-exclamation"

class AdvisoryHistoryAdmin(ModelView, model=AdvisoryHistory):
    column_list = [
        AdvisoryHistory.id,
        AdvisoryHistory.variety_id,
        AdvisoryHistory.risk_level,
        AdvisoryHistory.llm_provider,
        AdvisoryHistory.created_at
    ]
    column_searchable_list = [AdvisoryHistory.risk_level, AdvisoryHistory.llm_provider]
    icon = "fa-solid fa-comment-dots"

class ForecastDataAdmin(ModelView, model=ForecastData):
    column_list = [
        ForecastData.id,
        ForecastData.variety_id,
        ForecastData.metric_type,
        ForecastData.ds,
        ForecastData.yhat,
        ForecastData.yhat_lower,
        ForecastData.yhat_upper
    ]
    icon = "fa-solid fa-chart-line"

def register_admin(admin):
    admin.add_view(VarietyAdmin)
    admin.add_view(RiskThresholdAdmin)
    admin.add_view(AdvisoryHistoryAdmin)
    admin.add_view(ForecastDataAdmin)
