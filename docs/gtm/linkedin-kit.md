# LinkedIn kit

For a technical founder, LinkedIn is both your distribution channel and your credibility proof. The goal is not to go viral. It is to be findable and believable to two audiences: operators who might pilot, and investors or grant-makers who might fund. Build in public, show real work, and let the wedge do the talking.

Replace the bracketed parts. Keep your own voice; edit anything that does not sound like you. No em dashes.

---

## 1. Headline (the one line under your name)

Pick one and tune it:

- Building Vaticore: probabilistic load and solar forecasting for mini-grid and C&I operators in Africa
- Founder, Vaticore. Helping distributed energy operators burn less diesel with better forecasts
- Forecasting load and solar for mini-grids and C&I solar, so operators cut fuel, save batteries, and serve more demand

## 2. About section (first person, edit freely)

I build forecasting software for distributed energy operators.

Mini-grid and C&I solar operators make dispatch decisions every day: how much battery to hold, when to run the generator, how much demand to expect. Those calls are usually made on rules of thumb, and a bad one means diesel burned, batteries cycled for nothing, and customers left in the dark.

Vaticore forecasts each site's load and solar generation, as a probability range rather than a single guess, and turns it into a clear battery and generator advisory. It is built for the messy, sparse, low-frequency meter data these operators actually have, not the clean grid data most models assume.

The approach comes out of my benchmarking research on probabilistic time-series forecasting, where an ensemble of a task-adapted language model, gradient boosting, and an LSTM outperformed both classical methods and zero-shot LLM prompting. Vaticore turns that finding into a product for operators in Nigeria and Kenya.

Advisory only, always. We forecast and recommend; a human decides. If you run distributed energy sites and want a free pilot measured in your own cost terms, message me.

## 3. Launch post (the announcement)

I am building Vaticore.

Mini-grid and C&I solar operators in Africa run sites that mix solar, batteries, and a diesel generator. Every day they bet on tomorrow's load and sun. Get the bet wrong and you burn diesel you did not need, cycle the battery for nothing, or leave customers without power.

Most forecasting tools assume clean, dense data. Real operator data is sparse, messy, and sometimes missing entirely for a brand-new site. So I built for that reality instead of around it.

Vaticore forecasts load and solar as a range, not a single number, and turns it into a battery and generator advisory. Every forecast is scored honestly against a naive baseline. If it cannot beat "same as yesterday," it does not ship.

It is advisory only. We never touch dispatch. A human always decides.

I am running a small number of free pilots. If you operate distributed energy sites and have a few months of meter history, I would love to forecast one of your sites and show you the result in litres of diesel, not error metrics.

What would make a forecast genuinely useful for your operation? I am listening.

## 4. Four-week content calendar (two posts a week)

Consistency beats brilliance. Two short posts a week, each about the problem or the build, not about you.

**Week 1**
- Post A: The launch post above.
- Post B: "Why probabilistic beats point forecasts for anyone running a battery." A single number cannot size reserve. Show the P10 to P90 idea with one chart.

**Week 2**
- Post A: "The data operators actually have." Gaps, odd timestamps, low frequency, cold-start sites. Why building for messy data is the moat, not a chore.
- Post B: "What a bad forecast costs." Break it into diesel, battery cycles, and unserved demand. Link the idea to money.

**Week 3**
- Post A: "How we prove a model is real." Rolling-origin backtests against a baseline, pinball loss, no cherry-picking. Show a result.
- Post B: "Advisory, not autopilot." Why we will not touch dispatch early, and why serious operators want it that way.

**Week 4**
- Post A: "Cold start: forecasting a site with no history." The transfer-learning idea, explained plainly.
- Post B: "Forecasting is a climate lever." Every litre of diesel a better forecast avoids is cheaper and cleaner. Tie the mission to the maths.

## 5. Cadence and engagement rules

- Post twice a week, same days, so it becomes a habit.
- Every post ends with a genuine question, then reply to every comment.
- Comment thoughtfully on posts from operators, energy investors, and the mini-grid community (AMDA, GET.invest, sector funds) three times for every one post you publish.
- Share real artifacts: a forecast chart, a backtest result, a lesson learned. Show the work.
- Never post fabricated traction. "Building" is credible. Fake customers are not.
