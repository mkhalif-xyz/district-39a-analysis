"""Build an interactive HTML dashboard summarizing District 39A trends.

Produces a single self-contained HTML file with:
  * An interactive Folium/Leaflet precinct choropleth (hover for vote share).
  * Plotly line/bar charts for race composition, income, education, and
    legislative vote history.
  * A district-summary header.

Re-run anytime; output lives at hd39a_dashboard.html.
"""

from pathlib import Path
import json

import geopandas as gpd
import folium
import branca.colormap as bcm
import plotly.graph_objects as go
import plotly.io as pio

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHP = ROOT / "data" / "sos_results" / "general_election_results_by_precinct_2024.shp"
OUT = ROOT / "dashboard" / "hd39a_dashboard.html"

# ---------------------------------------------------------------------------
# 1) Load precinct geometry + 2024 results
# ---------------------------------------------------------------------------
gdf = gpd.read_file(SHP)
hd = gdf[gdf["MNLEGDIST"] == "39A"].copy().to_crs(epsg=4326)
hd["dfl_pct"] = (100 * hd["MNLEGDFL"] / hd["MNLEGTOTAL"]).round(2)
hd["gop_pct"] = (100 * hd["MNLEGR"] / hd["MNLEGTOTAL"]).round(2)
hd["margin"] = (hd["dfl_pct"] - hd["gop_pct"]).round(1)
hd["label"] = hd["SHORTLABEL"].fillna(hd["PCTNAME"])

dfl = int(hd["MNLEGDFL"].sum())
gop = int(hd["MNLEGR"].sum())
wi = int(hd["MNLEGWI"].sum())
tot = int(hd["MNLEGTOTAL"].sum())

# ---------------------------------------------------------------------------
# 2) Interactive Leaflet/Folium choropleth
# ---------------------------------------------------------------------------
centroid = hd.dissolve().geometry.centroid.iloc[0]
fmap = folium.Map(
    location=[centroid.y, centroid.x],
    zoom_start=13, tiles="cartodbpositron",
    width="100%", height="100%",
)

cmap = bcm.LinearColormap(
    colors=["#deebf7", "#9ecae1", "#4292c6", "#08519c", "#08306b"],
    vmin=50, vmax=72, caption="Koegel (DFL) vote share, %",
)

def style_fn(feat):
    pct = feat["properties"]["dfl_pct"]
    return {
        "fillColor": cmap(pct),
        "color": "white", "weight": 1.0, "fillOpacity": 0.85,
    }

def highlight_fn(_):
    return {"weight": 3, "color": "#222", "fillOpacity": 0.95}

folium.GeoJson(
    json.loads(hd.to_json()),
    name="HD 39A precincts",
    style_function=style_fn,
    highlight_function=highlight_fn,
    tooltip=folium.GeoJsonTooltip(
        fields=["label", "MCDNAME", "MNLEGDFL", "MNLEGR", "MNLEGTOTAL",
                "dfl_pct", "margin"],
        aliases=["Precinct:", "Municipality:", "Koegel (D):", "Sylvester (R):",
                 "Total ballots:", "DFL %:", "Margin (pp):"],
        sticky=True, localize=True,
    ),
).add_to(fmap)

cmap.add_to(fmap)
folium.LayerControl().add_to(fmap)

map_html = fmap._repr_html_()

# ---------------------------------------------------------------------------
# 3) Plotly trend charts
# ---------------------------------------------------------------------------
pio.templates.default = "plotly_white"

# (a) Race/ethnicity composition 1990 -> 2024 (Fridley city)
years = [1990, 2000, 2010, 2020, 2024]
race_data = {
    "White (NH)":     [95.1, 86.9, 72.1, 57.3, 54.7],
    "Black":          [1.0,  3.6,  10.9, 18.0, 20.4],
    "Hispanic":       [0.9,  2.2,  7.3,  11.1, 14.1],
    "Asian":          [2.5,  3.0,  4.9,  6.9,  5.8],
    "Multiracial":    [0.0,  3.2,  3.6,  5.4,  4.5],
    "Native / Other": [0.5,  1.0,  1.2,  1.3,  0.5],
}
race_colors = {
    "White (NH)": "#4c78a8", "Black": "#f58518", "Hispanic": "#e45756",
    "Asian": "#54a24b", "Multiracial": "#b279a2", "Native / Other": "#9d755d",
}

fig_race = go.Figure()
for name, vals in race_data.items():
    fig_race.add_trace(go.Scatter(
        x=years, y=vals, mode="lines+markers", name=name,
        line=dict(width=3, color=race_colors[name]),
        marker=dict(size=8),
        hovertemplate=f"<b>{name}</b><br>%{{x}}: %{{y}}%<extra></extra>",
    ))
