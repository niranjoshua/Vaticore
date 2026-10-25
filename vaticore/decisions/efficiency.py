"""Efficiency review: how a site should run its generator, from its own history.

Research note 4 found that most of the diesel a site can save is in how its
generator is run, not in the forecast: never start it just because the grid
failed (battery first), and at an off-grid site, run it hard, then off. This
module checks those rules against one site's own recent readings and says
which to adopt, with the litres and money at stake. Advice only.

How:

  - **What the site did:** litres the generator burned, estimated from its
    recorded output (`genset_kw`) through the site's own fuel curve, the same
    one the planner and fuel reconciliation use. Only when enough hours carry
    a reading.
  - **The rules,** replayed hour by hour on the site's actual net load and
    grid record, with the planner's physics:
      * generator whenever the grid is off (grid sites: the commonest
        practice; the comparison when no generator readings exist);
      * battery first: the generator starts only when the battery (and grid)
        would not cover the hour, then follows the load for at least its
        minimum run;
      * battery first, run hard: the same, with the generator loaded to the
        site's charge setpoint (0.8 if none is set) and the surplus charging
        the battery.
  - **Battery wear:** each rule's equivalent full cycles, from the energy it
    draws from the battery. Running hard cycles the battery more. When the
    site's record prices the battery (`battery.replacement_cost` and
    `battery.cycle_life`), each cycle has a cost, and the saving is net of it.
  - **The recommendation:** among the rules with no more outage hours than
    the most reliable one (plus an hour's slack), the cheapest: diesel plus
    priced battery wear, or the fewest litres when wear is not priced. With
    the litres and money it saves against what the site did (or, without
    readings, against the common practice).
  - **Findings straight from the readings:** hours the generator ran at light
    load, and hours it ran while the grid was on.

What it cannot see: a replay knows the actual load and grid, so a rule that
reacts in real time is replayed exactly; the site's real controller and
technicians may react later. The fuel curve is typical, not measured for
each engine (allow 10 to 15%). The battery's starting charge is the first
reading in the window, or half full. Wear is a throughput model: calendar
ageing and depth of discharge are not modelled, and what the site did is
counted from hourly charge readings, which miss cycling within the hour.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from vaticore.decisions.dispatch import SiteAssets, simulate_dispatch
from vaticore.schemas import (
    BATTERY_SOC_PCT,
    GENERATION_KW,
    GENSET_KW,
    GRID_AVAILABLE,
    LOAD_KW,
    TIMESTAMP,
)

if TYPE_CHECKING:  # the site model imports the planner; import it for type hints only
    from vaticore.sites.model import Site

GRID_OFF = "Generator whenever the grid is off"
BATTERY_FIRST = "Battery first"
RUN_HARD = "Battery first, run hard"
RECORDED = "What the site did"

DEFAULT_SETPOINT = 0.8
MIN_COVERAGE = 0.8  # share of hours with readings needed for a fair replay
MIN_DAYS = 7
RUNNING_ABOVE = 0.05  # output above this share of the rating counts as running
LIGHT_LOAD = 0.4  # running below this share of the rating is light load
OUTAGE_SLACK_HOURS = 1.0


@dataclass(frozen=True)
class RuleResult:
    """One way of running the generator over the review window."""

    name: str
    fuel_l: float
    genset_hours: float
    genset_starts: int
    unserved_kwh: float | None  # None: not recorded (what the site did)
    unserved_hours: float | None
    battery_cycles: float | None = None  # equivalent full cycles; None: not known
    wear_cost: float | None = None  # in the site's currency; None: not priced or not known


@dataclass(frozen=True)
class Finding:
    code: str
    text: str
    litres: float


@dataclass(frozen=True)
class EfficiencyReview:
    """What the site's history says about running its generator."""

    operator_id: str
    site_id: str
    start: pd.Timestamp
    end: pd.Timestamp
    currency: str
    price_per_l: float
    coverage: float  # share of hours with load readings
    genset_coverage: float  # share of hours with generator readings
    reference: str | None  # what savings are counted against
    wear_cost_per_kwh: float | None = None  # battery wear per kWh drawn; None: not priced
    results: tuple[RuleResult, ...] = ()
    recommended: str | None = None
    advice: tuple[str, ...] = ()
    findings: tuple[Finding, ...] = ()
    problems: tuple[str, ...] = field(default_factory=tuple)

    def result(self, name: str) -> RuleResult | None:
        return next((r for r in self.results if r.name == name), None)

    @property
    def litres_saved(self) -> float | None:
        """Litres the recommended rule saves against the reference."""
        if self.recommended is None or self.reference is None:
            return None
        best, ref = self.result(self.recommended), self.result(self.reference)
        if best is None or ref is None:
            return None
        return ref.fuel_l - best.fuel_l

    @property
    def extra_wear_cost(self) -> float | None:
        """Battery wear the recommended rule adds against the reference, if both are known."""
        best, ref = self.result(self.recommended or ""), self.result(self.reference or "")
        if best is None or ref is None or best.wear_cost is None or ref.wear_cost is None:
            return None
        return best.wear_cost - ref.wear_cost

    @property
    def money_saved(self) -> float | None:
        """Diesel money saved, net of any extra battery wear that is priced and known."""
        saved = self.litres_saved
        if saved is None:
            return None
        return saved * self.price_per_l - (self.extra_wear_cost or 0.0)

    @property
    def share_saved(self) -> float | None:
        saved, ref = self.litres_saved, self.result(self.reference or "")
        if saved is None or ref is None or ref.fuel_l <= 0:
            return None
        return saved / ref.fuel_l

    def to_dict(self) -> dict[str, object]:
        return {
            "operator_id": self.operator_id,
            "site_id": self.site_id,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "currency": self.currency,
            "price_per_l": self.price_per_l,
            "coverage": self.coverage,
            "genset_coverage": self.genset_coverage,
            "reference": self.reference,
            "wear_cost_per_kwh": self.wear_cost_per_kwh,
            "results": [r.__dict__ for r in self.results],
            "recommended": self.recommended,
            "litres_saved": self.litres_saved,
            "share_saved": self.share_saved,
            "extra_wear_cost": self.extra_wear_cost,
            "money_saved": self.money_saved,
            "advice": list(self.advice),
            "findings": [f.__dict__ for f in self.findings],
            "problems": list(self.problems),
        }

    def to_text(self, timezone: str = "UTC") -> str:
        days = (self.end - self.start) / pd.Timedelta(days=1)
        start = self.start.tz_convert(timezone).strftime("%d %b %Y")
        end = (self.end - pd.Timedelta(seconds=1)).tz_convert(timezone).strftime("%d %b %Y")
        lines = [f"Efficiency review: {self.operator_id}/{self.site_id}, {start} to {end}"]
        if self.problems:
            lines += [f"  Cannot review: {p}" for p in self.problems]
            return "\n".join(lines)
        lines.append(
            f"  {days:.0f} days; load readings {100 * self.coverage:.0f}% of hours, generator "
            f"readings {100 * self.genset_coverage:.0f}%."
        )
        lines.append("")
        priced = self.wear_cost_per_kwh is not None
        wear_head = f" {'wear ' + self.currency:>12s}" if priced else ""
        lines.append(
            f"  {'':42s} {'litres':>9s} {'gen h':>7s} {'starts':>7s} {'outage h':>9s} "
            f"{'cycles/day':>11s}{wear_head}"
        )
        for r in self.results:
            outage = "not seen" if r.unserved_hours is None else f"{r.unserved_hours:,.0f}"
            cycles = "not seen" if r.battery_cycles is None else f"{r.battery_cycles / days:.2f}"
            cell = ""
            if priced:
                cell = " " + ("not seen" if r.wear_cost is None else f"{r.wear_cost:,.0f}").rjust(
                    12
                )
            mark = " <" if r.name == self.recommended else ""
            lines.append(
                f"  {r.name:42s} {r.fuel_l:9,.0f} {r.genset_hours:7,.0f} "
                f"{r.genset_starts:7,d} {outage:>9s} {cycles:>11s}{cell}{mark}"
            )
        saved, share = self.litres_saved, self.share_saved
        if self.recommended and saved is not None and share is not None and saved > 0:
            line = (
                f"  {self.recommended}: {saved:,.0f} L less than {self.reference.lower()} "  # type: ignore[union-attr]
                f"({100 * share:.0f}%, {self.currency} {saved * self.price_per_l:,.0f} of diesel)"
            )
            wear, net = self.extra_wear_cost, self.money_saved
            if wear is not None and net is not None and abs(wear) >= 0.5:
                line += (
                    f"; {'extra' if wear > 0 else 'less'} battery wear {self.currency} "
                    f"{abs(wear):,.0f}; net {self.currency} {net:,.0f}"
                )
            lines += ["", line + "."]
        elif self.recommended:
            lines += ["", "  The site already runs about as well as the rules allow."]
        for a in self.advice:
            lines.append(f"  - {a}")
        for f in self.findings:
            lines.append(f"  * {f.text}")
        if self.reference == RECORDED and self.genset_coverage < 0.98:
            lines.append(
                f"  What the site did counts only the {100 * self.genset_coverage:.0f}% of hours "
                "with generator readings, so it is if anything an underestimate."
            )
        return "\n".join(lines)


