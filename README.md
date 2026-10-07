# Netflix Subscriber & Viewing Analytics

An interactive Netflix Subscriber and Viewing Analytics dashboard built using Python, Pandas, Streamlit, and Plotly.

The project analyzes customer subscription behavior, churn, revenue, engagement, viewing patterns, and content preferences through an interactive dashboard.

---

## Project Overview

This project analyzes Netflix customer and viewing data to identify patterns in:

- Customer churn
- Subscription plans
- Estimated customer lifetime value
- Revenue by country and subscription plan
- Customer engagement
- Viewing behavior
- Content preferences
- Genre performance
- Recommendation sources

The dashboard allows users to filter the data by:

- Subscription Plan
- Country
- Device Type
- Age Band
- Customer Status

---

## Dashboard Features

### 1. Churn Analysis

- Churn Rate by Subscription Plan
- Churn Rate by Country
- Churn Rate by Age Band
- Churn Rate by Device
- Active vs Churned customer behavior comparison

### 2. Revenue Analysis

- Estimated Revenue by Subscription Plan
- Estimated Revenue by Country
- Customer Signups Over Time
- Top 20 Customers by Estimated Revenue

### 3. Engagement Analysis

- Watch Time Distribution
- Sessions by Time of Day
- Sessions by Device Type
- Watch Time vs Monthly Fee
- Correlation Heatmap

### 4. Content Analysis

- Views by Genre
- Movies vs Series
- Content Discovery Sources
- Like Rate by Genre

### 5. Business Insights

The dashboard provides automatically generated insights related to:

- Churn
- Popular subscription plans
- Revenue-generating countries
- Popular genres
- Peak viewing periods
- ARPU
- Engagement vs churn

---

## Key Dashboard Metrics

The current dashboard displays:

- **50,000 customers**
- **17.2% churn rate**
- **85 min average watch time**
- **3.42 / 5 average rating**

These values update dynamically based on the selected filters.

---

## Tech Stack

- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Data Analysis
- Exploratory Data Analysis
- Business Intelligence
- Data Visualization

---

## Project Structure

```text
netflix-subscriber-viewing-analytics/
│
├── streamlit_app.py
├── netflix_cleaned.csv
├── requirements.txt
├── README.md
├── .gitignore


## Project Workflow

The project follows an end-to-end data analytics workflow:

```text
Raw Netflix Customer & Viewing Data
                ↓
        Data Cleaning & Preparation
                ↓
      Data Loading with Pandas
                ↓
      Exploratory Data Analysis
                ↓
       KPI & Metric Calculation
                ↓
       Customer Segmentation
                ↓
   Churn / Revenue / Engagement /
       Content Analysis
                ↓
       Interactive Visualizations
                ↓
      Streamlit Dashboard
                ↓
       Business Insights
                ↓
      Filtered Data Export

