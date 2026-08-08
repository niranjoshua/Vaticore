# Vaticore: what it takes to build this into a real company

An honest, prioritised plan from "working repo" to "operators paying for it." The order matters more than the dates. You want to go fast, so this is written to be aggressive but realistic. The one thing that cannot be rushed is other people's decisions: an operator handing over data, an investor wiring money. Everything you control, do now.

The guiding rule: **the product is not the bottleneck. Proof and distribution are.** You already have a working, honestly-evaluated engine. Do not add models until a real operator's data demands it.

---

## The six workstreams

Success is not one track. It is six, run in parallel, weighted differently over time.

1. **Proof and pilots** (most important). Turn backtest numbers into a measured result on a real operator's site.
2. **Product and reliability.** Keep the engine correct and make it easy to run a pilot end to end.
3. **Company and legal.** The boring scaffolding that lets you sign a customer and take money.
4. **Brand and distribution.** Website, LinkedIn, a clear story, so people find and believe you.
5. **Funding.** Grants first (non-dilutive, sector-friendly), then angels or a pre-seed once you have a pilot result.
6. **Team.** Stay solo until a pilot forces a second person. Then hire for your biggest gap.

---

## Phase 0: Foundations (weeks 1 to 3)

Everything here is fully in your control. Finish it fast.

- [ ] **Website live.** Merge the Pages workflow, enable GitHub Pages, point a domain (vaticore.com or .energy). Swap the contact to a domain email.
- [ ] **LinkedIn positioned.** Headline, About, launch post, and start the two-posts-a-week cadence (see `linkedin-kit.md`).
- [ ] **Pilot kit ready.** Proposal, outreach templates, data checklist, data-and-trust page (all in this folder).
- [ ] **Company formed.** Register the entity. For raising from international investors later, most African founders use a US Delaware C-corp with a local operating subsidiary in Nigeria or Kenya, but a local company is fine to start. Get an accountant's advice before you incorporate; the structure is hard to change later.
- [ ] **Bank account and basic tooling.** Business email, a place to receive money, simple bookkeeping.
- [ ] **A mutual NDA template.** Operators will not share data without one.
- [ ] **Target list of 40 operators** in Nigeria and Kenya, with a named contact where you can find one.

Exit criterion: you can send a credible operator a link, a proposal, and an NDA the same day they reply.

## Phase 1: First design partner (weeks 3 to 10)

This phase is the whole game. Nothing else matters as much as one operator's real data flowing through your pipeline.

- [ ] **Start 30 discovery conversations.** Your brief's number. Warm intros beat cold email; AMDA (Africa Minigrid Developers Association), GET.invest, and sector investors are faster routes than LinkedIn DMs.
- [ ] **Listen more than you pitch.** Learn how they forecast today, what a bad forecast costs them, and who owns the data.
- [ ] **Convert one to a free shadow-mode pilot.** One site, six to twelve months of history, success metric agreed in writing in their currency.
- [ ] **Run your existing pipeline on their data.** Expect it to break in new ways. That is the point; messy real data is your moat.
- [ ] **Produce a results one-pager in their terms.** Diesel, battery cycles, unserved energy, and CO2. Use `operator_savings.py` as the model, then replace the estimate with the measured number.

Exit criterion: one real operator, one measured result, one reference you can name (even anonymised).

## Phase 2: From pilot to product (weeks 8 to 20, overlapping)

Now you harden what the pilot exposed and turn a favour into a paid relationship.

- [ ] **Move from batch to rolling intraday forecasts** for the pilot site (your brief's staged autonomy step 2).
- [ ] **Anomaly and data-quality monitoring**, because real feeds break and you need to notice before the operator does.
- [ ] **A clean per-operator onboarding path**, so the second pilot takes days, not weeks.
- [ ] **Turn the free pilot into a paid pilot or a subscription.** Price it against value: a fraction of the diesel and battery savings you can show. Per-site-per-month is the simplest model operators understand.
- [ ] **Second and third design partners**, using the first result as proof.
- [ ] **Only now** consider the LSTM, TIME-LLM, and ensemble, and only if a real site's data shows the GBM leaving accuracy on the table. Cold-start via transfer learning is the highest-value model work because new sites are where forecasting matters most.

Exit criterion: at least one operator paying, and a repeatable way to onboard the next.

## Phase 3: Fundable and repeatable (months 5 to 12)

- [ ] **Raise, if you want to.** With a measured pilot result and one paying operator, you can raise a pre-seed or win a larger climate or energy-access grant. Grants first: they are non-dilutive and this sector has real grant capital (GET.invest, catalytic funds, energy-access programmes).
- [ ] **First hire** for your biggest gap. If that is sales and operator relationships, hire there, not another engineer.
- [ ] **Tighten the metric that wins pilots**: express everything in operator currency, and publish an honest case study.
- [ ] **Consider a short research paper** from your backtests and pilot. It doubles as credibility and as marketing in this technical buyer market.

Exit criterion: a repeatable pilot-to-paid motion and enough runway to run it.

---

## What to say no to (so you actually get there)

- No closed-loop control. Advisory only. This is a safety and liability line, not a roadmap item.
- No building or financing hardware mini-grids. You are the intelligence layer, not the asset owner.
- No new markets beyond Nigeria and Kenya until the wedge works in one.
- No model complexity before a real site's data asks for it.
- No React front end, no mobile app, no billing platform before a paying pilot.

## An honest note on speed

You can compress Phase 0 into two weeks by working hard, because it is all in your control. Phase 1 depends on operators, and enterprise energy sales are slow: expect weeks of conversations before one says yes, and more before their data actually arrives. Do not confuse being busy on the product with progress. Progress in Phase 1 is measured in conversations had and data received, not commits pushed.

The fastest path to a real company is not more code. It is one operator, one dataset, one measured result, told clearly.
