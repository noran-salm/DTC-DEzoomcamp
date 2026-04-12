import marimo

__generated_with = "0.20.3"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import textwrap
    return (mo, textwrap)


@app.cell
def _(mo):
    mo.md("""
    <div style="
        background: linear-gradient(135deg, #0a0a0f 0%, #111827 50%, #0d1117 100%);
        border-bottom: 1px solid #f5c518;
        padding: 2.5rem 3rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
    ">
        <div style="display:flex; align-items:center; gap:1rem; margin-bottom:.5rem;">
            <div style="
                background:#f5c518;
                color:#000;
                font-size:1.6rem;
                width:48px; height:48px;
                border-radius:8px;
                display:flex; align-items:center; justify-content:center;
                font-weight:900;
            ">🚕</div>
            <div>
                <div style="
                    font-family: 'Georgia', serif;
                    font-size: 2rem;
                    font-weight: 700;
                    color: #f5c518;
                    letter-spacing: -0.5px;
                    line-height: 1;
                ">NYC Taxi Analytics</div>
                <div style="
                    font-family: monospace;
                    font-size: .8rem;
                    color: #6b7280;
                    margin-top:.3rem;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                ">taxi_pipeline.duckdb · dlt pipeline</div>
            </div>
        </div>
    </div>
    """)
    return


