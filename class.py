# Advanced Dash Dashboard
# Install:
#   pip install dash dash-ag-grid pandas plotly numpy

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ══════════════════════════════════════════════════════════════════════════════
# 1. GENERATE RICH SAMPLE DATA
# ══════════════════════════════════════════════════════════════════════════════
np.random.seed(42)

REGIONS     = ["North", "South", "East", "West"]
CATEGORIES  = ["Electronics", "Clothing", "Food", "Furniture", "Sports"]
MONTHS      = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

rows = []
for month_i, month in enumerate(MONTHS):
    for region in REGIONS:
        for category in CATEGORIES:
            sales  = int(np.random.normal(500, 150))
            profit = int(sales * np.random.uniform(0.15, 0.40))
            units  = int(np.random.normal(80, 20))
            rows.append({
                "Month":    month,
                "MonthNum": month_i + 1,
                "Region":   region,
                "Category": category,
                "Sales":    max(sales,  50),
                "Profit":   max(profit, 10),
                "Units":    max(units,  5),
            })

df = pd.DataFrame(rows)

# ══════════════════════════════════════════════════════════════════════════════
# 2. THEME / STYLE CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
COLORS = {
    "bg":       "#0f1117",
    "sidebar":  "#1a1d27",
    "card":     "#1e2130",
    "accent":   "#635bff",
    "accent2":  "#00c9a7",
    "accent3":  "#ff6b6b",
    "accent4":  "#ffd166",
    "text":     "#e0e0e0",
    "subtext":  "#8b8fa8",
    "border":   "#2e3248",
}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "borderRadius":    "12px",
    "padding":         "20px",
    "boxShadow":       "0 4px 16px rgba(0,0,0,0.4)",
    "border":          f"1px solid {COLORS['border']}",
}

