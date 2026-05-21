"""Render a precinct-level choropleth of MN House District 39A (Fridley).

Uses the MN Geospatial Commons "General Election Results by Precinct, 2024"
shapefile, which already joins precinct boundaries to certified state-canvassed
vote totals. Output is a single PNG saved next to this script.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHP = ROOT / "data" / "sos_results" / "general_election_results_by_precinct_2024.shp"
OUT = ROOT / "maps" / "hd39a_2024_choropleth.png"

# ---------------------------------------------------------------------------
# Load + filter
# ---------------------------------------------------------------------------
gdf = gpd.read_file(SHP)
hd39a = gdf[gdf["MNLEGDIST"] == "39A"].copy()
print(f"Precincts in HD 39A: {len(hd39a)}")

# Reproject to a metric CRS suitable for the Twin Cities (UTM 15N).
hd39a = hd39a.to_crs(epsg=26915)

# Compute DFL (Koegel) vote share for the State Rep race.
hd39a["dfl_pct"] = 100 * hd39a["MNLEGDFL"] / hd39a["MNLEGTOTAL"]
hd39a["gop_pct"] = 100 * hd39a["MNLEGR"] / hd39a["MNLEGTOTAL"]
hd39a["margin"]  = hd39a["dfl_pct"] - hd39a["gop_pct"]

# Short labels for the map.
hd39a["label"] = hd39a["SHORTLABEL"].fillna(hd39a["PCTNAME"])

print(hd39a[["label", "MCDNAME", "MNLEGDFL", "MNLEGR", "MNLEGTOTAL",
             "dfl_pct"]].sort_values("dfl_pct", ascending=False)
      .to_string(index=False))

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
# Diverging blue scale: deeper blue = stronger DFL.
blues = LinearSegmentedColormap.from_list(
    "dfl_blues", ["#deebf7", "#9ecae1", "#4292c6", "#08519c", "#08306b"],
)

fig, (ax_main, ax_ctx) = plt.subplots(
    1, 2, figsize=(15, 11),
    gridspec_kw={"width_ratios": [3, 1.05]},
)

# --- Main map: Koegel (DFL) share by precinct ---
hd39a.plot(
    column="dfl_pct",
    cmap=blues,
    vmin=50, vmax=75,
    linewidth=0.8, edgecolor="white",
    ax=ax_main,
    legend=True,
    legend_kwds={
        "label": "Koegel (DFL) vote share, % — State Rep. 2024",
        "shrink": 0.55, "pad": 0.02,
    },
)

# Precinct labels with vote share.
for _, row in hd39a.iterrows():
    c = row.geometry.representative_point()
    label = f"{row['label']}\n{row['dfl_pct']:.1f}% D"
    ax_main.annotate(
        label, xy=(c.x, c.y),
        ha="center", va="center",
        fontsize=7.5, color="white" if row["dfl_pct"] >= 64 else "black",
        weight="bold",
    )

# Highlight municipal boundaries for context.
muni = hd39a.dissolve(by="MCDNAME", as_index=False)
muni.boundary.plot(ax=ax_main, color="#444", linewidth=1.4)
for _, row in muni.iterrows():
    c = row.geometry.representative_point()
    ax_main.annotate(
        row["MCDNAME"].upper(),
        xy=(c.x, c.y), xytext=(0, -28), textcoords="offset points",
        ha="center", fontsize=8, color="#222",
        weight="bold", alpha=0.55,
    )

ax_main.set_title(
    "MN House District 39A — 2024 State Representative race\n"
    "Erin Koegel (DFL) vs. Rod Sylvester (R) by precinct",
    fontsize=14, weight="bold",
)
ax_main.set_axis_off()

# District summary box.
dfl = int(hd39a["MNLEGDFL"].sum())
gop = int(hd39a["MNLEGR"].sum())
wi  = int(hd39a["MNLEGWI"].sum())
tot = int(hd39a["MNLEGTOTAL"].sum())
summary = (
    f"District-wide totals (2024)\n"
    f"  Koegel (DFL):   {dfl:>6,}  ({dfl/tot*100:5.2f}%)\n"
    f"  Sylvester (R):  {gop:>6,}  ({gop/tot*100:5.2f}%)\n"
    f"  Write-in:       {wi:>6,}  ({wi/tot*100:5.2f}%)\n"
    f"  Total ballots:  {tot:>6,}\n"
    f"  Margin: D +{(dfl-gop)/tot*100:.1f} pp"
)
ax_main.text(
    0.01, 0.01, summary, transform=ax_main.transAxes,
    fontsize=9, family="monospace", va="bottom", ha="left",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
              edgecolor="#888", alpha=0.92),
)

# --- Context panel: precinct ranking table ---
ax_ctx.set_axis_off()
ax_ctx.set_title("Precincts ranked by Koegel %", fontsize=11, weight="bold")
ranked = hd39a.sort_values("dfl_pct", ascending=False)[
    ["label", "dfl_pct", "MNLEGTOTAL"]
].reset_index(drop=True)
lines = [f"{'Rank':<5}{'Precinct':<24}{'DFL %':>7}{'Ballots':>9}"]
lines.append("-" * 45)
for i, r in ranked.iterrows():
    lines.append(
        f"{i+1:<5}{r['label'][:23]:<24}{r['dfl_pct']:>6.1f}%{int(r['MNLEGTOTAL']):>9,}"
    )
lines.append("-" * 45)
lines.append(f"{'Total':<29}{dfl/tot*100:>6.1f}%{tot:>9,}")
ax_ctx.text(
    0.0, 0.95, "\n".join(lines),
    transform=ax_ctx.transAxes,
    family="monospace", fontsize=8.5, va="top",
)

# Footer credits.
fig.text(
    0.5, 0.015,
    "Source: MN Secretary of State, certified 2024 General Election precinct "
    "results joined to MN Geospatial Commons precinct boundaries. "
    "Map: matplotlib + geopandas. Projection: UTM Zone 15N (EPSG:26915).",
    ha="center", fontsize=8, color="#444",
)

plt.tight_layout(rect=(0, 0.03, 1, 1))
plt.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved -> {OUT}")
