import pandas as pd
from typing import Optional
from app.core.logging import logger


class AnalyticsService:
    """Business Intelligence analytics engine."""

    def compute_dashboard_metrics(self, deals: pd.DataFrame, work_orders: pd.DataFrame) -> dict:
        metrics = {}

        if not deals.empty:
            revenue_col = self._find_column(deals, [
                "revenue", "amount", "deal_value", "value", "total",
                "amount in rupees", "masked deal value", "deal value",
                "billed value", "collected amount",
            ])
            if revenue_col:
                numeric = pd.to_numeric(deals[revenue_col].astype(str).str.replace(r'[^\d.\-]', '', regex=True), errors='coerce')
                metrics["revenue"] = float(numeric.sum())
                metrics["avg_deal_size"] = float(numeric.mean()) if not numeric.isna().all() else 0

            status_col = self._find_column(deals, [
                "status", "stage", "deal_stage", "deal status",
                "deal stage", "closure probability",
            ])
            if status_col:
                statuses = deals[status_col].astype(str).str.lower()
                won = deals[statuses.str.contains("won|closed|complete|closed won", na=False)]
                lost = deals[statuses.str.contains("lost|cancelled|dead|closed lost", na=False)]
                total = len(won) + len(lost)
                metrics["win_rate"] = float(len(won) / total * 100) if total > 0 else 0

            metrics["active_deals"] = len(deals)

            pipeline_col = self._find_column(deals, [
                "value", "amount", "revenue", "deal_value",
                "masked deal value", "amount in rupees", "deal value",
            ])
            if pipeline_col:
                active_statuses = statuses if status_col else pd.Series([''] * len(deals))
                active_mask = ~active_statuses.str.contains("won|lost|cancelled|closed|dead", case=False, na=False)
                active = deals[active_mask] if status_col else deals
                if not active.empty:
                    numeric = pd.to_numeric(active[pipeline_col].astype(str).str.replace(r'[^\d.\-]', '', regex=True), errors='coerce')
                    metrics["pipeline_value"] = float(numeric.sum())
                else:
                    metrics["pipeline_value"] = 0

        if not work_orders.empty:
            wo_status = self._find_column(work_orders, [
                "status", "order_status", "work_order_status",
                "execution status", "nature of work", "wo status",
                "billing status", "invoice status",
            ])
            if wo_status:
                counts = work_orders[wo_status].value_counts()
                metrics["work_orders"] = int(counts.sum())
                completed = counts[counts.index.str.contains("complete|done|finished|executed|billed", case=False, na=False)].sum()
                delayed = counts[counts.index.str.contains("delay|late|overdue|pending", case=False, na=False)].sum()
                metrics["completed_orders"] = int(completed)
                metrics["delayed_orders"] = int(delayed)
                metrics["completion_pct"] = float(completed / counts.sum() * 100) if counts.sum() > 0 else 0

        return metrics

    def _to_numeric(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series.astype(str).str.replace(r'[^\d.\-]', '', regex=True), errors='coerce').fillna(0)

    def pipeline_analysis(self, deals: pd.DataFrame) -> dict:
        result = {"stages": {}, "total_value": 0}

        stage_col = self._find_column(deals, [
            "stage", "status", "deal_stage", "pipeline_stage",
            "deal stage", "closure probability", "deal status",
        ])
        value_col = self._find_column(deals, [
            "value", "amount", "revenue", "deal_value",
            "masked deal value", "amount in rupees", "deal value",
        ])

        if stage_col and value_col and not deals.empty:
            deals = deals.copy()
            deals[value_col] = self._to_numeric(deals[value_col])
            grouped = deals.groupby(stage_col)[value_col].sum()
            result["stages"] = {k: float(v) for k, v in grouped.to_dict().items()}
            result["total_value"] = float(grouped.sum())

        return result

    def sector_analysis(self, deals: pd.DataFrame) -> dict:
        result = {"sectors": {}, "best_performing": None}

        sector_col = self._find_column(deals, [
            "sector", "industry", "category", "segment",
            "sector/service", "product deal",
        ])
        value_col = self._find_column(deals, [
            "value", "amount", "revenue",
            "masked deal value", "amount in rupees", "deal value",
        ])

        if sector_col and value_col and not deals.empty:
            deals = deals.copy()
            deals[value_col] = self._to_numeric(deals[value_col])
            grouped = deals.groupby(sector_col)[value_col].agg(["sum", "count", "mean"])
            result["sectors"] = {
                sector: {"total": float(row["sum"]), "count": int(row["count"]), "avg": float(row["mean"])}
                for sector, row in grouped.iterrows()
            }
            if not grouped.empty:
                best = grouped["sum"].idxmax()
                result["best_performing"] = str(best)

        return result

    def operational_metrics(self, work_orders: pd.DataFrame) -> dict:
        result = {"total": 0, "by_status": {}, "completion_rate": 0}

        status_col = self._find_column(work_orders, [
            "status", "order_status", "work_order_status",
            "execution status", "wo status", "billing status",
        ])

        if status_col and not work_orders.empty:
            counts = work_orders[status_col].value_counts()
            result["total"] = int(counts.sum())
            result["by_status"] = counts.to_dict()
            completed = counts[counts.index.str.contains("complete|done|finished", case=False, na=False)].sum()
            result["completion_rate"] = float(completed / counts.sum() * 100) if counts.sum() > 0 else 0

        return result

    def cross_board_analysis(self, deals: pd.DataFrame, work_orders: pd.DataFrame) -> dict:
        result = {
            "deals_count": len(deals),
            "work_orders_count": len(work_orders),
            "revenue": 0,
            "operational_efficiency": None,
        }

        value_col = self._find_column(deals, [
            "value", "amount", "revenue",
            "masked deal value", "amount in rupees", "deal value",
        ])
        if value_col and not deals.empty:
            numeric = pd.to_numeric(deals[value_col].astype(str).str.replace(r'[^\d.\-]', '', regex=True), errors='coerce')
            result["revenue"] = float(numeric.sum())

        wo_status = self._find_column(work_orders, [
            "status", "order_status", "execution status", "wo status",
        ])
        if wo_status and not work_orders.empty:
            counts = work_orders[wo_status].value_counts()
            completed = counts[counts.index.str.contains("complete|done", case=False, na=False)].sum()
            result["operational_efficiency"] = float(completed / counts.sum() * 100) if counts.sum() > 0 else 0

        return result

    def trend_analysis(self, deals: pd.DataFrame) -> dict:
        date_col = self._find_column(deals, [
            "date", "close_date", "created_at", "updated_at",
            "expected close", "tentative close date", "close date",
            "created date", "data delivery date",
        ])
        value_col = self._find_column(deals, [
            "value", "amount", "revenue",
            "masked deal value", "amount in rupees", "deal value",
        ])

        if date_col and value_col and not deals.empty:
            df = deals.copy()
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df[value_col] = self._to_numeric(df[value_col])
            df = df.dropna(subset=[date_col])
            if not df.empty:
                df = df.sort_values(date_col)
                df["period"] = df[date_col].dt.to_period("M")
                trend = df.groupby("period")[value_col].sum()
                return {
                    "periods": [str(p) for p in trend.index],
                    "values": [float(v) for v in trend.values],
                }

        return {"periods": [], "values": []}

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
        col_map = {c.lower(): c for c in df.columns}
        col_map.update({c.replace("_", " ").lower(): c for c in df.columns})
        for name in candidates:
            name_lower = name.lower().replace("_", " ")
            for norm, original in col_map.items():
                if name_lower == norm or name_lower in norm or norm in name_lower:
                    return original
        return None
