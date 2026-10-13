"""
Supply Chain Demand Distribution Map Generator
===============================================
Generates high-resolution cartographic maps (PNG and PDF) from customer demand data
in 'AI for DS Sample Data.csv'.

Key Features:
- Web Mercator projection (EPSG:3857) with high-detail CartoDB Positron light basemap
- Sequential Cool-to-Warm gradient with demand-weighted marker sizes and opacity
- Z-order layering so high-priority demand locations pop over dense clusters
- Geographic inset map showing Pan-India overview and national outlier locations (Bangalore, Surat, Raipur)
- Executive KPI card and demand distribution summary
- Cartographic graticules (Latitude/Longitude degrees), north arrow, and metric scale bar
"""

import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
import contextily as cx
import xyzservices.lib as xyz

# -----------------------------------------------------------------------------
# Configuration & Styling
# -----------------------------------------------------------------------------
CSV_PATH = "AI for DS Sample Data.csv"
OUTPUT_PNG = "supply_chain_map.png"
OUTPUT_PDF = "supply_chain_map.pdf"

# Demand tier specifications: [tier_value, color, size, alpha, label, edge_color]
TIER_SPECS = [
    (1.0, "#2563eb", 14, 0.50, "Tier 1.0 (Low)", None),
    (2.0, "#059669", 22, 0.60, "Tier 2.0 (Moderate)", None),
    (2.5, "#d97706", 36, 0.75, "Tier 2.5 (Medium)", None),
    (3.0, "#ea580c", 55, 0.85, "Tier 3.0 (High)", "#9a3412"),
    (5.0, "#dc2626", 85, 0.95, "Tier 5.0 (Critical)", "#7f1d1d"),
]

# Coordinate bounds for Eastern Uttar Pradesh regional focus (includes Sonbhadra)
REGIONAL_BOUNDS_DEG = {
    "lat_min": 23.75,
    "lat_max": 26.75,
    "lon_min": 81.25,
    "lon_max": 86.35,
}

# India extent for Pan-India overview inset
INDIA_BOUNDS_DEG = {
    "lat_min": 8.0,
    "lat_max": 33.5,
    "lon_min": 68.5,
    "lon_max": 92.5,
}

# -----------------------------------------------------------------------------
# Projection Utilities
# -----------------------------------------------------------------------------
def wgs84_to_mercator(lat, lon):
    """Converts WGS84 (EPSG:4326) latitude and longitude to Web Mercator (EPSG:3857) meters."""
    r_major = 6378137.0
    x = r_major * np.radians(lon)
    y = r_major * np.log(np.tan(np.pi / 4.0 + np.radians(lat) / 2.0))
    return x, y

def mercator_to_wgs84(x, y):
    """Converts Web Mercator (EPSG:3857) meters to WGS84 (EPSG:4326) latitude and longitude."""
    r_major = 6378137.0
    lon = np.degrees(x / r_major)
    lat = np.degrees(2.0 * np.arctan(np.exp(y / r_major)) - np.pi / 2.0)
    return lat, lon

def get_carto_provider():
    """Returns an xyzservices TileProvider for CartoDB Positron without API key restrictions."""
    return xyz.TileProvider(
        name="CartoDB.Positron",
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        subdomains="abcd",
        attribution="© OpenStreetMap contributors © CARTO",
    )

