#!/usr/bin/env python
# coding: utf-8
# Open the file in read mode
with open("docs/html.txt", "r") as f:
    # Read the contents of the file
    asadas = f.read()

# print(asadas)

import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import date

# import openpyxl
import matplotlib.pyplot as plt
import bs4
import html5lib

# import telegram
# from telegram import InputFile


# Load data from the URL
url = "https://merolagani.com/Indices.aspx"
df = pd.read_html(url)[0]
df = df.iloc[::-1].reset_index(drop=True)

# Create X and Y arrays for regression analysis
y = np.array(df["Index Value"])
x = np.linspace(1, len(y), len(y)).reshape(-1, 1)

# Perform linear regression on the data
reg = LinearRegression()
reg.fit(x, y)

# Predict the next data point using the linear regression model
next_index = reg.predict(np.array(len(y) + 1).reshape(1, -1))[0]

# Get today's date
today = date.today()
date_str = date.isoformat(today)

# Plot the data and regression line
plt.figure(figsize=(16, 8))
plt.plot(df["Date (AD)"], df["Index Value"], "bo-", label="Index Value")
plt.plot(date_str, next_index, "ro", label="Predicted Next Index Value")

# Add annotations
plt.annotate(
    f"Predicted: {next_index:.2f}",
    xy=(date_str, next_index),
    xytext=(-50, 30),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->", color="red"),
)
plt.annotate(
    f"Regression Line: {reg.coef_[0]:.2f}x + {reg.intercept_:.2f}",
    xy=(0.05, 0.95),
    xycoords="axes fraction",
    fontsize=12,
    ha="left",
    va="top",
)

# Add regression line
plt.plot(df["Date (AD)"], reg.predict(x), "g--", label="Regression Line")

# Format x-axis
plt.xticks(rotation=45, ha="right")
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))

plt.xlabel("Date")
plt.ylabel("Index Value")
plt.title("Nepal Stock Exchange NEPSE Index Value")
plt.legend()
plt.grid()
plt.savefig("docs/graph.png")
plt.show()


# FOR STOCK

urlstock = "https://www.sharesansar.com/market"
htmlstock = requests.get(urlstock).content
df_list_stock = pd.read_html(htmlstock)

df_stock = df_list_stock[3]
df_stock.to_csv("docs/stock.csv")
stok_html = df_stock.to_html()
# df_stock.to_html("stock.html")
# df_stock

# make stock.html by appending asadas and stok_html
stok_html = asadas + stok_html + "</body> </html>"

# save stock.html
with open("docs/stock.html", "w") as output:
    output.write(stok_html)


top_trans = df_list_stock[-2].to_html()
# append asadas with top_trans and save as toptransactions.html
html = asadas + str(top_trans) + "</body> </html>"
with open("docs/toptransactions.html", "w") as output:
    output.write(html)


top_volum = df_list_stock[-3].to_html()
# append asadas with top_volum and save as topvolume.html
html = asadas + str(top_volum) + "</body> </html>"
with open("docs/topvolume.html", "w") as output:
    output.write(html)


gold = df_list_stock[-7].to_html()
# append asadas with gold and save as gold.html
html = asadas + str(gold) + "</body> </html>"
with open("docs/gold.html", "w") as output:
    output.write(html)


compare = df_list_stock[-8].to_html("compare.html")
# append asadas with compare and save as compare.html
html = asadas + str(compare) + "</body> </html>"
with open("docs/compare.html", "w") as output:
    output.write(html)


index = df_list_stock[-12].to_html()

# === JSON EXPORTS ===
import json
from datetime import date as _date

_today = _date.today().isoformat()

# Export index data as JSON
# df_list_stock[-12] has columns: Index, Open, High, Low, Close, Point Change, % Change, Turnover
_index_df = df_list_stock[-12]
_index_records = []
for _, row in _index_df.iterrows():
    _index_records.append(
        {
            "name": str(row.get("Index", "")),
            "open": float(row.get("Open", 0)),
            "high": float(row.get("High", 0)),
            "low": float(row.get("Low", 0)),
            "current": float(row.get("Close", 0)),
            "points_change": float(row.get("Point Change", 0)),
            "pct_change": float(row.get("% Change", 0)),
            "turnover": float(row.get("Turnover", 0)),
        }
    )

# Sub-indices from table 3
# Columns: Sub Index, Open, High, Low, Close, Point, % Change, Turnover
_sub_index_df = df_list_stock[3]


