import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from dotenv import load_dotenv
import os

load_dotenv()

# ── 1. CONFIGURATION ──────────────────────────────────────────────
API_KEY = os.getenv("CENSUS_API_KEY")

YEAR    = 2022

# States to compare: name, FIPS code
STATES = {
    "Minnesota":  "27",
    "Wisconsin":  "55",
    "Illinois":   "17",
    "Iowa":       "19",
    "Michigan":   "26",
}

# ACS variables:
# B25077_001E = Median home value
# B19013_001E = Median household income
# B25002_003E = Vacant units
# B25003_002E = Owner occupied
# B25003_003E = Renter occupied
VARIABLES = "NAME,B25077_001E,B19013_001E,B25002_003E,B25003_002E,B25003_003E"

# ── 2. PULL DATA FOR ALL STATES ───────────────────────────────────
print("Pulling Census data for all states...")
all_data = []

for state_name, state_fips in STATES.items():
    url = (
        f"https://api.census.gov/data/{YEAR}/acs/acs5"
        f"?get={VARIABLES}"
        f"&for=county:*"
        f"&in=state:{state_fips}"
        f"&key={API_KEY}"
    )
    response = requests.get(url)
    data     = response.json()

    # First row is headers
    df = pd.DataFrame(data[1:], columns=data[0])
    df["state_name"] = state_name
    all_data.append(df)
    print(f"  ✓ {state_name} — {len(df)} counties")

# Combine all states into one dataframe
df = pd.concat(all_data, ignore_index=True)

# ── 3. CLEAN THE DATA ─────────────────────────────────────────────
df = df.rename(columns={
    "B25077_001E": "median_home_value",
    "B19013_001E": "median_income",
    "B25002_003E": "vacant_units",
    "B25003_002E": "owner_occupied",
    "B25003_003E": "renter_occupied",
})

# Convert to numbers
for col in ["median_home_value","median_income","vacant_units",
            "owner_occupied","renter_occupied"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop rows with missing key data
df = df.dropna(subset=["median_home_value","median_income"])

# Clean up county name (remove state suffix e.g. ", Minnesota")
df["county_name"] = df["NAME"].str.split(",").str[0]

# Calculate renter percentage
df["renter_pct"] = (
    df["renter_occupied"] /
    (df["owner_occupied"] + df["renter_occupied"]) * 100
).round(1)

# Calculate owner percentage
df["owner_pct"] = (100 - df["renter_pct"]).round(1)

print(f"\nTotal counties loaded: {len(df)}")

# ── 4. BUILD STATE-LEVEL SUMMARY ──────────────────────────────────
state_summary = df.groupby("state_name").agg(
    avg_home_value  = ("median_home_value", "median"),
    avg_income      = ("median_income",     "median"),
    avg_renter_pct  = ("renter_pct",        "mean"),
    avg_owner_pct   = ("owner_pct",         "mean"),
    county_count    = ("county_name",       "count"),
).reset_index().round(1)

# Sort by avg home value for charts
state_summary = state_summary.sort_values("avg_home_value", ascending=True)

# ── 5. BUILD DASHBOARD ────────────────────────────────────────────
print("\nBuilding dashboard...")

# Color palette — one color per state
STATE_COLORS = {
    "Minnesota": "#2597F5",
    "Wisconsin":  "#4CAF50",
    "Illinois":   "#FF5722",
    "Iowa":       "#9C27B0",
    "Michigan":   "#FF9800",
}

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Median Home Value by State",
        "Owner vs. Renter Rate by State",
        "Home Value vs. Median Income by County",
        "Top 20 Counties by Median Home Value",
    ),
    vertical_spacing  = 0.18,
    horizontal_spacing= 0.12,
)

# ── CHART 1: Median Home Value by State (horizontal bar) ──────────
fig.add_trace(
    go.Bar(
        x         = state_summary["avg_home_value"],
        y         = state_summary["state_name"],
        orientation = "h",
        marker_color= [STATE_COLORS[s] for s in state_summary["state_name"]],
        text      = [f"${v:,.0f}" for v in state_summary["avg_home_value"]],
        textposition = "outside",
        showlegend= False,
    ),
    row=1, col=1,
)

# ── CHART 2: Owner vs Renter Rate (grouped bar) ───────────────────
fig.add_trace(
    go.Bar(
        name         = "Owner Occupied %",
        x            = state_summary["state_name"],
        y            = state_summary["avg_owner_pct"],
        marker_color = "#42A5F5",
        text         = [f"{v:.1f}%" for v in state_summary["avg_owner_pct"]],
        textposition = "outside",
    ),
    row=1, col=2,
)
fig.add_trace(
    go.Bar(
        name         = "Renter Occupied %",
        x            = state_summary["state_name"],
        y            = state_summary["avg_renter_pct"],
        marker_color = "#EF5350",
        text         = [f"{v:.1f}%" for v in state_summary["avg_renter_pct"]],
        textposition = "outside",
    ),
    row=1, col=2,
)

# ── CHART 3: Scatter — Home Value vs Income by County ─────────────
for state_name, group in df.groupby("state_name"):
    fig.add_trace(
        go.Scatter(
            x       = group["median_income"],
            y       = group["median_home_value"],
            mode    = "markers",
            name    = state_name,
            marker  = dict(
                color   = STATE_COLORS[state_name],
                size    = 7,
                opacity = 0.7,
            ),
            text    = group["county_name"],
            hovertemplate = (
                "<b>%{text}</b><br>"
                "Income: $%{x:,.0f}<br>"
                "Home Value: $%{y:,.0f}<extra></extra>"
            ),
        ),
        row=2, col=1,
    )

# ── CHART 4: Top 20 Counties by Home Value (horizontal bar) ───────
top20 = df.nlargest(20, "median_home_value").sort_values(
    "median_home_value", ascending=True
)
fig.add_trace(
    go.Bar(
        x            = top20["median_home_value"],
        y            = top20["county_name"] + ", " + top20["state_name"],
        orientation  = "h",
        marker_color = [STATE_COLORS[s] for s in top20["state_name"]],
        text         = [f"${v:,.0f}" for v in top20["median_home_value"]],
        textposition = "outside",
        showlegend   = False,
    ),
    row=2, col=2,
)

# ── 6. LAYOUT AND STYLING ─────────────────────────────────────────
fig.update_layout(
    title = dict(
        text     = "Midwest Regional Housing Market Dashboard — 2022 ACS Data",
        font     = dict(size=20),
        x        = 0.5,
        xanchor  = "center",
    ),
    height      = 900,
    barmode     = "group",
    plot_bgcolor= "#F8F9FA",
    paper_bgcolor="#FFFFFF",
    font        = dict(family="Arial", size=12),
    legend      = dict(
        orientation = "h",
        yanchor     = "bottom",
        y           = 1.02,
        xanchor     = "right",
        x           = 1,
    ),
)

# Axis labels
fig.update_xaxes(title_text="Median Home Value ($)", row=1, col=1)
fig.update_xaxes(title_text="State",                 row=1, col=2)
fig.update_xaxes(title_text="Median Household Income ($)", row=2, col=1)
fig.update_xaxes(title_text="Median Home Value ($)", row=2, col=2)
fig.update_yaxes(title_text="Median Home Value ($)", row=2, col=1)

# ── 7. SAVE OUTPUT ────────────────────────────────────────────────
output_file = "housing_dashboard.html"
pio.write_html(fig, output_file, full_html=True)
print(f"\nDashboard saved! Open '{output_file}' in your browser.")