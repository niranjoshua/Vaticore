# Vaticore in full: what we are building, and for whom

A single, plain-language reference for what Vaticore is. Use it to brief a new hire, an investor, or yourself on a foggy morning. No jargon, no em dashes.

---

## In one sentence

Vaticore forecasts how much electricity a distributed energy site will use and how much its solar will generate, as a probability range, and turns that into a clear call on how much battery to hold and when to run the generator, so operators burn less diesel, waste fewer battery cycles, and leave less demand unserved.

## The problem

Mini-grid and commercial-and-industrial (C&I) solar operators run sites that combine solar panels, battery storage, and often a diesel generator. Every single day, someone has to decide:

- How much to charge the battery.
- How much reserve to hold back for later.
- When to lean on the diesel generator.
- How much demand to expect.

Today those decisions are made on weak forecasts or rules of thumb. The cost of getting them wrong is concrete and measurable:

- **Diesel burned** that better planning would have avoided. Fuel is the single largest running cost at most of these sites.
- **Batteries cycled** unnecessarily, shortening expensive battery life.
- **Unserved demand**, meaning customers lose power, and the operator loses revenue and trust.

There is a second, harder problem specific to these markets. The data is bad. Metering is often sparse, low-frequency, and messy, and a brand-new site has no operating history at all. Any forecasting system that assumes clean, dense, long-history data simply does not work here. Handling imperfect data is the core requirement, not an edge case.

## The solution

Vaticore is a multi-tenant, multi-site forecasting service with three layers.

1. **The forecasting engine.** It ingests each site's historical and live load and generation data, tolerates the gaps and irregularities in real operator feeds, and produces a probabilistic forecast: not a single guessed number, but a calibrated range (for example P10, P50, P90) for both electricity demand and solar generation.
2. **The decision layer.** It translates the forecast into an operational recommendation: how much battery reserve to hold, whether to plan generator runtime, and how much demand might go unserved, each with an uncertainty range.
3. **The dashboard.** It shows forecast versus actual, the uncertainty band, and the recommendation, per site and across a fleet.

Three commitments make this a real product rather than a science project:

- **Probabilistic, not point forecasts.** You cannot size a battery reserve or decide whether to run a generator from a single number. You need the range of likely outcomes, including the bad day. We output quantiles and evaluate on the metrics that reward honest ranges.
- **Honest evaluation, always.** Every forecast is scored against a naive baseline ("same as yesterday") on the operator's own history. If a model cannot beat that, we say so. No cherry-picked numbers.
- **Advisory, never control.** Vaticore forecasts and recommends. A human always decides. We never connect to or automate dispatch. This is a deliberate safety and liability boundary.

There is also a hard part we are built for: **cold start.** A brand-new site has no history, which is exactly when a good forecast is most valuable. The engine is designed to produce useful forecasts for a new site by transferring from similar sites, then adapt as local data arrives.

## The strategy

- **Win a narrow wedge first.** Short-term load and solar forecasting for mini-grid and C&I solar operators in Nigeria and Kenya. Say no to everything else until this works.
- **Sell one measurable promise.** Lower fuel and battery costs through better forecasts, proven in the operator's own currency: litres of diesel, battery cycles, kWh unserved, and tonnes of CO2.
- **Land design partners with free shadow-mode pilots.** Run alongside the operator's existing process, touch nothing, prove the number, then convert to paid.
- **Prove before you scale.** One operator, one dataset, one measured result, told clearly, is worth more than five half-built models or ten cold pitches.
- **Grow from evidence.** Use the first result to win the next pilot, to raise non-dilutive grant capital, and only then to raise from investors.
- **Be the intelligence layer, not the hardware.** We do not build or finance mini-grids. We make the ones that exist cheaper to run and cleaner at the same time. That is both the business and the climate impact, and they are the same thing.

## The customers we can serve

The wedge is deliberately narrow, but the ground under it is large. In order of priority:

1. **Mini-grid operators** (primary). Companies running fleets of solar-battery-diesel mini-grids serving villages, towns, and rural businesses. They own their metering data, run many sites, and live or die on fuel cost. This is the sharpest fit.
2. **C&I solar-plus-storage operators** (primary). Companies that build and run on-site solar and storage for commercial and industrial customers (factories, telecoms towers, malls, farms). They need to forecast on-site generation against building load.
3. **Telecom tower power operators** (adjacent). Towers run on solar, battery, and diesel, exactly the mix Vaticore forecasts. A natural early expansion.
4. **Energy-as-a-service and asset-management providers** (adjacent). Firms that manage distributed assets for others and need forecasting across a portfolio.
5. **Later, and deliberately out of scope for now:** grid-scale utility forecasting, developed-market operators, and closed-loop optimisation. Note the ideas, keep building the wedge.

Within primary customers, the buyers are the operations and data leads: Head of Operations, Head of Data or Analytics, VP Engineering, and asset-management teams. They think in fuel and uptime, not machine-learning error.

## What a customer actually gets

Concretely, when an operator works with Vaticore, they receive:

- **A per-site probabilistic forecast** of load and solar generation, day ahead and updated intraday, expressed as a range so they can plan for the likely case and the bad case.
- **A battery-reserve and generator advisory** for each site, with an uncertainty range, that tells them how much to hold back and whether to plan generator runtime.
- **An honest accuracy report**, scored against their own baseline on their own history, so they can trust the numbers rather than take them on faith.
- **Results in their own language:** estimated litres of diesel avoided, battery cycles saved, kWh of unserved energy reduced, and tonnes of CO2 avoided, not error metrics.
- **A dashboard** showing forecast versus actual, the uncertainty band, and the recommendation, per site and across their fleet.
- **A safe boundary:** advisory only, their data stays theirs, and a human always makes the final call.

In short: they get a forecast they can trust and act on, in terms they already use, that pays for itself in fuel and battery savings, and helps them keep the lights on for more customers with less diesel.
