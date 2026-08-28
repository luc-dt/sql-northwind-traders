# Learning Diary — SQL Window Functions & CTE Project

> **Analyst:** [Your Name]
> **Project:** Northwind Traders — Window Functions & CTEs
> **Purpose:** Log what worked, what didn't, and what I learned — turning mistakes into growth.

---

## Phase 0–1 — DE Setup (Docker + Postgres)

**What I did**
- Got the source files (`docker-compose.yml`, `northwind.sql`, ER diagrams) from the
  [Northwind for PostgreSQL](https://github.com/pthom/northwind_psql) repo.
- Started Docker Desktop, ran `docker compose up -d` → `northwind_db` (PostgreSQL on port
  `55432`) + `northwind_pgadmin` (port `5050`), auto-seeded.
- Verified tables (`\dt`), explored schema with `\d`, browsed the ER diagram in pgAdmin.

**What I learned**
- The container runs the **Postgres server inside Docker**; our machine talks to it through a
  **published port** (`55432` → container `5432`). From inside the docker network it's `db:5432`.
- `docker compose down` stops containers but **keeps data** (named volume). `down -v` wipes it.
- psycopg + pandas is a clean "raw Postgres" connection layer — no SQLAlchemy needed.

**Mistake / fix**
- First connection attempts failed until I used `localhost:55432` (published port) instead of
  the internal `db:5432` from the notebook. → Read the published port in `docker ps`.

---

## Phase 2 — SQL Baseline (JOINs, GROUP BY)

**What I did**
- Warm-ups: `SELECT` / `WHERE` / `ORDER BY`; joined `orders`, `order_details`, `products`,
  `categories`, `customers`, `employees`; aggregated with `SUM` / `AVG` / `COUNT`.
- Verified the grain: `(order_id, product_id)` is unique in `order_details` (returns 0 dup rows).

**What I learned**
- Grain matters: one row per product-in-order, not one row per order or per unit.
- Always sanity-check joins for **row multiplication** (a bad JOIN can silently inflate SUMs).

---

## Phase 3 — Window Functions & CTEs (the core)

### 3.1 — Employee ranking (`RANK()`)
- **Pattern:** CTE aggregates revenue per employee → outer query `RANK() OVER (ORDER BY Total_Sales DESC)`.
- **Learned:** `RANK()` vs `ROW_NUMBER()` vs `DENSE_RANK()`. `RANK()` leaves gaps after ties;
  `DENSE_RANK()` doesn't. Use the right one for the business question.
- **Result:** Peacock #1 (\$232,891), Leverling #2, Davolio #3; bottom = Suyama, Buchanan.

### 3.2 — Running total per month (`SUM() OVER (ORDER BY ...)`)
- **Pattern:** `monthlySales` CTE → `SUM(Total_Sales) OVER (ORDER BY "Month")`.
- **Learned:** With only `ORDER BY` (no frame), the **default frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`** — so it accumulates correctly.
- **Result:** cumulative climbs from \$27,862 (Jul '96) to **\$1,265,793** (May '98).
- **Gotcha:** pandas showed scientific notation (`1.265793e+06`) — fixed the **display** with
  `pd.set_option('display.float_format', lambda x: f'{x:,.2f}')`. The SQL value was always correct.

### 3.3 — Month-over-month growth (`LAG()`)
- **Pattern:** `LAG(TotalSales) OVER (ORDER BY Year, Month)` → `(cur - prev) / prev * 100`.
- **Learned:** The **first row returns NULL** (no previous value) — that's expected, not a bug.
  NULL propagates through arithmetic, so guard for it in reporting.
- **Result:** Dec '97 +64%, Oct '96 +42%, Jul '97 +40%; biggest dip May '98 −85%.

### 3.4 — Above-average order values (`AVG() OVER ()`)
- **Pattern:** empty window frame = **whole table**. Compare each order to the global average.
- **Learned:** `AVG() OVER ()` is much cleaner than a self-join or subquery for the denominator.
- **Result:** avg order \$1,525; flagged QUICK 10865 (\$16,388), HANAR 10981 (\$15,810), etc.

### 3.5 — Category % of total (`SUM() OVER ()`)
- **Pattern:** `category_sales / SUM(total) OVER () * 100`.
- **Learned:** same empty-frame trick as the average — denominator is the grand total.
- **Result:** Beverages 21.3%, Dairy 18.6%, Confections 13.3%, Meat 12.9%.

### 3.6 — Top 3 products per category (`ROW_NUMBER() OVER (PARTITION BY ...)`)
- **Pattern:** `ROW_NUMBER() OVER (PARTITION BY Category_ID ORDER BY Total_Sales DESC)`, then filter `rn <= 3`.
- **Learned:** **You can't filter on a window function in WHERE** — must wrap in a subquery/CTE.
- **Result:** top product per category: Côte de Blaye (\$153.9K), Raclette (\$76.7K), Thüringer (\$84.8K), etc.

---

## Phase 4 — Deliverables

**What I created**
- `queries.sql` — all final queries, commented, consolidated in one runnable script.
- `analysis.md` — "report to management" with the real numbers and business recommendations.
- Updated `plan.md` + `README.md` to mark the project **complete**.

**What I learned**
- The notebook was the *workspace*; the deliverables are the *portfolio* that proves I can
  write window functions and turn results into business decisions.

---

## Overall takeaways
- Window functions run **after** `WHERE`/`GROUP BY` but **before** `ORDER BY`/`LIMIT` — that
  ordering is everything.
- CTEs make complex queries readable and reusable.
- Always verify a result makes sense against the data (running total ends at total revenue,
  growth = ±seasonal rhythm, categories sum to ~100%).

---
*End of diary.*