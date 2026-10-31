# Reference data: Nigeria

Read by `vaticore/sites/nigeria.py`. Context and lookups only: these files
never drive a plan.

| File | What | Source and licence |
|---|---|---|
| `nigeria_states.geojson` | State boundaries (ADM1), simplified for display | geoBoundaries gbOpen NGA ADM1, 2022 (source: GRID3); Runfola, D. et al. (2020), PLoS ONE 15(4): e0231866. CC BY 4.0 |
| `nigeria_states.csv` | For each state: zone, distribution company (DisCo) and electricity regulator (NERC, a state regulator, or a transfer ordered), as reported to August 2025 | Nigeria Energy Atlas v1.0, S. H. Amool (2026), https://shagbaor.com/energy-atlas/. CC BY 4.0 |
| `nigeria_grid_events.csv` | National grid collapses and disturbances, 2022 to 2026, each with its source (NERC quarterly reports from 2024) | Nigeria Energy Atlas v1.0, as above. CC BY 4.0; the cited reports keep their own terms |

The atlas describes its data as indicative, for research and planning
discussion, not for engineering or investment decisions.

Keeping it current: regulator transfers and collapses change. Check each NERC
quarterly report (nerc.gov.ng, "NERC reports") and add new collapses with
their source; update a state's regulator when NERC orders a transfer.
Lagos has two DisCos (Eko and Ikeja Electric) and, since October 2025, new
licensed DisCos alongside them; a Lagos site's DisCo is confirmed with the
operator.
