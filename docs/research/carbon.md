# Carbon: how litres become CO2

The website turns litres of diesel into CO2. This note shows every step, so
anyone can check the arithmetic. It is a conversion of published results, not
a study.

## The factor

**2.66 kg of CO2 per litre of diesel burned** (100% mineral diesel, the UK
government's greenhouse gas conversion factors, combustion only). Well-to-tank
emissions (producing and moving the fuel) would add roughly a fifth more; they
are left out, so the figures are conservative. Nigerian diesel varies; the
factor moves little with it.

## Per site, from research note 4

Litres from the held-out year (2018) in `results/diesel_test_*.md`:

| Site | Saved | Litres a year | CO2 a year |
|---|---|---|---|
| Off-grid tower: Vaticore plan against the best-run practice | 7,636 to 6,140 L | 1,496 | 3,979 kg, about **4 t** |
| Weak-grid tower: battery first (Vaticore's plan) against the generator whenever the grid is off | 6,476 to 1,128 L | 5,348 | 14,226 kg, about **14 t** |

These are shaped sites (note 4 explains how); a real site's figure comes from
its own litres.

## A national scenario, not a forecast

GSMA reports that mobile operators and tower companies in Nigeria buy over
40 million litres of diesel a month: about 480 million litres a year. If
those towers cut their diesel by a fifth (about the off-grid result above),
that is 96 million litres a year, or about **255,000 t of CO2 a year**
(96,000,000 x 2.66 kg).

What would change it: the share of towers that adopt, how each runs today
(towers that start the generator on every grid failure can save far more,
towers already well run less), and the real diesel volume, which GSMA gives
as a lower bound.

## Sources

- UK government, greenhouse gas reporting conversion factors (fuels: diesel,
  100% mineral diesel).
- GSMA Mobile for Development, "Why and how mobile operators are looking to
  renewables to power networks across Africa" (Nigerian tower diesel
  purchases).