def _cell(row, *names, default=0.0):
    """Fetch the first present column by name, else fall back to 0."""
    for n in names:
        if n in row.index:
            try:
                return float(row[n])
            except (TypeError, ValueError):
                return default
    return default


_sub_records = []
for _, row in _sub_index_df.iterrows():
    _sub_records.append(
        {
            "name": str(row.iloc[0]) if len(row) > 0 else "",
            "open": _cell(row, "Open"),
            "high": _cell(row, "High"),
            "low": _cell(row, "Low"),
            "current": _cell(row, "Close"),
            "points_change": _cell(row, "Point", "Point Change"),
            "pct_change": _cell(row, "% Change", "Change %"),
            "turnover": _cell(row, "Turnover"),
        }
    )

_index_data = {
    "date": _today,
    "primary": _index_records,
    "sub_indices": _sub_records,
}
with open("docs/index_data.json", "w") as f:
    json.dump(_index_data, f, indent=2)


# Export market summary (gainers, losers, turnover, volume) as JSON
def _parse_gainer_loser(df):
    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "symbol": str(row.iloc[0]) if len(row) > 0 else "",
                "ltp": float(row.iloc[1]) if len(row) > 1 else 0,
                "point_change": float(row.iloc[2]) if len(row) > 2 else 0,
                "pct_change": float(row.iloc[3]) if len(row) > 3 else 0,
            }
        )
    return records


def _parse_turnover(df):
    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "symbol": str(row.iloc[0]) if len(row) > 0 else "",
                "turnover": float(row.iloc[1]) if len(row) > 1 else 0,
                "ltp": float(row.iloc[2]) if len(row) > 2 else 0,
            }
        )
    return records


def _parse_volume(df):
    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "symbol": str(row.iloc[0]) if len(row) > 0 else "",
                "volume": float(row.iloc[1]) if len(row) > 1 else 0,
                "ltp": float(row.iloc[2]) if len(row) > 2 else 0,
            }
        )
    return records


_market_summary = {
    "date": _today,
    "top_gainers": _parse_gainer_loser(df_list_stock[-6]),
    "top_losers": _parse_gainer_loser(df_list_stock[-5]),
    "top_turnover": _parse_turnover(df_list_stock[-4]),
    "top_volume": _parse_volume(df_list_stock[-3]),
}
with open("docs/market_summary.json", "w") as f:
    json.dump(_market_summary, f, indent=2)

print(
    f"[JSON] Exported index_data.json ({len(_index_records)} primary, {len(_sub_records)} sub-indices)"
)
print(
    f"[JSON] Exported market_summary.json ({len(_market_summary['top_gainers'])} gainers, {len(_market_summary['top_losers'])} losers)"
)
# === END JSON EXPORTS ===

urlshare = "https://www.sharesansar.com/?show=home"
htmlshare = requests.get(urlshare).content
df_list_share = pd.read_html(htmlshare)
df_share = df_list_share[2]

# df_share.to_html("ipo.html")
# df_list_share[1].to_html("bonous.html")
# df_list_share[4].to_html("newsofbank.html")
# df_list_share[5].to_html("stock.html")
# df_list_share[6].to_html("gradeofcompany.html")
# df_list_share[7].to_html("companymerged.html")
# df_list_share[0].to_html("bookclosure.html")

# merge df_list_share[7] to df_list_share[0] and save as details.html with appropriate html tags
html = (
    asadas
    + str("<h2> Share </h2>")
    + str(df_share.to_html())
    + str("<h2> Bonous </h2>")
    + str(df_list_share[1].to_html())
    + str("<h2> News of Bank </h2>")
    + str(df_list_share[4].to_html())
    + str("<h2> Stock </h2>")
    + str(df_list_share[5].to_html())
    + str("<h2> Grade of Company </h2>")
    + str(df_list_share[6].to_html())
    + str("<h2> Company Merged </h2>")
    + str(df_list_share[7].to_html())
    + str("<h2> Book Closure </h2>")
    + str(df_list_share[0].to_html())
    + "</body> </html>"
)
with open("docs/details.html", "w") as output:
    output.write(html)


# === Per-stock trading universe (JSON API + legacy data table) ===
# NOTE: docs/index.html is now the static terminal UI (assets/terminal.*).
# The full pandas table lives at docs/data_table.html so CI never clobbers the UI.
_stock_df = pd.read_html("https://www.sharesansar.com/today-share-price")[-1]

# Back-compatible JSON keyed by row index -> {field: value} (consumed by the terminal)
_stock_df.T.to_json("docs/nepsesimple.json")

