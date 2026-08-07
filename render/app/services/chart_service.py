"""Generates Chart.js-compatible chart configurations from analytics data."""

import math
from typing import Any


def _safe_float(val: Any) -> float:
    if val is None:
        return 0.0
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def generate_charts(metrics: dict, analytics: dict) -> list[dict]:
    """Build a list of Chart.js chart configs from metrics + analytics."""
    charts = []

    # 1. Revenue & Pipeline bar chart
    revenue = _safe_float(metrics.get("revenue", 0))
    pipeline = _safe_float(metrics.get("pipeline_value", 0))
    avg_deal = _safe_float(metrics.get("avg_deal_size", 0))
    if revenue or pipeline:
        charts.append({
            "type": "bar",
            "title": "Revenue vs Pipeline",
            "data": {
                "labels": ["Revenue", "Pipeline Value", "Avg Deal Size"],
                "datasets": [{
                    "label": "USD",
                    "data": [revenue, pipeline, avg_deal],
                    "backgroundColor": ["#4f46e5", "#06b6d4", "#8b5cf6"],
                }],
            },
            "options": {
                "responsive": True,
                "plugins": {"legend": {"display": False}},
                "scales": {"y": {"beginAtZero": True}},
            },
        })

    # 2. Win rate doughnut
    win_rate = _safe_float(metrics.get("win_rate", 0))
    if win_rate:
        charts.append({
            "type": "doughnut",
            "title": "Win Rate",
            "data": {
                "labels": ["Won", "Lost"],
                "datasets": [{
                    "data": [win_rate, 100 - win_rate],
                    "backgroundColor": ["#22c55e", "#ef4444"],
                }],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "bottom"},
                    "title": {"display": True, "text": f"Win Rate: {win_rate:.1f}%"},
                },
            },
        })

    # 3. Sector breakdown pie chart
    sector_data = analytics.get("sector_analysis", {})
    sectors = sector_data.get("sectors", {})
    if sectors:
        labels = list(sectors.keys())
        values = [_safe_float(s.get("total", 0)) for s in sectors.values()]
        charts.append({
            "type": "pie",
            "title": "Revenue by Sector",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": values,
                    "backgroundColor": [
                        "#4f46e5", "#06b6d4", "#22c55e", "#f59e0b",
                        "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6",
                    ],
                }],
            },
            "options": {
                "responsive": True,
                "plugins": {"legend": {"position": "right"}},
            },
        })

    # 4. Pipeline stages horizontal bar
    pipeline_stages = analytics.get("pipeline_analysis", {}).get("stages", {})
    if pipeline_stages:
        labels = list(pipeline_stages.keys())
        values = [_safe_float(v) for v in pipeline_stages.values()]
        charts.append({
            "type": "bar",
            "title": "Pipeline by Stage",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Value",
                    "data": values,
                    "backgroundColor": "#06b6d4",
                }],
            },
            "options": {
                "indexAxis": "y",
                "responsive": True,
                "plugins": {"legend": {"display": False}},
                "scales": {"x": {"beginAtZero": True}},
            },
        })

    # 5. Work order status bar
    op = analytics.get("operational_metrics", {})
    by_status = op.get("by_status", {})
    if by_status:
        labels = list(by_status.keys())
        values = [_safe_float(v) for v in by_status.values()]
        charts.append({
            "type": "bar",
            "title": "Work Orders by Status",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Count",
                    "data": values,
                    "backgroundColor": "#8b5cf6",
                }],
            },
            "options": {
                "responsive": True,
                "plugins": {"legend": {"display": False}},
                "scales": {"y": {"beginAtZero": True, "ticks": {"stepSize": 1}}},
            },
        })

    # 6. Trend line chart
    trends = analytics.get("trends", {})
    periods = trends.get("periods", [])
    trend_values = trends.get("values", [])
    if periods and trend_values:
        charts.append({
            "type": "line",
            "title": "Revenue Trend",
            "data": {
                "labels": periods,
                "datasets": [{
                    "label": "Revenue",
                    "data": [_safe_float(v) for v in trend_values],
                    "borderColor": "#4f46e5",
                    "backgroundColor": "rgba(79,70,229,0.1)",
                    "fill": True,
                    "tension": 0.3,
                }],
            },
            "options": {
                "responsive": True,
                "plugins": {"legend": {"display": False}},
                "scales": {"y": {"beginAtZero": True}},
            },
        })

    # 7. Completion rate gauge (horizontal bar styled as gauge)
    completion = _safe_float(op.get("completion_rate", 0))
    if completion:
        charts.append({
            "type": "doughnut",
            "title": "Work Order Completion Rate",
            "data": {
                "labels": ["Completed", "Remaining"],
                "datasets": [{
                    "data": [completion, 100 - completion],
                    "backgroundColor": ["#22c55e", "#e5e7eb"],
                    "cutout": "75%",
                }],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"display": False},
                    "title": {"display": True, "text": f"Completion: {completion:.1f}%"},
                },
            },
        })

    # 8. Summary KPI cards
    charts.append({
        "type": "kpi",
        "title": "Key Metrics",
        "data": {
            "items": [
                {"label": "Revenue", "value": f"${revenue:,.0f}", "color": "#4f46e5"},
                {"label": "Pipeline", "value": f"${pipeline:,.0f}", "color": "#06b6d4"},
                {"label": "Win Rate", "value": f"{win_rate:.1f}%", "color": "#22c55e"},
                {"label": "Active Deals", "value": str(metrics.get("active_deals", 0)), "color": "#8b5cf6"},
                {"label": "Work Orders", "value": str(metrics.get("work_orders", 0)), "color": "#f59e0b"},
                {"label": "Completion", "value": f"{completion:.1f}%", "color": "#ec4899"},
            ],
        },
    })

    return charts
