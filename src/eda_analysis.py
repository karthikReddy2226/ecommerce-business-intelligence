
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. LOAD CLEANED DATASET
# ==========================================

file_path = "data/processed/cleaned_online_retail.csv"

df = pd.read_csv(
    file_path,
    dtype={"InvoiceNo": str},
    low_memory=False
)

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Create output folders
os.makedirs("reports/figures", exist_ok=True)
os.makedirs("reports/summaries", exist_ok=True)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)


# ==========================================
# 2. BUSINESS KPIs
# ==========================================

total_revenue = df["Revenue"].sum()

total_orders = df["InvoiceNo"].nunique()

total_customers = df["CustomerID"].nunique()

total_products = df["StockCode"].nunique()

total_quantity = df["Quantity"].sum()

average_order_value = total_revenue / total_orders

print("\n========== BUSINESS KPIs ==========")

print("Total Revenue:", round(total_revenue, 2))
print("Total Orders:", total_orders)
print("Total Customers:", total_customers)
print("Total Products:", total_products)
print("Total Quantity Sold:", total_quantity)
print("Average Order Value:", round(average_order_value, 2))


# ==========================================
# 3. MONTHLY REVENUE ANALYSIS
# ==========================================

monthly_sales = (
    df.groupby(["Year", "Month", "MonthName"])["Revenue"]
    .sum()
    .reset_index()
)

monthly_sales = monthly_sales.sort_values(
    ["Year", "Month"]
)

monthly_sales["Period"] = (
    monthly_sales["Year"].astype(str)
    + "-"
    + monthly_sales["Month"].astype(str).str.zfill(2)
)

monthly_sales.to_csv(
    "reports/summaries/monthly_revenue.csv",
    index=False
)

fig1 = px.line(
    monthly_sales,
    x="Period",
    y="Revenue",
    markers=True,
    title="Monthly Revenue Trend",
    labels={
        "Period": "Month",
        "Revenue": "Revenue"
    }
)

fig1.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue",
    template="plotly_white"
)

fig1.write_html(
    "reports/figures/monthly_revenue.html"
)


# ==========================================
# 4. TOP 10 PRODUCTS
# ==========================================

top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

top_products.to_csv(
    "reports/summaries/top_products.csv",
    index=False
)

fig2 = px.bar(
    top_products.sort_values("Revenue"),
    x="Revenue",
    y="Description",
    orientation="h",
    title="Top 10 Products by Revenue",
    labels={
        "Revenue": "Revenue",
        "Description": "Product"
    }
)

fig2.update_layout(
    template="plotly_white"
)

fig2.write_html(
    "reports/figures/top_products.html"
)


# ==========================================
# 5. COUNTRY-WISE REVENUE
# ==========================================

country_sales = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

country_sales.to_csv(
    "reports/summaries/country_revenue.csv",
    index=False
)

fig3 = px.bar(
    country_sales.sort_values("Revenue"),
    x="Revenue",
    y="Country",
    orientation="h",
    title="Top 10 Countries by Revenue",
    labels={
        "Revenue": "Revenue",
        "Country": "Country"
    }
)

fig3.update_layout(
    template="plotly_white"
)

fig3.write_html(
    "reports/figures/country_revenue.html"
)


# ==========================================
# 6. DAILY SALES ANALYSIS
# ==========================================

daily_sales = (
    df.groupby("DayName")["Revenue"]
    .sum()
    .reindex([
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ])
    .reset_index()
)

daily_sales.columns = ["DayName", "Revenue"]

daily_sales.to_csv(
    "reports/summaries/daily_revenue.csv",
    index=False
)

fig4 = px.bar(
    daily_sales,
    x="DayName",
    y="Revenue",
    title="Revenue by Day of Week",
    labels={
        "DayName": "Day",
        "Revenue": "Revenue"
    }
)

fig4.update_layout(
    template="plotly_white"
)

fig4.write_html(
    "reports/figures/daily_revenue.html"
)


# ==========================================
# 7. HOURLY SALES ANALYSIS
# ==========================================

hourly_sales = (
    df.groupby("Hour")["Revenue"]
    .sum()
    .reset_index()
)

hourly_sales.to_csv(
    "reports/summaries/hourly_revenue.csv",
    index=False
)

fig5 = px.bar(
    hourly_sales,
    x="Hour",
    y="Revenue",
    title="Revenue by Hour of Day",
    labels={
        "Hour": "Hour",
        "Revenue": "Revenue"
    }
)

fig5.update_layout(
    template="plotly_white"
)

fig5.write_html(
    "reports/figures/hourly_revenue.html"
)


# ==========================================
# 8. CUSTOMER ANALYSIS
# ==========================================

customer_data = df.dropna(
    subset=["CustomerID"]
)

customer_sales = (
    customer_data.groupby("CustomerID")
    .agg(
        TotalRevenue=("Revenue", "sum"),
        TotalOrders=("InvoiceNo", "nunique"),
        TotalQuantity=("Quantity", "sum")
    )
    .reset_index()
)

customer_sales = customer_sales.sort_values(
    "TotalRevenue",
    ascending=False
)

customer_sales.to_csv(
    "reports/summaries/customer_analysis.csv",
    index=False
)

top_customers = customer_sales.head(10)

fig6 = px.bar(
    top_customers.sort_values("TotalRevenue"),
    x="TotalRevenue",
    y="CustomerID",
    orientation="h",
    title="Top 10 Customers by Revenue",
    labels={
        "TotalRevenue": "Revenue",
        "CustomerID": "Customer ID"
    }
)

fig6.update_layout(
    template="plotly_white"
)

fig6.write_html(
    "reports/figures/top_customers.html"
)


# ==========================================
# 9. SAVE KPI SUMMARY
# ==========================================

kpi_data = pd.DataFrame({
    "Metric": [
        "Total Revenue",
        "Total Orders",
        "Total Customers",
        "Total Products",
        "Total Quantity Sold",
        "Average Order Value"
    ],
    "Value": [
        total_revenue,
        total_orders,
        total_customers,
        total_products,
        total_quantity,
        average_order_value
    ]
})

kpi_data.to_csv(
    "reports/summaries/business_kpis.csv",
    index=False
)


# ==========================================
# 10. FINAL OUTPUT
# ==========================================

print("\n========== EDA COMPLETED ==========")

print("\nTop 10 Products:")
print(top_products)

print("\nTop 10 Countries:")
print(country_sales)

print("\nTop 10 Customers:")
print(top_customers)

print("\nAll charts saved in reports/figures/")
print("All summaries saved in reports/summaries/")
