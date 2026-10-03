"""Domain models and data structures for aggregated DATADIS energy consumption metrics."""

from dataclasses import dataclass


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
