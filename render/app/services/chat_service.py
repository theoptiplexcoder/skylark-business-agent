import pandas as pd
import time
import json
import math

from app.services.monday.boards import get_boards as fetch_boards, get_all_items as fetch_all_items
from app.services.cleaning_service import CleaningService
from app.services.analytics_service import AnalyticsService
from app.services.query_service import QueryService
from app.services.insight_service import InsightService
from app.services.llm_service import llm_service
from app.services.chart_service import generate_charts
from app.core.logging import logger


def sanitize(obj):
    """Recursively replace NaN/Inf with None for JSON serialization."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj


class ChatService:
    """Orchestrates the full BI query pipeline."""

    def __init__(self):
        self.cleaning = CleaningService()
        self.analytics = AnalyticsService()
        self.query = QueryService()
        self.insights = InsightService()

    async def process_message(self, message: str) -> dict:
        start_time = time.time()

        try:
            query_analysis = self.query.analyze_query(message)

            if query_analysis["needs_clarification"]:
                return {
                    "answer": query_analysis["clarification_question"],
                    "confidence": 0.3,
                    "execution_time": round(time.time() - start_time, 2),
                }

            boards = await fetch_boards()
            board_ids = self.query.determine_required_boards(query_analysis["intents"], boards)

            all_deals = []
            all_work_orders = []

            for board_id in board_ids:
                try:
                    items = await fetch_all_items(board_id, max_items=500)
                except Exception as e:
                    logger.warning("Failed to fetch items for board %s: %s", board_id, e)
                    continue
                if items:
                    column_map = {}
                    for board in boards:
                        if str(board.get("id")) == str(board_id):
                            for col in board.get("columns", []):
                                column_map[col["id"]] = col["title"]
                            break
                    df = pd.DataFrame([self._flatten_item(item, column_map) for item in items])
                    df, quality = self.cleaning.clean_dataframe(df)

                    board_name = self._get_board_name(boards, board_id).lower()
                    if any(kw in board_name for kw in ["deal", "sales", "pipeline"]):
                        all_deals.append(df)
                    elif any(kw in board_name for kw in ["work", "order", "project"]):
                        all_work_orders.append(df)
                    else:
                        all_deals.append(df)

            deals = pd.concat(all_deals, ignore_index=True) if all_deals else pd.DataFrame()
            work_orders = pd.concat(all_work_orders, ignore_index=True) if all_work_orders else pd.DataFrame()

            metrics = self.analytics.compute_dashboard_metrics(deals, work_orders)

            analytics = {
                "pipeline_analysis": self.analytics.pipeline_analysis(deals),
                "sector_analysis": self.analytics.sector_analysis(deals),
                "operational_metrics": self.analytics.operational_metrics(work_orders),
                "cross_board": self.analytics.cross_board_analysis(deals, work_orders),
                "trends": self.analytics.trend_analysis(deals),
            }

            insight_result = self.insights.generate_insights(metrics, analytics, query_analysis)

            charts = generate_charts(metrics, analytics)

            data_summary = self._build_data_summary(metrics, analytics)
            llm_answer = await llm_service.generate_insight(data_summary, message)

            if not llm_answer or llm_answer.startswith("Error") or llm_answer.startswith("LLM service"):
                answer = self._build_fallback_answer(metrics, query_analysis["intents"], analytics)
            else:
                answer = llm_answer

            return sanitize({
                "answer": answer,
                "charts": charts,
                "metrics": metrics,
                "insights": insight_result["insights"],
                "recommendations": insight_result["recommendations"],
                "warnings": insight_result["warnings"],
                "confidence": insight_result["confidence"],
                "quality": {
                    "boards_analyzed": len(board_ids),
                    "deals_count": len(deals),
                    "work_orders_count": len(work_orders),
                },
                "execution_time": round(time.time() - start_time, 2),
            })

        except Exception as e:
            logger.error("Chat processing failed: %s", e)
            return {
                "answer": f"I encountered an error processing your request: {str(e)}",
                "confidence": 0.0,
                "warnings": [str(e)],
                "execution_time": round(time.time() - start_time, 2),
            }

    def _flatten_item(self, item: dict, column_map: dict = None) -> dict:
        row = {"id": item.get("id"), "name": item.get("name")}
        for col_id, col_val in item.get("values", {}).items():
            text = col_val.get("text", "") if isinstance(col_val, dict) else col_val
            row[col_id] = text
            if column_map and col_id in column_map:
                row[column_map[col_id]] = text
        return row

    def _get_board_name(self, boards: list[dict], board_id: str) -> str:
        for b in boards:
            if str(b.get("id")) == str(board_id):
                return b.get("name", "Unknown")
        return "Unknown"

    def _build_data_summary(self, metrics: dict, analytics: dict) -> str:
        parts = []
        for k, v in metrics.items():
            if isinstance(v, float):
                parts.append(f"{k}: {v:,.2f}")
            else:
                parts.append(f"{k}: {v}")

        sector = analytics.get("sector_analysis", {})
        if sector.get("sectors"):
            parts.append("Sectors: " + ", ".join(
                f"{s} (${d.get('total', 0):,.0f})" for s, d in sector["sectors"].items()
            ))

        return "\n".join(parts)

    def _build_fallback_answer(self, metrics: dict, intents: list[str], analytics: dict = None) -> str:
        analytics = analytics or {}
        parts = []

        revenue = metrics.get("revenue", 0)
        pipeline = metrics.get("pipeline_value", 0)
        win_rate = metrics.get("win_rate", 0)
        active = metrics.get("active_deals", 0)
        avg_deal = metrics.get("avg_deal_size", 0)
        work_orders = metrics.get("work_orders", 0)
        completion = metrics.get("completion_pct", 0)
        delayed = metrics.get("delayed_orders", 0)

        if revenue:
            parts.append(f"Total revenue stands at Rs. {revenue:,.0f}")
            if avg_deal:
                parts.append(f"with an average deal size of Rs. {avg_deal:,.0f}")
            parts.append(".")

        if active:
            if pipeline:
                parts.append(f"There are {active} active deals in the pipeline worth Rs. {pipeline:,.0f}.")
            else:
                parts.append(f"There are {active} active deals in the pipeline.")

        if win_rate:
            rating = "strong" if win_rate > 50 else "moderate" if win_rate > 30 else "below-average"
            parts.append(f"The win rate is {win_rate:.1f}%, which is {rating}.")

        sector_data = analytics.get("sector_analysis", {})
        sectors = sector_data.get("sectors", {})
        if sectors:
            sorted_sectors = sorted(sectors.items(), key=lambda x: x[1].get("total", 0), reverse=True)
            top_sector = sorted_sectors[0]
            parts.append(f"The top-performing sector is {top_sector[0]} with Rs. {top_sector[1]['total']:,.0f} across {top_sector[1]['count']} deals.")
            if len(sorted_sectors) > 1:
                second = sorted_sectors[1]
                parts.append(f"Followed by {second[0]} at Rs. {second[1]['total']:,.0f}.")

        stages = analytics.get("pipeline_analysis", {}).get("stages", {})
        if stages:
            stage_list = [f"{k}: Rs. {v:,.0f}" for k, v in list(stages.items())[:4]]
            parts.append(f"Pipeline breakdown: {' | '.join(stage_list)}.")

        if work_orders:
            parts.append(f"There are {work_orders} work orders")
            if completion:
                parts.append(f"with a {completion:.1f}% completion rate")
            if delayed:
                parts.append(f"and {delayed} delayed orders requiring attention")
            parts.append(".")

        trends = analytics.get("trends", {})
        trend_values = trends.get("values", [])
        if len(trend_values) >= 2:
            if trend_values[-1] > trend_values[-2]:
                parts.append("Revenue trend is upward.")
            elif trend_values[-1] < trend_values[-2]:
                parts.append("Revenue trend is declining — worth monitoring.")

        if not parts:
            parts.append(f"Across {active} active deals, total revenue is Rs. {revenue:,.0f} with a pipeline of Rs. {pipeline:,.0f}.")

        answer = " ".join(parts)

        warnings = []
        if win_rate and win_rate < 30:
            warnings.append("Win rate is below 30% — review the sales process.")
        if pipeline and revenue and pipeline < revenue * 2:
            warnings.append("Pipeline coverage is below 2x revenue — consider generating more leads.")
        if delayed:
            warnings.append(f"{delayed} delayed orders need immediate attention.")

        if warnings:
            answer += "\n\n" + " ".join(warnings)

        return answer


chat_service = ChatService()
