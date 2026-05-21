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

## Reproducing the analysis
The full pipeline runs in about two minutes on a recent Mac. Source data is
not committed (large + freely re-downloadable), so step 2 below is required
before the build scripts will work.

### Requirements
- Python 3.10+ (tested on 3.14)
- ~30 MB free disk (≈25 MB raw shapefile + small generated outputs)
- Internet access (for the one-time data download)

### Step 1 — Set up the Python environment
From the project root:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install geopandas matplotlib pandas requests pyogrio shapely \
            folium plotly branca
```

### Step 2 — Download the source shapefile
The MN Geospatial Commons ships a single zip with precinct boundaries joined
to certified 2022 and 2024 election results — the only data file the build
scripts need:
```bash
mkdir -p data
curl -L -o data/sos_results.zip \
  "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_sos/bdry_electionresults_2022_2030/shp_bdry_electionresults_2022_2030.zip"
unzip -o data/sos_results.zip -d data/sos_results
rm data/sos_results.zip
```
After this you should see
`data/sos_results/general_election_results_by_precinct_2024.shp` (and its
sidecar `.dbf`, `.shx`, `.prj` files).

### Step 3 — Regenerate the deliverables
```bash
python3 scripts/make_map.py        # → maps/hd39a_2024_choropleth.png
python3 scripts/make_dashboard.py  # → dashboard/hd39a_dashboard.html
```
Both scripts are idempotent — re-run them anytime new SoS data is published
(the shapefile is updated after each November general election) and the
outputs will refresh automatically.

### Step 4 — View the outputs
```bash
open maps/hd39a_2024_choropleth.png         # macOS Preview
open dashboard/hd39a_dashboard.html         # default browser
```

### Customizing
- **Switch elections:** change `general_election_results_by_precinct_2024.shp`
  to `..._2022.shp` in the two scripts to render the 2022 map.
- **Switch districts:** change `gdf["MNLEGDIST"] == "39A"` to any other
  Minnesota House district code (e.g. `"39B"`, `"60A"`).
- **Switch races:** the shapefile contains columns for U.S. President
  (`USPRSR`, `USPRSDFL`, `USPRSTOTAL`), U.S. Senator (`USSEN*`), U.S. House
  (`USREP*`), MN Senate (`MNSEN*`), and the 2024 constitutional amendment
  (`MNCA1*`). Swap the column names in the scripts to retarget the analysis.

## License
Released under the **MIT License** — see [`LICENSE`](LICENSE). Source data
remains under the licenses of the originating agencies (Census Bureau, MN
Secretary of State, MN Geospatial Commons); see the LICENSE file's data
notice.

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