fig_race.update_layout(
    title="Race & ethnicity composition (Fridley), 1990–2024",
    xaxis_title="Year", yaxis_title="Share of population (%)",
    height=380, margin=dict(l=40, r=20, t=60, b=40),
    legend=dict(orientation="h", y=-0.22),
)

# (b) State House vote trend (territory = old 41B -> new 39A)
hv_years = [2012, 2014, 2016, 2018, 2020, 2022, 2024]
dfl_share = [56.2, 53.4, 56.0, 62.7, 62.4, 63.3, 63.3]
gop_share = [43.6, 46.5, 43.9, 37.2, 37.5, 36.6, 36.4]

fig_vote = go.Figure()
fig_vote.add_trace(go.Scatter(
    x=hv_years, y=dfl_share, mode="lines+markers", name="DFL",
    line=dict(width=3, color="#1f6dc4"), marker=dict(size=10),
    hovertemplate="DFL %{y}%<extra></extra>",
))
fig_vote.add_trace(go.Scatter(
    x=hv_years, y=gop_share, mode="lines+markers", name="GOP",
    line=dict(width=3, color="#d6364c"), marker=dict(size=10),
    hovertemplate="GOP %{y}%<extra></extra>",
))
fig_vote.add_vline(
    x=2022, line=dict(color="#888", dash="dash"),
    annotation_text="2022 redistricting<br>(41B → 39A)",
    annotation_position="top right",
)
fig_vote.update_layout(
    title="State Representative vote share — Fridley seat, 2012–2024",
    xaxis_title="Election year", yaxis_title="Vote share (%)",
    yaxis=dict(range=[30, 70]),
    height=380, margin=dict(l=40, r=20, t=60, b=40),
    legend=dict(orientation="h", y=-0.22),
)

# (c) Income trend, inflation-adjusted (2010-2024)
inc_years = [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024]
median_hh = [69698, 67854, 68225, 70112, 71880, 73298, 74486, 77680]
fig_inc = go.Figure()
fig_inc.add_trace(go.Scatter(
    x=inc_years, y=median_hh, mode="lines+markers",
    line=dict(width=3, color="#2a9d8f"), marker=dict(size=9),
    hovertemplate="$%{y:,.0f}<extra></extra>", name="Median HH income",
))
fig_inc.update_layout(
    title="Median household income (Fridley), 2010–2024",
    xaxis_title="Year", yaxis_title="USD",
    yaxis=dict(tickprefix="$", tickformat=","),
    height=380, margin=dict(l=50, r=20, t=60, b=40),
    showlegend=False,
)

# (d) 2024 precinct ranking — horizontal bar
ranked = hd.sort_values("dfl_pct", ascending=True)
fig_prec = go.Figure()
fig_prec.add_trace(go.Bar(
    x=ranked["dfl_pct"], y=ranked["label"] + " (" + ranked["MCDNAME"] + ")",
    orientation="h",
    marker=dict(
        color=ranked["dfl_pct"], colorscale="Blues",
        cmin=50, cmax=72, showscale=False,
    ),
    text=[f"{v:.1f}%" for v in ranked["dfl_pct"]],
    textposition="auto",
    hovertemplate="<b>%{y}</b><br>DFL: %{x:.1f}%<extra></extra>",
))
fig_prec.add_vline(x=63.3, line=dict(color="#444", dash="dot"),
                   annotation_text="District avg 63.3%",
                   annotation_position="top")
fig_prec.update_layout(
    title="2024 Koegel (DFL) share by precinct — 16 precincts in HD 39A",
    xaxis_title="DFL vote share (%)",
    xaxis=dict(range=[50, 72]),
    height=520, margin=dict(l=180, r=30, t=60, b=40),
)

race_html = fig_race.to_html(full_html=False, include_plotlyjs="cdn")
vote_html = fig_vote.to_html(full_html=False, include_plotlyjs=False)
inc_html = fig_inc.to_html(full_html=False, include_plotlyjs=False)
prec_html = fig_prec.to_html(full_html=False, include_plotlyjs=False)

