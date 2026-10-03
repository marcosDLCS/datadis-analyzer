"""Tests for community energy data aggregation and share calculation logic."""

from pathlib import Path

import pytest

from src.ingestion.loader import DatadisLoader
from src.processing.aggregator import DataAggregator


def test_aggregator_annual_shares_sum_to_100(sample_input_hierarchy: Path) -> None:
    """The sum of CUPS percentage shares for any year must equal 100%."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    summary = DataAggregator.aggregate_community(df)

    # Check 2024:
    # cups1: 10 + 20 = 30 kWh
    # cups2: 30 + 40 = 70 kWh
    # total: 100 kWh
    # cups1 share = 30.00%, cups2 share = 70.00%
    summary_2024 = summary.annual_summaries[2024]
    assert summary_2024.community_total_kwh == pytest.approx(100.0)
    assert len(summary_2024.cups_shares) == 2

    # Top consumer is cups2
    assert summary_2024.top_consumer.cups == "ES0021000000000002BB"
    assert summary_2024.top_consumer.share_pct == pytest.approx(70.0)

    # Lowest consumer is cups1
    assert summary_2024.lowest_consumer.cups == "ES0021000000000001AA"
    assert summary_2024.lowest_consumer.share_pct == pytest.approx(30.0)

    total_shares = sum(s.share_pct for s in summary_2024.cups_shares)
    assert total_shares == pytest.approx(100.0)


def test_aggregator_monthly_shares_and_timeline(sample_input_hierarchy: Path) -> None:
    """Monthly summaries must compute correct period totals and identify peak months."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    summary = DataAggregator.aggregate_community(df)

    # 2024 has months 05 and 06:
    # 2024-05: cups1=10, cups2=30 -> total 40 kWh (cups2 share = 75%)
    # 2024-06: cups1=20, cups2=40 -> total 60 kWh (cups2 share = 66.67%)
    # 2025-01: cups1=50, cups2=50 -> total 100 kWh (50% each)
    assert len(summary.monthly_summaries) == 3

    m_2024_05 = next(m for m in summary.monthly_summaries if m.period_label == "2024-05")
    assert m_2024_05.community_total_kwh == pytest.approx(40.0)
    top_cups = m_2024_05.top_consumer
    assert top_cups.cups == "ES0021000000000002BB"
    assert top_cups.share_pct == pytest.approx(75.0)

    # Peak month across all data is 2025-01 (100 kWh) or 2024-06 (60 kWh)
    assert summary.peak_month_label == "2025-01"
    assert summary.peak_month_kwh == pytest.approx(100.0)
    assert summary.lowest_month_label == "2024-05"
    assert summary.lowest_month_kwh == pytest.approx(40.0)


def test_aggregator_build_monthly_pivot(sample_input_hierarchy: Path) -> None:
    """Aggregator should generate a clean pivot table indexed by CUPS."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    pivot_2024 = DataAggregator.build_monthly_pivot(df, year=2024)

    assert not pivot_2024.empty
    assert "Total_kWh" in pivot_2024.columns
    assert "Share_%" in pivot_2024.columns
    assert pivot_2024.loc["ES0021000000000002BB", "Total_kWh"] == pytest.approx(70.0)
    assert pivot_2024.loc["ES0021000000000002BB", "Share_%"] == pytest.approx(70.0)
