import pandas as pd
import re
from typing import Optional
from app.core.logging import logger


class CleaningService:
    """Handles messy business data from Monday.com."""

    def clean_dataframe(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        original_count = len(df)
        warnings = []

        df = self._remove_exact_duplicates(df, warnings)
        df = self._clean_whitespace(df)
        df = self._normalize_text_columns(df)
        df = self._normalize_dates(df, warnings)
        df = self._normalize_currency_columns(df)
        df = self._fill_missing_values(df, warnings)
        df = self._normalize_column_names(df)

        missing_count = df.isnull().sum().sum()
        dupes_removed = original_count - len(df)

        quality = {
            "original_rows": original_count,
            "cleaned_rows": len(df),
            "duplicates_removed": dupes_removed,
            "missing_values": int(missing_count),
            "warnings": warnings,
        }

        logger.info("Data cleaning complete: %s", quality)
        return df, quality

    def _remove_exact_duplicates(self, df: pd.DataFrame, warnings: list) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        if removed > 0:
            warnings.append(f"Removed {removed} duplicate record(s).")
        return df

    def _clean_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].apply(lambda x: re.sub(r"\s+", " ", str(x)).strip() if pd.notna(x) else x)
        return df

    def _normalize_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.select_dtypes(include=["object"]).columns:
            if col.lower() in ("status", "sector", "region", "stage"):
                df[col] = df[col].str.title() if df[col].dtype == "object" else df[col]
        return df

    def _normalize_dates(self, df: pd.DataFrame, warnings: list) -> pd.DataFrame:
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",
            r"\d{2}/\d{2}/\d{4}",
            r"\d{2}-\d{2}-\d{4}",
        ]
        for col in df.columns:
            if df[col].dtype == "object":
                sample = df[col].dropna().head(10).astype(str)
                is_date_like = any(
                    sample.str.match(p).any() for p in date_patterns
                )
                if is_date_like:
                    try:
                        df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
                    except Exception:
                        pass
        return df

    def _normalize_currency_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if df[col].dtype == "object":
                sample = df[col].dropna().head(10).astype(str)
                has_currency = sample.str.contains(r"[\$\€\£\₹]", regex=True).any()
                if has_currency:
                    df[col] = df[col].apply(self._parse_currency)
        return df

    def _parse_currency(self, value) -> Optional[float]:
        if pd.isna(value) or not isinstance(value, str):
            return value
        cleaned = re.sub(r"[^\d.\-]", "", value)
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    def _fill_missing_values(self, df: pd.DataFrame, warnings: list) -> pd.DataFrame:
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                pct = (null_count / len(df)) * 100
                if pct > 50:
                    warnings.append(f"Column '{col}' has {pct:.0f}% missing values.")
                elif df[col].dtype == "object":
                    df[col] = df[col].fillna("Unknown")
                elif df[col].dtype in ("float64", "int64"):
                    df[col] = df[col].fillna(0)
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    pass
        return df

    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in df.columns
        ]
        return df


cleaning_service = CleaningService()
