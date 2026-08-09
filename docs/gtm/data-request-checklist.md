# Pilot data checklist

What we need to run a forecasting pilot on one site. The short version: as much load and generation history as you have, plus where the site is. We handle gaps, odd timestamps, and low-frequency data, so send what you have rather than waiting for it to be perfect.

---

## Essential

- [ ] **Site load history.** Metered demand over time. Six to twelve months is ideal; three is workable.
- [ ] **Solar generation history.** Inverter or meter output for the same period, if the site has solar.
- [ ] **Timestamps.** Any consistent format. Tell us the time zone if it is not in the file.
- [ ] **Resolution.** Whatever you record: 1-minute, 15-minute, hourly, or daily. Just tell us which.
- [ ] **Site location.** Latitude and longitude, or a town name precise enough to fetch weather.

## Helpful, not required

- [ ] Genset fuel logs or runtime hours for the same period (lets us estimate diesel impact directly).
- [ ] Battery capacity (usable kWh) and any charge/discharge logs.
- [ ] Installed solar capacity (kWp) and panel orientation.
- [ ] Known outages or data-quality issues you are already aware of.
- [ ] The site's local currency diesel price, so savings come out in money you recognise.

## Format

- CSV or Excel is perfect. One row per timestamp.
- A minimal file has three columns: `timestamp`, `load_kw`, `generation_kw`. Extra columns are fine; we will map them.
- Missing values: leave them blank. Do not fill or interpolate for us; gap handling is our job and hiding gaps hurts accuracy.
- One file per site, or one file with a site column if you send more than one.

## How to send it securely

- We will share a mutual NDA first.
- Send via a link (your cloud drive) rather than email attachment where possible.
- If any column is sensitive, tell us and we will scope it out.

## What happens next

Once the data lands, you get a first accuracy read within a few days and a full report in about two to three weeks. You keep your data. We run advisory only and touch nothing live.
