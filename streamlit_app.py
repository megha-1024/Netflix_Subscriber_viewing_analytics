import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_dark"


# Page config
st.set_page_config(page_title="Netflix Analytics Dashboard", layout="wide", page_icon="🎬")

NETFLIX_RED = "#E50914"
NETFLIX_DARK = "#221f1f"
NETFLIX_GRAY = "#B3B3B3"


# Data loading (cached so it doesn't reload on every filter interaction)
@st.cache_data
def load_data():
    df = pd.read_csv(
        "netflix_cleaned.csv",
        parse_dates=["subscription_start_date", "subscription_end_date", "date_watched"]
    )
    return df

df = load_data()


# Sidebar filters
st.sidebar.header("Filters")

plans = st.sidebar.multiselect(
    "Subscription Plan", options=sorted(df["subscription_plan"].unique()),
    default=sorted(df["subscription_plan"].unique())
)
countries = st.sidebar.multiselect(
    "Country", options=sorted(df["country"].unique()),
    default=sorted(df["country"].unique())
)
devices = st.sidebar.multiselect(
    "Device Type", options=sorted(df["device_type"].unique()),
    default=sorted(df["device_type"].unique())
)
age_bands = st.sidebar.multiselect(
    "Age Band", options=sorted(df["age_band"].dropna().unique()),
    default=sorted(df["age_band"].dropna().unique())
)
churn_filter = st.sidebar.radio("Customer Status", ["All", "Active only", "Churned only"], index=0)

filtered = df[
    df["subscription_plan"].isin(plans)
    & df["country"].isin(countries)
    & df["device_type"].isin(devices)
    & df["age_band"].isin(age_bands)
]

if churn_filter == "Active only":
    filtered = filtered[filtered["is_churned"] == 0]
elif churn_filter == "Churned only":
    filtered = filtered[filtered["is_churned"] == 1]

st.sidebar.markdown(f"**{len(filtered):,}** of {len(df):,} customers match filters")


# Header
st.title("🎬 Netflix Subscriber & Viewing Analytics")
st.caption("Interactive dashboard — filter using the sidebar to explore customer segments")

if filtered.empty:
    st.warning("No rows match the current filters. Adjust filters in the sidebar.")
    st.stop()


# KPI row
col1, col2, col3, col4, col5 = st.columns(5)

total_customers = len(filtered)
churn_rate = filtered["is_churned"].mean() * 100
valid_ltv = filtered.dropna(subset=["tenure_days"])
est_revenue = (valid_ltv["monthly_fee"] * (valid_ltv["tenure_days"] / 30)).sum()
avg_watch_time = filtered["watch_time_minutes"].mean()
avg_rating = filtered["rating"].mean()

col1.metric("Customers", f"{total_customers:,}")
col2.metric("Churn Rate", f"{churn_rate:.1f}%")
col3.metric("Est. Revenue (LTV proxy)", f"${est_revenue:,.0f}")
col4.metric("Avg Watch Time", f"{avg_watch_time:.0f} min")
col5.metric("Avg Rating", f"{avg_rating:.2f} / 5")

st.divider()


# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Churn", "Revenue", "Engagement", "Content", "Insights"]
)

