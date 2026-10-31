-- ==========================================
-- E-COMMERCE BUSINESS INTELLIGENCE
-- PHASE 4: SQL BUSINESS ANALYSIS
-- ==========================================


-- QUERY 1: Overall Business Performance

SELECT
    ROUND(SUM(revenue)::numeric, 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT stock_code) AS total_products,
    SUM(quantity) AS total_quantity_sold,
    ROUND(
        SUM(revenue)::numeric /
        NULLIF(COUNT(DISTINCT invoice_no), 0), 2
    ) AS average_order_value
FROM online_retail;


-- QUERY 2: Monthly Revenue

SELECT
    DATE_TRUNC('month', invoice_date) AS sales_month,
    ROUND(SUM(revenue)::numeric, 2) AS monthly_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders
FROM online_retail
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY sales_month;


-- QUERY 3: Top 10 Products

SELECT
    stock_code,
    MAX(description) AS product_name,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(revenue)::numeric, 2) AS total_revenue
FROM online_retail
GROUP BY stock_code
ORDER BY total_revenue DESC
LIMIT 10;


-- QUERY 4: Country-wise Revenue

SELECT
    country,
    ROUND(SUM(revenue)::numeric, 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers
FROM online_retail
GROUP BY country
ORDER BY total_revenue DESC;


-- QUERY 5: Top 10 Customers

SELECT
    customer_id,
    ROUND(SUM(revenue)::numeric, 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(quantity) AS total_quantity
FROM online_retail
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;


-- QUERY 6: Repeat Customer Analysis

WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS total_orders
    FROM online_retail
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (
        WHERE total_orders > 1
    ) AS repeat_customers,
    COUNT(*) FILTER (
        WHERE total_orders = 1
    ) AS one_time_customers
FROM customer_orders;


-- QUERY 7: Monthly Revenue Growth

WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', invoice_date) AS sales_month,
        SUM(revenue) AS revenue
    FROM online_retail
    GROUP BY DATE_TRUNC('month', invoice_date)
),
sales_growth AS (
    SELECT
        sales_month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY sales_month
        ) AS previous_month_revenue
    FROM monthly_sales
)
SELECT
    sales_month,
    ROUND(revenue::numeric, 2) AS current_revenue,
    ROUND(previous_month_revenue::numeric, 2)
        AS previous_revenue,
    ROUND(
        (
            (revenue - previous_month_revenue)
            / NULLIF(previous_month_revenue, 0) * 100
        )::numeric,
        2
    ) AS growth_percentage
FROM sales_growth
ORDER BY sales_month;


-- QUERY 8: Best Performing Weekday

SELECT
    day_name,
    ROUND(SUM(revenue)::numeric, 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders
FROM online_retail
GROUP BY day_name
ORDER BY total_revenue DESC;


-- QUERY 9: Peak Shopping Hours

SELECT
    hour,
    ROUND(SUM(revenue)::numeric, 2) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS total_orders
FROM online_retail
GROUP BY hour
ORDER BY total_revenue DESC;


-- QUERY 10: Customer Revenue Ranking

WITH customer_revenue AS (
    SELECT
        customer_id,
        SUM(revenue) AS total_revenue
    FROM online_retail
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT
    customer_id,
    ROUND(total_revenue::numeric, 2) AS total_revenue,
    RANK() OVER (
        ORDER BY total_revenue DESC
    ) AS revenue_rank
FROM customer_revenue
ORDER BY revenue_rank
LIMIT 20;


-- ==========================================
-- DATABASE INDEXES
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_retail_invoice
ON online_retail(invoice_no);

CREATE INDEX IF NOT EXISTS idx_retail_customer
ON online_retail(customer_id);

CREATE INDEX IF NOT EXISTS idx_retail_country
ON online_retail(country);

CREATE INDEX IF NOT EXISTS idx_retail_date
ON online_retail(invoice_date);

CREATE INDEX IF NOT EXISTS idx_retail_product
ON online_retail(stock_code);