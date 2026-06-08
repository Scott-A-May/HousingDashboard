# Regional Housing Market Dashboard

An interactive multi-chart dashboard comparing county-level housing metrics across five Upper Midwest states using Census data and Plotly.

## Overview

This project pulls 2022 ACS 5-Year Estimates from the U.S. Census Bureau API for all counties across five Upper Midwest states (MN, WI, IL, IA, MI), builds a state-level summary, and renders a four-chart interactive dashboard comparing home values, income, and occupancy rates.

## Data Source

- **Dataset:** American Community Survey (ACS) 5-Year Estimates
- **Vintage:** 2022
- **Source:** U.S. Census Bureau API
- **Geography:** All counties in MN, WI, IL, IA, MI
- **Variables:**
  - Median home value
  - Median household income
  - Vacant housing units
  - Owner-occupied units
  - Renter-occupied units

## Features

- Pulls live county-level data for five states in a single run
- Calculates owner vs. renter occupancy rates by county
- Builds state-level summaries using median aggregation
- Renders a four-chart interactive dashboard:
  - **Median Home Value by State** — horizontal bar chart
  - **Owner vs. Renter Rate by State** — grouped bar chart
  - **Home Value vs. Median Income by County** — scatter plot
  - **Top 20 Counties by Median Home Value** — horizontal bar chart
- Outputs a standalone HTML dashboard viewable in any browser

## Project Structure

HousingDashboard/
├── housing_dashboard.py   # Main script
├── index.html             # GitHub Pages entry point
└── requirements.txt       # Python dependencies

## Technologies Used

- Python 3.14
- pandas
- Plotly
- U.S. Census Bureau API

## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Census API key to a `.env` file:  CENSUS_API_KEY=your_key_here
4. Run the script:  python housing_dashboard.py
5. Open `housing_dashboard.html` in your browser

## Author

Scott A. May | [GitHub](https://github.com/Scott-A-May)
   5. 
