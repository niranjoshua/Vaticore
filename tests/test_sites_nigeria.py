"""Nigerian reference data: where a site is, and national grid collapse days."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from vaticore.pipeline.health import site_health_report
from vaticore.sites import Site
from vaticore.sites.check import Level, check_site
from vaticore.sites.nigeria import (
    _distance_to_ring,
    _inside,
    check_grid_against_collapses,
    grid_events,
    locate,
)

COLLAPSE = date(2026, 1, 23)  # total collapse, NERC 2026 Q1 report


def test_cities_land_in_their_state_with_its_disco_and_regulator() -> None:
    expected = {
        (9.0765, 7.3986): ("FCT", "AEDC", "NERC"),
        (12.0022, 8.5920): ("Kano", "KEDCO", "NERC"),
        (4.8156, 7.0498): ("Rivers", "PHED", "NERC"),
        (6.4584, 7.5464): ("Enugu", "EEDC", "State (EERC)"),
        (6.6018, 3.3515): ("Lagos", "EKEDC/IE", "State (LASERC)"),
    }
    for (lat, lon), (state, disco, regulator) in expected.items():
        area = locate(lat, lon)
        assert area is not None and not area.approximate
        assert (area.state, area.disco, area.regulator) == (state, disco, regulator)
    assert "the FCT" in locate(9.0765, 7.3986).describe()  # type: ignore[union-attr]


def test_positions_outside_nigeria_have_no_state() -> None:
    assert locate(5.0, 4.0) is None  # the Atlantic, inside Nigeria's outline box
    assert locate(5.6037, -0.187) is None  # Accra


def test_point_in_polygon_and_distance_on_a_square() -> None:
    square = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0))
    assert _inside(0.5, 0.5, square) and not _inside(1.5, 0.5, square)
    assert abs(_distance_to_ring(1.03, 0.5, square) - 0.03) < 1e-9


def test_grid_events_are_sourced_and_in_order() -> None:
    events = grid_events()
    assert [e.day for e in events] == sorted(e.day for e in events)
    assert all(e.source_url.startswith("https://") for e in events)
    totals = [e.day for e in grid_events(("Total",))]
    assert COLLAPSE in totals and date(2025, 9, 10) in totals


def _grid_record(off_minutes: int = 0, every: str = "15min") -> pd.DataFrame:
    """A Lagos site's grid record over three local days around the collapse."""
    start = pd.Timestamp("2026-01-22", tz="Africa/Lagos").tz_convert("UTC")
    stamps = pd.date_range(start, periods=3 * 24 * 4, freq="15min")
    grid = np.ones(len(stamps))
    if off_minutes:  # the collapse, from 11:00 local on the day
        local = stamps.tz_convert("Africa/Lagos")
        at = (local.date == COLLAPSE) & (local.hour == 11) & (local.minute < off_minutes)
        grid[at] = 0.0
    frame = pd.DataFrame({"timestamp": stamps, "grid_available": grid, "load_kw": 4.0})
    return frame.iloc[:: {"15min": 1, "1h": 4, "6h": 24}[every]].reset_index(drop=True)


def test_a_record_that_never_saw_the_collapse_is_flagged() -> None:
    (missed,) = check_grid_against_collapses(_grid_record())
    assert missed.day == COLLAPSE and missed.readings == 96


def test_a_record_that_saw_the_collapse_or_is_too_sparse_is_not_flagged() -> None:
    assert check_grid_against_collapses(_grid_record(off_minutes=30)) == []
    assert check_grid_against_collapses(_grid_record(every="6h")) == []  # 4 readings that day
    assert check_grid_against_collapses(pd.DataFrame()) == []


def test_the_health_report_flags_it_only_for_a_nigerian_grid_site() -> None:
    args = {"operator_id": "op", "site_id": "s1", "end": pd.Timestamp("2026-01-25", tz="UTC"),
            "days": 7, "timezone": "Africa/Lagos", "longitude": 3.35, "has_grid": True,
            "has_solar": False, "has_battery": False}  # fmt: skip
    in_lagos = site_health_report(_grid_record(), latitude=6.6, **args)  # type: ignore[arg-type]
    codes = [f.code for f in in_lagos.findings]
    assert "grid_on_in_collapse" in codes
    unknown = site_health_report(_grid_record(), **args)  # type: ignore[arg-type]
    assert "grid_on_in_collapse" not in [f.code for f in unknown.findings]


def _site(**overrides: object) -> Site:
    base: dict[str, object] = {
        "operator_id": "op",
        "site_id": "ikd-01",
        "name": "Ikorodu tower",
        "site_type": "telecom_tower",
        "latitude": 6.6194,
        "longitude": 3.5105,
        "timezone": "Africa/Lagos",
        "currency": "NGN",
        "value_of_lost_load_per_kwh": 5000.0,
        "battery": {"usable_kwh": 20.0, "power_kw": 10.0, "min_soc_kwh": 8.0},
        "generator": {"rated_kw": 15.0, "fuel_price_per_l": 1250.0, "tank_l": 300.0},
        "grid": {"capacity_kw": 10.0, "price_per_kwh": 225.0},
    }
    base.update(overrides)
    return Site(**base)  # type: ignore[arg-type]


def test_site_check_names_the_state_disco_and_regulator() -> None:
    messages = [f.message for f in check_site(_site())]
    assert any("Lagos state" in m and "LASERC" in m for m in messages)
    assert any("more than one DisCo" in m for m in messages)


def test_site_check_warns_about_a_position_in_no_state() -> None:
    findings = check_site(_site(latitude=5.0, longitude=4.0))
    assert any(f.level is Level.WARN and "in no state" in f.message for f in findings)
