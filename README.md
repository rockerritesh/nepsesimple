# nepsesimple

A fast, black-and-white **NEPSE market terminal** — the whole Nepal Stock Exchange on one screen, plus a deep technical lookup for any security. Static site, refreshed twice a day by GitHub Actions.

**Live:** [nepse.sumityadav.com.np](https://nepse.sumityadav.com.np)

[![Update file(s)](https://github.com/rockerritesh/nepsesimple/actions/workflows/update.yml/badge.svg)](https://github.com/rockerritesh/nepsesimple/actions/workflows/update.yml)
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/J3J1TRQBI)

## Pages

| Page | What it shows |
|---|---|
| `index.html` — **Overview** | Everything a trader needs at a glance: NEPSE index + breadth, primary indices, top gainers / losers / volume leaders, 52-week extremes, sector heatmap, and live alpha signals. |
| `terminal.html` — **Terminal** | Deep technical view of any symbol: OHLCV, VWAP, 120/180-day averages, 52-week range bar, price-band peers, a quant next-close estimate, and a fully sortable/filterable trading universe. |
| `report.html` — **Report** | Auto-compiled daily market brief (breadth, index moves, standout movers, where turnover concentrated, top quant candidates). |
| `ipo.html` — **IPO** | Open / upcoming / recent IPO · FPO · rights issues. |
| `data_table.html` | Raw pandas data table (for API consumers). |

The UI is a static front-end (`assets/terminal.css` + `assets/terminal.js`) that reads the JSON the pipeline publishes — the alpha scanners and the per-stock quant model run **in the browser**, so the pages work off the committed data with no backend.

## Data pipeline (`simple.py`, run by CI)

Scrapes sharesansar / merolagani (with an optional best-effort enrichment from the official `nepalstock.com.np` export) and writes to `docs/`:

| File | Contents |
|---|---|
| `nepsesimple.json` | Full trading universe (OHLC, LTP, VWAP, volume, turnover, 120/180-day avg, 52-week H/L). |
| `index_data.json` | Primary indices (OHLC + turnover) and sector sub-indices. |
| `market_summary.json` | Top gainers / losers / turnover / volume. |
| `predictions.json` | NEPSE next-index regression forecast + ranked alpha candidates (momentum / liquidity / value-bounce). |
| `ipo.json` | Current IPO / FPO / rights issues. |
| `report.md` | Human-readable daily brief. |
| `graph.png` | NEPSE index history with a linear-regression forecast point. |

## Alpha signals

Three quantitative screens, taxonomy shared with the [my-agents](https://github.com/rockerritesh/my-agents) insights bot and computed both server-side (for `predictions.json`) and client-side (for the live tables):

- **Momentum** — trading above the 120/180-day average with a positive day and real volume.
- **Liquidity** — top ~20% by combined turnover / volume / transaction percentile rank.
- **Value-bounce** — within 10% of the 52-week low and turning up.

Names hitting two or more screens get a score bonus. **This is a quantitative screen, not investment advice.**

## Develop locally

```bash
pip install -r requirements.txt
python simple.py            # refresh docs/*.json (needs network)
cd docs && python -m http.server 8000   # then open http://localhost:8000
```

Made with ❤️ by [Sumit Yadav](https://sumityadav.com.np).