# Legacy raw table page (kept for reference / API consumers)
_table_html = asadas + index + _stock_df.to_html(index=False) + "</body> </html>"
with open("docs/data_table.html", "w") as output:
    output.write(_table_html)


# === Optional enrichment from the official NEPSE API (best-effort) ===
# The streamlit branch pulls the official export; we mirror it here so the
# universe can carry MARKET_CAPITALIZATION / TOTAL_TRADES when reachable.
def _enrich_from_official_api(records):
    try:
        _d = _date.today().isoformat()
        _url = (
            "https://www.nepalstock.com.np/api/nots/market/export/" f"todays-price/{_d}"
        )
        _resp = requests.get(
            _url,
            headers={"User-Agent": "Mozilla/5.0", "Accept": "text/csv"},
            timeout=20,
            verify=False,
        )
        if _resp.status_code != 200 or not _resp.text.strip():
            print("[API] official NEPSE export unavailable — skipping enrichment")
            return records
        import io

        _api = pd.read_csv(io.StringIO(_resp.text))
        _api.columns = [str(c).strip().upper().replace(" ", "_") for c in _api.columns]
        _sym_col = next((c for c in _api.columns if "SYMBOL" in c), None)
        if not _sym_col:
            return records
        _by_sym = {str(r[_sym_col]).strip(): r for _, r in _api.iterrows()}
        _extra = [
            "MARKET_CAPITALIZATION",
            "TOTAL_TRADES",
            "FIFTY_TWO_WEEKS_HIGH",
            "FIFTY_TWO_WEEKS_LOW",
            "AVERAGE_TRADED_PRICE",
        ]
        _hits = 0
        for rec in records:
            _m = _by_sym.get(str(rec.get("Symbol", "")).strip())
            if _m is None:
                continue
            _hits += 1
            for k in _extra:
                if k in _api.columns:
                    try:
                        rec[k.title().replace("_", " ")] = float(_m[k])
                    except (TypeError, ValueError):
                        pass
        print(f"[API] enriched {_hits} stocks from official NEPSE export")
    except Exception as _e:  # never break CI on the optional source
        print(f"[API] enrichment skipped: {_e}")
    return records


# === Alpha signal scanners + predictions (ported from my-agents) ===
def _num(v):
    try:
        f = float(v)
        return f if f == f else None  # drop NaN
    except (TypeError, ValueError):
        return None


def _compute_predictions(records):
    """Momentum / liquidity / value-bounce scanners over the universe."""
    stocks = []
    for r in records:
        stocks.append(
            {
                "symbol": r.get("Symbol"),
                "ltp": _num(r.get("LTP")),
                "diffPct": _num(r.get("Diff %")),
                "vol": _num(r.get("Vol")),
                "turnover": _num(r.get("Turnover")),
                "trans": _num(r.get("Trans.")),
                "d120": _num(r.get("120 Days")),
                "d180": _num(r.get("180 Days")),
                "w52h": _num(r.get("52 Weeks High")),
                "w52l": _num(r.get("52 Weeks Low")),
            }
        )

    def clamp01(x):
        return max(0.0, min(1.0, x))

    signals = []
    # momentum
    for s in stocks:
        if not s["symbol"] or not s["ltp"] or s["ltp"] <= 0:
            continue
        if s["diffPct"] is None or s["diffPct"] <= 0 or not s["vol"] or s["vol"] <= 0:
            continue
        if not s["d120"] or s["d120"] <= 0 or s["ltp"] <= s["d120"]:
            continue
        comp = s["ltp"] / s["d120"] - 1
        if s["d180"] and s["d180"] > 0:
            comp += s["ltp"] / s["d180"] - 1
        if s["w52h"] and s["w52l"] and s["w52h"] > s["w52l"]:
            comp += (s["ltp"] - s["w52l"]) / (s["w52h"] - s["w52l"]) * 0.5
        comp += min(s["diffPct"], 10.0) / 20.0
        signals.append(
            (
                s["symbol"],
                "momentum",
                clamp01(comp / 2),
                1.0 if s["d180"] and s["w52h"] else 0.7,
            )
        )
    # liquidity (top 20% by combined pct-rank)
    liq = [
        s
        for s in stocks
        if s["symbol"]
        and s["turnover"] is not None
        and s["vol"] is not None
        and s["trans"] is not None
    ]
    if liq:

        def prank(vals):
            n = len(vals)
            order = sorted(range(n), key=lambda i: vals[i])
            out = [0.0] * n
            for rank, idx in enumerate(order):
                out[idx] = rank / max(n - 1, 1)
            return out

        tr = prank([s["turnover"] or 0 for s in liq])
        vr = prank([s["vol"] or 0 for s in liq])
        nr = prank([s["trans"] or 0 for s in liq])
        scored = sorted(
            [(liq[i]["symbol"], (tr[i] + vr[i] + nr[i]) / 3) for i in range(len(liq))],
            key=lambda x: -x[1],
        )
        for sym, sc in scored[: max(1, int(len(scored) * 0.2))]:
            signals.append((sym, "liquidity", sc, 1.0))
    # value bounce
    for s in stocks:
        if not s["symbol"] or not s["ltp"] or s["ltp"] <= 0:
            continue
        if s["diffPct"] is None or s["diffPct"] <= 0:
            continue
        if not s["w52l"] or s["w52l"] <= 0 or not s["w52h"] or s["w52h"] <= 0:
            continue
        if s["ltp"] > s["w52l"] * 1.10:
            continue
        upside = (s["w52h"] - s["ltp"]) / s["ltp"]
        proximity = clamp01(1 - (s["ltp"] - s["w52l"]) / max(s["w52l"] * 0.10, 1e-9))
        signals.append(
            (
                s["symbol"],
                "value_bounce",
                clamp01(
                    proximity * 0.5 + min(s["diffPct"], 10) / 20 + min(upside, 2) / 4
                ),
                0.8,
            )
        )

    by_sym = {}
    for sym, typ, strength, conf in signals:
        by_sym.setdefault(sym, []).append((typ, strength * conf))
    candidates = []
    for sym, sigs in by_sym.items():
        combined = sum(sc for _, sc in sigs)
        types = sorted({t for t, _ in sigs})
        if len(types) >= 2:
            combined *= 1.2
        candidates.append(
            {"symbol": sym, "combined_score": round(combined, 3), "signal_types": types}
        )
    candidates.sort(key=lambda c: -c["combined_score"])
    return candidates[:25]


