"""
Northwind Traders — Analytics Dashboard
========================================
A Streamlit dashboard that visualizes all insights from analysis.md,
pulling live data from the Dockerized PostgreSQL database.

Run:  streamlit run dashboard.py
Requires: docker compose up -d  (PostgreSQL on localhost:55432)
"""

import os
import streamlit as st
import psycopg
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIG (must be first Streamlit call)
# ============================================================================
st.set_page_config(
    page_title="Northwind Traders — Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# THEME TOGGLE
# ============================================================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


IS_DARK = st.session_state.theme == "dark"

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
# Check Streamlit Cloud secrets, then env variable, then default local docker
DB_URL = st.secrets.get("DB_URL", os.getenv("DB_URL", "postgresql://postgres:postgres@localhost:55432/northwind"))


@st.cache_resource
def get_connection():
    """Persistent DB connection (cached across reruns)."""
    return psycopg.connect(DB_URL, autocommit=True)


@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    """Run a SQL query and return as DataFrame. Cached for 5 minutes."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d.name for d in cur.description] if cur.description else []
    return pd.DataFrame(rows, columns=cols)


# ============================================================================
# COLOR PALETTE & DESIGN TOKENS
# ============================================================================
COLORS = {
    "bg": "#09090b" if IS_DARK else "#ffffff",
    "bg_subtle": "#0c0c0f" if IS_DARK else "#f9fafb",
    "card": "#0c0c0f" if IS_DARK else "#ffffff",
    "card_hover": "#131316" if IS_DARK else "#f4f4f5",
    "border": "#1e1e24" if IS_DARK else "#e4e4e7",
    "border_subtle": "#16161a" if IS_DARK else "#f0f0f2",
    "text": "#fafafa" if IS_DARK else "#09090b",
    "text_muted": "#71717a",
    "text_dim": "#52525b" if IS_DARK else "#a1a1aa",
    "accent": "#2563eb",
    "accent_muted": "#1d4ed8",
    "green": "#22c55e" if IS_DARK else "#16a34a",
    "green_muted": "rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)",
    "red": "#ef4444" if IS_DARK else "#dc2626",
    "red_muted": "rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)",
    "amber": "#f59e0b" if IS_DARK else "#d97706",
    "amber_muted": "rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)",
    "shadow": "none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)",
    "grid": "rgba(255,255,255,0.04)" if IS_DARK else "rgba(0,0,0,0.04)",
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="DM Sans, sans-serif",
        color=COLORS["text_muted"],
        size=11,
    ),
    margin=dict(l=0, r=0, t=8, b=0),
    xaxis=dict(
        gridcolor=COLORS["grid"],
        zerolinecolor=COLORS["grid"],
        tickfont=dict(size=10, color=COLORS["text_muted"]),
    ),
    yaxis=dict(
        gridcolor=COLORS["grid"],
        zerolinecolor=COLORS["grid"],
        tickfont=dict(size=10, color=COLORS["text_muted"]),
    ),
)

# ============================================================================
# CSS INJECTION
# ============================================================================
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
    --bg: {COLORS['bg']};
    --bg-subtle: {COLORS['bg_subtle']};
    --card: {COLORS['card']};
    --card-hover: {COLORS['card_hover']};
    --border: {COLORS['border']};
    --border-subtle: {COLORS['border_subtle']};
    --text: {COLORS['text']};
    --text-muted: {COLORS['text_muted']};
    --text-dim: {COLORS['text_dim']};
    --accent: {COLORS['accent']};
    --green: {COLORS['green']};
    --green-muted: {COLORS['green_muted']};
    --red: {COLORS['red']};
    --red-muted: {COLORS['red_muted']};
    --amber: {COLORS['amber']};
    --amber-muted: {COLORS['amber_muted']};
    --shadow: {COLORS['shadow']};
    --radius: 10px;
}}

/* --- Hide Streamlit chrome --- */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

/* --- Global --- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
.main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}
.block-container {{
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1360px !important;
}}

/* --- Column gaps --- */
[data-testid="stHorizontalBlock"] {{ gap: 1.25rem !important; }}
[data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]) {{
    margin-bottom: 0.5rem !important;
}}

/* --- Tabs (pill-style) --- */
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.835rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1rem !important;
    border: 1px solid transparent !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
    display: none !important;
}}
[data-baseweb="tab-list"] {{
    gap: 4px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 3px;
}}

/* --- Metric cards --- */
.metric-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow);
    transition: border-color 0.2s ease;
}}
.metric-card:hover {{
    border-color: var(--accent);
}}
.metric-label {{
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.metric-value {{
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.3rem;
}}
.metric-delta {{
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.4rem;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}}
.delta-up {{ color: var(--green); background: var(--green-muted); }}
.delta-down {{ color: var(--red); background: var(--red-muted); }}
.delta-warn {{ color: var(--amber); background: var(--amber-muted); }}

/* --- Chart wrapper --- */
.chart-wrap {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.2rem 0.6rem;
    box-shadow: var(--shadow);
}}
.chart-title {{
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
}}
.chart-subtitle {{
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-bottom: 0.8rem;
}}

/* --- Data tables --- */
.data-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.8rem;
}}
.data-table th {{
    text-align: left;
    padding: 0.6rem 0.8rem;
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border);
}}
.data-table td {{
    padding: 0.65rem 0.8rem;
    color: var(--text);
    border-bottom: 1px solid var(--border-subtle);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
}}
.data-table td.name-col {{
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
}}
.data-table tr:last-child td {{ border-bottom: none; }}
.data-table tr:hover td {{ background: var(--card-hover); }}

/* --- Badges --- */
.badge {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 500;
}}
.badge-green {{ color: var(--green); background: var(--green-muted); }}
.badge-red {{ color: var(--red); background: var(--red-muted); }}
.badge-amber {{ color: var(--amber); background: var(--amber-muted); }}
.badge-blue {{ color: var(--accent); background: rgba(37,99,235,0.1); }}

/* --- Recommendation cards --- */
.rec-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}}
.rec-card:hover {{
    border-color: var(--accent);
}}
.rec-number {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(37,99,235,0.1);
    color: var(--accent);
    font-weight: 700;
    font-size: 0.82rem;
    margin-bottom: 0.6rem;
    font-family: 'JetBrains Mono', monospace;
}}
.rec-title {{
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.4rem;
}}
.rec-body {{
    font-size: 0.82rem;
    color: var(--text-muted);
    line-height: 1.5;
}}

/* --- Brand header --- */
.brand {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}
.brand-icon {{
    font-size: 1.3rem;
}}
.brand-name {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.02em;
}}
.brand-sub {{
    font-size: 0.75rem;
    color: var(--text-dim);
    margin-left: 0.3rem;
}}

/* --- Streamlit button override --- */
.stButton > button {{
    background: var(--card) !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    border-color: var(--accent) !important;
    color: var(--text) !important;
}}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def metric_card(label: str, value: str, delta: str = None, delta_type: str = "up"):
    """Render a styled KPI metric card."""
    cls = f"delta-{delta_type}"
    arrow = "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "→")
    delta_html = (
        f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    )
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def chart_container(title: str, subtitle: str = ""):
    """Open a chart wrapper div. Must call chart_container_end() after the chart."""
    sub_html = f'<div class="chart-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
    <div class="chart-wrap">
        <div class="chart-title">{title}</div>
        {sub_html}
    """,
        unsafe_allow_html=True,
    )