CHART_LAYOUT = dict(
    plot_bgcolor  = COLORS["card"],
    paper_bgcolor = COLORS["card"],
    font_color    = COLORS["text"],
    margin        = dict(l=40, r=20, t=40, b=40),
    legend        = dict(bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"]),
    xaxis         = dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
    yaxis         = dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
)

# ══════════════════════════════════════════════════════════════════════════════
# 3. HELPER: KPI CARD
# ══════════════════════════════════════════════════════════════════════════════
def kpi_card(title, value, delta, color):
    arrow = "▲" if delta >= 0 else "▼"
    delta_color = COLORS["accent2"] if delta >= 0 else COLORS["accent3"]
    return html.Div(style={**CARD_STYLE, "borderTop": f"3px solid {color}"}, children=[
        html.P(title,  style={"margin": 0, "color": COLORS["subtext"], "fontSize": "13px", "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.H2(value, style={"margin": "8px 0 4px", "color": COLORS["text"], "fontSize": "28px"}),
        html.Span(f"{arrow} {abs(delta):.1f}% vs last period",
                  style={"color": delta_color, "fontSize": "12px"}),
    ])

# ══════════════════════════════════════════════════════════════════════════════
# 4. APP LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Advanced Analytics Dashboard"

app.layout = html.Div(style={"display": "flex", "minHeight": "100vh", "backgroundColor": COLORS["bg"], "fontFamily": "'Segoe UI', Arial, sans-serif"}, children=[

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    html.Div(style={"width": "185px", "backgroundColor": COLORS["sidebar"], "padding": "16px 10px", "display": "flex", "flexDirection": "column", "gap": "6px", "borderRight": f"1px solid {COLORS['border']}", "position": "fixed", "top": 0, "bottom": 0, "overflowY": "auto"}, children=[

        html.H2("Analytics", style={"color": COLORS["accent"], "marginBottom": "12px", "fontSize": "17px", "letterSpacing": "1px"}),

        html.P("NAVIGATION", style={"color": COLORS["subtext"], "fontSize": "9px", "letterSpacing": "2px", "marginBottom": "2px"}),

        *[html.Button(label, id=f"nav-{page}", n_clicks=0, style={
            "display": "block", "width": "100%", "textAlign": "left",
            "background": "none", "border": "none", "color": COLORS["text"],
            "padding": "7px 10px", "borderRadius": "6px", "cursor": "pointer",
            "fontSize": "12px", "marginBottom": "1px",
        }) for label, page in [("📊 Overview", "overview"), ("📈 Trends", "trends"), ("🗺️ Regional", "regional"), ("📋 Data Table", "table")]],

        html.Hr(style={"borderColor": COLORS["border"], "margin": "10px 0"}),

        html.P("FILTERS", style={"color": COLORS["subtext"], "fontSize": "9px", "letterSpacing": "2px", "marginBottom": "4px"}),

        html.Label("Region", style={"color": COLORS["subtext"], "fontSize": "11px"}),
        dcc.Dropdown(
            id="filter-region",
            options=[{"label": "All Regions", "value": "ALL"}] + [{"label": r, "value": r} for r in REGIONS],
            value="ALL", clearable=False,
            style={"marginBottom": "8px", "fontSize": "12px"},
        ),

        html.Label("Category", style={"color": COLORS["subtext"], "fontSize": "11px"}),
        dcc.Dropdown(
            id="filter-category",
            options=[{"label": "All Categories", "value": "ALL"}] + [{"label": c, "value": c} for c in CATEGORIES],
            value="ALL", clearable=False,
            style={"marginBottom": "8px", "fontSize": "12px"},
        ),

        html.Label("Month Range", style={"color": COLORS["subtext"], "fontSize": "11px"}),
        dcc.RangeSlider(
            id="filter-months",
            min=1, max=12, step=1,
            marks={1: "Jan", 7: "Jul", 12: "Dec"},
            value=[1, 12],
            tooltip={"placement": "bottom"},
        ),

        html.Hr(style={"borderColor": COLORS["border"], "margin": "10px 0"}),

        html.P("TOOLS", style={"color": COLORS["subtext"], "fontSize": "9px", "letterSpacing": "2px", "marginBottom": "4px"}),

        html.Label("Top N Categories", style={"color": COLORS["subtext"], "fontSize": "11px"}),
        dcc.Slider(
            id="filter-topn",
            min=1, max=5, step=1, value=5,
            marks={1: "1", 2: "2", 3: "3", 4: "4", 5: "All"},
            tooltip={"placement": "bottom"},
        ),

        html.Label("Sales Target", style={"color": COLORS["subtext"], "fontSize": "11px", "marginTop": "10px"}),
        dcc.Input(
            id="filter-target",
            type="number", value=10000, min=0, step=500,
            style={
                "width": "100%", "backgroundColor": COLORS["bg"],
                "color": COLORS["text"], "border": f"1px solid {COLORS['border']}",
                "borderRadius": "6px", "padding": "5px 8px", "fontSize": "12px",
                "boxSizing": "border-box",
            },
        ),
        html.Span("shown as dashed line on charts", style={"color": COLORS["subtext"], "fontSize": "10px"}),
    ]),

    # ── MAIN CONTENT ─────────────────────────────────────────────────────────
    html.Div(style={"marginLeft": "240px", "flex": 1, "padding": "28px", "minWidth": 0}, children=[

        # Header bar
        html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "24px"}, children=[
            html.Div(id="page-title", style={"color": COLORS["text"], "fontSize": "24px", "fontWeight": "bold"}),
            html.Div(style={"display": "flex", "gap": "12px", "alignItems": "center"}, children=[
                dcc.RadioItems(
                    id="metric-toggle",
                    options=[
                        {"label": " Sales",  "value": "Sales"},
                        {"label": " Profit", "value": "Profit"},
                        {"label": " Units",  "value": "Units"},
                    ],
                    value="Sales",
                    inline=True,
                    style={"color": COLORS["text"]},
                    inputStyle={"marginRight": "4px", "accentColor": COLORS["accent"]},
                    labelStyle={"marginRight": "16px", "fontSize": "14px"},
                ),
                html.Button("⬇ Export CSV", id="export-btn", n_clicks=0, style={
                    "backgroundColor": COLORS["accent"], "color": "#fff",
                    "border": "none", "padding": "8px 16px", "borderRadius": "8px",
                    "cursor": "pointer", "fontSize": "13px",
                }),
                dcc.Download(id="download-csv"),
            ]),
        ]),

        # Hidden store for active page
        dcc.Store(id="active-page", data="overview"),

        # Page content container
        html.Div(id="page-content"),
    ]),
])

# ══════════════════════════════════════════════════════════════════════════════
# 5. PAGE CONTENT BUILDERS
# ══════════════════════════════════════════════════════════════════════════════
def overview_layout():
    return html.Div([
        html.Div(id="kpi-row",    style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "16px", "marginBottom": "24px"}),
        html.Div(style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "16px", "marginBottom": "16px"}, children=[
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="bar-chart",      config={"displayModeBar": False})]),
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="pie-chart",      config={"displayModeBar": False})]),
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}, children=[
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="line-chart",     config={"displayModeBar": False})]),
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="scatter-chart",  config={"displayModeBar": False})]),
        ]),
    ])

