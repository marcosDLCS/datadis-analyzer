"""Core data processing and aggregation logic for DATADIS energy consumption."""

import pandas as pd

from src.config import (
    COL_CONSUMPTION_KWH,
    COL_CUPS,
    COL_DATE,
    COL_MONTH,
    COL_YEAR,
)
from src.ingestion.schema import DatadisError
from src.processing.models import (
    AnnualPeriodSummary,
    CommunitySummary,
    CupsShare,
    MonthlyPeriodSummary,
)


class DataAggregator:
    """Processes normalized energy consumption DataFrames into structured community metrics."""

    @classmethod
    def aggregate_community(cls, df: pd.DataFrame) -> CommunitySummary:
        """Aggregate total community consumption and compute period percentage shares per CUPS.

        Args:
            df: Normalized pandas DataFrame containing DATADIS hourly readings.

        Returns:
            CommunitySummary with annual, monthly, and overall share breakdowns.

        Raises:
            DatadisError: If DataFrame is empty or missing expected columns.
        """
        if df.empty:
            raise DatadisError("Cannot aggregate an empty DataFrame.")

        required = [COL_CUPS, COL_DATE, COL_YEAR, COL_MONTH, COL_CONSUMPTION_KWH]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise DatadisError(
                f"DataFrame missing required aggregation columns: {', '.join(missing)}"
            )

        total_community_kwh = float(df[COL_CONSUMPTION_KWH].sum())
        total_readings = len(df)
        unique_cups = sorted(df[COL_CUPS].unique().tolist())
        date_min = str(df[COL_DATE].min().strftime("%Y-%m-%d"))
        date_max = str(df[COL_DATE].max().strftime("%Y-%m-%d"))

        # 1. Overall CUPS shares across all data
        overall_cups_shares = cls._calculate_cups_shares(
            df=df,
            group_cols=[COL_CUPS],
            total_kwh=total_community_kwh,
        )

        # 2. Monthly summaries
        monthly_summaries: list[MonthlyPeriodSummary] = []
        monthly_grouped = df.groupby([COL_YEAR, COL_MONTH])

        month_totals: dict[str, float] = {}

        for (year, month), month_df in sorted(monthly_grouped):
            period_label = f"{year:04d}-{month:02d}"
            month_total_kwh = float(month_df[COL_CONSUMPTION_KWH].sum())
            month_totals[period_label] = month_total_kwh

            shares = cls._calculate_cups_shares(
                df=month_df,
                group_cols=[COL_CUPS],
                total_kwh=month_total_kwh,
            )

            top_consumer = shares[0] if shares else CupsShare("", 0.0, 0.0, 0, 0.0)

            monthly_summaries.append(
                MonthlyPeriodSummary(
                    year=int(year),
                    month=int(month),
                    period_label=period_label,
                    community_total_kwh=month_total_kwh,
                    cups_shares=shares,
                    top_consumer=top_consumer,
                )
            )

        # Find peak and lowest months
        if month_totals:
            peak_month_label = max(month_totals, key=month_totals.get)
            peak_month_kwh = month_totals[peak_month_label]
            lowest_month_label = min(month_totals, key=month_totals.get)
            lowest_month_kwh = month_totals[lowest_month_label]
        else:
            peak_month_label = "N/A"
            peak_month_kwh = 0.0
            lowest_month_label = "N/A"
            lowest_month_kwh = 0.0

        # 3. Annual summaries
        annual_summaries: dict[int, AnnualPeriodSummary] = {}
        annual_grouped = df.groupby(COL_YEAR)

        for year, year_df in sorted(annual_grouped):
            year_int = int(year)
            year_total_kwh = float(year_df[COL_CONSUMPTION_KWH].sum())

            year_shares = cls._calculate_cups_shares(
                df=year_df,
                group_cols=[COL_CUPS],
                total_kwh=year_total_kwh,
            )

            # Monthly totals within this year
            month_dict: dict[int, float] = {}
            for m, m_df in year_df.groupby(COL_MONTH):
                month_dict[int(m)] = float(m_df[COL_CONSUMPTION_KWH].sum())

            top_consumer = year_shares[0] if year_shares else CupsShare("", 0.0, 0.0, 0, 0.0)
            lowest_consumer = year_shares[-1] if year_shares else CupsShare("", 0.0, 0.0, 0, 0.0)

            annual_summaries[year_int] = AnnualPeriodSummary(
                year=year_int,
                period_label=str(year_int),
                community_total_kwh=year_total_kwh,
                cups_shares=year_shares,
                monthly_totals=month_dict,
                top_consumer=top_consumer,
                lowest_consumer=lowest_consumer,
            )

        return CommunitySummary(
            total_community_kwh=total_community_kwh,
            total_readings=total_readings,
            unique_cups_count=len(unique_cups),
            cups_list=unique_cups,
            date_min=date_min,
            date_max=date_max,
            annual_summaries=annual_summaries,
            monthly_summaries=monthly_summaries,
            overall_cups_shares=overall_cups_shares,
            peak_month_label=peak_month_label,
            peak_month_kwh=peak_month_kwh,
            lowest_month_label=lowest_month_label,
            lowest_month_kwh=lowest_month_kwh,
        )

    @classmethod
    def _calculate_cups_shares(
        cls, df: pd.DataFrame, group_cols: list[str], total_kwh: float
    ) -> list[CupsShare]:
        """Calculate consumption and relative community percentage share per CUPS.

        Args:
            df: Subset DataFrame for the period.
            group_cols: Grouping columns (e.g. ['cups']).
            total_kwh: Denominator for percentage calculation.

        Returns:
            List of CupsShare sorted in descending order of consumption.
        """
        grouped = df.groupby(group_cols)[COL_CONSUMPTION_KWH].agg(["sum", "count"]).reset_index()

        shares: list[CupsShare] = []
        for _, row in grouped.iterrows():
            cups = str(row[COL_CUPS])
            kwh = float(row["sum"])
            count = int(row["count"])
            avg_hourly = kwh / count if count > 0 else 0.0
            share_pct = (kwh / total_kwh * 100.0) if total_kwh > 0 else 0.0

            shares.append(
                CupsShare(
                    cups=cups,
                    consumption_kwh=kwh,
                    share_pct=share_pct,
                    readings_count=count,
                    avg_hourly_kwh=avg_hourly,
                )
            )

        # Sort descending by energy consumption
        shares.sort(key=lambda s: s.consumption_kwh, reverse=True)
        return shares

    @classmethod
    def build_monthly_pivot(cls, df: pd.DataFrame, year: int | None = None) -> pd.DataFrame:
        """Create a matrix pivot table of CUPS consumption per month.

        Args:
            df: Normalized DataFrame.
            year: Optional year filter.

        Returns:
            Pivot DataFrame with CUPS as index, months as columns, plus Total and Share % columns.
        """
        target_df = df if year is None else df[df[COL_YEAR] == year]
        if target_df.empty:
            return pd.DataFrame()

        pivot = target_df.pivot_table(
            index=COL_CUPS,
            columns=COL_MONTH,
            values=COL_CONSUMPTION_KWH,
            aggfunc="sum",
            fill_value=0.0,
        )

        # Add total and share
        pivot["Total_kWh"] = pivot.sum(axis=1)
        total_all = pivot["Total_kWh"].sum()
        pivot["Share_%"] = (pivot["Total_kWh"] / total_all * 100.0) if total_all > 0 else 0.0
        pivot = pivot.sort_values(by="Total_kWh", ascending=False)
        return pivot
