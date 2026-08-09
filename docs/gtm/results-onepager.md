# Vaticore: what better forecasts are worth

**Probabilistic load and solar forecasting for mini-grid and C&I solar operators. Fewer litres of diesel, fewer wasted battery cycles, less unserved demand.**

---

## The evidence so far

Vaticore's engine is a probabilistic gradient-boosting model, evaluated with rolling-origin backtests and scored on pinball loss, the metric that rewards a well-calibrated range rather than a lucky average. Every run is measured against a naive baseline ("same as yesterday"). These are current backtest results, not cherry-picked:

| Series | Data | Pinball loss vs baseline |
| --- | --- | --- |
| Site load | Benchmark demand profile | About 40% lower |
| Solar generation | Real solar-resource data (Open-Meteo) | About 18% lower |

Every forecast comes as a range (P10 to P90), so an operator can size battery reserve for the bad day, not just the average one. Pilot data replaces these numbers site by site.

## What that accuracy is worth (illustrative)

Accuracy only matters if it turns into money and fuel. The figures below are an illustrative, deliberately conservative estimate for one representative site, produced by a transparent model (`examples/operator_savings.py`) whose assumptions are all shown and editable. They are an estimate, not a measured result. The real number comes from a shadow-mode pilot on the operator's own site.

**Representative site:** 120 kW average load, 35% of energy from a diesel genset, 0.30 L/kWh fuel intensity, diesel at $1.10/L, a 40% forecast-error reduction, and only 15% of diesel burn assumed to be an uncertainty buffer that better forecasts can shave.

| Illustrative annual impact | Per site | Across a 50-site fleet |
| --- | --- | --- |
| Diesel avoided | About 6,600 litres (roughly 6% of diesel) | About 330,000 litres |
| Money saved | About $7,300 | About $364,000 |
| CO2 avoided | About 18 tonnes | About 887 tonnes |

Change any assumption and the estimate moves with it. That is the point: we hand operators the model, plug in their real site, and then prove it in a pilot.

## Why this is also the affordable, clean-energy play

Every litre of diesel a better forecast avoids is both cheaper for the operator and lower-carbon for the grid it serves. A right-sized battery reserve also means fewer unnecessary cycles, which extends battery life and lowers the lifetime cost of clean power. Vaticore does not build hardware or touch dispatch. It is the forecasting intelligence that makes existing solar-plus-storage mini-grids cheaper to run and cleaner at the same time.

## The boundary

Advisory only. Vaticore forecasts and recommends; a human always decides. We never connect to or control dispatch, and operators keep their data. This is a deliberate safety and liability boundary.

## Next step

We run a small number of free shadow-mode pilots. Share six to twelve months of history for one site and we will forecast its load and solar, score it against your own baseline, and estimate the diesel, cost and CO2 impact in your terms. See the pilot proposal and data checklist alongside this page.
