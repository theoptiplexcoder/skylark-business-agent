from fastapi import APIRouter, Depends
import pandas as pd

from app.core.dependencies import get_current_user
from app.services.monday_service import monday_service
from app.services.analytics_service import AnalyticsService
from app.services.cleaning_service import CleaningService
from app.schemas.boards import MetricsResponse, LeadershipRequest, LeadershipResponse
from app.services.insight_service import InsightService

router = APIRouter(tags=["metrics"])
analytics_service = AnalyticsService()
cleaning_service = CleaningService()
insight_service = InsightService()


async def _fetch_all_board_data():
    boards = await monday_service.get_boards()
    all_deals = []
    all_work_orders = []

    for board in boards:
        board_id = str(board.get("id"))
        board_name = board.get("name", "").lower()
        items = await monday_service.get_all_items(board_id, max_items=500)
        if items:
            df = pd.DataFrame([{
                "id": item.get("id"),
                "name": item.get("name"),
                **{c.get("id", ""): c.get("text", "") for c in item.get("column_values", [])}
            } for item in items])
            df, _ = cleaning_service.clean_dataframe(df)
            if any(kw in board_name for kw in ["deal", "sales", "pipeline"]):
                all_deals.append(df)
            else:
                all_work_orders.append(df)

    deals = pd.concat(all_deals, ignore_index=True) if all_deals else pd.DataFrame()
    work_orders = pd.concat(all_work_orders, ignore_index=True) if all_work_orders else pd.DataFrame()
    return deals, work_orders


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(user: dict = Depends(get_current_user)):
    deals, work_orders = await _fetch_all_board_data()
    metrics = analytics_service.compute_dashboard_metrics(deals, work_orders)
    return MetricsResponse(
        pipeline_value=metrics.get("pipeline_value", 0),
        revenue=metrics.get("revenue", 0),
        win_rate=metrics.get("win_rate", 0),
        active_deals=metrics.get("active_deals", 0),
        work_orders=metrics.get("work_orders", 0),
        completed_orders=metrics.get("completed_orders", 0),
        avg_deal_size=metrics.get("avg_deal_size", 0),
        completion_pct=metrics.get("completion_pct", 0),
    )


@router.post("/leadership-update", response_model=LeadershipResponse)
async def leadership_update(
    body: LeadershipRequest = LeadershipRequest(),
    user: dict = Depends(get_current_user),
):
    deals, work_orders = await _fetch_all_board_data()
    metrics = analytics_service.compute_dashboard_metrics(deals, work_orders)
    analytics = {
        "sector_analysis": analytics_service.sector_analysis(deals),
        "operational_metrics": analytics_service.operational_metrics(work_orders),
    }
    result = insight_service.generate_leadership_summary(metrics, analytics)
    return LeadershipResponse(**result)
