"""Where a Nigerian site is, who supplies its grid, and the days the national grid fell.

Two uses:

  - **Locate a site.** Its latitude and longitude give its state, then the
    state's distribution company (DisCo) and electricity regulator (NERC or,
    since the Electricity Act 2023, a state regulator). Site check reports
    it, catches a position that is inside Nigeria's box but in no state, and
    the grid evidence work adds supply hours up by DisCo and regulator.
  - **Check a grid record against national collapses.** On the day of a total
    national grid collapse every grid-connected site lost the grid, if only
    for minutes. A site whose record shows the grid on through every reading
    of such a day is probably reading the wrong signal (the inverter's output,
    not the grid). The data health report flags it.

The data are in `reference/` with their sources and licences (CC BY 4.0,
credit the Nigeria Energy Atlas and geoBoundaries). They are context and
lookups only: nothing here drives a plan.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path

import pandas as pd

_REFERENCE = Path(__file__).parent / "reference"
NEAREST_TOLERANCE_DEG = 0.05  # about 5 km: the simplified borders leave slivers between states
SOURCE = "Nigeria Energy Atlas (S. H. Amool, 2026) and geoBoundaries, CC BY 4.0"


@dataclass(frozen=True)
class NigerianArea:
    """The state a position is in, and who supplies and regulates its grid."""

    state: str
    zone: str
    disco: str
    disco_name: str
    regulator: str  # "NERC", a state regulator, or "Transfer ordered"
    approximate: bool = False  # True: just outside the simplified border, nearest state

    def describe(self) -> str:
        where = "the FCT" if self.state == "FCT" else f"{self.state} state"
        where += f" ({self.zone})"
        if self.approximate:
            where += ", nearest state to a point just outside the simplified border"
        regulator = "a state regulator" if self.regulator == "State" else self.regulator
        return (
            f"{where}; the state's DisCo: {self.disco_name} (areas near a border can be "
            f"served by a neighbour); electricity regulator: {regulator} (as reported to "
            "August 2025)"
        )


@dataclass(frozen=True)
class GridEvent:
    day: date  # local (Africa/Lagos) date
    kind: str  # Total, Partial, Collapse (unclassified), Disturbance, Disputed
    notes: str
    source_url: str


@dataclass(frozen=True)
class CollapseCheck:
    """A total national collapse day on which the site's record never showed the grid off."""

    day: date
    readings: int
    notes: str
    source_url: str


def locate(latitude: float, longitude: float) -> NigerianArea | None:
    """The Nigerian state at a position, with its DisCo and regulator; None if outside."""
    states = _states()
    for name, ring in _boundaries():
        if _inside(longitude, latitude, ring):
            return _area(states, name, approximate=False)
    best, best_distance = None, math.inf
    for name, ring in _boundaries():
        distance = _distance_to_ring(longitude, latitude, ring)
        if distance < best_distance:
            best, best_distance = name, distance
    if best is not None and best_distance <= NEAREST_TOLERANCE_DEG:
        return _area(states, best, approximate=True)
    return None


def grid_events(kinds: tuple[str, ...] | None = None) -> list[GridEvent]:
    """National grid events, oldest first; optionally only some kinds (e.g. ("Total",))."""
    events = _events()
    return [e for e in events if kinds is None or e.kind in kinds]


def check_grid_against_collapses(
    readings: pd.DataFrame,
    *,
    timezone: str = "Africa/Lagos",
    min_readings: int = 12,
) -> list[CollapseCheck]:
    """Total-collapse days on which a site's grid record was on at every reading.

    readings: the site's raw rows with `timestamp` (UTC) and `grid_available`.
    A day counts only if it has at least `min_readings` grid readings, so a
    sparse record is not flagged. One reading off, however brief, clears it.
    """
    if readings.empty or "grid_available" not in readings:
        return []
    grid = readings[["timestamp", "grid_available"]].dropna()
    if grid.empty:
        return []
    local_day = pd.to_datetime(grid["timestamp"], utc=True).dt.tz_convert(timezone).dt.date
    by_day = grid.groupby(local_day)["grid_available"]
    counts, lowest = by_day.size(), by_day.min()
    flagged = []
    for event in grid_events(("Total",)):
        if (
            event.day in counts.index
            and counts[event.day] >= min_readings
            and float(lowest[event.day]) >= 0.5
        ):
            flagged.append(
                CollapseCheck(event.day, int(counts[event.day]), event.notes, event.source_url)
            )
    return flagged


# -- internals -----------------------------------------------------------------


def _area(states: dict[str, dict[str, str]], name: str, *, approximate: bool) -> NigerianArea:
    row = states[name]
    return NigerianArea(
        state=name,
        zone=row["zone"],
        disco=row["disco"],
        disco_name=row["disco_name"],
        regulator=row["regulator"],
        approximate=approximate,
    )


@cache
def _states() -> dict[str, dict[str, str]]:
    with open(_REFERENCE / "nigeria_states.csv", encoding="utf-8") as fh:
        return {row["state"]: row for row in csv.DictReader(fh)}


@cache
def _boundaries() -> tuple[tuple[str, tuple[tuple[float, float], ...]], ...]:
    data = json.loads((_REFERENCE / "nigeria_states.geojson").read_text(encoding="utf-8"))
    out = []
    for feature in data["features"]:
        geometry = feature["geometry"]
        polygons = (
            [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
        )
        for polygon in polygons:  # the outer ring of each part; the states have no holes
            ring = tuple((float(x), float(y)) for x, y in polygon[0])
            out.append((feature["properties"]["name"], ring))
    return tuple(out)


@cache
def _events() -> tuple[GridEvent, ...]:
    with open(_REFERENCE / "nigeria_grid_events.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return tuple(
        GridEvent(date.fromisoformat(r["date"]), r["type"], r["notes"], r["source_url"])
        for r in sorted(rows, key=lambda r: r["date"])
    )


def _inside(x: float, y: float, ring: tuple[tuple[float, float], ...]) -> bool:
    """Ray casting: a point is inside if a ray to its right crosses the ring an odd count."""
    inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def _distance_to_ring(x: float, y: float, ring: tuple[tuple[float, float], ...]) -> float:
    """Shortest distance in degrees from a point to the ring's edges (fine at this scale)."""
    best = math.inf
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        length = dx * dx + dy * dy
        t = 0.0 if length == 0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / length))
        px, py = x1 + t * dx, y1 + t * dy
        best = min(best, math.hypot(x - px, y - py))
    return best
