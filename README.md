# Minnesota House District 39A — Demographic & Electoral Analysis

Project archive of the demographic and voting-pattern analysis for MN House
District 39A (Fridley, Spring Lake Park slice, Columbia Heights slice, Hilltop)
in Anoka County.

## Repository layout
```
.
├── README.md                  this file
├── report/
│   └── FINAL_REPORT.md        full written report
├── dashboard/
│   └── hd39a_dashboard.html   interactive Plotly + Folium dashboard
├── maps/
│   └── hd39a_2024_choropleth.png   static precinct choropleth
├── scripts/
│   ├── make_map.py            regenerates the static PNG map
│   └── make_dashboard.py      regenerates the interactive HTML dashboard
└── data/                      raw shapefiles (gitignored)
    ├── sos_results/           MN SoS precinct boundaries + results 2022 & 2024
    └── mn_vtd_2020/           Census TIGER 2020 VTDs (backup)
```

## Reproducing the deliverables
The Python environment lives in `.venv/` (gitignored). To recreate it:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install geopandas matplotlib pandas requests pyogrio shapely \
            folium plotly branca
```
Then re-run either build script from the project root:
```bash
python3 scripts/make_map.py        # → maps/hd39a_2024_choropleth.png
python3 scripts/make_dashboard.py  # → dashboard/hd39a_dashboard.html
```

## Headline findings
- **Demographics:** ~30,200 residents, median age 34.7, median HH income
  $77,680. Non-White share rose from 28 % (2010) to 45.4 % (2024); Black
  population doubled, Hispanic +116 %.
- **Vote 2024:** Erin Koegel (DFL) **63.3 %**, Rod Sylvester (R) 36.4 %,
  margin D +27.0 pp on 18,555 ballots.
- **Geography:** all 16 precincts went DFL; strongest in Columbia Heights P-8
  (69.2 %) and Fridley W-1 P-3 (68.9 %); weakest in Spring Lake Park P-1R
  (56.0 %) and P-2 (56.1 %).
- **Trend:** seat realigned from D+13 (2012) → D+27 (2018) and has held there.

See `report/FINAL_REPORT.md` for the full analysis.

## Data sources
- U.S. Census Bureau ACS 2020-2024 5-year and 2024 1-year estimates
- U.S. Census Bureau 2020 Decennial PL 94-171
- Minnesota Secretary of State certified 2022 & 2024 General Election precinct
  results
- MN Geospatial Commons "General Election Results by Precinct, 2022-2030"
  shapefile
- Ballotpedia HD 39A and HD 41B pages
- Anoka County Abstract of Votes Cast (Nov 8, 2022)