try:
    _records = list(_stock_df.to_dict(orient="records"))
    _records = _enrich_from_official_api(_records)
    # re-write the universe JSON including any enrichment fields
    pd.DataFrame(_records).T.to_json("docs/nepsesimple.json")
    _predictions = {
        "date": _today,
        "nepse_index_forecast": {
            "next_value": round(float(next_index), 2),
            "trend_slope": round(float(reg.coef_[0]), 4),
            "method": "linear regression on merolagani index history",
        },
        "alpha_candidates": _compute_predictions(_records),
    }
    with open("docs/predictions.json", "w") as f:
        json.dump(_predictions, f, indent=2)
    print(
        f"[JSON] Exported predictions.json ({len(_predictions['alpha_candidates'])} candidates)"
    )
except Exception as _e:
    print(f"[JSON] predictions skipped: {_e}")


# === IPO JSON export (for the styled IPO page) ===
try:
    _ipo_df = df_list_share[2]
    _ipo_df.to_json("docs/ipo.json", orient="records")
    print(f"[JSON] Exported ipo.json ({len(_ipo_df)} rows)")
except Exception as _e:
    print(f"[JSON] ipo.json skipped: {_e}")


# === Human-readable daily brief (markdown, for README / Telegram) ===
try:
    _nepse_row = _index_records[0] if _index_records else {}
    _mkt = _market_summary
    _lines = [
        f"# NEPSE Daily Brief — {_today}",
        "",
        f"**{_nepse_row.get('name','NEPSE Index')}**: "
        f"{_nepse_row.get('current','?')} "
        f"({_nepse_row.get('points_change',0):+.2f}, "
        f"{_nepse_row.get('pct_change',0):+.2f}%) · "
        f"turnover {_nepse_row.get('turnover',0):,.0f}",
        "",
        "## Top Gainers",
    ]
    for g in _mkt["top_gainers"][:5]:
        _lines.append(f"- {g['symbol']}: {g['ltp']} ({g['pct_change']:+.2f}%)")
    _lines += ["", "## Top Losers"]
    for g in _mkt["top_losers"][:5]:
        _lines.append(f"- {g['symbol']}: {g['ltp']} ({g['pct_change']:+.2f}%)")
    _lines += [
        "",
        f"_Auto-generated. NEPSE index forecast (next session): "
        f"{next_index:.2f}. Not investment advice._",
    ]
    with open("docs/report.md", "w") as f:
        f.write("\n".join(_lines))
    print("[REPORT] Exported report.md")
except Exception as _e:
    print(f"[REPORT] report.md skipped: {_e}")