def chart_container_end():
    """Close the chart wrapper div."""
    st.markdown("</div>", unsafe_allow_html=True)


def fmt_currency(val) -> str:
    """Format a number as currency."""
    return f"${val:,.0f}"


def fmt_pct(val) -> str:
    """Format as percentage."""
    return f"{val:+.1f}%" if val is not None else "N/A"


# ============================================================================
# QUERIES
# ============================================================================
QUERY_KPIS = """
SELECT
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(od.unit_price * od.quantity * (1 - od.discount))
        / COUNT(DISTINCT o.order_id) AS avg_order_value
FROM orders o
JOIN order_details od ON o.order_id = od.order_id;
"""

QUERY_BEST_MONTH = """
SELECT
    DATE_TRUNC('month', order_date)::date AS month,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY total_sales DESC
LIMIT 1;
"""

QUERY_EMPLOYEE_RANK = """
WITH employee_sales AS (
    SELECT
        e.employee_id,
        e.first_name || ' ' || e.last_name AS employee_name,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    JOIN employees e ON e.employee_id = o.employee_id
    GROUP BY e.employee_id, e.first_name, e.last_name
)
SELECT
    employee_name,
    total_sales,
    RANK() OVER (ORDER BY total_sales DESC) AS sales_rank,
    total_sales / SUM(total_sales) OVER () * 100 AS pct_of_total
FROM employee_sales
ORDER BY sales_rank;
"""