def trends_layout():
    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "16px", "marginBottom": "16px"}, children=[
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="trend-area",    config={"displayModeBar": False})]),
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}, children=[
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="trend-heatmap", config={"displayModeBar": False})]),
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="trend-box",     config={"displayModeBar": False})]),
        ]),
    ])

def regional_layout():
    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"}, children=[
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="region-bar",    config={"displayModeBar": False})]),
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="region-radar",  config={"displayModeBar": False})]),
        ]),
        html.Div(style=CARD_STYLE, children=[dcc.Graph(id="region-grouped",    config={"displayModeBar": False})]),
    ])

def table_layout():
    return html.Div([
        html.Div(style={**CARD_STYLE, "marginBottom": "16px"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "12px"}, children=[
                html.H3("Raw Data Table", style={"color": COLORS["text"], "margin": 0}),
                html.Span(id="row-count", style={"color": COLORS["subtext"], "fontSize": "13px"}),
            ]),
            dash_table.DataTable(
                id="data-table",
                columns=[{"name": c, "id": c} for c in ["Month","Region","Category","Sales","Profit","Units"]],
                page_size=15,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": COLORS["sidebar"], "color": COLORS["text"], "fontWeight": "bold", "border": f"1px solid {COLORS['border']}"},
                style_cell ={"backgroundColor": COLORS["card"],    "color": COLORS["text"],  "border": f"1px solid {COLORS['border']}", "padding": "10px 14px", "fontSize": "13px"},
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": COLORS["sidebar"]},
                    {"if": {"filter_query": "{Profit} > 150"}, "color": COLORS["accent2"]},
                ],
            ),
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
# 6. CALLBACKS
# ══════════════════════════════════════════════════════════════════════════════

# ── 6a. Navigation: track active page ────────────────────────────────────────
@app.callback(
    Output("active-page",  "data"),
    Output("page-title",   "children"),
    [Input(f"nav-{p}", "n_clicks") for p in ["overview","trends","regional","table"]],
    prevent_initial_call=False,
)
def switch_page(*args):
    pages = ["overview", "trends", "regional", "table"]
    titles = {
        "overview": "📊  Overview",
        "trends":   "📈  Trends",
        "regional": "🗺️  Regional",
        "table":    "📋  Data Table",
    }
    ctx = callback_context
    if not ctx.triggered or ctx.triggered[0]["value"] == 0:
        return "overview", titles["overview"]
    page = ctx.triggered[0]["prop_id"].split(".")[0].replace("nav-", "")
    return page, titles.get(page, "Overview")

# ── 6b. Render page skeleton ──────────────────────────────────────────────────
@app.callback(
    Output("page-content", "children"),
    Input("active-page",   "data"),
)
def render_page(page):
    if page == "trends":   return trends_layout()
    if page == "regional": return regional_layout()
    if page == "table":    return table_layout()
    return overview_layout()

# ── SHARED FILTER helper ─────────────────────────────────────────────────────
def apply_filters(region, category, month_range):
    d = df.copy()
    if region   != "ALL": d = d[d["Region"]   == region]
    if category != "ALL": d = d[d["Category"] == category]
    d = d[(d["MonthNum"] >= month_range[0]) & (d["MonthNum"] <= month_range[1])]
    return d

# ── 6c. OVERVIEW charts ───────────────────────────────────────────────────────
@app.callback(
    Output("kpi-row",       "children"),
    Output("bar-chart",     "figure"),
    Output("pie-chart",     "figure"),
    Output("line-chart",    "figure"),
    Output("scatter-chart", "figure"),
    Input("active-page",      "data"),
    Input("metric-toggle",    "value"),
    Input("filter-region",    "value"),
    Input("filter-category",  "value"),
    Input("filter-months",    "value"),
)
def update_overview(page, metric, region, category, month_range):
    if page != "overview":
        empty = go.Figure()
        empty.update_layout(**CHART_LAYOUT)
        return [], empty, empty, empty, empty

    d = apply_filters(region, category, month_range)

    # KPI cards
    total   = d[metric].sum()
    avg     = d[metric].mean()
    mx      = d[metric].max()
    profit_margin = (d["Profit"].sum() / d["Sales"].sum() * 100) if d["Sales"].sum() else 0
    kpis = [
        kpi_card("Total " + metric,  f"{total:,.0f}",          np.random.uniform(-10, 20), COLORS["accent"]),
        kpi_card("Average / Row",    f"{avg:,.1f}",             np.random.uniform(-5,  15), COLORS["accent2"]),
        kpi_card("Peak Value",       f"{mx:,.0f}",              np.random.uniform(0,   25), COLORS["accent4"]),
        kpi_card("Profit Margin",    f"{profit_margin:.1f}%",   np.random.uniform(-3,  12), COLORS["accent3"]),
    ]

    # Bar chart — by category
    bar_data = d.groupby("Category")[metric].sum().reset_index()
    bar = px.bar(bar_data, x="Category", y=metric, color="Category",
                 title=f"{metric} by Category", color_discrete_sequence=px.colors.qualitative.Bold)
    bar.update_layout(**CHART_LAYOUT)
    bar.update_traces(texttemplate="%{y:,.0f}", textposition="outside")

    # Pie chart — by region
    pie_data = d.groupby("Region")[metric].sum().reset_index()
    pie = px.pie(pie_data, names="Region", values=metric,
                 title=f"{metric} Share by Region", hole=0.45,
                 color_discrete_sequence=px.colors.qualitative.Bold)
    pie.update_layout(**CHART_LAYOUT)

    # Line chart — over months
    line_data = d.groupby("MonthNum")[metric].sum().reset_index()
    line_data["Month"] = line_data["MonthNum"].apply(lambda x: MONTHS[x-1])
    line = px.line(line_data, x="Month", y=metric, markers=True,
                   title=f"{metric} Trend Over Months")
    line.update_traces(line_color=COLORS["accent"], marker_color=COLORS["accent2"], line_width=2.5)
    line.update_layout(**CHART_LAYOUT)

    # Scatter — Sales vs Profit
    scatter_data = d.groupby("Category").agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Units=("Units","sum")).reset_index()
    scatter = px.scatter(scatter_data, x="Sales", y="Profit", size="Units", color="Category",
                         title="Sales vs Profit (bubble = Units)",
                         color_discrete_sequence=px.colors.qualitative.Bold, size_max=50)
    scatter.update_layout(**CHART_LAYOUT)

    return kpis, bar, pie, line, scatter

