# Leeds Cycle Patterns Analysis

This analysis examines cycling patterns across Leeds to help understand infrastructure usage, inform future planning decisions, and track changes in sustainable transportation adoption over time. It features an analysis of ride volumes during 2018-2023 across 11 recording sites based on 1.2 million data points &amp; +80% daily completeness over a continuous 6 year period.

## Data Structure

The database structure as seen below consists of 2 tables, 'Cycle Counts' and 'Recording Sites':

![ERD Diagram for Leeds Cycling Analysis](visualizations/ERD-diagram.png)

The underlying data was sourced from <a href="https://datamillnorth.org/dataset/e1dmk/leeds-annual-cycle-growth" target="_blank">Data Mill North</a> and the steps taken to clean and check for quality control prior for analysis in Tableau can be found [here](documentation/data-prep-summary.md).

## Methodology

Data was cleaned & prepared for analysis as detailed here [here](documentation/data-prep-summary.md). It was then imported into Tableeau & augmented with calculated fields to support further analysis.

Three dashboards created within Tableau:

### Overview Dashboard - The Entry Point

- Key metrics at the top:
-- Total rides across 2018-2023
Year-over-Year growth rates (bar chart with color coding for negative values)
Peak hour by ride volume
Peak day by ride volume
Peak month by ride volume


City map showing the 11 recording sites with size/color coding for volume
Primary time series showing overall cycling volume 2018-2023 with COVID periods clearly marked (2020-2021)

Custom y-axis range (with note explaining non-zero baseline)


Small multiples of temporal patterns:

Volume by day of week (bar chart)
Volume by month (bar chart)
Volume by hour (line chart)


Brief summary text explaining key insights from the overview dashboard

## Key findings

xxx

## How to view the dashboard

xx

## Caveats & Assumptions

xxx