QUERY_MONTHLY_SALES = """
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date)::date AS month,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    month,
    total_sales,
    SUM(total_sales) OVER (ORDER BY month) AS running_total
FROM monthly
ORDER BY month;
"""

QUERY_MOM_GROWTH = """
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date)::date AS month,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY DATE_TRUNC('month', order_date)
),
lagged AS (
    SELECT
        month,
        total_sales,
        LAG(total_sales) OVER (ORDER BY month) AS prev_sales
    FROM monthly
)
SELECT
    month,
    total_sales,
    CASE WHEN prev_sales IS NOT NULL AND prev_sales > 0
         THEN ((total_sales - prev_sales) / NULLIF(prev_sales, 0)) * 100
         ELSE NULL
    END AS growth_rate
FROM lagged
ORDER BY month;
"""

QUERY_CUSTOMER_ORDERS = """
WITH order_values AS (
    SELECT
        o.order_id,
        c.customer_id,
        c.company_name,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS order_value
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.order_id, c.customer_id, c.company_name
)
SELECT
    customer_id,
    company_name,
    COUNT(*) AS order_count,
    SUM(order_value) AS total_spent,
    AVG(order_value) AS avg_order_value,
    CASE
        WHEN AVG(order_value) > (SELECT AVG(order_value) FROM order_values) THEN 'Above Average'
        ELSE 'Below Average'
    END AS value_category
FROM order_values
GROUP BY customer_id, company_name
ORDER BY total_spent DESC;
"""

QUERY_CATEGORY_SHARE = """
WITH category_sales AS (
    SELECT
        c.category_id,
        c.category_name,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
    FROM categories c
    JOIN products p ON c.category_id = p.category_id
    JOIN order_details od ON p.product_id = od.product_id
    GROUP BY c.category_id, c.category_name
)
SELECT
    category_id,
    category_name,
    total_sales,
    total_sales / SUM(total_sales) OVER () * 100 AS sales_pct
FROM category_sales
ORDER BY sales_pct DESC;
"""

QUERY_TOP_PRODUCTS = """
WITH product_sales AS (
    SELECT
        c.category_name,
        p.product_id,
        p.product_name,
        SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
    FROM products p
    JOIN order_details od ON p.product_id = od.product_id
    JOIN categories c ON p.category_id = c.category_id
    GROUP BY c.category_name, p.product_id, p.product_name
),
ranked AS (
    SELECT
        category_name,
        product_name,
        total_sales,
        ROW_NUMBER() OVER (PARTITION BY category_name ORDER BY total_sales DESC) AS rn
    FROM product_sales
)
SELECT category_name, product_name, total_sales
FROM ranked
WHERE rn <= 3
ORDER BY category_name, rn;
"""


# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data(ttl=300)
def load_all_data():
    """Load all dashboard data in one pass."""
    return {
        "kpis": run_query(QUERY_KPIS),
        "best_month": run_query(QUERY_BEST_MONTH),
        "employees": run_query(QUERY_EMPLOYEE_RANK),
        "monthly": run_query(QUERY_MONTHLY_SALES),
        "growth": run_query(QUERY_MOM_GROWTH),
        "customers": run_query(QUERY_CUSTOMER_ORDERS),
        "categories": run_query(QUERY_CATEGORY_SHARE),
        "top_products": run_query(QUERY_TOP_PRODUCTS),
    }


try:
    data = load_all_data()
    db_connected = True
except Exception as e:
    db_connected = False
    db_error = str(e)


# ============================================================================
# HEADER
# ============================================================================
head_left, head_right = st.columns([8, 1])
with head_left:
    st.markdown(
        """
    <div class="brand">
        <span class="brand-icon">◆</span>
        <span class="brand-name">Northwind Traders</span>
        <span class="brand-sub">Analytics Dashboard</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)

# ============================================================================
# CONNECTION ERROR STATE
# ============================================================================
if not db_connected:
    st.error(
        f"**Could not connect to database.** Make sure Docker is running "
        f"(`docker compose up -d`).\n\nError: `{db_error}`"
    )
    st.stop()

# ============================================================================
# KPI ROW
# ============================================================================
kpi_row = data["kpis"].iloc[0]
best_month_row = data["best_month"].iloc[0]
best_month_label = pd.to_datetime(best_month_row["month"]).strftime("%b %Y")

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Total Revenue", fmt_currency(kpi_row["total_revenue"]))
with c2:
    metric_card("Total Orders", f"{int(kpi_row['total_orders']):,}")
with c3:
    metric_card("Avg Order Value", fmt_currency(kpi_row["avg_order_value"]))
with c4:
    metric_card(
        "Best Month",
        best_month_label,
        delta=fmt_currency(best_month_row["total_sales"]),
        delta_type="up",
    )

st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "👥 Employee Performance",
        "📈 Sales Growth",
        "🛒 Customer Insights",
        "📦 Category & Products",
        "💡 Recommendations",
    ]
)

# ------------------------------------------------------------------
# TAB 1 — Employee Performance
# ------------------------------------------------------------------
with tab1:
    df_emp = data["employees"]

    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        chart_container(
            "Employee Revenue Ranking",
            "Total net revenue per sales representative (all time)",
        )
        fig = px.bar(
            df_emp.sort_values("total_sales"),
            x="total_sales",
            y="employee_name",
            orientation="h",
            color_discrete_sequence=[COLORS["accent"]],
        )
        fig.update_layout(**PLOT_LAYOUT)
        fig.update_layout(
            yaxis_title="",
            xaxis_title="",
            height=380,
            xaxis=dict(
                tickprefix="$",
                tickformat=",.0f",
                gridcolor=COLORS["grid"],
                tickfont=dict(size=10, color=COLORS["text_muted"]),
            ),
            yaxis=dict(
                tickfont=dict(size=11, color=COLORS["text"]),
                gridcolor=COLORS["grid"],
            ),
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        chart_container_end()

    with col_table:
        chart_container("Detailed Ranking", "Rank, sales, and share of company total")
        rows_html = ""
        for _, r in df_emp.iterrows():
            rank_badge = (
                "badge-green"
                if r["sales_rank"] <= 3
                else ("badge-amber" if r["sales_rank"] <= 5 else "badge-red")
            )
            rows_html += f"""
            <tr>
                <td><span class="badge {rank_badge}">#{int(r['sales_rank'])}</span></td>
                <td class="name-col">{r['employee_name']}</td>
                <td>${r['total_sales']:,.0f}</td>
                <td>{r['pct_of_total']:.1f}%</td>
            </tr>"""
        st.markdown(
            f"""
        <table class="data-table">
            <thead><tr>
                <th>Rank</th><th>Employee</th><th>Revenue</th><th>Share</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""",
            unsafe_allow_html=True,
        )
        chart_container_end()

# ------------------------------------------------------------------
# TAB 2 — Sales Growth
# ------------------------------------------------------------------
with tab2:
    df_monthly = data["monthly"].copy()
    df_growth = data["growth"].copy()
    df_monthly["month"] = pd.to_datetime(df_monthly["month"])
    df_growth["month"] = pd.to_datetime(df_growth["month"])

    # --- Monthly revenue + running total ---
    chart_container(
        "Monthly Revenue & Cumulative Total",
        "Net revenue per month with running total overlay (Jul 1996 – May 1998)",
    )
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=df_monthly["month"],
            y=df_monthly["total_sales"],
            name="Monthly Revenue",
            marker_color=COLORS["accent"],
            opacity=0.7,
            hovertemplate="<b>%{x|%b %Y}</b><br>Monthly: $%{y:,.0f}<extra></extra>",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=df_monthly["month"],
            y=df_monthly["running_total"],
            name="Cumulative",
            mode="lines+markers",
            line=dict(color=COLORS["green"], width=2.5),
            marker=dict(size=4),
            yaxis="y2",
            hovertemplate="<b>%{x|%b %Y}</b><br>Cumulative: $%{y:,.0f}<extra></extra>",
        )
    )
    fig2.update_layout(**PLOT_LAYOUT)
    fig2.update_layout(
        height=360,
        yaxis=dict(
            title="Monthly ($)",
            tickprefix="$",
            tickformat=",.0f",
            gridcolor=COLORS["grid"],
            tickfont=dict(size=10, color=COLORS["text_muted"]),
        ),
        yaxis2=dict(
            title="Cumulative ($)",
            overlaying="y",
            side="right",
            tickprefix="$",
            tickformat=",.0f",
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(size=10, color=COLORS["green"]),
        ),
        xaxis=dict(
            tickformat="%b %Y",
            gridcolor=COLORS["grid"],
            tickfont=dict(size=10, color=COLORS["text_muted"]),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11),
        ),
        bargap=0.3,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    chart_container_end()

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # --- Month-over-month growth rate ---
    chart_container(
        "Month-over-Month Growth Rate",
        "Percentage change vs. previous month (positive = green, negative = red)",
    )
    df_g = df_growth.dropna(subset=["growth_rate"]).copy()
    df_g["color"] = df_g["growth_rate"].apply(
        lambda x: COLORS["green"] if x >= 0 else COLORS["red"]
    )
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=df_g["month"],
            y=df_g["growth_rate"],
            marker_color=df_g["color"].tolist(),
            hovertemplate="<b>%{x|%b %Y}</b><br>Growth: %{y:+.1f}%<extra></extra>",
        )
    )
    fig3.update_layout(**PLOT_LAYOUT)
    fig3.update_layout(
        height=300,
        xaxis=dict(
            tickformat="%b %Y",
            gridcolor=COLORS["grid"],
            tickfont=dict(size=10, color=COLORS["text_muted"]),
        ),
        yaxis=dict(
            title="Growth (%)",
            ticksuffix="%",
            gridcolor=COLORS["grid"],
            tickfont=dict(size=10, color=COLORS["text_muted"]),
            zerolinecolor=COLORS["text_muted"],
            zerolinewidth=1,
        ),
        bargap=0.3,
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    chart_container_end()

    # --- Highlight best & worst months ---
    best = df_g.loc[df_g["growth_rate"].idxmax()]
    worst = df_g.loc[df_g["growth_rate"].idxmin()]
    hl1, hl2 = st.columns(2)
    with hl1:
        metric_card(
            "Strongest Growth",
            pd.to_datetime(best["month"]).strftime("%b %Y"),
            delta=f"{best['growth_rate']:+.1f}%",
            delta_type="up",
        )
    with hl2:
        metric_card(
            "Largest Decline",
            pd.to_datetime(worst["month"]).strftime("%b %Y"),
            delta=f"{worst['growth_rate']:+.1f}%",
            delta_type="down",
        )

# ------------------------------------------------------------------
# TAB 3 — Customer Insights
# ------------------------------------------------------------------
with tab3:
    df_cust = data["customers"]

    col_scatter, col_tbl = st.columns([3, 2])

    with col_scatter:
        chart_container(
            "Customer Value Map",
            "Each dot = one customer. Size = total spent. Color = above/below average order value.",
        )
        fig4 = px.scatter(
            df_cust,
            x="order_count",
            y="avg_order_value",
            size="total_spent",
            color="value_category",
            color_discrete_map={
                "Above Average": COLORS["green"],
                "Below Average": COLORS["text_dim"],
            },
            hover_name="company_name",
            hover_data={
                "order_count": True,
                "avg_order_value": ":.0f",
                "total_spent": ":.0f",
                "value_category": False,
            },
            size_max=40,
        )
        fig4.update_layout(**PLOT_LAYOUT)
        fig4.update_layout(
            height=420,
            xaxis=dict(
                title="Order Count",
                gridcolor=COLORS["grid"],
                tickfont=dict(size=10, color=COLORS["text_muted"]),
            ),
            yaxis=dict(
                title="Avg Order Value ($)",
                tickprefix="$",
                tickformat=",.0f",
                gridcolor=COLORS["grid"],
                tickfont=dict(size=10, color=COLORS["text_muted"]),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=11),
            ),
        )
        st.plotly_chart(
            fig4, use_container_width=True, config={"displayModeBar": False}
        )
        chart_container_end()

    with col_tbl:
        chart_container("Top 15 Customers", "Ranked by total spending")
        df_top15 = df_cust.head(15)
        rows_html = ""
        for _, r in df_top15.iterrows():
            badge_cls = (
                "badge-green"
                if r["value_category"] == "Above Average"
                else "badge-amber"
            )
            rows_html += f"""
            <tr>
                <td class="name-col">{r['company_name']}</td>
                <td>{int(r['order_count'])}</td>
                <td>${r['total_spent']:,.0f}</td>
                <td><span class="badge {badge_cls}">{r['value_category']}</span></td>
            </tr>"""
        st.markdown(
            f"""
        <table class="data-table">
            <thead><tr>
                <th>Customer</th><th>Orders</th><th>Total Spent</th><th>Avg Value</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""",
            unsafe_allow_html=True,
        )
        chart_container_end()

# ------------------------------------------------------------------
# TAB 4 — Category & Product Performance
# ------------------------------------------------------------------
with tab4:
    df_cat = data["categories"]
    df_prods = data["top_products"]

    col_donut, col_bar = st.columns(2)

    with col_donut:
        chart_container(
            "Category Share of Total Sales",
            "Percentage of total revenue by product category",
        )
        fig5 = go.Figure(
            go.Pie(
                labels=df_cat["category_name"],
                values=df_cat["total_sales"],
                hole=0.55,
                marker=dict(
                    colors=px.colors.qualitative.Set2[: len(df_cat)],
                    line=dict(color=COLORS["bg"], width=2),
                ),
                textinfo="label+percent",
                textposition="outside",
                textfont=dict(size=11, color=COLORS["text_muted"]),
                hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
            )
        )
        fig5.update_layout(**PLOT_LAYOUT)
        fig5.update_layout(
            height=400,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(
            fig5, use_container_width=True, config={"displayModeBar": False}
        )
        chart_container_end()

    with col_bar:
        chart_container(
            "Top 3 Products by Category",
            "Best-selling product in each category by net revenue",
        )
        fig6 = px.bar(
            df_prods,
            x="total_sales",
            y="category_name",
            color="product_name",
            orientation="h",
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig6.update_layout(**PLOT_LAYOUT)
        fig6.update_layout(
            height=400,
            yaxis_title="",
            xaxis=dict(
                title="",
                tickprefix="$",
                tickformat=",.0f",
                gridcolor=COLORS["grid"],
                tickfont=dict(size=10, color=COLORS["text_muted"]),
            ),
            yaxis=dict(
                tickfont=dict(size=11, color=COLORS["text"]),
                gridcolor=COLORS["grid"],
                categoryorder="total ascending",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=10),
                title="",
            ),
        )
        fig6.update_traces(
            hovertemplate="<b>%{y}</b> — %{data.name}<br>Revenue: $%{x:,.0f}<extra></extra>"
        )
        st.plotly_chart(
            fig6, use_container_width=True, config={"displayModeBar": False}
        )
        chart_container_end()

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # --- Category detail table ---
    chart_container("Category Details", "All 8 product categories with revenue and share")
    rows_html = ""
    for _, r in df_cat.iterrows():
        bar_width = r["sales_pct"]
        rows_html += f"""
        <tr>
            <td class="name-col">{r['category_name']}</td>
            <td>${r['total_sales']:,.0f}</td>
            <td>
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="width:{bar_width * 3}px;height:6px;background:{COLORS['accent']};border-radius:3px"></div>
                    <span>{r['sales_pct']:.1f}%</span>
                </div>
            </td>
        </tr>"""
    st.markdown(
        f"""
    <table class="data-table">
        <thead><tr>
            <th>Category</th><th>Revenue</th><th>Share of Total</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""",
        unsafe_allow_html=True,
    )
    chart_container_end()

# ------------------------------------------------------------------
# TAB 5 — Recommendations
# ------------------------------------------------------------------
with tab5:
    st.markdown(
        "<div style='height: 0.5rem'></div>",
        unsafe_allow_html=True,
    )

    recommendations = [
        {
            "title": "Employee Performance",
            "body": "Reward top 5 reps who drive ~73% of revenue. Investigate the "
            "productivity gap between the top (Peacock — $232K) and bottom "
            "(Buchanan — $69K). Consider a mentoring program to uplift the lower tier.",
        },
        {
            "title": "Inventory Optimization",
            "body": "Prioritize Beverages & Dairy Products stock — they account for ~40% "
            "of all sales. Never stock-out Côte de Blaye (top product at ~$141K) "
            "or Raclette Courdavault (~$71K). Consider deeper marketing for smaller "
            "categories (Produce, Grains/Cereals — each < 8%).",
        },
        {
            "title": "Seasonal Planning",
            "body": "Plan for the December spike (+64% MoM in Dec 1997) and the post-spike "
            "trough (Feb, May patterns). Adjust staffing and inventory pre-orders to "
            "smooth revenue through slow months.",
        },
        {
            "title": "Customer Loyalty Program",
            "body": "Launch a loyalty program targeting high-repeat / high-value accounts "
            "(QUICK, HANAR, SAVEA, RATTC). The top order ($16,388) is ~11× the "
            "average — a handful of accounts carry disproportionate revenue. "
            "Personalized promotions could increase retention and order frequency.",
        },
    ]

    col_left, col_right = st.columns(2)
    for i, rec in enumerate(recommendations):
        with col_left if i % 2 == 0 else col_right:
            st.markdown(
                f"""
            <div class="rec-card">
                <div class="rec-number">{i + 1}</div>
                <div class="rec-title">{rec['title']}</div>
                <div class="rec-body">{rec['body']}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown(
    f"""
<div style="text-align:center; margin-top:3rem; padding:1.5rem 0; border-top:1px solid {COLORS['border']}">
    <span style="font-size:0.72rem; color:{COLORS['text_dim']}">
        Northwind Traders Analytics · Data period: Jul 1996 – May 1998 · 
        Source: PostgreSQL (localhost:55432)
    </span>
</div>
""",
    unsafe_allow_html=True,
)
