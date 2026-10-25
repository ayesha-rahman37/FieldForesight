"""
Scenario service alias exporting compute().
"""

from app.services.scenario_planner_service import compute, run_scenario

__all__ = ["compute", "run_scenario"]