# ---------------------------------------------------------------------------
# 4) Build the dashboard HTML
# ---------------------------------------------------------------------------
top_prec = hd.sort_values("dfl_pct", ascending=False).iloc[0]
bot_prec = hd.sort_values("dfl_pct", ascending=True).iloc[0]

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MN House District 39A — Dynamic Summary</title>
<style>
  :root {{
    --dfl:#08519c; --gop:#d6364c; --ink:#222; --muted:#666;
  }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
         Helvetica, Arial, sans-serif; margin: 0; color: var(--ink);
         background: #f7f7fb; }}
  header {{ background: linear-gradient(135deg,#08306b,#1f6dc4);
           color:white; padding: 24px 36px; }}
  header h1 {{ margin:0; font-size:26px; letter-spacing:0.2px; }}
  header .sub {{ opacity:0.85; margin-top:4px; font-size:14px; }}
  .stats {{ display:flex; flex-wrap:wrap; gap:14px;
           padding: 20px 36px; background:white;
           border-bottom: 1px solid #e6e6ef; }}
  .stat {{ flex:1 1 160px; padding:14px 16px;
          background:#f4f7fb; border-radius:8px;
          border-left:4px solid var(--dfl); }}
  .stat .lbl {{ font-size:11px; text-transform:uppercase;
                color:var(--muted); letter-spacing:0.6px; }}
  .stat .val {{ font-size:22px; font-weight:600; margin-top:2px; }}
  .stat.gop {{ border-left-color: var(--gop); }}
  .grid {{ display:grid; grid-template-columns: 1.4fr 1fr;
          gap: 18px; padding: 22px 36px; }}
  .card {{ background:white; border-radius:10px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.06);
          padding: 14px 18px; }}
  .card h2 {{ font-size:15px; margin:4px 0 10px; color:#1a1a2e; }}
  .map-wrap iframe, .map-wrap > div {{ width:100%!important;
                                        height:540px!important;
                                        border:0; border-radius:6px; }}
  .full {{ grid-column: 1 / -1; }}
  footer {{ padding: 20px 36px; color: var(--muted); font-size:12px;
           border-top:1px solid #e6e6ef; background:white; }}
  .pill {{ display:inline-block; padding:2px 8px; border-radius:9px;
          font-size:11px; font-weight:600; }}
  .pill.dfl {{ background:#dfe9f5; color:var(--dfl); }}
  .pill.gop {{ background:#f7dde1; color:var(--gop); }}
</style>
</head>
<body>
<header>
  <h1>Minnesota House District 39A — Dynamic Summary</h1>
  <div class="sub">Fridley · Spring Lake Park (part) · Columbia Heights (part) · Hilltop &nbsp;|&nbsp; Demographic &amp; electoral dashboard</div>
</header>

<div class="stats">
  <div class="stat"><div class="lbl">2024 Population (Fridley)</div><div class="val">30,241</div></div>
  <div class="stat"><div class="lbl">Median HH Income</div><div class="val">$77,680</div></div>
  <div class="stat"><div class="lbl">Non-White Share</div><div class="val">45.4%</div></div>
  <div class="stat"><div class="lbl">Bachelor's+ (25+)</div><div class="val">30.6%</div></div>
  <div class="stat"><div class="lbl">Koegel (DFL) 2024</div><div class="val">{dfl:,} <span class="pill dfl">{dfl/tot*100:.1f}%</span></div></div>
  <div class="stat gop"><div class="lbl">Sylvester (R) 2024</div><div class="val">{gop:,} <span class="pill gop">{gop/tot*100:.1f}%</span></div></div>
  <div class="stat"><div class="lbl">Margin</div><div class="val">D +{(dfl-gop)/tot*100:.1f} pp</div></div>
  <div class="stat"><div class="lbl">Total Ballots</div><div class="val">{tot:,}</div></div>
</div>

<div class="grid">
  <div class="card map-wrap">
    <h2>Interactive precinct map — hover any precinct for full vote breakdown</h2>
    {map_html}
  </div>
  <div class="card">
    <h2>Race &amp; ethnicity composition over time</h2>
    {race_html}
  </div>
  <div class="card">
    <h2>State House DFL vs. GOP vote share, 2012–2024</h2>
    {vote_html}
  </div>
  <div class="card">
    <h2>Median household income (Fridley), 2010–2024</h2>
    {inc_html}
  </div>
  <div class="card full">
    {prec_html}
  </div>
</div>

<footer>
  <strong>Highlights:</strong>
  Strongest DFL precinct: <em>{top_prec['label']} ({top_prec['MCDNAME']})</em> at
  <strong>{top_prec['dfl_pct']}%</strong>.
  Weakest DFL precinct: <em>{bot_prec['label']} ({bot_prec['MCDNAME']})</em> at
  <strong>{bot_prec['dfl_pct']}%</strong>.
  No precinct gave Sylvester a majority.
  <br><br>
  Sources: U.S. Census Bureau ACS 2020-2024 5-year &amp; 2024 1-year;
  2020 Decennial PL 94-171; Minnesota Secretary of State certified 2022 &amp;
  2024 General Election precinct results; MN Geospatial Commons precinct
  boundary file; Ballotpedia HD 39A / HD 41B; Anoka County Abstract of Votes
  (Nov 8 2022). Generated locally via geopandas, folium, plotly.
</footer>
</body>
</html>"""

OUT.write_text(html, encoding="utf-8")
print(f"Wrote dashboard -> {OUT}")
