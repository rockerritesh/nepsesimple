/* ==========================================================================
   NEPSE QUANT TERMINAL — shared data layer + compute (client-side)
   Fetches the JSON exports produced by the CI pipeline (simple.py) and
   computes alpha signals in-browser (port of my-agents/alpha_scanner.py).
   ========================================================================== */
(function (global) {
  "use strict";

  const BASE = ""; // same-origin (served from docs/ root at nepse.sumityadav.com.np)

  /* ---- fetch helpers ---------------------------------------------------- */
  async function getJSON(path) {
    const res = await fetch(`${BASE}${path}?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
    return res.json();
  }

  // nepsesimple.json is keyed by row index ("0","1",...) → array of stock objs
  function normalizeStocks(raw) {
    if (!raw) return [];
    const rows = Array.isArray(raw) ? raw : Object.values(raw);
    return rows
      .filter((r) => r && r.Symbol)
      .map((r) => ({
        symbol: String(r.Symbol),
        open: num(r.Open),
        high: num(r.High),
        low: num(r.Low),
        close: num(r.Close),
        ltp: num(r.LTP),
        vwap: num(r.VWAP),
        vol: num(r.Vol),
        prevClose: num(r["Prev. Close"]),
        turnover: num(r.Turnover),
        trans: num(r["Trans."]),
        diff: num(r.Diff),
        range: num(r.Range),
        diffPct: num(r["Diff %"]),
        rangePct: num(r["Range %"]),
        vwapPct: num(r["VWAP %"]),
        d120: num(r["120 Days"]),
        d180: num(r["180 Days"]),
        w52h: num(r["52 Weeks High"]),
        w52l: num(r["52 Weeks Low"]),
      }));
  }

  function num(v) {
    if (v === null || v === undefined || v === "-" || v === "") return null;
    const n = typeof v === "number" ? v : parseFloat(String(v).replace(/,/g, ""));
    return Number.isFinite(n) ? n : null;
  }

  /* ---- formatting ------------------------------------------------------- */
  const fmt = {
    n(v, d = 2) {
      if (v === null || v === undefined || !Number.isFinite(v)) return "—";
      return v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
    },
    int(v) {
      if (v === null || v === undefined || !Number.isFinite(v)) return "—";
      return Math.round(v).toLocaleString("en-US");
    },
    // 1.2 L (lakh), 3.4 Cr (crore) — NEPSE convention
    vol(v) {
      if (v === null || !Number.isFinite(v)) return "—";
      if (v >= 1e7) return (v / 1e7).toFixed(2) + " Cr";
      if (v >= 1e5) return (v / 1e5).toFixed(2) + " L";
      if (v >= 1e3) return (v / 1e3).toFixed(1) + "k";
      return String(Math.round(v));
    },
    money(v) {
      if (v === null || !Number.isFinite(v)) return "—";
      if (v >= 1e7) return "Rs " + (v / 1e7).toFixed(2) + " Cr";
      if (v >= 1e5) return "Rs " + (v / 1e5).toFixed(2) + " L";
      return "Rs " + Math.round(v).toLocaleString("en-US");
    },
    pct(v, sign = true) {
      if (v === null || !Number.isFinite(v)) return "—";
      const s = (sign && v > 0 ? "+" : "") + v.toFixed(2) + "%";
      return s;
    },
    signPts(v) {
      if (v === null || !Number.isFinite(v)) return "—";
      return (v > 0 ? "▲ " : v < 0 ? "▼ " : "= ") + (v > 0 ? "+" : "") + v.toFixed(2);
    },
  };
  function cls(v) { return v > 0 ? "up" : v < 0 ? "down" : "flat"; }

  /* ---- alpha scanners (port of alpha_scanner.py) ------------------------ */
  function clamp01(x) { return Math.max(0, Math.min(1, x)); }

  function scanMomentum(stocks) {
    const out = [];
    for (const s of stocks) {
      if (!s.ltp || s.ltp <= 0) continue;
      if (s.diffPct === null || s.diffPct <= 0) continue;
      if (!s.vol || s.vol <= 0) continue;
      if (!s.d120 || s.d120 <= 0 || s.ltp <= s.d120) continue;
      let comp = s.ltp / s.d120 - 1;
      if (s.d180 && s.d180 > 0) comp += s.ltp / s.d180 - 1;
      if (s.w52h && s.w52l && s.w52h > s.w52l) comp += ((s.ltp - s.w52l) / (s.w52h - s.w52l)) * 0.5;
      comp += Math.min(s.diffPct, 10) / 20;
      const strength = clamp01(comp / 2);
      const confidence = s.d180 && s.w52h && s.w52l ? 1.0 : 0.7;
      out.push(mkSig(s.symbol, "momentum", 1, strength, confidence,
        `LTP ${s.ltp.toFixed(1)} > 120d ${s.d120.toFixed(1)}, today ${fmt.pct(s.diffPct)}`));
    }
    return out;
  }

  function pctRank(vals) {
    const n = vals.length; if (!n) return [];
    const idx = vals.map((v, i) => [i, v]).sort((a, b) => a[1] - b[1]);
    const ranks = new Array(n).fill(0);
    idx.forEach(([orig], r) => { ranks[orig] = r / Math.max(n - 1, 1); });
    return ranks;
  }

  function scanLiquidity(stocks) {
    const valid = stocks.filter((s) => s.turnover !== null && s.vol !== null && s.trans !== null &&
      ((s.turnover || 0) > 0 || (s.vol || 0) > 0 || (s.trans || 0) > 0));
    if (!valid.length) return [];
    const tr = pctRank(valid.map((s) => s.turnover || 0));
    const vr = pctRank(valid.map((s) => s.vol || 0));
    const nr = pctRank(valid.map((s) => s.trans || 0));
    const scored = valid.map((s, i) => ({ s, score: (tr[i] + vr[i] + nr[i]) / 3 }));
    scored.sort((a, b) => b.score - a.score);
    const cutoff = Math.max(1, Math.floor(scored.length * 0.2));
    return scored.slice(0, cutoff).map(({ s, score }) =>
      mkSig(s.symbol, "liquidity", 1, score, 1.0,
        `Turnover ${fmt.money(s.turnover)}, Vol ${fmt.vol(s.vol)} (pct rank ${score.toFixed(2)})`));
  }

  function scanValueBounce(stocks) {
    const out = [];
    for (const s of stocks) {
      if (!s.ltp || s.ltp <= 0) continue;
      if (s.diffPct === null || s.diffPct <= 0) continue;
      if (!s.w52l || s.w52l <= 0 || !s.w52h || s.w52h <= 0) continue;
      if (s.ltp > s.w52l * 1.1) continue;
      const upside = (s.w52h - s.ltp) / s.ltp;
      const proximity = clamp01(1 - (s.ltp - s.w52l) / Math.max(s.w52l * 0.1, 1e-9));
      const strength = clamp01(proximity * 0.5 + Math.min(s.diffPct, 10) / 20 + Math.min(upside, 2) / 4);
      out.push(mkSig(s.symbol, "value_bounce", 1, strength, 0.8,
        `Near 52w low ${s.w52l.toFixed(1)} (${fmt.pct((s.ltp / s.w52l - 1) * 100)}), upside ${(upside * 100).toFixed(0)}%`));
    }
    return out;
  }

  function mkSig(symbol, type, direction, strength, confidence, reasoning) {
    return { symbol, type, direction, strength, confidence, reasoning,
      score: direction * strength * confidence };
  }

  function computeSignals(stocks) {
    const all = [...scanMomentum(stocks), ...scanLiquidity(stocks), ...scanValueBounce(stocks)];
    const bySym = {};
    all.forEach((sig) => { (bySym[sig.symbol] = bySym[sig.symbol] || []).push(sig); });
    const candidates = Object.entries(bySym).map(([symbol, sigs]) => {
      let combined = sigs.reduce((a, s) => a + s.score, 0);
      const types = [...new Set(sigs.map((s) => s.type))];
      if (types.length >= 2) combined *= 1.2;
      return { symbol, combined: +combined.toFixed(3), types,
        reasonings: sigs.map((s) => s.reasoning) };
    }).sort((a, b) => b.combined - a.combined);
    const byType = {};
    all.forEach((s) => { byType[s.type] = (byType[s.type] || 0) + 1; });
    return { candidates, byType, total: all.length };
  }

  /* ---- naive next-close prediction (per stock) -------------------------- */
  // Mirrors my-agents / streamlit predict_price heuristic: drift the last
  // close by (mean momentum vs prev). With only a daily snapshot we use the
  // relationship between LTP, VWAP and the 120/180-day averages as the drift.
  function predictNextClose(s) {
    if (!s.ltp || s.ltp <= 0) return null;
    const anchors = [];
    if (s.vwap) anchors.push(s.vwap);
    if (s.d120) anchors.push(s.d120);
    if (s.d180) anchors.push(s.d180);
    if (!anchors.length) return { value: s.ltp, drift: 0, confidence: 0.2 };
    // pull LTP toward the mean of its moving anchors (mean-reversion + trend blend)
    const anchor = anchors.reduce((a, b) => a + b, 0) / anchors.length;
    const trend = s.ltp - (s.prevClose || s.ltp);
    const revert = (anchor - s.ltp) * 0.25;
    const value = s.ltp + trend * 0.4 + revert;
    const drift = ((value - s.ltp) / s.ltp) * 100;
    const confidence = clamp01((anchors.length / 3) * 0.7 + (s.vol ? 0.3 : 0));
    return { value, drift, confidence };
  }

  /* ---- per-company history + charts ------------------------------------ */
  const HIST_BASE = "https://raw.githubusercontent.com/Aabishkar2/nepse-data/refs/heads/main/data/company-wise/";

  function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/);
    const head = lines[0].split(",").map((h) => h.trim());
    return lines.slice(1).map((ln) => {
      const cells = ln.split(",");
      const o = {}; head.forEach((h, i) => { o[h] = cells[i]; });
      return o;
    });
  }

  async function loadHistory(symbol) {
    const res = await fetch(`${HIST_BASE}${encodeURIComponent(symbol)}.csv`, { cache: "no-store" });
    if (!res.ok) throw new Error(`history HTTP ${res.status}`);
    const rows = parseCSV(await res.text());
    return rows.map((r) => ({
      date: r.published_date,
      o: num(r.open), h: num(r.high), l: num(r.low), c: num(r.close),
      vol: num(r.traded_quantity),
    })).filter((b) => b.c !== null && b.o !== null).sort((a, b) => a.date < b.date ? -1 : 1);
  }

  function sma(bars, period) {
    const out = new Array(bars.length).fill(null);
    let sum = 0;
    for (let i = 0; i < bars.length; i++) {
      sum += bars[i].c;
      if (i >= period) sum -= bars[i - period].c;
      if (i >= period - 1) out[i] = sum / period;
    }
    return out;
  }

  // Dependency-free SVG candlestick + volume chart.
  function drawChart(container, bars, opts = {}) {
    if (!bars || !bars.length) { container.innerHTML = '<div class="loading">No history available.</div>'; return; }
    const W = 1000, H = 420, padR = 54, padL = 6, priceH = 300, volTop = 330, volH = 78;
    const n = bars.length;
    const useCandles = n <= 260;
    const lo = Math.min(...bars.map((b) => b.l ?? b.c));
    const hi = Math.max(...bars.map((b) => b.h ?? b.c));
    const pad = (hi - lo) * 0.06 || 1;
    const yMin = lo - pad, yMax = hi + pad;
    const maxVol = Math.max(...bars.map((b) => b.vol || 0), 1);
    const x = (i) => padL + (i / Math.max(n - 1, 1)) * (W - padL - padR);
    const y = (v) => 8 + (1 - (v - yMin) / (yMax - yMin)) * priceH;
    const yv = (v) => volTop + (1 - v / maxVol) * volH;
    const bw = Math.max(1, ((W - padL - padR) / n) * 0.62);
    const up = "#29d17c", down = "#ff5b5b", amber = "#d9a441";

    let svg = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" style="width:100%;height:${H}px;display:block">`;
    // grid + price labels
    for (let g = 0; g <= 4; g++) {
      const v = yMin + (g / 4) * (yMax - yMin), yy = y(v);
      svg += `<line x1="${padL}" y1="${yy}" x2="${W - padR}" y2="${yy}" stroke="#181818"/>`;
      svg += `<text x="${W - padR + 4}" y="${yy + 3}" fill="#5a5a5a" font-size="10" font-family="monospace">${fmt.n(v)}</text>`;
    }
    if (useCandles) {
      bars.forEach((b, i) => {
        const cx = x(i), col = b.c >= b.o ? up : down;
        svg += `<line x1="${cx}" y1="${y(b.h)}" x2="${cx}" y2="${y(b.l)}" stroke="${col}" stroke-width="1"/>`;
        const y1 = y(Math.max(b.o, b.c)), y2 = y(Math.min(b.o, b.c));
        svg += `<rect x="${cx - bw / 2}" y="${y1}" width="${bw}" height="${Math.max(1, y2 - y1)}" fill="${col}"/>`;
      });
    } else {
      // area + line for long ranges
      const pts = bars.map((b, i) => `${x(i)},${y(b.c)}`).join(" ");
      svg += `<polyline points="${pts}" fill="none" stroke="${amber}" stroke-width="1.4"/>`;
      svg += `<polygon points="${padL},${y(yMin)} ${pts} ${x(n - 1)},${y(yMin)}" fill="rgba(217,164,65,.08)"/>`;
    }
    // moving average
    const ma = sma(bars, Math.min(20, Math.max(5, Math.floor(n / 6))));
    const mapts = ma.map((v, i) => v == null ? null : `${x(i)},${y(v)}`).filter(Boolean).join(" ");
    if (mapts) svg += `<polyline points="${mapts}" fill="none" stroke="#5aa9e6" stroke-width="1.2" stroke-dasharray="3 3"/>`;
    // last price line
    const last = bars[n - 1].c;
    svg += `<line x1="${padL}" y1="${y(last)}" x2="${W - padR}" y2="${y(last)}" stroke="${amber}" stroke-width=".6" stroke-dasharray="2 3"/>`;
    // volume
    bars.forEach((b, i) => {
      const col = b.c >= b.o ? "rgba(41,209,124,.4)" : "rgba(255,91,91,.4)";
      const vy = yv(b.vol || 0);
      svg += `<rect x="${x(i) - bw / 2}" y="${vy}" width="${bw}" height="${volTop + volH - vy}" fill="${col}"/>`;
    });
    // x date labels
    const ticks = 5;
    for (let t = 0; t <= ticks; t++) {
      const i = Math.round((t / ticks) * (n - 1));
      svg += `<text x="${x(i)}" y="${H - 4}" fill="#5a5a5a" font-size="10" font-family="monospace" text-anchor="middle">${bars[i].date}</text>`;
    }
    svg += `</svg>`;
    container.innerHTML = svg;
  }

  /* ---- expose ----------------------------------------------------------- */
  global.NQT = {
    getJSON, normalizeStocks, num, fmt, cls,
    computeSignals, scanMomentum, scanLiquidity, scanValueBounce, predictNextClose,
    loadHistory, drawChart, sma,
    async loadAll() {
      const [stocksRaw, indexData, marketSummary] = await Promise.all([
        getJSON("/nepsesimple.json").catch(() => null),
        getJSON("/index_data.json").catch(() => null),
        getJSON("/market_summary.json").catch(() => null),
      ]);
      const stocks = normalizeStocks(stocksRaw);
      return { stocks, indexData, marketSummary };
    },
  };
})(window);