@app.cell
def _():
    from dataclasses import dataclass
    from typing import Dict, List, Optional, Tuple
    import contextlib
    import pathlib
    import statistics

    import duckdb
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    DB_PATH = "taxi_pipeline.duckdb"

    # ── Column names ──────────────────────────────────────────────────────────
    COL_FARE       = "fare_amt"
    COL_TIP        = "tip_amt"
    COL_TOTAL      = "total_amt"
    COL_TOLLS      = "tolls_amt"
    COL_DISTANCE   = "trip_distance"
    COL_PAYMENT    = "payment_type"
    COL_PASSENGERS = "passenger_count"
    COL_PICKUP     = "trip_pickup_date_time"
    COL_DROPOFF    = "trip_dropoff_date_time"
    COL_START_LAT  = "start_lat"
    COL_START_LON  = "start_lon"
    COL_END_LAT    = "end_lat"
    COL_END_LON    = "end_lon"

    # ── Design system ─────────────────────────────────────────────────────────
    YELLOW   = "#f5c518"
    CYAN     = "#06b6d4"
    ORANGE   = "#f97316"
    ROSE     = "#f43f5e"
    VIOLET   = "#8b5cf6"
    EMERALD  = "#10b981"
    BG_DARK  = "#0d1117"
    BG_CARD  = "#161b22"
    BORDER   = "#30363d"
    TEXT_MUT = "#8b949e"

    PALETTE  = [YELLOW, CYAN, ORANGE, ROSE, VIOLET, EMERALD]

    # ── Plotly dark theme ─────────────────────────────────────────────────────
    PLOT_LAYOUT = dict(
        paper_bgcolor=BG_CARD,
        plot_bgcolor="#0d1117",
        font=dict(family="Georgia, serif", color="#e6edf3", size=12),
        title_font=dict(family="Georgia, serif", size=15, color="#e6edf3"),
        xaxis=dict(
            gridcolor="#21262d", gridwidth=1,
            linecolor=BORDER, tickcolor=BORDER,
            tickfont=dict(color=TEXT_MUT, size=11),
            title_font=dict(color=TEXT_MUT),
        ),
        yaxis=dict(
            gridcolor="#21262d", gridwidth=1,
            linecolor=BORDER, tickcolor=BORDER,
            tickfont=dict(color=TEXT_MUT, size=11),
            title_font=dict(color=TEXT_MUT),
        ),
        legend=dict(
            bgcolor="#161b22",
            bordercolor=BORDER,
            borderwidth=1,
            font=dict(color="#e6edf3", size=11),
        ),
        margin=dict(l=50, r=30, t=55, b=45),
        hoverlabel=dict(
            bgcolor="#161b22",
            bordercolor=BORDER,
            font=dict(color="#e6edf3", family="monospace", size=12),
        ),
    )

    def styled(fig, title=None):
        """Apply the dark theme to any plotly figure."""
        updates = dict(**PLOT_LAYOUT)
        if title:
            updates["title"] = dict(
                text=title,
                font=dict(family="Georgia, serif", size=15, color="#e6edf3"),
                x=0.02, xanchor="left",
            )
        fig.update_layout(**updates)
        return fig

    def section(title, icon):
        return f"""
        <div style="
            display:flex; align-items:center; gap:.75rem;
            margin: 2.5rem 0 1.2rem;
            padding-bottom:.75rem;
            border-bottom: 1px solid {BORDER};
        ">
            <span style="font-size:1.4rem">{icon}</span>
            <span style="
                font-family:'Georgia',serif;
                font-size:1.25rem;
                font-weight:700;
                color:#e6edf3;
                letter-spacing:-.3px;
            ">{title}</span>
        </div>"""

    def stat_card(label, value, sub=None, color=YELLOW):
        sub_html = (f'<div style="color:{TEXT_MUT};font-size:.72rem;'
                    f'font-family:monospace;margin-top:.25rem">{sub}</div>'
                    if sub else "")
        return f"""
        <div style="
            background:{BG_CARD};
            border:1px solid {BORDER};
            border-top: 3px solid {color};
            border-radius:8px;
            padding:1.1rem 1.4rem;
            min-width:140px;
        ">
            <div style="color:{TEXT_MUT};font-family:monospace;font-size:.72rem;
                        text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.4rem">{label}</div>
            <div style="color:#e6edf3;font-family:'Georgia',serif;
                        font-size:1.6rem;font-weight:700;line-height:1">{value}</div>
            {sub_html}
        </div>"""

    # ── Formatters ────────────────────────────────────────────────────────────
    def fmt_int(v):        return f"{v:,}"        if v is not None else "N/A"
    def fmt_float(v, d=2): return f"{v:.{d}f}"   if v is not None else "N/A"
    def fmt_dollar(v):     return f"${v:.2f}"     if v is not None else "N/A"
    def fmt_k(v):          return f"{v/1000:.1f}k" if v and v >= 1000 else fmt_int(v)
    def fmt_pct(v, d=1):   return f"{v:.{d}f}%"  if v is not None else "N/A"

    # ── Dataclasses ───────────────────────────────────────────────────────────
    @dataclass(frozen=True)
    class ColumnInfo:
        name: str
        type: str

    @dataclass(frozen=True)
    class TableInfo:
        schema: str
        name: str

        @property
        def qualified(self) -> str:
            return f'"{self.schema}"."{self.name}"'

    # ── Database manager ──────────────────────────────────────────────────────
    class DatabaseManager:
        def __init__(self, db_path: str = DB_PATH):
            self.db_path = db_path

        @contextlib.contextmanager
        def connection(self):
            conn = duckdb.connect(self.db_path, read_only=True)
            try:
                yield conn
            finally:
                conn.close()

        def list_tables(self) -> List[TableInfo]:
            with self.connection() as c:
                rows = c.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE'
                      AND table_schema NOT IN ('information_schema', 'pg_catalog')
                    ORDER BY table_schema, table_name
                """).fetchall()
            return [TableInfo(schema=r[0], name=r[1]) for r in rows]

        def get_columns(self, table: TableInfo) -> List[ColumnInfo]:
            with self.connection() as c:
                rows = c.execute(f"DESCRIBE {table.qualified}").fetchall()
            return [ColumnInfo(name=r[0], type=r[1]) for r in rows]

        def col_names(self, table: TableInfo):
            return {c.name.lower() for c in self.get_columns(table)}

        def has_cols(self, table: TableInfo, *cols: str) -> bool:
            names = self.col_names(table)
            return all(c.lower() in names for c in cols)

        def row_count(self, table: TableInfo) -> int:
            with self.connection() as c:
                return c.execute(
                    f"SELECT COUNT(*) FROM {table.qualified}"
                ).fetchone()[0]

        def date_range(self, table: TableInfo, col: str):
            with self.connection() as c:
                mn, mx = c.execute(
                    f"SELECT MIN({col}), MAX({col}) FROM {table.qualified}"
                ).fetchone()
            return (str(mn)[:19] if mn else None, str(mx)[:19] if mx else None)

        def primary_table(self) -> Optional[TableInfo]:
            tables = self.list_tables()
            if not tables:
                return None
            hits = [t for t in tables
                    if any(w in t.name.lower() for w in ("taxi", "trip", "nyc"))
                    and not t.name.startswith("_dlt")]
            return hits[0] if hits else next(
                (t for t in tables if not t.name.startswith("_dlt")), tables[0]
            )

        def preferred_dt_col(self, table: TableInfo) -> Optional[str]:
            cols = self.get_columns(table)
            dt = [c.name for c in cols
                  if any(k in c.type.upper() for k in ("TIMESTAMP", "DATE"))]
            pickup = [c for c in dt if "pickup" in c.lower()]
            return pickup[0] if pickup else (dt[0] if dt else None)

    return (
        BG_CARD, BG_DARK, BORDER, CYAN, COL_DISTANCE, COL_DROPOFF,
        COL_END_LAT, COL_END_LON, COL_FARE, COL_PASSENGERS, COL_PAYMENT,
        COL_PICKUP, COL_START_LAT, COL_START_LON, COL_TIP, COL_TOLLS, COL_TOTAL,
        ColumnInfo, DatabaseManager, DB_PATH, EMERALD, ORANGE, PALETTE,
        PLOT_LAYOUT, ROSE, TEXT_MUT, TableInfo, VIOLET, YELLOW,
        contextlib, dataclass, duckdb, fmt_dollar, fmt_float, fmt_int,
        fmt_k, fmt_pct, go, make_subplots, np, pathlib, pd, px,
        section, stat_card, statistics, styled,
    )


# ── Connect ───────────────────────────────────────────────────────────────────
@app.cell
def _(DatabaseManager, mo, pathlib, stat_card, YELLOW, EMERALD, ROSE, BG_CARD, BORDER, TEXT_MUT):
    _f = pathlib.Path(DatabaseManager().db_path)

    if not _f.exists():
        db_manager = None
        _out = mo.md(f"⚠️ **Database not found at `{_f}`.** Run your pipeline first!")
    else:
        try:
            _dbm = DatabaseManager()
            with _dbm.connection() as _c:
                _c.execute("SELECT 1").fetchone()
            _mb   = _f.stat().st_size / (1024 * 1024)
            db_manager = _dbm
            _out = mo.Html(f"""
            <div style="
                background:{BG_CARD};
                border:1px solid {BORDER};
                border-left:4px solid {EMERALD};
                border-radius:8px;
                padding:.9rem 1.3rem;
                display:flex; align-items:center; gap:1rem;
                font-family:monospace; font-size:.85rem;
            ">
                <span style="color:{EMERALD};font-size:1.2rem">●</span>
                <span style="color:#e6edf3">Connected to
                    <strong style="color:{YELLOW}">{_f.name}</strong>
                </span>
                <span style="color:{TEXT_MUT};margin-left:auto">{_mb:.2f} MB on disk</span>
            </div>
            """)
        except Exception as _e:
            db_manager = None
            _out = mo.md(f"❌ **Connection error:** {_e}")

    _out
    return (db_manager,)


# ── KPI Summary ───────────────────────────────────────────────────────────────
@app.cell
def _(COL_DISTANCE, COL_FARE, COL_PASSENGERS, COL_TIP, COL_TOTAL,
      CYAN, EMERALD, ORANGE, ROSE, YELLOW,
      db_manager, fmt_dollar, fmt_float, fmt_k, mo, section, stat_card):
    if db_manager is None:
        _out = mo.md("")
    else:
        _t = db_manager.primary_table()
        if not _t:
            _out = mo.md("")
        else:
            try:
                _sel = ["COUNT(*) AS total_trips"]
                if db_manager.has_cols(_t, COL_FARE):
                    _sel.append(f"AVG({COL_FARE}) AS avg_fare")
                    _sel.append(f"SUM({COL_FARE}) AS total_revenue")
                if db_manager.has_cols(_t, COL_TIP):
                    _sel.append(f"AVG({COL_TIP}) AS avg_tip")
                if db_manager.has_cols(_t, COL_DISTANCE):
                    _sel.append(f"AVG({COL_DISTANCE}) AS avg_dist")
                if db_manager.has_cols(_t, COL_PASSENGERS):
                    _sel.append(f"AVG({COL_PASSENGERS}) AS avg_pax")
                if db_manager.has_cols(_t, COL_TOTAL):
                    _sel.append(f"SUM({COL_TOTAL}) AS total_amt_sum")

                with db_manager.connection() as _c:
                    _row = _c.execute(
                        f"SELECT {', '.join(_sel)} FROM {_t.qualified}"
                    ).fetchone()
                    _cols_out = [d[0] for d in _c.description]

                _kpi = dict(zip(_cols_out, _row))

                _cards_html = "".join([
                    stat_card("Total Trips",    fmt_k(_kpi.get("total_trips")),    color=YELLOW),
                    stat_card("Avg Fare",        fmt_dollar(_kpi.get("avg_fare")),  color=CYAN),
                    stat_card("Avg Tip",         fmt_dollar(_kpi.get("avg_tip")),   color=EMERALD),
                    stat_card("Avg Distance",    f"{fmt_float(_kpi.get('avg_dist'))} mi", color=ORANGE),
                    stat_card("Avg Passengers",  fmt_float(_kpi.get("avg_pax"), 1), color=ROSE),
                    stat_card("Total Revenue",
                              f"${fmt_k(_kpi.get('total_amt_sum') or _kpi.get('total_revenue'))}",
                              sub="gross fare collected", color="#8b5cf6"),
                ])

                _out = mo.Html(
                    section("Fleet at a Glance", "📋") +
                    f'<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:.5rem">{_cards_html}</div>'
                )
            except Exception as _e:
                _out = mo.md(f"❌ KPI error: `{_e}`")

    _out
    return


# ── Payment Analysis ──────────────────────────────────────────────────────────
@app.cell
def _(COL_FARE, COL_PAYMENT, COL_TIP, PALETTE, YELLOW, CYAN, ORANGE,
      db_manager, fmt_dollar, fmt_int, fmt_pct, mo, px, section, styled):
    if db_manager is None:
        _out = mo.md("")
    else:
        _t = db_manager.primary_table()
        if not _t or not db_manager.has_cols(_t, COL_PAYMENT, COL_FARE, COL_TIP):
            _out = mo.md("")
        else:
            try:
                with db_manager.connection() as _c:
                    _dist = _c.execute(f"""
                        SELECT {COL_PAYMENT} AS ptype, COUNT(*) AS trips,
                               AVG({COL_FARE}) AS avg_fare,
                               AVG({COL_TIP})  AS avg_tip,
                               100.0 * AVG(CASE WHEN {COL_FARE} > 0
                                               THEN {COL_TIP}/{COL_FARE}
                                               ELSE NULL END) AS tip_pct
                        FROM {_t.qualified}
                        WHERE {COL_PAYMENT} IS NOT NULL
                          AND {COL_FARE} IS NOT NULL
                        GROUP BY {COL_PAYMENT} ORDER BY trips DESC
                    """).df()

                # Donut chart
                _fig_donut = px.pie(
                    _dist, names="ptype", values="trips", hole=0.58,
                    color_discrete_sequence=PALETTE,
                )
                _fig_donut.update_traces(
                    textinfo="percent",
                    textfont=dict(size=12, color="#e6edf3"),
                    hovertemplate="<b>%{label}</b><br>%{value:,} trips<br>%{percent}<extra></extra>",
                )
                _fig_donut.add_annotation(
                    text=f"<b>{fmt_int(int(_dist['trips'].sum()))}</b><br><span style='font-size:10px'>trips</span>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=18, color="#e6edf3", family="Georgia, serif"),
                )
                styled(_fig_donut, "Payment Mix")

                # Grouped bar - avg fare vs avg tip
                _fig_bar = px.bar(
                    _dist, x="ptype", y=["avg_fare", "avg_tip"],
                    barmode="group",
                    labels={"ptype": "", "value": "USD", "variable": ""},
                    color_discrete_sequence=[YELLOW, CYAN],
                )
                _fig_bar.update_traces(
                    marker_line_width=0,
                    hovertemplate="<b>%{x}</b><br>%{y:.2f}<extra></extra>",
                )
                _fig_bar.update_layout(
                    bargap=0.25, bargroupgap=0.05,
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1,
                    ),
                )
                styled(_fig_bar, "Avg Fare & Tip by Payment Type")

                # Tip % horizontal bar
                _dist_sorted = _dist.sort_values("tip_pct")
                _fig_tip = px.bar(
                    _dist_sorted, x="tip_pct", y="ptype",
                    orientation="h",
                    labels={"tip_pct": "Tip %", "ptype": ""},
                    color="tip_pct",
                    color_continuous_scale=[[0, "#1a2a1a"], [0.5, CYAN], [1, YELLOW]],
                )
                _fig_tip.update_traces(
                    marker_line_width=0,
                    hovertemplate="<b>%{y}</b><br>Tip rate: %{x:.1f}%<extra></extra>",
                )
                _fig_tip.update_layout(coloraxis_showscale=False)
                styled(_fig_tip, "Tip Rate by Payment Type")

                # Summary table HTML
                _rows_html = "".join([
                    f"""<tr>
                        <td style="color:#e6edf3;padding:.5rem .8rem">{r.ptype}</td>
                        <td style="color:{YELLOW};padding:.5rem .8rem;text-align:right;font-family:monospace">{fmt_int(int(r.trips))}</td>
                        <td style="color:{CYAN};padding:.5rem .8rem;text-align:right;font-family:monospace">{fmt_dollar(r.avg_fare)}</td>
                        <td style="color:{ORANGE};padding:.5rem .8rem;text-align:right;font-family:monospace">{fmt_dollar(r.avg_tip)}</td>
                        <td style="color:#10b981;padding:.5rem .8rem;text-align:right;font-family:monospace">{fmt_pct(r.tip_pct)}</td>
                    </tr>"""
                    for r in _dist.itertuples()
                ])
                _table_html = f"""
                <table style="width:100%;border-collapse:collapse;font-size:.85rem">
                    <thead><tr style="border-bottom:1px solid #30363d">
                        <th style="color:#8b949e;padding:.5rem .8rem;text-align:left;font-family:monospace;font-weight:400;font-size:.75rem;text-transform:uppercase;letter-spacing:1px">Type</th>
                        <th style="color:#8b949e;padding:.5rem .8rem;text-align:right;font-family:monospace;font-weight:400;font-size:.75rem;text-transform:uppercase;letter-spacing:1px">Trips</th>
                        <th style="color:#8b949e;padding:.5rem .8rem;text-align:right;font-family:monospace;font-weight:400;font-size:.75rem;text-transform:uppercase;letter-spacing:1px">Avg Fare</th>
                        <th style="color:#8b949e;padding:.5rem .8rem;text-align:right;font-family:monospace;font-weight:400;font-size:.75rem;text-transform:uppercase;letter-spacing:1px">Avg Tip</th>
                        <th style="color:#8b949e;padding:.5rem .8rem;text-align:right;font-family:monospace;font-weight:400;font-size:.75rem;text-transform:uppercase;letter-spacing:1px">Tip Rate</th>
                    </tr></thead>
                    <tbody>{_rows_html}</tbody>
                </table>"""

                _out = mo.vstack([
                    mo.Html(section("Payment Analysis", "💳")),
                    mo.hstack([mo.ui.plotly(_fig_donut), mo.ui.plotly(_fig_bar), mo.ui.plotly(_fig_tip)]),
                    mo.Html(f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem;margin-top:.5rem">{_table_html}</div>'),
                ])
            except Exception as _e:
                _out = mo.md(f"❌ {_e}")

    _out
    return


# ── Trip Distance ─────────────────────────────────────────────────────────────
@app.cell
def _(COL_DISTANCE, YELLOW, CYAN, ORANGE, ROSE,
      db_manager, fmt_float, fmt_int, mo, px, go, section, stat_card, styled, statistics):
    if db_manager is None:
        _out = mo.md("")
    else:
        _t = db_manager.primary_table()
        if not _t or not db_manager.has_cols(_t, COL_DISTANCE):
            _out = mo.md("")
        else:
            try:
                with db_manager.connection() as _c:
                    _df = _c.execute(f"""
                        WITH base AS (
                            SELECT {COL_DISTANCE} AS d FROM {_t.qualified}
                            WHERE {COL_DISTANCE} IS NOT NULL AND {COL_DISTANCE} > 0
                        ),
                        bounds AS (
                            SELECT quantile_cont(d, 0.01) AS p1,
                                   quantile_cont(d, 0.99) AS p99
                            FROM base
                        )
                        SELECT b.d AS dist FROM base b, bounds
                        WHERE b.d BETWEEN bounds.p1 AND bounds.p99
                        USING SAMPLE 8000 ROWS
                    """).df()
                    _ntile = _c.execute(f"""
                        WITH ranked AS (
                            SELECT {COL_DISTANCE} AS d,
                                   NTILE(4) OVER (ORDER BY {COL_DISTANCE}) AS q
                            FROM {_t.qualified}
                            WHERE {COL_DISTANCE} IS NOT NULL AND {COL_DISTANCE} > 0
                        )
                        SELECT q, COUNT(*) AS trips, AVG(d) AS avg_d,
                               MIN(d) AS min_d, MAX(d) AS max_d
                        FROM ranked GROUP BY q ORDER BY q
                    """).df()

                _vals   = _df["dist"].tolist()
                _mean   = statistics.mean(_vals)
                _median = statistics.median(_vals)
                _p75    = _df["dist"].quantile(0.75)
                _p95    = _df["dist"].quantile(0.95)

                # Histogram with KDE-style overlay via violin
                _fig_hist = px.histogram(
                    _df, x="dist", nbins=70,
                    labels={"dist": "Distance (miles)", "count": "Trips"},
                    color_discrete_sequence=[YELLOW],
                    opacity=0.8,
                )
                _fig_hist.update_traces(
                    marker_line_width=0,
                    hovertemplate="<b>%{x:.1f} mi</b><br>%{y:,} trips<extra></extra>",
                )
                for _xv, _col, _label, _dash in [
                    (_mean,   CYAN,   f"Mean {fmt_float(_mean)} mi",   "dash"),
                    (_median, ORANGE, f"Median {fmt_float(_median)} mi", "dot"),
                    (_p75,    ROSE,   f"P75 {fmt_float(_p75)} mi",     "dashdot"),
                ]:
                    _fig_hist.add_vline(
                        x=_xv, line_color=_col, line_dash=_dash, line_width=2,
                        annotation_text=_label,
                        annotation_font=dict(color=_col, size=11),
                        annotation_position="top right",
                    )
                styled(_fig_hist, "Trip Distance Distribution")

                # Box plot per quartile
                _ntile["label"] = _ntile["q"].map({1: "Q1 Short", 2: "Q2", 3: "Q3", 4: "Q4 Long"})
                _fig_box = px.bar(
                    _ntile, x="label", y="avg_d",
                    error_y=_ntile["max_d"] - _ntile["avg_d"],
                    error_y_minus=_ntile["avg_d"] - _ntile["min_d"],
                    labels={"label": "", "avg_d": "Avg Miles"},
                    color="avg_d",
                    color_continuous_scale=[[0, "#1a1a2e"], [0.5, CYAN], [1, YELLOW]],
                )
                _fig_box.update_traces(
                    marker_line_width=0,
                    hovertemplate="<b>%{x}</b><br>Avg: %{y:.2f} mi<extra></extra>",
                )
                _fig_box.update_layout(coloraxis_showscale=False)
                styled(_fig_box, "Distance Quartiles")

                _stat_cards = "".join([
                    stat_card("Mean",    f"{fmt_float(_mean)} mi",   color=CYAN),
                    stat_card("Median",  f"{fmt_float(_median)} mi", color=ORANGE),
                    stat_card("P75",     f"{fmt_float(_p75)} mi",    color=ROSE),
                    stat_card("P95",     f"{fmt_float(_p95)} mi",    color="#8b5cf6"),
                    stat_card("Sampled", fmt_int(len(_df)),           color="#10b981"),
                ])

                _out = mo.vstack([
                    mo.Html(section("Trip Distance", "🛣️")),
                    mo.Html(f'<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem">{_stat_cards}</div>'),
                    mo.hstack([mo.ui.plotly(_fig_hist), mo.ui.plotly(_fig_box)]),
                ])
            except Exception as _e:
                _out = mo.md(f"❌ {_e}")

    _out
    return


# ── Time Series + Hourly / DOW Heatmap ───────────────────────────────────────
@app.cell
def _(COL_DISTANCE, COL_FARE, COL_PICKUP, COL_TIP, YELLOW, CYAN, ORANGE,
      db_manager, fmt_int, mo, go, np, pd, px, section, make_subplots, styled, PLOT_LAYOUT):
    if db_manager is None:
        _out = mo.md("")
    else:
        _t     = db_manager.primary_table()
        _dtcol = db_manager.preferred_dt_col(_t) if _t else None
        if not _t or not _dtcol:
            _out = mo.md("ℹ️ No datetime column — skipping time series.")
        else:
            try:
                _sel = [f"DATE({_dtcol}) AS d", "COUNT(*) AS trips"]
                if db_manager.has_cols(_t, COL_DISTANCE):
                    _sel.append(f"AVG(NULLIF({COL_DISTANCE},0)) AS avg_dist")
                if db_manager.has_cols(_t, COL_FARE):
                    _sel.append(f"AVG(NULLIF({COL_FARE},0)) AS avg_fare")
                if db_manager.has_cols(_t, COL_TIP):
                    _sel.append(f"SUM({COL_TIP}) AS total_tips")

                with db_manager.connection() as _c:
                    _df = _c.execute(f"""
                        SELECT {', '.join(_sel)}
                        FROM {_t.qualified}
                        WHERE {_dtcol} IS NOT NULL
                        GROUP BY d ORDER BY d
                    """).df()

                    # Hourly x DOW heatmap
                    _hdf = _c.execute(f"""
                        SELECT DAYOFWEEK({_dtcol}) AS dow,
                               HOUR({_dtcol})      AS hr,
                               COUNT(*)            AS trips
                        FROM {_t.qualified}
                        WHERE {_dtcol} IS NOT NULL
                        GROUP BY dow, hr ORDER BY dow, hr
                    """).df()

                # ── Daily time series ─────────────────────────────────────────
                _df["d"] = pd.to_datetime(_df["d"])
                _df = _df.sort_values("d")
                for _col in ["trips", "avg_dist", "avg_fare", "total_tips"]:
                    if _col in _df.columns:
                        _df[f"{_col}_ma7"] = _df[_col].rolling(7, min_periods=1).mean()

                _fig_ts = go.Figure()
                _fig_ts.add_trace(go.Bar(
                    x=_df["d"], y=_df["trips"],
                    name="Daily trips",
                    marker_color=YELLOW, opacity=0.35,
                    hovertemplate="%{x|%b %d}<br><b>%{y:,} trips</b><extra></extra>",
                ))
                _fig_ts.add_trace(go.Scatter(
                    x=_df["d"], y=_df["trips_ma7"],
                    name="7-day avg", mode="lines",
                    line=dict(color=CYAN, width=2.5),
                    hovertemplate="%{x|%b %d}<br>7d avg: <b>%{y:.0f}</b><extra></extra>",
                ))
                _fig_ts.update_layout(
                    bargap=0.05, legend=dict(orientation="h", y=1.05),
                    xaxis=dict(
                        rangeselector=dict(
                            bgcolor="#161b22", bordercolor="#30363d",
                            activecolor="#f5c518",
                            font=dict(color="#e6edf3"),
                            buttons=[
                                dict(count=7,  label="1w", step="day", stepmode="backward"),
                                dict(count=14, label="2w", step="day", stepmode="backward"),
                                dict(step="all", label="All"),
                            ],
                        ),
                        rangeslider=dict(visible=True, bgcolor="#0d1117", thickness=0.06),
                        type="date",
                    ),
                )
                styled(_fig_ts, f"Daily Trip Volume — {fmt_int(len(_df))} days")

                # ── Hourly heatmap ────────────────────────────────────────────
                _dow_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                _pivot = _hdf.pivot_table(index="dow", columns="hr",
                                          values="trips", aggfunc="sum", fill_value=0)
                _pivot.index = [_dow_labels[i] for i in _pivot.index]

                _fig_heat = go.Figure(go.Heatmap(
                    z=_pivot.values,
                    x=[f"{h:02d}:00" for h in _pivot.columns],
                    y=_pivot.index,
                    colorscale=[[0, "#0d1117"], [0.3, "#1a3a2a"],
                                [0.6, CYAN], [0.85, YELLOW], [1.0, "#fff"]],
                    hovertemplate="<b>%{y} %{x}</b><br>%{z:,} trips<extra></extra>",
                    showscale=True,
                    colorbar=dict(
                        tickfont=dict(color="#8b949e"),
                        outlinecolor="#30363d", outlinewidth=1,
                    ),
                ))
                styled(_fig_heat, "Trip Volume Heatmap — Day × Hour")

                _out = mo.vstack([
                    mo.Html(section("Time Series & Patterns", "📈")),
                    mo.ui.plotly(_fig_ts),
                    mo.ui.plotly(_fig_heat),
                ])
            except Exception as _e:
                _out = mo.md(f"❌ {_e}")

    _out
    return


# ── Fare / Tip Correlation ────────────────────────────────────────────────────
@app.cell
def _(COL_FARE, COL_TIP, YELLOW, CYAN, ORANGE, ROSE,
      db_manager, fmt_float, mo, go, np, px, section, stat_card, styled):
    if db_manager is None:
        _out = mo.md("")
    else:
        _t = db_manager.primary_table()
        if not _t or not db_manager.has_cols(_t, COL_FARE, COL_TIP):
            _out = mo.md("")
        else:
            try:
                with db_manager.connection() as _c:
                    _df = _c.execute(f"""
                        SELECT
                            {COL_FARE} AS fare,
                            {COL_TIP}  AS tip,
                            CASE WHEN {COL_FARE} > 0
                                 THEN 100.0 * {COL_TIP} / {COL_FARE}
                                 ELSE NULL END AS tip_pct
                        FROM {_t.qualified}
                        WHERE {COL_FARE} BETWEEN 1 AND 100
                          AND {COL_TIP}  >= 0
                        USING SAMPLE 6000 ROWS
                    """).df()

                _corr    = _df[["fare", "tip"]].corr().iloc[0, 1]
                _avg_pct = _df["tip_pct"].mean()
                _med_pct = _df["tip_pct"].median()
                _zero_tip_pct = 100 * (_df["tip"] == 0).mean()

                # OLS via numpy
                _x     = _df["fare"].values
                _y     = _df["tip"].values
                _slope, _intercept = np.polyfit(_x, _y, 1)
                _x_fit = np.linspace(_x.min(), _x.max(), 200)
                _y_fit = _slope * _x_fit + _intercept

                # 2D density hex scatter
                _fig_scatter = px.density_heatmap(
                    _df, x="fare", y="tip", nbinsx=40, nbinsy=40,
                    labels={"fare": "Fare ($)", "tip": "Tip ($)"},
                    color_continuous_scale=[[0, "#0d1117"], [0.2, "#0d2a1a"],
                                            [0.5, CYAN], [0.8, YELLOW], [1, "#fff"]],
                )
                _fig_scatter.add_trace(go.Scatter(
                    x=_x_fit, y=_y_fit, mode="lines",
                    line=dict(color=ROSE, width=2.5, dash="dash"),
                    name=f"OLS (slope={_slope:.3f})",
                ))
                _fig_scatter.update_layout(coloraxis_showscale=False)
                styled(_fig_scatter, "Fare vs Tip Density")

                # Tip % histogram
                _df_clean = _df.dropna(subset=["tip_pct"])
                _df_clean = _df_clean[_df_clean["tip_pct"] <= 60]
                _fig_hist = px.histogram(
                    _df_clean, x="tip_pct", nbins=50,
                    labels={"tip_pct": "Tip %"},
                    color_discrete_sequence=[CYAN],
                    opacity=0.85,
                )
                _fig_hist.update_traces(
                    marker_line_width=0,
                    hovertemplate="<b>%{x:.0f}%</b><br>%{y:,} trips<extra></extra>",
                )
                _fig_hist.add_vline(x=_avg_pct, line_color=YELLOW, line_dash="dash",
                                    line_width=2,
                                    annotation_text=f"Mean {fmt_float(_avg_pct,1)}%",
                                    annotation_font=dict(color=YELLOW))
                _fig_hist.add_vline(x=_med_pct, line_color=ORANGE, line_dash="dot",
                                    line_width=2,
                                    annotation_text=f"Median {fmt_float(_med_pct,1)}%",
                                    annotation_font=dict(color=ORANGE))
                styled(_fig_hist, "Tip % Distribution")

                _kpi_cards = "".join([
                    stat_card("Correlation", fmt_float(_corr, 3),         color=YELLOW),
                    stat_card("Avg Tip %",   fmt_float(_avg_pct, 1) + "%", color=CYAN),
                    stat_card("Median Tip %", fmt_float(_med_pct, 1) + "%", color=ORANGE),
                    stat_card("Zero-Tip Trips", fmt_float(_zero_tip_pct, 1) + "%", color=ROSE),
                ])

                _out = mo.vstack([
                    mo.Html(section("Fare & Tip Correlation", "💰")),
                    mo.Html(f'<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem">{_kpi_cards}</div>'),
                    mo.hstack([mo.ui.plotly(_fig_scatter), mo.ui.plotly(_fig_hist)]),
                ])
            except Exception as _e:
                _out = mo.md(f"❌ {_e}")

    _out
    return


# ── Passenger Analysis ────────────────────────────────────────────────────────
@app.cell
def _(COL_DISTANCE, COL_FARE, COL_PASSENGERS, COL_TIP,
      YELLOW, CYAN, ORANGE,
      db_manager, fmt_float, fmt_int, mo, px, section, styled):
    if db_manager is None:
        _out = mo.md("")
    else:
        _t = db_manager.primary_table()
        if not _t or not db_manager.has_cols(_t, COL_PASSENGERS):
            _out = mo.md("")
        else:
            _sel = [f"{COL_PASSENGERS} AS pax", "COUNT(*) AS trips"]
            if db_manager.has_cols(_t, COL_FARE):
                _sel.append(f"AVG(NULLIF({COL_FARE},0)) AS avg_fare")
            if db_manager.has_cols(_t, COL_DISTANCE):
                _sel.append(f"AVG(NULLIF({COL_DISTANCE},0)) AS avg_dist")
            if db_manager.has_cols(_t, COL_TIP):
                _sel.append(f"AVG(NULLIF({COL_TIP},0)) AS avg_tip")
            try:
                with db_manager.connection() as _c:
                    _df = _c.execute(f"""
                        SELECT {', '.join(_sel)}
                        FROM {_t.qualified}
                        WHERE {COL_PASSENGERS} BETWEEN 1 AND 6
                        GROUP BY {COL_PASSENGERS} ORDER BY {COL_PASSENGERS}
                    """).df()

                _df["pct"] = 100 * _df["trips"] / _df["trips"].sum()

                # Funnel-style bar
                _fig_vol = px.bar(
                    _df, x="pax", y="trips",
                    labels={"pax": "Passengers", "trips": "Trips"},
                    color="trips",
                    color_continuous_scale=[[0, "#1a1a2e"], [0.5, CYAN], [1, YELLOW]],
                    text=_df["pct"].map(lambda v: f"{v:.1f}%"),
                )
                _fig_vol.update_traces(
                    textposition="outside",
                    textfont=dict(color="#8b949e", size=11),
                    marker_line_width=0,
                    hovertemplate="<b>%{x} pax</b><br>%{y:,} trips<extra></extra>",
                )
                _fig_vol.update_layout(coloraxis_showscale=False)
                styled(_fig_vol, "Trip Volume by Passenger Count")

                # Multi-metric lines
                _melt_cols = [c for c in ["avg_fare", "avg_dist", "avg_tip"]
                              if c in _df.columns]
                if _melt_cols:
                    _df_m = _df.melt(id_vars="pax", value_vars=_melt_cols,
                                     var_name="metric", value_name="val")
                    _df_m["metric"] = _df_m["metric"].map({
                        "avg_fare": "Avg Fare ($)",
                        "avg_dist": "Avg Distance (mi)",
                        "avg_tip":  "Avg Tip ($)",
                    })
                    _fig_line = px.line(
                        _df_m, x="pax", y="val", color="metric",
                        markers=True,
                        labels={"pax": "Passengers", "val": "Value"},
                        color_discrete_sequence=[YELLOW, CYAN, ORANGE],
                    )
                    _fig_line.update_traces(
                        line_width=2.5,
                        marker=dict(size=9, line=dict(width=2, color="#0d1117")),
                        hovertemplate="<b>%{x} pax</b><br>%{y:.2f}<extra></extra>",
                    )
                    styled(_fig_line, "Avg Metrics by Passenger Count")
                    _charts = mo.hstack([mo.ui.plotly(_fig_vol), mo.ui.plotly(_fig_line)])
                else:
                    _charts = mo.ui.plotly(_fig_vol)

                _out = mo.vstack([
                    mo.Html(section("Passenger Analysis", "👥")),
                    _charts,
                ])
            except Exception as _e:
                _out = mo.md(f"❌ {_e}")

    _out
    return


# ── Pickup Map ────────────────────────────────────────────────────────────────
@app.cell
def _(COL_FARE, COL_START_LAT, COL_START_LON, db_manager, mo, px, section, styled):
    if db_manager is None:
        _out = mo.md("")
    else:
        _t = db_manager.primary_table()
        if not _t or not db_manager.has_cols(_t, COL_START_LAT, COL_START_LON):
            _out = mo.md("")
        else:
            try:
                _fare_col = f", {COL_FARE} AS fare" if db_manager.has_cols(_t, COL_FARE) else ""
                with db_manager.connection() as _c:
                    _df = _c.execute(f"""
                        SELECT {COL_START_LAT} AS lat, {COL_START_LON} AS lon
                               {_fare_col}
                        FROM {_t.qualified}
                        WHERE {COL_START_LAT} BETWEEN 40.4 AND 41.0
                          AND {COL_START_LON} BETWEEN -74.3 AND -73.6
                        USING SAMPLE 4000 ROWS
                    """).df()

                _fig = px.scatter_map(
                    _df, lat="lat", lon="lon",
                    color="fare" if "fare" in _df.columns else None,
                    size_max=6,
                    color_continuous_scale=[
                        [0.0, "#0d1117"],
                        [0.3, "#06b6d4"],
                        [0.7, "#f5c518"],
                        [1.0, "#f43f5e"],
                    ],
                    zoom=10,
                    map_style="carto-darkmatter",
                    opacity=0.65,
                )
                _fig.update_layout(
                    height=520,
                    margin=dict(l=0, r=0, t=45, b=0),
                    paper_bgcolor="#0d1117",
                    title=dict(
                        text="Pickup Locations — coloured by fare",
                        font=dict(family="Georgia, serif", size=15, color="#e6edf3"),
                        x=0.02,
                    ),
                    coloraxis_colorbar=dict(
                        tickfont=dict(color="#8b949e"),
                        title=dict(text="Fare $", font=dict(color="#8b949e")),
                    ),
                )
                _out = mo.vstack([
                    mo.Html(section("Pickup Location Map", "🗺️")),
                    mo.ui.plotly(_fig),
                ])
            except Exception as _e:
                _out = mo.md(f"ℹ️ Map skipped: `{_e}`")

    _out
    return


# ── Footer ────────────────────────────────────────────────────────────────────
@app.cell
def _(mo, BORDER, TEXT_MUT, YELLOW):
    mo.Html(f"""
    <div style="
        margin-top:3rem;
        border-top:1px solid {BORDER};
        padding:1.5rem 0 .5rem;
        display:flex; justify-content:space-between; align-items:center;
        font-family:monospace; font-size:.78rem; color:{TEXT_MUT};
    ">
        <span>🚕 <strong style="color:{YELLOW}">NYC Taxi Analytics</strong> · taxi_pipeline.duckdb</span>
        <span>Re-run cells from sidebar · <strong style="color:{YELLOW}">File → Export as HTML</strong> to share</span>
    </div>
    """)
    return


if __name__ == "__main__":
    app.run()