# ── 6d. TRENDS charts ────────────────────────────────────────────────────────
@app.callback(
    Output("trend-area",    "figure"),
    Output("trend-heatmap", "figure"),
    Output("trend-box",     "figure"),
    Input("active-page",     "data"),
    Input("metric-toggle",   "value"),
    Input("filter-region",   "value"),
    Input("filter-category", "value"),
    Input("filter-months",   "value"),
)
def update_trends(page, metric, region, category, month_range):
    empty = go.Figure()
    empty.update_layout(**CHART_LAYOUT)
    if page != "trends":
        return empty, empty, empty

    d = apply_filters(region, category, month_range)

    # Stacked area — by category over months
    area_data = d.groupby(["MonthNum","Category"])[metric].sum().reset_index()
    area_data["Month"] = area_data["MonthNum"].apply(lambda x: MONTHS[x-1])
    area = px.area(area_data, x="Month", y=metric, color="Category",
                   title=f"{metric} by Category (Stacked Area)",
                   color_discrete_sequence=px.colors.qualitative.Bold)
    area.update_layout(**CHART_LAYOUT)

    # Heatmap — month × category
    heat_data = d.groupby(["MonthNum","Category"])[metric].sum().unstack(fill_value=0)
    heat_data.index = [MONTHS[i-1] for i in heat_data.index]
    heatmap = go.Figure(go.Heatmap(
        z=heat_data.values.tolist(), x=heat_data.columns.tolist(), y=heat_data.index.tolist(),
        colorscale="Viridis", showscale=True,
    ))
    heatmap.update_layout(title=f"{metric} Heatmap (Month × Category)", **CHART_LAYOUT)

    # Box plot — distribution by region
    box = px.box(d, x="Region", y=metric, color="Region",
                 title=f"{metric} Distribution by Region",
                 color_discrete_sequence=px.colors.qualitative.Bold)
    box.update_layout(**CHART_LAYOUT)

    return area, heatmap, box

