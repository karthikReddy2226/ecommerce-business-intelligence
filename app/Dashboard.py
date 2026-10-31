
import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import create_engine, URL, text


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="E-Commerce Business Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 E-Commerce Business Intelligence Dashboard")

st.markdown(
    "Analyze sales performance, products, customers "
    "and markets using interactive business insights."
)


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

@st.cache_resource
def get_engine():
    config = st.secrets["postgres"]

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=config["user"],
        password=config["password"],
        host=config["host"],
        port=int(config["port"]),
        database=config["database"]
    )

    return create_engine(connection_url)


# ==========================================
# 3. LOAD DATA
# ==========================================

@st.cache_data(ttl=300)
def load_data(_engine):

    query = """
        SELECT
            invoice_no,
            stock_code,
            description,
            quantity,
            invoice_date,
            unit_price,
            customer_id,
            country,
            revenue,
            year,
            month,
            month_name,
            day,
            hour,
            day_name
        FROM online_retail
    """

    with _engine.connect() as connection:
        df = pd.read_sql_query(
            text(query),
            connection
        )

    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"]
    )

    return df


try:
    engine = get_engine()
    df = load_data(engine)

except Exception as error:
    st.error("Unable to connect to PostgreSQL.")
    st.exception(error)
    st.stop()


# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Dashboard Filters")

min_date = df["invoice_date"].min().date()
max_date = df["invoice_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("Please select both a start date and an end date.")
    st.stop()

start_date, end_date = selected_dates

if start_date > end_date:
    st.error("Start date cannot be after end date.")
    st.stop()

all_countries = sorted(
    df["country"].dropna().unique().tolist()
)

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=all_countries
)

if not selected_countries:
    st.warning("Select at least one country to view the dashboard.")
    st.stop()


# ==========================================
# 5. APPLY FILTERS
# ==========================================

filtered_df = df[
    (df["invoice_date"].dt.date >= start_date)
    & (df["invoice_date"].dt.date <= end_date)
    & (df["country"].isin(selected_countries))
].copy()

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()


# ==========================================
# 6. CALCULATE BUSINESS KPIs
# ==========================================

total_revenue = filtered_df["revenue"].sum()

total_orders = filtered_df["invoice_no"].nunique()

total_customers = filtered_df["customer_id"].nunique()

total_products = filtered_df["stock_code"].nunique()

total_quantity = filtered_df["quantity"].sum()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0 else 0
)


# ==========================================
# 7. KPI CARDS
# ==========================================

st.subheader("Business Performance Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"£{total_revenue:,.2f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Unique Customers",
    f"{total_customers:,}"
)

col4.metric(
    "Unique Products",
    f"{total_products:,}"
)

col5, col6 = st.columns(2)

col5.metric(
    "Quantity Sold",
    f"{total_quantity:,}"
)

col6.metric(
    "Average Order Value",
    f"£{average_order_value:,.2f}"
)


st.divider()


# ==========================================
# 8. MONTHLY REVENUE TREND
# ==========================================

st.subheader("Monthly Revenue Analysis")

monthly_sales = (
    filtered_df
    .groupby(
        filtered_df["invoice_date"].dt.to_period("M")
    )["revenue"]
    .sum()
    .reset_index()
)

monthly_sales.columns = ["Month", "Revenue"]

monthly_sales["Month"] = (
    monthly_sales["Month"].astype(str)
)

fig_monthly = px.line(
    monthly_sales,
    x="Month",
    y="Revenue",
    markers=True,
    title="Monthly Revenue Trend",
    template="plotly_white"
)

st.plotly_chart(
    fig_monthly,
    width="stretch"
)


# ==========================================
# 9. COUNTRY-WISE REVENUE
# ==========================================

left_col, right_col = st.columns(2)

country_sales = (
    filtered_df
    .groupby("country")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

with left_col:

    st.subheader("Top 10 Countries")

    fig_country = px.bar(
        country_sales.sort_values("revenue"),
        x="revenue",
        y="country",
        orientation="h",
        labels={
            "revenue": "Revenue (£)",
            "country": "Country"
        },
        template="plotly_white"
    )

    st.plotly_chart(
        fig_country,
        width="stretch"
    )


# ==========================================
# 10. TOP 10 PRODUCTS
# ==========================================

product_sales = (
    filtered_df
    .groupby(
        ["stock_code", "description"],
        dropna=False
    )["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

with right_col:

    st.subheader("Top 10 Products")

    fig_products = px.bar(
        product_sales.sort_values("revenue"),
        x="revenue",
        y="description",
        orientation="h",
        hover_data=["stock_code"],
        labels={
            "revenue": "Revenue (£)",
            "description": "Product"
        },
        template="plotly_white"
    )

    st.plotly_chart(
        fig_products,
        width="stretch"
    )


# ==========================================
# 11. CUSTOMER ANALYSIS
# ==========================================

st.divider()

st.subheader("Customer Performance")

customer_df = filtered_df.dropna(
    subset=["customer_id"]
)

customer_sales = (
    customer_df
    .groupby("customer_id")
    .agg(
        total_revenue=("revenue", "sum"),
        total_orders=("invoice_no", "nunique"),
        total_quantity=("quantity", "sum")
    )
    .reset_index()
    .sort_values(
        "total_revenue",
        ascending=False
    )
)

top_customers = customer_sales.head(10)

fig_customers = px.bar(
    top_customers.sort_values("total_revenue"),
    x="total_revenue",
    y="customer_id",
    orientation="h",
    labels={
        "total_revenue": "Revenue (£)",
        "customer_id": "Customer ID"
    },
    template="plotly_white",
    title="Top 10 Customers by Revenue"
)

st.plotly_chart(
    fig_customers,
    width="stretch"
)


# ==========================================
# 12. SALES BY DAY AND HOUR
# ==========================================

left_col, right_col = st.columns(2)

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

daily_sales = (
    filtered_df
    .groupby("day_name")["revenue"]
    .sum()
    .reindex(day_order)
    .reset_index()
)

daily_sales.columns = ["Day", "Revenue"]

with left_col:

    st.subheader("Revenue by Weekday")

    fig_day = px.bar(
        daily_sales,
        x="Day",
        y="Revenue",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_day,
        width="stretch"
    )


hourly_sales = (
    filtered_df
    .groupby("hour")["revenue"]
    .sum()
    .reset_index()
)

with right_col:

    st.subheader("Revenue by Hour")

    fig_hour = px.bar(
        hourly_sales,
        x="hour",
        y="revenue",
        labels={
            "hour": "Hour of Day",
            "revenue": "Revenue (£)"
        },
        template="plotly_white"
    )

    st.plotly_chart(
        fig_hour,
        width="stretch"
    )


# ==========================================
# 13. CUSTOMER DATA TABLE
# ==========================================

st.divider()

st.subheader("Top Customer Details")

st.dataframe(
    top_customers,
    width="stretch",
    hide_index=True
)


# ==========================================
# 14. PRODUCT DATA TABLE
# ==========================================

st.subheader("Top Product Details")

st.dataframe(
    product_sales,
    width="stretch",
    hide_index=True
)


# ==========================================
# 15. DOWNLOAD FILTERED DATA
# ==========================================

st.divider()

st.subheader("Download Analysis Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Sales Data",
    data=csv_data,
    file_name="ecommerce_sales_analysis.csv",
    mime="text/csv"
)


# ==========================================
# 16. FOOTER
# ==========================================

st.caption(
    "E-Commerce Business Intelligence | "
    "Built using Python, PostgreSQL, Pandas, "
    "Plotly and Streamlit"
)

