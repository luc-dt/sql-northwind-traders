# Northwind Traders — Analysis Report (for Management)

> **Prepared by:** LN - Data Analyst
> **Date:** 2026-08-28
> **Source:** Queries in `queries.sql` run against the Northwind PostgreSQL database.
> **Period covered:** July 1996 – May 1998 (23 months of sales).

---

## Executive Summary

| Metric | Value |
|---|---|
| Total revenue (Jul 1996 – May 1998) | **$1,265,793** |
| Average order value | **$1,525** |
| Best-performing category | **Beverages — 21.3% of all sales** |
| Best individual product | **Côte de Blaye — $153,897** |
| Fastest growth month | **Dec 1997 — +64.0% MoM** |

**Top 3 takeaways:**
1. **Five sales reps drive ~2/3 of revenue** — Margaret Peacock alone sold \$232,891 (>18% of the company total). Focus on recognizing this group and coaching the bottom of the team.
2. **Beverages + Dairy Products = ~40% of all sales** — these are our strategic core. Inventory and marketing should prioritize them.
3. **Revenue is strongly upward-trending** but with repeating monthly volatility — a year-end (Dec) boost and an early-Q1 surge pattern; plan staffing and stock accordingly.

---

## 1. Employee Sales Performance (Ranking)

**Query (Section 3, `queries.sql`):** `RANK() OVER (ORDER BY Total_Sales DESC)`

| Rank | Employee | Total Sales |
|---|---|---|
| 1 | Margaret Peacock | **$232,891** |
| 2 | Janet Leverling | $202,813 |
| 3 | Nancy Davolio | $192,108 |
| 4 | Andrew Fuller | $166,538 |
| 5 | Laura Callahan | $126,862 |
| 6 | Robert King | $124,568 |
| 7 | Anne Dodsworth | $77,308 |
| 8 | Michael Suyama | $73,913 |
| 9 | Steven Buchanan | $68,792 |

**Insight for management:** The top 5 reps (#1–5) generate about **$921k** of the **$1.27M** in revenue (**~73%**). Margaret Peacock's \$232,891 is more than **3.4×** Steven Buchanan's \$68,792. Recommended actions: recognize top performers, investigate whether the gap is territory/team size vs. performance, and coach or rebalance the bottom tier.

---

## 2. Running Total of Sales (Growth Trend)

**Query (Section 4, `queries.sql`):** `SUM(Total_Sales) OVER (ORDER BY Month)`

| Month | Monthly Sales | Cumulative |
|---|---|---|
| Jul 1996 | $27,862 | $27,862 |
| ... | ... | ... |
| Nov 1997 | $43,534 | $753,771 |
| Dec 1997 | $71,398 | **$825,169** |
| Jan 1998 | $94,222 | $919,391 |
| Feb 1998 | $99,415 | $1,018,807 |
| Mar 1998 | $104,854 | $1,123,661 |
| Apr 1998 | $123,799 | $1,247,459 |
| May 1998 | $18,334 | **$1,265,793** |

**Insight for management:** Revenue compounded from ~$28K (first month) to a **$1.27M** cumulative run-rate over 23 months. The strongest stretch is clearly **Q1 1998** (Jan–Apr each > $94K, peaking at $123.8K in Apr). This suggests growing demand we should plan inventory and hiring to support.

---

## 3. Month-over-Month Sales Growth Rate

**Query (Section 5, `queries.sql`):** `LAG(TotalSales) OVER (ORDER BY Year, Month)`

| Month | Growth Rate |
|---|---|
| Dec 1997 | **+64.0%** |
| Oct 1996 | +42.2% |
| Jul 1997 | +40.3% |
| Apr 1997 | +37.6% |
| Jan 1997 | +35.4% |
| ... | ... |
| Feb 1997 | −37.2% |
| Jun 1997 | −32.4% |
| May 1998 | −85.2% |

**Insight for management:** Sales grow **strongly but unevenly**. The biggest monthly spike is **Dec 1997 (+64%)** — clearly a seasonal year-end pattern. The drops (Feb 1997 −37%, May 1998 −85%) align with months following a peak, suggesting a **spike-then-ease rhythm**: plan inventory & promotions to smooth the troughs after high-demand months.

---

## 4. Customers with Above-Average Order Values

**Query (Section 6, `queries.sql`):** `AVG(Order_Value) OVER ()` — flag orders worth more than the global average of **$1,525**.

| Customer | Order | Order Value | Category |
|---|---|---|---|
| QUICK | 10865 | **$16,388** | Above Average |
| HANAR | 10981 | $15,810 | Above Average |
| SAVEA | 11030 | $12,615 | Above Average |
| RATTC | 10889 | $11,380 | Above Average |
| SIMOB | 10417 | $11,188 | Above Average |
| ... | ... | ... | ... |

**Insight for management:** A small set of customers (QUICK, HANAR, SAVEA, RATTC, SIMOB) place **very high-value orders** multiple times. These are prime targets for **loyalty programs and personalized promotions**. Also worth checking: the order-value *distribution* is quite extreme (the top order \$16,388 is ~11× the average) — so a handful of accounts carry a disproportionate share of revenue.

---

## 5. Category & Product Performance

**Query (Section 7, `queries.sql`):** `SUM("Total Sales") OVER ()` to get % of total; **Section 8:** `ROW_NUMBER() OVER (PARTITION BY Category_ID ...)` for top-3 per category.

### Category share of total sales

| Category | % of total sales |
|---|---|
| **Beverages** | **21.3%** |
| Dairy Products | 18.6% |
| Confections | 13.3% |
| Meat/Poultry | 12.9% |
| Seafood | 10.2% |
| Condiments | 8.4% |
| Produce | 7.8% |
| Grains/Cereals | 7.5% |

### Top products by category

| Category | Top product | Total Sales |
|---|---|---|
| Beverages | Côte de Blaye | **$153,897** |
| Dairy | Raclette Courdavault | $76,684 |
| Meat | Thüringer Rostbratwurst | $84,784 |
| Confections | Tarte au sucre | $50,737 |

**Insight for management:** **Beverages + Dairy = ~40% of revenue**, and Côte de Blaye alone accounts for more than every product in Grains/Cereals combined. We should ensure these fast-movers are **never out of stock**, and consider deeper marketing in the smaller categories (Produce, Grains/Cereals — each <8%) to grow them.

---

## 6. Recommended Next Steps

1. **Employee performance:** reward top 5 reps; investigate the bottom-2 productivity gap; consider a mentoring program.
2. **Inventory:** prioritize Beverages & Dairy stock; never stock-out Côte de Blaye / Raclette Courdavault.
3. **Seasonality:** plan for the December spike and the post-spike trough (Feb 1997, May 1998 patterns).
4. **Customers:** launch a loyalty program targeting high-repeat/high-value accounts (QUICK, HANAR, SAVEA, RATTC).

---

*End of report.*