# -----------------------------------------------------------------------------
# Main Plotting Routine
# -----------------------------------------------------------------------------
def build_supply_chain_map():
    print(f"Loading data from '{CSV_PATH}'...")
    df = pd.read_csv(CSV_PATH)

    total_locations = len(df)
    total_demand = df["points"].sum()
    avg_demand = df["points"].mean()
    print(f"Loaded {total_locations:,} records. Total demand: {total_demand:,.1f}")

    # Project coordinates to Web Mercator
    df["merc_x"], df["merc_y"] = wgs84_to_mercator(df["lat"].values, df["long"].values)

    # Separate regional cluster from distant national outliers
    is_regional = (
        (df["lat"] >= REGIONAL_BOUNDS_DEG["lat_min"]) &
        (df["lat"] <= REGIONAL_BOUNDS_DEG["lat_max"]) &
        (df["long"] >= REGIONAL_BOUNDS_DEG["lon_min"]) &
        (df["long"] <= REGIONAL_BOUNDS_DEG["lon_max"])
    )
    df_regional = df[is_regional].copy()
    df_outliers = df[~is_regional].copy()
    print(f"Regional points: {len(df_regional):,} ({len(df_regional)/total_locations*100:.2f}%)")
    print(f"National outliers: {len(df_outliers):,} ({len(df_outliers)/total_locations*100:.2f}%)")

    # Set up matplotlib figure
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    # Determine Mercator extents for regional view
    x_min, y_min = wgs84_to_mercator(REGIONAL_BOUNDS_DEG["lat_min"], REGIONAL_BOUNDS_DEG["lon_min"])
    x_max, y_max = wgs84_to_mercator(REGIONAL_BOUNDS_DEG["lat_max"], REGIONAL_BOUNDS_DEG["lon_max"])
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # 1. Add basemap tiles
    print("Downloading Esri WorldStreetMap basemap tiles for regional frame...")
    cx.add_basemap(
        ax,
        source=cx.providers.Esri.WorldStreetMap,
        crs="EPSG:3857",
        alpha=0.62,
        reset_extent=False,
        attribution="© Esri, DeLorme, TomTom, USGS",
    )

    # 2. Render regional scatter points by tier (ascending points for clean layering)
    legend_elements = []
    for tier_val, color, size, alpha, tier_name, edge in TIER_SPECS:
        subset = df_regional[df_regional["points"] == tier_val]
        count = len(subset)
        pct = (count / total_locations) * 100

        ax.scatter(
            subset["merc_x"],
            subset["merc_y"],
            s=size,
            c=color,
            alpha=alpha,
            edgecolors=edge if edge else "none",
            linewidth=0.6 if edge else 0,
            label=f"{tier_name} ({count:,} - {pct:.1f}%)",
            zorder=3 + int(tier_val * 2),
        )

        legend_elements.append(
            Line2D(
                [0], [0],
                marker="o",
                color="w",
                label=f"{tier_name}  •  {count:,} pts ({pct:.1f}%)",
                markerfacecolor=color,
                markeredgecolor=edge if edge else color,
                markersize=np.sqrt(size) * 1.3,
            )
        )

    # 3. Format Axes & Geographic Graticules
    def format_x_lon(x_val, pos):
        _, lon = mercator_to_wgs84(x_val, y_min)
        return f"{lon:.1f}°E"

    def format_y_lat(y_val, pos):
        lat, _ = mercator_to_wgs84(x_min, y_val)
        return f"{lat:.1f}°N"

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_x_lon))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_y_lat))
    ax.tick_params(axis="both", which="major", labelsize=9.5, colors="#475569", length=5, width=1)
    ax.grid(True, linestyle="--", linewidth=0.6, color="#94a3b8", alpha=0.35, zorder=2)
    for spine in ax.spines.values():
        spine.set_color("#cbd5e1")
        spine.set_linewidth(1.2)

    # 4. North Arrow and Scale Bar
    # North Arrow in top-left
    ax.annotate(
        "N\n▲",
        xy=(0.025, 0.94),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#0f172a",
        bbox=dict(boxstyle="circle,pad=0.35", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.92, lw=1.2),
        zorder=20,
    )

    # Scale Bar (100 km) in bottom-left
    # 1 degree longitude at lat 25.4 deg is ~100.5 km; in Web Mercator meters, 100 km is ~111,000 m
    # Mercator scale factor at lat = 1 / cos(lat)
    center_lat = (REGIONAL_BOUNDS_DEG["lat_min"] + REGIONAL_BOUNDS_DEG["lat_max"]) / 2.0
    mercator_factor = 1.0 / np.cos(np.radians(center_lat))
    scale_100km_merc_meters = 100000.0 * mercator_factor

    scale_x0 = x_min + (x_max - x_min) * 0.04
    scale_y0 = y_min + (y_max - y_min) * 0.05
    ax.plot([scale_x0, scale_x0 + scale_100km_merc_meters], [scale_y0, scale_y0], color="#0f172a", lw=3.5, zorder=20)
    ax.text(
        scale_x0 + scale_100km_merc_meters / 2.0,
        scale_y0 + (y_max - y_min) * 0.015,
        "100 km",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        color="#0f172a",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="none", alpha=0.85),
        zorder=20,
    )

    # 5. Executive Header / Title Card (Top Center-Left)
    title_box = patches.FancyBboxPatch(
        (0.065, 0.88),
        0.42,
        0.10,
        transform=ax.transAxes,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor="#ffffff",
        edgecolor="#cbd5e1",
        alpha=0.95,
        linewidth=1.2,
        zorder=25,
    )
    ax.add_patch(title_box)

    ax.text(
        0.08, 0.945,
        "Supply Chain Demand Distribution Map",
        transform=ax.transAxes,
        fontsize=13,
        fontweight="bold",
        color="#0f172a",
        zorder=26,
    )
    ax.text(
        0.08, 0.90,
        f"Regional Network: Eastern Uttar Pradesh & Environs • {len(df_regional):,} delivery points\n"
        f"Demand Weight Spectrum (1.0 to 5.0) • Esri WorldStreetMap Basemap Context",
        transform=ax.transAxes,
        fontsize=8.2,
        color="#475569",
        linespacing=1.35,
        zorder=26,
    )

    # 6. KPI Metrics Card (Top Right)
    kpi_box = patches.FancyBboxPatch(
        (0.68, 0.77),
        0.30,
        0.21,
        transform=ax.transAxes,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor="#ffffff",
        edgecolor="#cbd5e1",
        alpha=0.95,
        linewidth=1.2,
        zorder=25,
    )
    ax.add_patch(kpi_box)

    ax.text(
        0.695, 0.945,
        "NETWORK KPI SUMMARY",
        transform=ax.transAxes,
        fontsize=8.5,
        fontweight="bold",
        color="#64748b",
        zorder=26,
    )

    kpi_lines = [
        f"Total Demand Locations:  {total_locations:,}",
        f"Regional Focus (E. UP):  {len(df_regional):,} ({len(df_regional)/total_locations*100:.1f}%)",
        f"National Outliers:       {len(df_outliers):,} (shown in inset)",
        f"Aggregate Demand Weight: {total_demand:,.1f}",
        f"Mean Demand / Location:  {avg_demand:.2f}",
        f"High Demand Tier (≥ 3.0): {len(df[df['points'] >= 3.0]):,} ({len(df[df['points'] >= 3.0])/total_locations*100:.1f}%)",
    ]
    ax.text(
        0.695, 0.785,
        "\n".join(kpi_lines),
        transform=ax.transAxes,
        fontsize=8.2,
        family="monospace",
        color="#1e293b",
        linespacing=1.45,
        zorder=26,
    )

    # 7. Demand Tier Legend (Middle Right)
    legend = ax.legend(
        handles=legend_elements,
        title="DEMAND TIER CLASSIFICATION",
        loc="center right",
        bbox_to_anchor=(0.985, 0.62),
        frameon=True,
        framealpha=0.95,
        facecolor="#ffffff",
        edgecolor="#cbd5e1",
        fontsize=8,
        title_fontsize=8.5,
        borderpad=0.8,
        labelspacing=0.55,
    )
    legend.get_title().set_fontweight("bold")
    legend.get_title().set_color("#64748b")
    legend.set_zorder(25)

    # 8. Pan-India Inset Map (Bottom Right: lat < 24.8, lon > 84.5 has 0 data points)
    print("Building Pan-India Overview Inset Map...")
    # Placement in figure coordinates: [left, bottom, width, height]
    ax_inset = fig.add_axes([0.67, 0.12, 0.28, 0.34], facecolor="#f8fafc")
    
    in_xmin, in_ymin = wgs84_to_mercator(INDIA_BOUNDS_DEG["lat_min"], INDIA_BOUNDS_DEG["lon_min"])
    in_xmax, in_ymax = wgs84_to_mercator(INDIA_BOUNDS_DEG["lat_max"], INDIA_BOUNDS_DEG["lon_max"])
    ax_inset.set_xlim(in_xmin, in_xmax)
    ax_inset.set_ylim(in_ymin, in_ymax)

    # Add basemap to inset
    cx.add_basemap(
        ax_inset,
        source=cx.providers.Esri.WorldStreetMap,
        crs="EPSG:3857",
        alpha=0.68,
        reset_extent=False,
        attribution="",
    )

    # Draw regional bounding box on inset
    rect = patches.Rectangle(
        (x_min, y_min),
        x_max - x_min,
        y_max - y_min,
        linewidth=1.8,
        edgecolor="#dc2626",
        facecolor="#ef4444",
        alpha=0.25,
        linestyle="--",
        zorder=10,
    )
    ax_inset.add_patch(rect)
    ax_inset.text(
        x_min + (x_max - x_min) * 0.5,
        y_max + (in_ymax - in_ymin) * 0.02,
        "Primary Network\n(20,976 pts)",
        ha="center",
        va="bottom",
        fontsize=7,
        fontweight="bold",
        color="#b91c1c",
        zorder=12,
    )

    # Plot outlier locations on inset
    outlier_summary = [
        {"name": "Bangalore", "lat": 12.93, "lon": 77.49, "pts": 8},
        {"name": "Surat", "lat": 21.23, "lon": 72.79, "pts": 1},
        {"name": "Raipur area", "lat": 21.07, "lon": 82.75, "pts": 14},
    ]

    for item in outlier_summary:
        ox, oy = wgs84_to_mercator(item["lat"], item["lon"])
        ax_inset.scatter(ox, oy, s=35, c="#7c3aed", edgecolors="#4c1d95", linewidth=0.8, zorder=15)
        # Annotation placement offset
        dx = 50000 if item["name"] != "Surat" else -100000
        dy = -40000 if item["name"] == "Bangalore" else 35000
        ha = "left" if item["name"] != "Surat" else "right"
        ax_inset.annotate(
            f"{item['name']}\n({item['pts']} pts)",
            xy=(ox, oy),
            xytext=(ox + dx, oy + dy),
            fontsize=6.5,
            fontweight="bold",
            color="#4c1d95",
            ha=ha,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#ffffff", edgecolor="#c4b5fd", alpha=0.9, lw=0.8),
            arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=0.7),
            zorder=16,
        )

    ax_inset.set_title("PAN-INDIA OVERVIEW & OUTLIERS", fontsize=7.5, fontweight="bold", color="#334155", pad=4)
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    for spine in ax_inset.spines.values():
        spine.set_color("#94a3b8")
        spine.set_linewidth(1.2)

    # 9. Save Deliverables
    print(f"Saving high-resolution PNG ({OUTPUT_PNG})...")
    plt.savefig(OUTPUT_PNG, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())

    print(f"Saving publication vector PDF ({OUTPUT_PDF})...")
    plt.savefig(OUTPUT_PDF, bbox_inches="tight", facecolor=fig.get_facecolor())

    plt.close()
    print("Done! All map artifacts successfully created.")

if __name__ == "__main__":
    build_supply_chain_map()