# ── 6e. REGIONAL charts ───────────────────────────────────────────────────────
@app.callback(
    Output("region-bar",     "figure"),
    Output("region-radar",   "figure"),
    Output("region-grouped", "figure"),
    Input("active-page",     "data"),
    Input("metric-toggle",   "value"),
    Input("filter-region",   "value"),
    Input("filter-category", "value"),
    Input("filter-months",   "value"),
)
def update_regional(page, metric, region, category, month_range):
    empty = go.Figure()
    empty.update_layout(**CHART_LAYOUT)
    if page != "regional":
        return empty, empty, empty

    d = apply_filters(region, category, month_range)

    # Horizontal bar — region totals
    rbar_data = d.groupby("Region")[metric].sum().sort_values().reset_index()
    rbar = px.bar(rbar_data, x=metric, y="Region", orientation="h",
                  color="Region", title=f"Total {metric} by Region",
                  color_discrete_sequence=px.colors.qualitative.Bold)
    rbar.update_layout(**CHART_LAYOUT)

    # Radar chart — regions across categories
    radar_data = d.groupby(["Region","Category"])[metric].sum().reset_index()
    radar = go.Figure()
    cats  = CATEGORIES
    for reg in REGIONS:
        vals = [radar_data[(radar_data.Region==reg) & (radar_data.Category==c)][metric].sum() for c in cats]
        vals += [vals[0]]
        radar.add_trace(go.Scatterpolar(r=vals, theta=cats+[cats[0]], name=reg, fill="toself"))
    radar.update_layout(title=f"Radar: {metric} by Region & Category",
                        polar=dict(bgcolor=COLORS["card"],
                                   angularaxis=dict(color=COLORS["text"]),
                                   radialaxis=dict(color=COLORS["text"])),
                        **CHART_LAYOUT)

    # Grouped bar — region × category
    grp_data = d.groupby(["Region","Category"])[metric].sum().reset_index()
    grp = px.bar(grp_data, x="Category", y=metric, color="Region", barmode="group",
                 title=f"{metric} by Category & Region",
                 color_discrete_sequence=px.colors.qualitative.Bold)
    grp.update_layout(**CHART_LAYOUT)

    return rbar, radar, grp

# ── 6f. DATA TABLE ────────────────────────────────────────────────────────────
@app.callback(
    Output("data-table", "data"),
    Output("row-count",  "children"),
    Input("active-page",     "data"),
    Input("filter-region",   "value"),
    Input("filter-category", "value"),
    Input("filter-months",   "value"),
)
def update_table(page, region, category, month_range):
    if page != "table":
        return [], ""
    d = apply_filters(region, category, month_range)
    return d[["Month","Region","Category","Sales","Profit","Units"]].to_dict("records"), f"{len(d):,} rows"

# ── 6g. CSV Export ────────────────────────────────────────────────────────────
@app.callback(
    Output("download-csv", "data"),
    Input("export-btn",       "n_clicks"),
    State("filter-region",    "value"),
    State("filter-category",  "value"),
    State("filter-months",    "value"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, region, category, month_range):
    d = apply_filters(region, category, month_range)
    return dcc.send_data_frame(d.to_csv, "dashboard_export.csv", index=False)

# ══════════════════════════════════════════════════════════════════════════════
# 7. RUN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=True)
