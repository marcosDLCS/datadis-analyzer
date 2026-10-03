"""Processing module containing aggregation logic and models."""

from src.processing.aggregator import DataAggregator
from src.processing.models import (
    AnnualPeriodSummary,
    CommunitySummary,
    CupsShare,
    MonthlyPeriodSummary,
)

__all__ = [
    "AnnualPeriodSummary",
    "CommunitySummary",
    "CupsShare",
    "DataAggregator",
    "MonthlyPeriodSummary",
]