# ---------------- Churn tab ----------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        churn_by_plan = (
            filtered.groupby("subscription_plan")["is_churned"].mean().sort_values(ascending=False) * 100
        ).reset_index()
        fig = px.bar(
            churn_by_plan, x="subscription_plan", y="is_churned",
            title="Churn Rate by Plan", labels={"is_churned": "Churn Rate (%)", "subscription_plan": "Plan"},
            color_discrete_sequence=[NETFLIX_RED]
        )
        st.plotly_chart(fig, width="stretch", theme=None)

    with c2:
        churn_by_country = (
            filtered.groupby("country")["is_churned"].mean().sort_values(ascending=False) * 100
        ).reset_index()
        fig = px.bar(
            churn_by_country, x="is_churned", y="country", orientation="h",
            title="Churn Rate by Country", labels={"is_churned": "Churn Rate (%)", "country": "Country"},
            color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", theme=None)

    c3, c4 = st.columns(2)

    with c3:
        churn_by_age = (
            filtered.groupby("age_band", observed=True)["is_churned"].mean().sort_index() * 100
        ).reset_index()
        fig = px.bar(
            churn_by_age, x="age_band", y="is_churned", text_auto=".1f",
            title="Churn Rate by Age Band", labels={"is_churned": "Churn Rate (%)", "age_band": "Age Band"},
            color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch", theme=None)

    with c4:
        churn_by_device = (
            filtered.groupby("device_type")["is_churned"].mean().sort_values(ascending=False) * 100
        ).reset_index()
        fig = px.bar(
            churn_by_device, x="device_type", y="is_churned", text_auto=".1f",
            title="Churn Rate by Device", labels={"is_churned": "Churn Rate (%)", "device_type": "Device"},
            color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch", theme=None)

    st.subheader("Active vs Churned — Behavior Comparison")
    behavior_cols = ["watch_time_minutes", "session_count", "completion_percentage",
                      "days_since_last_watch", "avg_weekly_watch_time", "rating"]
    compare = filtered.groupby("is_churned")[behavior_cols].mean().rename(
        index={0: "Active", 1: "Churned"}
    ).T.reset_index().rename(columns={"index": "Metric"})
    group_cols = [c for c in ["Active", "Churned"] if c in compare.columns]
    if len(group_cols) < 2:
        st.info("Behavior comparison needs both Active and Churned customers in the current filter — "
                 "select 'All' under Customer Status to see this chart.")
    else:
        fig = px.bar(
            compare, x="Metric", y=group_cols, barmode="group",
            title="Behavior: Active vs Churned",
            color_discrete_sequence=[NETFLIX_GRAY, NETFLIX_RED]
        )
        st.plotly_chart(fig, width="stretch", theme=None)

# ---------------- Revenue tab ----------------
with tab2:
    user_level = filtered.dropna(subset=["tenure_days"]).copy()
    user_level["est_ltv"] = user_level["monthly_fee"] * (user_level["tenure_days"] / 30)

    c1, c2 = st.columns(2)
    with c1:
        rev_by_plan = user_level.groupby("subscription_plan")["est_ltv"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(
            rev_by_plan, x="subscription_plan", y="est_ltv",
            title="Estimated Revenue by Plan", labels={"est_ltv": "Revenue ($)", "subscription_plan": "Plan"},
            color_discrete_sequence=[NETFLIX_RED]
        )
        st.plotly_chart(fig, width="stretch", theme=None)

    with c2:
        rev_by_country = user_level.groupby("country")["est_ltv"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(
            rev_by_country, x="est_ltv", y="country", orientation="h",
            title="Estimated Revenue by Country", labels={"est_ltv": "Revenue ($)", "country": "Country"},
            color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", theme=None)

    st.subheader("Signups Over Time")
    monthly_signups = filtered.groupby("signup_month").size().reset_index(name="new_customers")
    monthly_signups = monthly_signups.sort_values("signup_month")
    fig = px.line(
        monthly_signups, x="signup_month", y="new_customers", markers=True,
        title="New Customer Signups by Month", color_discrete_sequence=[NETFLIX_RED]
    )
    fig.update_xaxes(tickangle=90)
    st.plotly_chart(fig, width="stretch", theme=None)

    st.subheader("Top 20 Customers by Estimated Revenue")
    top20 = user_level.nlargest(20, "est_ltv")[
        ["user_id", "country", "subscription_plan", "tenure_days", "est_ltv"]
    ].reset_index(drop=True)
    st.dataframe(top20, width=800)

    excluded = filtered["tenure_days"].isna().sum()
    if excluded:
        st.caption(f"Note: {excluded} customer(s) excluded from revenue figures due to invalid tenure data.")

# ---------------- Engagement tab ----------------
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(
            filtered, x="watch_time_minutes", nbins=30,
            title="Watch Time Distribution", color_discrete_sequence=[NETFLIX_RED]
        )
        st.plotly_chart(fig, width="stretch", theme=None)

    with c2:
        time_counts = filtered["time_of_day"].value_counts().reset_index()
        time_counts.columns = ["time_of_day", "sessions"]
        fig = px.bar(
            time_counts, x="time_of_day", y="sessions", text_auto=True,
            title="Sessions by Time of Day", color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch", theme=None)

    c3, c4 = st.columns(2)
    with c3:
        device_counts = filtered["device_type"].value_counts().reset_index()
        device_counts.columns = ["device_type", "sessions"]
        fig = px.pie(
            device_counts, names="device_type", values="sessions",
            title="Sessions by Device Type", color_discrete_sequence=px.colors.sequential.Reds_r
        )
        st.plotly_chart(fig, width="stretch", theme=None)

    with c4:
        fig = px.scatter(
            filtered, x="watch_time_minutes", y="monthly_fee", color="subscription_plan",
            title="Watch Time vs Monthly Fee", opacity=0.4
        )
        st.plotly_chart(fig, width="stretch", theme=None)

    st.subheader("Correlation Heatmap")
    numeric_cols = ["age", "monthly_fee", "watch_time_minutes", "session_count", "completion_percentage",
                     "rating", "days_since_last_watch", "avg_weekly_watch_time", "content_diversity_score",
                     "tenure_days", "is_churned"]
    corr = filtered[numeric_cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Correlation Between Numeric Features"
    )
    st.plotly_chart(fig, width="stretch", theme=None)

# ---------------- Content tab ----------------
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        genre_stats = filtered.groupby("genre").agg(
            views=("user_id", "count"), avg_rating=("rating", "mean")
        ).sort_values("views", ascending=False).reset_index()
        fig = px.bar(
            genre_stats, x="genre", y="views", title="Views by Genre",
            color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, width="stretch", theme=None)

    with c2:
        content_type_counts = filtered["content_type"].value_counts().reset_index()
        content_type_counts.columns = ["content_type", "count"]
        fig = px.pie(
            content_type_counts, names="content_type", values="count",
            title="Movies vs Series", color_discrete_sequence=[NETFLIX_RED, NETFLIX_GRAY]
        )
        st.plotly_chart(fig, width="stretch", theme=None)

    c3, c4 = st.columns(2)
    with c3:
        rec_source = filtered["recommendation_source"].value_counts().reset_index()
        rec_source.columns = ["recommendation_source", "count"]
        fig = px.bar(
            rec_source, x="recommendation_source", y="count", text_auto=True,
            title="How Customers Discover Content", color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch", theme=None)

    with c4:
        liked_rate = filtered.groupby("genre")["liked"].apply(
            lambda x: (x == "Yes").mean() * 100
        ).sort_values(ascending=False).reset_index()
        liked_rate.columns = ["genre", "liked_pct"]
        fig = px.bar(
            liked_rate, x="genre", y="liked_pct",
            title="Like Rate by Genre (%)", color_discrete_sequence=[NETFLIX_RED]
        )
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, width="stretch", theme=None)

# ---------------- Insights tab ----------------
with tab5:
    st.subheader("Key Business Insights")

    churned_n = int(filtered["is_churned"].sum())
    top_plan = filtered["subscription_plan"].value_counts().idxmax()
    top_genre = filtered["genre"].value_counts().idxmax()
    top_country_rev = (
        filtered.dropna(subset=["tenure_days"])
        .assign(est_ltv=lambda d: d["monthly_fee"] * (d["tenure_days"] / 30))
        .groupby("country")["est_ltv"].sum().idxmax()
    )
    top_time = filtered["time_of_day"].value_counts().idxmax()
    arpu = filtered["monthly_fee"].mean()

    st.markdown(f"""
- **Churn:** {churn_rate:.1f}% of the filtered customer base has cancelled ({churned_n:,} customers). Basic-plan subscribers churn at a noticeably higher rate than Premium subscribers across the full dataset.
- **Most popular plan:** {top_plan}, by subscriber count.
- **Top revenue country:** {top_country_rev}, by estimated lifetime value.
- **Most-watched genre:** {top_genre}.
- **Peak viewing window:** {top_time}.
- **ARPU (Average Revenue Per User):** ${arpu:.2f}/month within the current filter selection.
- **Engagement vs churn:** Active customers show higher average watch time and weekly engagement than churned customers, suggesting engagement level is a leading churn indicator worth monitoring.
    """)

    st.subheader("Raw Filtered Data")
    st.dataframe(filtered.head(500), width=800)
    st.download_button(
        "Download filtered data as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="netflix_filtered.csv",
        mime="text/csv"
    )
