"""Core data processing and aggregation logic for DATADIS energy consumption."""

import calendar

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
    ComparisonSummary,
    CupsComparison,
    CupsShare,
    MonthComparison,
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

            # Mathematical Invariant: Fair-Share Percentage Calculation
            # Share_i = (kWh_i / total_community_kwh) * 100.0
            # Guaranteed to sum to exactly 100.00% across all community meters for any period.
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

    @classmethod
    def compare_years(
        cls,
        df: pd.DataFrame,
        target_years: list[int] | None = None,
    ) -> ComparisonSummary:
        """Compare community energy consumption across multiple calendar years.

        Args:
            df: Normalized pandas DataFrame.
            target_years: Optional list of years to compare. If None, all years in df are used.

        Returns:
            ComparisonSummary containing monthly comparisons, annual deltas, and CUPS shifts.

        Raises:
            DatadisError: If fewer than two years are available or if requested years are missing.
        """
        if df.empty:
            raise DatadisError("Cannot compare an empty DataFrame.")

        available_years = sorted(df[COL_YEAR].unique().tolist())
        if len(available_years) < 2:
            raise DatadisError(
                f"At least two years are required for comparison; found only: {', '.join(map(str, available_years))}."
            )

        if target_years:
            missing = [y for y in target_years if y not in available_years]
            if missing:
                raise DatadisError(
                    f"Requested year(s) {', '.join(map(str, missing))} not found in dataset. "
                    f"Available years: {', '.join(map(str, available_years))}."
                )
            selected_years = sorted(dict.fromkeys(target_years))
            if len(selected_years) < 2:
                raise DatadisError("At least two distinct years must be selected for comparison.")
        else:
            selected_years = available_years

        filtered_df = df[df[COL_YEAR].isin(selected_years)]

        earliest_year = selected_years[0]
        latest_year = selected_years[-1]

        # 1. Pre-aggregate monthly sums and distinct days per (year, month)
        monthly_sums = (
            filtered_df.groupby([COL_YEAR, COL_MONTH])[COL_CONSUMPTION_KWH].sum().to_dict()
        )
        monthly_days = filtered_df.groupby([COL_YEAR, COL_MONTH])[COL_DATE].nunique().to_dict()

        monthly_comparisons: list[MonthComparison] = []
        for m in range(1, 13):
            # Check if any year has records for this month
            has_records = any((y, m) in monthly_sums for y in selected_years)
            if not has_records:
                continue

            yearly_kwh: dict[int, float | None] = {}
            year_status: dict[int, str] = {}
            year_days: dict[int, tuple[int, int]] = {}
            all_years_complete = True

            # Completeness Verification Heuristic:
            # An apples-to-apples comparison requires that all compared years have full data
            # for the entire calendar month (actual_days == expected_days_in_month).
            # If a month has partial data in any year (e.g. only 15 days in an in-progress year),
            # calculating deltas would be mathematically misleading and distort year-over-year trends.
            for y in selected_years:
                expected_days = calendar.monthrange(y, m)[1]
                actual_days = int(monthly_days.get((y, m), 0))
                year_days[y] = (actual_days, expected_days)

                if (y, m) not in monthly_sums or actual_days == 0:
                    yearly_kwh[y] = None
                    year_status[y] = "no_data"
                    all_years_complete = False
                elif actual_days < expected_days:
                    yearly_kwh[y] = float(monthly_sums[(y, m)])
                    year_status[y] = "incomplete"
                    all_years_complete = False
                else:
                    yearly_kwh[y] = float(monthly_sums[(y, m)])
                    year_status[y] = "complete"

            # Invariant: If a month lacks complete data in ANY year, exclude it from delta comparison
            if all_years_complete:
                base_kwh = float(yearly_kwh[earliest_year] or 0.0)
                target_kwh = float(yearly_kwh[latest_year] or 0.0)
                diff_kwh: float | None = target_kwh - base_kwh
                pct_change: float | None = (
                    ((diff_kwh / base_kwh) * 100.0)
                    if base_kwh > 0
                    else (0.0 if target_kwh == 0 else None)
                )
            else:
                diff_kwh = None
                pct_change = None

            monthly_comparisons.append(
                MonthComparison(
                    month=m,
                    yearly_kwh=yearly_kwh,
                    diff_kwh=diff_kwh,
                    pct_change=pct_change,
                    is_complete=all_years_complete,
                    year_status=year_status,
                    year_days=year_days,
                )
            )

        # 2. Determine comparable and excluded months
        comparable_months = [m.month for m in monthly_comparisons if m.is_complete]
        excluded_months = [m.month for m in monthly_comparisons if not m.is_complete]

        # 3. Annual totals (raw overall consumption)
        annual_totals = {
            y: float(filtered_df[filtered_df[COL_YEAR] == y][COL_CONSUMPTION_KWH].sum())
            for y in selected_years
        }

        # 4. Comparable annual totals & variations (apples-to-apples across complete months)
        if comparable_months:
            comp_df = filtered_df[filtered_df[COL_MONTH].isin(comparable_months)]
            comparable_annual_totals = {
                y: float(comp_df[comp_df[COL_YEAR] == y][COL_CONSUMPTION_KWH].sum())
                for y in selected_years
            }
            total_diff_kwh: float | None = (
                comparable_annual_totals[latest_year] - comparable_annual_totals[earliest_year]
            )
            base_comp = comparable_annual_totals[earliest_year]
            total_pct_change: float | None = (
                ((total_diff_kwh / base_comp) * 100.0)
                if base_comp > 0
                else (0.0 if comparable_annual_totals[latest_year] == 0 else None)
            )
        else:
            comp_df = filtered_df
            comparable_annual_totals = dict.fromkeys(selected_years, 0.0)
            total_diff_kwh = None
            total_pct_change = None

        # 5. Peak increase and decrease months (evaluated strictly among complete months)
        valid_months = [
            m for m in monthly_comparisons if m.is_complete and m.pct_change is not None
        ]
        max_increase_month = (
            max(valid_months, key=lambda m: m.pct_change or 0.0) if valid_months else None
        )
        if max_increase_month and (max_increase_month.pct_change or 0.0) <= 0:
            max_increase_month = None

        max_decrease_month = (
            min(valid_months, key=lambda m: m.pct_change or 0.0) if valid_months else None
        )
        if max_decrease_month and (max_decrease_month.pct_change or 0.0) >= 0:
            max_decrease_month = None

        # 6. CUPS-level monthly data for visualization & comparable evaluation
        all_cups = sorted(filtered_df[COL_CUPS].unique().tolist())
        cups_monthly_grouped = (
            filtered_df.groupby([COL_CUPS, COL_YEAR, COL_MONTH])[COL_CONSUMPTION_KWH]
            .sum()
            .to_dict()
        )

        cups_monthly_data: dict[str, dict[int, dict[int, float]]] = {}
        for c in all_cups:
            cups_monthly_data[c] = {}
            for y in selected_years:
                cups_monthly_data[c][y] = {}
                for m in range(1, 13):
                    cups_monthly_data[c][y][m] = float(cups_monthly_grouped.get((c, y, m), 0.0))

        # Evaluate CUPS shifts on comparable period if available
        cups_eval_grouped = (
            comp_df.groupby([COL_CUPS, COL_YEAR])[COL_CONSUMPTION_KWH].sum().to_dict()
        )

        cups_comparisons: list[CupsComparison] = []
        for c in all_cups:
            c_yearly = {y: float(cups_eval_grouped.get((c, y), 0.0)) for y in selected_years}
            c_base = c_yearly[earliest_year]
            c_target = c_yearly[latest_year]
            c_diff = c_target - c_base
            c_pct = ((c_diff / c_base) * 100.0) if c_base > 0 else (0.0 if c_target == 0 else None)
            cups_comparisons.append(
                CupsComparison(
                    cups=c,
                    yearly_kwh=c_yearly,
                    diff_kwh=c_diff,
                    pct_change=c_pct,
                    monthly_kwh=cups_monthly_data[c],
                )
            )

        # Sort by diff_kwh ascending (largest savings first)
        cups_comparisons.sort(key=lambda x: x.diff_kwh)

        top_saving_cups = (
            cups_comparisons[0] if cups_comparisons and cups_comparisons[0].diff_kwh < 0 else None
        )
        top_increasing_cups = (
            cups_comparisons[-1] if cups_comparisons and cups_comparisons[-1].diff_kwh > 0 else None
        )

        return ComparisonSummary(
            years=selected_years,
            monthly_comparisons=monthly_comparisons,
            annual_totals=annual_totals,
            comparable_annual_totals=comparable_annual_totals,
            comparable_months=comparable_months,
            excluded_months=excluded_months,
            total_diff_kwh=total_diff_kwh,
            total_pct_change=total_pct_change,
            max_increase_month=max_increase_month,
            max_decrease_month=max_decrease_month,
            top_saving_cups=top_saving_cups,
            top_increasing_cups=top_increasing_cups,
            cups_comparisons=cups_comparisons,
            cups_monthly_data=cups_monthly_data,
        )
