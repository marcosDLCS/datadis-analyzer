"""Domain models and data structures for aggregated DATADIS energy consumption metrics."""

from dataclasses import dataclass, field


@dataclass
class CupsShare:
    """Represents a single CUPS's consumption and share within a given period.

    Attributes:
        cups: Universal Supply Point Code (Código Unificado de Punto de Suministro).
        consumption_kwh: Total energy consumed in kilowatt-hours.
        share_pct: Percentage share of total community consumption (0.0 to 100.0).
        readings_count: Number of hourly meter readings in the period.
        avg_hourly_kwh: Average hourly consumption in kilowatt-hours.
    """

    cups: str
    consumption_kwh: float
    share_pct: float
    readings_count: int
    avg_hourly_kwh: float


@dataclass
class MonthlyPeriodSummary:
    """Summary metrics for the residential community during a specific month.

    Attributes:
        year: Calendar year.
        month: Calendar month (1-12).
        period_label: Human-readable identifier (e.g. '2025-01').
        community_total_kwh: Sum of consumption across all CUPS for the month.
        cups_shares: List of CUPS metrics for this month, sorted by consumption descending.
        top_consumer: CUPS with the highest consumption in this month.
    """

    year: int
    month: int
    period_label: str
    community_total_kwh: float
    cups_shares: list[CupsShare]
    top_consumer: CupsShare


@dataclass
class AnnualPeriodSummary:
    """Summary metrics for the residential community during a calendar year.

    Attributes:
        year: Calendar year.
        period_label: Human-readable identifier (e.g. '2025').
        community_total_kwh: Sum of consumption across all CUPS for the full year.
        cups_shares: List of CUPS metrics for this year, sorted by consumption descending.
        monthly_totals: Mapping of month number (1-12) to community total kWh.
        top_consumer: CUPS with the highest annual consumption.
        lowest_consumer: CUPS with the lowest non-zero (or overall lowest) annual consumption.
    """

    year: int
    period_label: str
    community_total_kwh: float
    cups_shares: list[CupsShare]
    monthly_totals: dict[int, float]
    top_consumer: CupsShare
    lowest_consumer: CupsShare


@dataclass
class CommunitySummary:
    """Overall summary aggregation for the residential building community across all loaded data.

    Attributes:
        total_community_kwh: Cumulative community consumption across all loaded years.
        total_readings: Cumulative count of hourly reading rows parsed.
        unique_cups_count: Total distinct CUPS meters detected.
        cups_list: Sorted list of all distinct CUPS codes.
        date_min: Earliest recorded date in the dataset.
        date_max: Latest recorded date in the dataset.
        annual_summaries: Dictionary of annual summaries keyed by year.
        monthly_summaries: Chronological list of monthly summaries.
        overall_cups_shares: Overall CUPS shares across the full dataset period.
        peak_month_label: Period label for the month with highest community consumption.
        peak_month_kwh: Consumption of the peak month.
        lowest_month_label: Period label for the month with lowest community consumption.
        lowest_month_kwh: Consumption of the lowest month.
    """

    total_community_kwh: float
    total_readings: int
    unique_cups_count: int
    cups_list: list[str]
    date_min: str
    date_max: str
    annual_summaries: dict[int, AnnualPeriodSummary]
    monthly_summaries: list[MonthlyPeriodSummary]
    overall_cups_shares: list[CupsShare]
    peak_month_label: str
    peak_month_kwh: float
    lowest_month_label: str
    lowest_month_kwh: float


@dataclass
class MonthComparison:
    """Monthly comparison across years for the community.

    Attributes:
        month: Calendar month (1-12).
        yearly_kwh: Mapping of year to community total kWh for this month (or None if no data).
        diff_kwh: Difference between target (latest) and base (earliest) year (None if incomplete/missing).
        pct_change: Percentage change between base and target year (None if incomplete or base is zero).
        is_complete: True if ALL compared years have full data covering all days of that calendar month.
        year_status: Mapping of year to status string ('complete', 'incomplete', 'no_data').
        year_days: Mapping of year to tuple of (actual_days_with_data, expected_days_in_month).
    """

    month: int
    yearly_kwh: dict[int, float | None]
    diff_kwh: float | None
    pct_change: float | None
    is_complete: bool = True
    year_status: dict[int, str] = field(default_factory=dict)
    year_days: dict[int, tuple[int, int]] = field(default_factory=dict)


@dataclass
class CupsComparison:
    """Year-over-year comparison for an individual supply point (CUPS).

    Attributes:
        cups: Universal Supply Point Code.
        yearly_kwh: Mapping of year to consumption over comparable periods.
        diff_kwh: Consumption difference between target (latest) and base (earliest) year.
        pct_change: Percentage change between base and target year (None if base is zero).
        monthly_kwh: Mapping of year -> month -> consumption kWh for this CUPS.
    """

    cups: str
    yearly_kwh: dict[int, float]
    diff_kwh: float
    pct_change: float | None
    monthly_kwh: dict[int, dict[int, float]] = field(default_factory=dict)


@dataclass
class ComparisonSummary:
    """Complete multi-year comparison summary for the residential community.

    Attributes:
        years: Sorted list of calendar years being compared.
        monthly_comparisons: Comparison for each month with recorded data.
        annual_totals: Total community consumption per year (all recorded data).
        comparable_annual_totals: Community consumption per year restricted to complete months.
        comparable_months: Sorted list of months that have complete data across all compared years.
        excluded_months: Sorted list of months excluded from comparison due to missing/incomplete data.
        total_diff_kwh: Net community consumption difference over comparable months.
        total_pct_change: Overall percentage variation over comparable months.
        max_increase_month: Month with highest consumption increase among complete months.
        max_decrease_month: Month with highest consumption decrease among complete months.
        top_saving_cups: CUPS with largest kWh reduction over comparable months.
        top_increasing_cups: CUPS with largest kWh increase over comparable months.
        cups_comparisons: Full list of individual CUPS comparisons over comparable months.
        cups_monthly_data: Nested mapping: cups -> year -> month -> kWh.
    """

    years: list[int]
    monthly_comparisons: list[MonthComparison]
    annual_totals: dict[int, float]
    comparable_annual_totals: dict[int, float]
    comparable_months: list[int]
    excluded_months: list[int]
    total_diff_kwh: float | None
    total_pct_change: float | None
    max_increase_month: MonthComparison | None
    max_decrease_month: MonthComparison | None
    top_saving_cups: CupsComparison | None
    top_increasing_cups: CupsComparison | None
    cups_comparisons: list[CupsComparison]
    cups_monthly_data: dict[str, dict[int, dict[int, float]]] = field(default_factory=dict)