def review_efficiency(
    site: Site,
    readings: pd.DataFrame,
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> EfficiencyReview:
    """Review one site's generator use between `start` and `end` (UTC)."""
    hours = pd.date_range(start.ceil("h"), end, freq="1h", inclusive="left", name=TIMESTAMP)
    base = EfficiencyReview(
        operator_id=site.operator_id,
        site_id=site.site_id,
        start=start,
        end=end,
        currency=site.currency,
        price_per_l=site.generator.fuel_price_per_l if site.generator else 0.0,
        coverage=0.0,
        genset_coverage=0.0,
        reference=None,
    )
    if site.generator is None:
        return replace(base, problems=("the site has no generator",))
    if len(hours) < MIN_DAYS * 24:
        return replace(base, problems=(f"the window is shorter than {MIN_DAYS} days",))

    hourly = _hourly(readings, hours)
    load = hourly.get(LOAD_KW, pd.Series(np.nan, index=hours))
    solar = hourly.get(GENERATION_KW, pd.Series(np.nan, index=hours))
    if site.solar is None:
        solar = solar.fillna(0.0)
    net = load - solar
    coverage = float(net.notna().mean())
    genset = hourly.get(GENSET_KW, pd.Series(np.nan, index=hours))
    genset_coverage = float(genset.notna().mean())
    base = replace(base, coverage=coverage, genset_coverage=genset_coverage)

    problems = []
    if coverage < MIN_COVERAGE:
        problems.append(
            f"load (and solar) readings cover {100 * coverage:.0f}% of hours; "
            f"{100 * MIN_COVERAGE:.0f}% is needed"
        )
    has_grid = site.grid is not None and not site.grid.reliable
    grid = None
    if has_grid:
        grid_raw = hourly.get(GRID_AVAILABLE, pd.Series(np.nan, index=hours))
        if grid_raw.notna().mean() < MIN_COVERAGE:
            problems.append(
                f"grid on/off is recorded for {100 * grid_raw.notna().mean():.0f}% of hours; "
                f"{100 * MIN_COVERAGE:.0f}% is needed"
            )
        grid = (grid_raw >= 0.5).astype(float).where(grid_raw.notna())
    elif site.grid is not None:
        grid = pd.Series(1.0, index=hours)  # a reliable grid: always on
    if problems:
        return replace(base, problems=tuple(problems))

    assets = site.dispatch_assets()
    wear = site.battery.wear_cost_per_kwh
    base = replace(base, wear_cost_per_kwh=wear)
    setpoint = assets.genset_charge_setpoint or DEFAULT_SETPOINT
    following = replace(assets, genset_charge_setpoint=None, look_ahead=False)
    hard = replace(following, genset_charge_setpoint=max(setpoint, assets.genset_min_load))
    soc0 = _starting_soc(hourly, assets)
    net_values = net.to_numpy(dtype=float)
    grid_values = None if grid is None else grid.to_numpy(dtype=float)

    results: list[RuleResult] = []
    if has_grid:
        assert grid_values is not None
        off = np.nan_to_num(grid_values, nan=0.0) < 0.5
        results.append(_replay(GRID_OFF, net_values, off, soc0, following, grid_values, wear))
    nothing = np.zeros(len(hours), dtype=bool)
    results.append(_replay(BATTERY_FIRST, net_values, nothing, soc0, following, grid_values, wear))
    if assets.battery_kwh > 0:
        results.append(_replay(RUN_HARD, net_values, nothing, soc0, hard, grid_values, wear))

    recorded = None
    if genset_coverage >= MIN_COVERAGE:
        recorded = _recorded(genset, site, hourly.get(BATTERY_SOC_PCT))
        results.insert(0, recorded)

    rules = [r for r in results if r.name != RECORDED]
    fewest_outages = min(r.unserved_hours or 0.0 for r in rules)
    eligible = [
        r for r in rules if (r.unserved_hours or 0.0) <= fewest_outages + OUTAGE_SLACK_HOURS
    ]
    price = base.price_per_l
    if wear is not None:  # the cheapest: diesel plus battery wear
        best = min(eligible, key=lambda r: r.fuel_l * price + (r.wear_cost or 0.0))
    else:
        best = min(eligible, key=lambda r: r.fuel_l)
    reference = RECORDED if recorded is not None else (GRID_OFF if has_grid else None)
    if (
        wear is not None
        and recorded is not None
        and recorded.wear_cost is not None
        and recorded.fuel_l * price + recorded.wear_cost
        <= best.fuel_l * price + (best.wear_cost or 0.0)
    ):
        return replace(
            base,
            reference=reference,
            results=tuple(results),
            recommended=RECORDED,
            advice=(
                "Once battery wear is priced, how the site runs today costs less than either "
                "rule: keep it. The battery's price and cycle life in the site's record decide "
                "this, so check them.",
            ),
            findings=tuple(_findings(genset, grid, site)),
        )

    worn = _wear_advice(best, eligible, price=price, wear=wear, currency=site.currency)
    advice = _advice(
        best, has_grid=has_grid, setpoint=hard.genset_charge_setpoint, wear_decided=bool(worn)
    )
    advice += worn
    findings = _findings(genset, grid, site) if recorded is not None else []
    return replace(
        base,
        reference=reference,
        results=tuple(results),
        recommended=best.name,
        advice=tuple(advice),
        findings=tuple(findings),
    )


# -- internals -----------------------------------------------------------------


def _hourly(readings: pd.DataFrame, hours: pd.DatetimeIndex) -> dict[str, pd.Series]:
    if readings.empty:
        return {}
    window = readings[
        (readings[TIMESTAMP] >= hours[0])
        & (readings[TIMESTAMP] < hours[-1] + pd.Timedelta(hours=1))
    ]
    cols = [
        c
        for c in (LOAD_KW, GENERATION_KW, GENSET_KW, GRID_AVAILABLE, BATTERY_SOC_PCT)
        if c in window
    ]
    if window.empty or not cols:
        return {}
    frame = window.set_index(TIMESTAMP)[cols].astype(float).resample("1h").mean().reindex(hours)
    return {c: frame[c] for c in cols}


def _starting_soc(hourly: dict[str, pd.Series], assets: SiteAssets) -> float:
    lo, hi = assets.min_soc_kwh, assets.battery_kwh
    soc = hourly.get(BATTERY_SOC_PCT)
    if soc is not None and soc.notna().any():
        first = float(soc.dropna().iloc[0]) / 100.0 * assets.battery_kwh
        return min(max(first, lo), hi)
    return lo + 0.5 * (hi - lo)


def _replay(
    name: str,
    net: np.ndarray,
    planned_on: np.ndarray,
    soc: float,
    assets: SiteAssets,
    grid: np.ndarray | None,
    wear_per_kwh: float | None,
) -> RuleResult:
    """Run the window hour by hour: planned hours, plus a start whenever it would go short."""
    on = np.zeros(net.size, dtype=bool)
    owed = 0
    level = soc
    for i in range(net.size):
        g = None if grid is None else grid[i : i + 1]
        if owed > 0:
            run, owed = True, owed - 1
        elif planned_on[i]:
            run = True
        else:
            trial = simulate_dispatch(
                net[i : i + 1], np.array([False]), soc_kwh=level, assets=assets, grid_available=g
            )
            run = trial.unserved_kwh > 1e-9
            if run:
                owed = assets.genset_min_run_steps - 1
        on[i] = run
        level = simulate_dispatch(
            net[i : i + 1], np.array([run]), soc_kwh=level, assets=assets, grid_available=g
        ).soc_end_kwh
    out = simulate_dispatch(net, on, soc_kwh=soc, assets=assets, grid_available=grid)
    # Each step either charges or discharges, so every fall in charge is energy drawn.
    before = np.concatenate([[soc], out.soc_kwh[:-1]])
    drawn = float(np.clip(before - out.soc_kwh, 0.0, None).sum())
    return RuleResult(
        name=name,
        fuel_l=out.fuel_l,
        genset_hours=out.genset_hours,
        genset_starts=out.genset_starts,
        unserved_kwh=out.unserved_kwh,
        unserved_hours=out.unserved_hours,
        battery_cycles=drawn / assets.battery_kwh if assets.battery_kwh > 0 else None,
        wear_cost=None if wear_per_kwh is None else drawn * wear_per_kwh,
    )


def _recorded(genset: pd.Series, site: Site, soc_pct: pd.Series | None) -> RuleResult:
    """Litres the generator burned, from its recorded output and the site's fuel curve.

    Battery cycles come from the recorded charge, when enough hours carry it:
    every fall from one hour to the next is energy drawn.
    """
    cycles = wear = None
    if soc_pct is not None and soc_pct.notna().mean() >= MIN_COVERAGE:
        kwh = soc_pct / 100.0 * site.battery.usable_kwh
        drawn = float((-kwh.diff()).clip(lower=0.0).sum())  # gaps contribute nothing
        cycles = drawn / site.battery.usable_kwh
        per_kwh = site.battery.wear_cost_per_kwh
        wear = None if per_kwh is None else drawn * per_kwh
    gen = site.generator
    assert gen is not None
    running = (genset > RUNNING_ABOVE * gen.rated_kw).fillna(False)
    litres = np.where(
        running,
        gen.fuel_intercept_l_per_kw_h * gen.rated_kw
        + gen.fuel_slope_l_per_kwh * genset.fillna(0.0),
        0.0,
    )
    starts = int((running & ~running.shift(1, fill_value=False)).sum())
    return RuleResult(
        name=RECORDED,
        fuel_l=float(litres.sum()),
        genset_hours=float(running.sum()),
        genset_starts=starts,
        unserved_kwh=None,
        unserved_hours=None,
        battery_cycles=cycles,
        wear_cost=wear,
    )


def _advice(
    best: RuleResult, *, has_grid: bool, setpoint: float | None, wear_decided: bool = False
) -> list[str]:
    advice = []
    if best.name in (BATTERY_FIRST, RUN_HARD) and has_grid:
        advice.append(
            "Do not start the generator just because the grid failed: let the battery go "
            "first and start the generator only when it reaches its floor (set the automatic "
            "transfer switch or controller to start on low battery, not on grid loss)."
        )
    elif best.name == BATTERY_FIRST:
        advice.append(
            "Start the generator only when the battery reaches its floor, and stop it once the "
            "minimum run is done and the battery and solar can carry the load."
        )
    if best.name == RUN_HARD and setpoint is not None:
        advice.append(
            f"While the generator runs, load it to about {100 * setpoint:.0f}% of its rating "
            "and charge the battery with the surplus (the charge current on the inverter or "
            "hybrid controller), so it runs fewer hours: set generator.charge_setpoint = "
            f"{setpoint:g} in the site's record, if its charger can do this."
        )
    elif best.name == BATTERY_FIRST and not wear_decided:  # wear advice says why instead
        advice.append(
            "Do not run the generator hard to fill the battery: here it saves no diesel"
            + (", because the grid refills the battery for free." if has_grid else ".")
        )
    return advice


def _wear_advice(
    best: RuleResult,
    eligible: list[RuleResult],
    *,
    price: float,
    wear: float | None,
    currency: str,
) -> list[str]:
    """What battery wear changes: a rule it rules out, or that it is not priced."""
    hard = next((r for r in eligible if r.name == RUN_HARD), None)
    if hard is None or hard.battery_cycles is None:
        return []
    first = next((r for r in eligible if r.name == BATTERY_FIRST), None)
    if wear is not None and best.name != RUN_HARD and hard.fuel_l < best.fuel_l:
        diesel = (best.fuel_l - hard.fuel_l) * price
        extra = (hard.wear_cost or 0.0) - (best.wear_cost or 0.0)
        return [
            f"Running the generator hard would burn {best.fuel_l - hard.fuel_l:,.0f} L less "
            f"({currency} {diesel:,.0f}), but the extra battery cycling costs about "
            f"{currency} {extra:,.0f} in wear, more than the diesel it saves: do not."
        ]
    if (
        wear is None
        and best.name == RUN_HARD
        and first is not None
        and first.battery_cycles is not None
        and hard.battery_cycles > first.battery_cycles
    ):
        ratio = hard.battery_cycles / max(first.battery_cycles, 1e-9)
        return [
            f"Running hard cycles the battery about {ratio:.1f} times as much as battery "
            "first. Battery wear is not priced for this site: add battery.replacement_cost "
            "and battery.cycle_life to its record to net the wear off the saving."
        ]
    return []


def _findings(genset: pd.Series, grid: pd.Series | None, site: Site) -> list[Finding]:
    gen = site.generator
    assert gen is not None
    running = (genset > RUNNING_ABOVE * gen.rated_kw).fillna(False)
    burn = pd.Series(
        np.where(
            running,
            gen.fuel_intercept_l_per_kw_h * gen.rated_kw
            + gen.fuel_slope_l_per_kwh * genset.fillna(0.0),
            0.0,
        ),
        index=genset.index,
    )
    findings: list[Finding] = []
    hours = int(running.sum())
    if hours:
        light = running & (genset < LIGHT_LOAD * gen.rated_kw)
        if light.sum() >= max(3, 0.1 * hours):
            findings.append(
                Finding(
                    "light_load",
                    f"The generator ran below {100 * LIGHT_LOAD:.0f}% of its rating in "
                    f"{int(light.sum()):,} of its {hours:,} hours ({100 * light.sum() / hours:.0f}%), "
                    f"burning about {burn[light].sum():,.0f} L there; at light load each kWh "
                    "costs far more diesel.",
                    float(burn[light].sum()),
                )
            )
        if grid is not None:
            both = running & (grid.fillna(0.0) >= 0.5)
            if both.sum() >= 1:
                findings.append(
                    Finding(
                        "ran_with_grid",
                        f"The generator ran in {int(both.sum()):,} hours while the grid was on, "
                        f"burning about {burn[both].sum():,.0f} L "
                        f"({site.currency} {burn[both].sum() * gen.fuel_price_per_l:,.0f}).",
                        float(burn[both].sum()),
                    )
                )
    return findings
