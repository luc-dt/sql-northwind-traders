-- ============================================================================
-- Northwind Traders — Window Functions & CTE Practice
-- ============================================================================
-- A collection of the final analytical queries from the Jupyter notebook
-- (eda-northwind-traders.ipynb), consolidated into a single runnable script.
-- Each query answers one of the four business questions and demonstrates a
-- specific window function / CTE pattern.
--
-- Source DB : Northwind for PostgreSQL (Dockerized, port 55432)
-- How to run: psql -U postgres -d northwind -f queries.sql
--             (or run each query individually in pgAdmin / psql)
--
-- Sections:
--   3. Rank employees by sales performance .............. RANK()
--   4. Running total of sales per month ................. SUM() OVER (ORDER BY ...)
--   5. Month-over-month sales growth rate ............... LAG()
--   6. Customers with above-average order values ........ AVG() OVER ()
--   7. Category percentage of total sales ............... SUM() OVER ()
--   8. Top 3 products sold in each category ............. ROW_NUMBER() OVER (PARTITION BY ...)
-- ============================================================================


-- ============================================================================
-- SECTION 3 — Rank employees by sales performance
-- ----------------------------------------------------------------------------
-- BUSINESS QUESTION (#1): Who are our best-selling sales representatives?
-- WINDOW FUNCTION: RANK() OVER (ORDER BY Total_Sales DESC)
--   - RANK() assigns a position number ordered by the largest revenue.
--   - Use RANK (not ROW_NUMBER) so equal revenues share the same rank.
-- PATTERN: CTE aggregates revenue per employee, OUTER query ranks them.
-- ============================================================================
WITH employeeSales AS (
    SELECT
        e.employee_id,
        e.first_name,
        e.last_name,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS Total_Sales
    FROM orders o
        JOIN order_details od ON o.order_id = od.order_id
        JOIN employees     e  ON e.employee_id = o.employee_id
    GROUP BY e.employee_id
)
SELECT
    employee_id,
    first_name,
    last_name,
    RANK() OVER (ORDER BY Total_Sales DESC) AS Sales_Rank
FROM employeeSales
ORDER BY Sales_Rank;


-- ============================================================================
-- SECTION 4 — Running total of sales per month
-- ----------------------------------------------------------------------------
-- BUSINESS QUESTION (#3): How does cumulative revenue build up month over month?
-- WINDOW FUNCTION: SUM(Total_Sales) OVER (ORDER BY "Month")
--   - With only an ORDER BY (no frame), the default frame is
--     RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.
--   - So each row = sum of ALL months up to AND including the current month.
-- PATTERN: monthlySales CTE gives total revenue per month; the window adds
--          the running (cumulative) total. Final row = lifetime revenue.
-- ============================================================================
WITH monthlySales AS (
    SELECT
        DATE_TRUNC('month', order_date)::date AS "Month",
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS Total_Sales
    FROM orders o
        INNER JOIN order_details od ON o.order_id = od.order_id
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    "Month",
    Total_Sales,
    SUM(Total_Sales) OVER (ORDER BY "Month") AS "Running Total"
FROM monthlySales
ORDER BY "Month";


-- ============================================================================
-- SECTION 5 — Month-over-month sales growth rate
-- ----------------------------------------------------------------------------
-- BUSINESS QUESTION (#3): Is the business growing? By how much month over month?
-- WINDOW FUNCTION: LAG(TotalSales) OVER (ORDER BY Year, Month)
--   - LAG() reads a value from a PREVIOUS row in the window (offset 1 by default).
--   - The FIRST month has no previous row  ->  LAG() returns NULL.
--   - NULL propagates through arithmetic, so the first month's growth is NULL too
--     (expected: there's nothing to compare it with).
-- PATTERN: MonthlySales CTE aggregates per month; LaggedSales CTE pulls the
--          previous month; outer query computes the % change.
-- ============================================================================
WITH MonthlySales AS (
    SELECT
        EXTRACT('month' FROM Order_Date) AS Month,
        EXTRACT('year'  FROM Order_Date) AS Year,
        SUM(Unit_Price * Quantity * (1 - Discount)) AS TotalSales
    FROM orders o
        JOIN order_details od ON o.order_id = od.order_id
    GROUP BY EXTRACT('month' FROM Order_Date), EXTRACT('year' FROM Order_Date)
),
LaggedSales AS (
    SELECT
        Year,
        Month,
        TotalSales,
        LAG(TotalSales) OVER (ORDER BY Year, Month) AS PreviousMonthSales
    FROM MonthlySales
)
SELECT
    Year,
    Month,
    ((TotalSales - PreviousMonthSales) / PreviousMonthSales) * 100 AS "Growth Rate"
FROM LaggedSales
ORDER BY Year, Month;
-- ============================================================================
-- SECTION 6 — Customers with above-average order values
-- ----------------------------------------------------------------------------
-- BUSINESS QUESTION (#4): Which orders are worth more than the company average?
-- WINDOW FUNCTION: AVG(Order_Value) OVER ()
--   - With an EMPTY window frame, AVG() runs over the ENTIRE result set.
--   - So every row is compared against one global average (no PARTITION BY).
-- PATTERN: OrderValues CTE computes total value per order; outer query labels
--          each order Above/Below the global average with a CASE expression.
-- ============================================================================
WITH OrderValues AS (
    SELECT
        o.customer_id,
        o.order_id,
        SUM(unit_price * quantity * (1 - discount)) AS "Order Value"
    FROM orders o
        INNER JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id, o.order_id
)
SELECT
    customer_id,
    order_id,
    "Order Value",
    CASE
        WHEN "Order Value" > AVG("Order Value") OVER () THEN 'Above Average'
        ELSE 'Below Average'
    END AS "Value Category"
FROM OrderValues
ORDER BY "Order Value" DESC;


-- ============================================================================
-- SECTION 7 — Percentage of total sales for each product category
-- ----------------------------------------------------------------------------
-- BUSINESS QUESTION (#2): Which product categories drive the most revenue?
-- WINDOW FUNCTION: SUM("Total Sales") OVER ()
--   - The empty frame again = grand total across ALL categories.
--   - Used as the denominator: category_sales / grand_total * 100 = percentage.
--   - This is much cleaner than a self-join or a subquery for the denominator.
-- PATTERN: CategorySales CTE aggregates revenue per category; outer query
--          divides by the global window total to get the share.
-- ============================================================================
WITH CategorySales AS (
    SELECT
        c.category_id,
        c.category_name,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS "Total Sales"
    FROM categories c
        INNER JOIN products p       ON c.category_id = p.Category_ID
        INNER JOIN order_details od ON p.product_id = od.product_id
    GROUP BY c.category_id
)
SELECT
    category_id,
    category_name,
    "Total Sales",
    ("Total Sales" / SUM("Total Sales") OVER ()) * 100 AS "Sales Percentage"
FROM CategorySales
ORDER BY "Sales Percentage" DESC;


-- ============================================================================
-- SECTION 8 — Top 3 products sold in each category
-- ----------------------------------------------------------------------------
-- BUSINESS QUESTION (#2): Within each category, which are the top sellers?
-- WINDOW FUNCTION: ROW_NUMBER() OVER (PARTITION BY Category_ID ORDER BY ...)
--   - PARTITION BY groups the rows per category; the rank restarts at 1 in
--     every category.
--   - ORDER BY "Total Sales" DESC ranks within each partition.
-- PATTERN: ProductSales CTE aggregates revenue per product; a subquery assigns
--          the row number per category; outer query filters to rn <= 3.
--   - Filtering on a window function requires a subquery/CTE because window
--     functions run after WHERE.
-- ============================================================================
WITH ProductSales AS (
    SELECT
        p.category_id,
        p.product_id,
        p.product_name,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS "Total Sales"
    FROM products p
        INNER JOIN order_details od ON p.product_id = od.product_id
    GROUP BY p.category_id, p.product_id
)
SELECT
    Category_ID,
    Product_ID,
    Product_Name,
    "Total Sales"
FROM (
    SELECT
        Category_ID,
        Product_ID,
        Product_Name,
        "Total Sales",
        ROW_NUMBER() OVER (PARTITION BY Category_ID ORDER BY "Total Sales" DESC) AS rn
    FROM ProductSales
) tmp
WHERE rn <= 3
ORDER BY Category_ID, rn;