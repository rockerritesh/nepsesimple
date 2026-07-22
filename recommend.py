#!/usr/bin/env python
# coding: utf-8
"""Gemini-powered daily recommendations for nepsesimple.

Reads the JSON the data pipeline (simple.py) publishes, asks Gemini to turn the
quantitative candidates + market context into a ranked recommendation list, and
writes docs/recommendations.json for the site to render.

Uses the SAME GEMINI_API_KEY secret as the my-agents insights bot. If the key is
absent or the call fails, it degrades gracefully to a quant-only list so the
GitHub Action never breaks and the page always has data.
"""
import json
import os
import re
from datetime import date


def _load_dotenv(path=".env"):
    """Minimal .env loader (no dependency) so local runs can read the key.
    CI passes the key via GitHub Actions secrets, so this is a local convenience.
    """
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass


_load_dotenv()

DOCS = "docs"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Cheapest Gemini flash tier by default; override with GEMINI_MODEL_NAME.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")

SYSTEM_PROMPT = """You are a disciplined NEPSE (Nepal Stock Exchange) buy-side analyst.
You are given today's market snapshot and a list of quantitatively-screened
candidate stocks. Produce a concise, honest recommendation list.

Rules:
- Only recommend from the candidates provided, plus notable movers if clearly justified.
- Every call must cite concrete numbers from the data (price vs averages, 52w range, volume/turnover, day change).
- Be skeptical: if breadth is weak or a name looks extended, say WATCH or AVOID rather than BUY.
- This is educational, not licensed advice. Never promise returns.

Respond with ONLY valid JSON, no markdown fences, in exactly this shape:
{
  "market_summary": "2-3 sentence read on the session and breadth",
  "recommendations": [
    {"symbol": "XXX", "action": "BUY|ACCUMULATE|WATCH|AVOID",
     "conviction": "high|medium|low",
     "rationale": "one or two sentences citing numbers",
     "risk": "the main risk in a few words"}
  ],
  "outlook": "one sentence on what to watch next session"
}
Return 6-10 recommendations, most compelling first."""


def _read(name, default=None):
    try:
        with open(f"{DOCS}/{name}") as f:
            return json.load(f)
    except Exception:
        return default


def _extract_json(text):
    m = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if m:
        text = m.group(1)
    a, b = text.find("{"), text.rfind("}")
    if a != -1 and b != -1 and b > a:
        text = text[a:b + 1]
    return json.loads(text)


def build_context():
    universe = _read("nepsesimple.json", {}) or {}
    index_data = _read("index_data.json", {}) or {}
    summary = _read("market_summary.json", {}) or {}
    preds = _read("predictions.json", {}) or {}

    rows = list(universe.values()) if isinstance(universe, dict) else (universe or [])
    by_sym = {str(r.get("Symbol")): r for r in rows if r.get("Symbol")}

    def enrich(sym):
        r = by_sym.get(sym, {})
        return {
            "symbol": sym,
            "ltp": r.get("LTP"),
            "diff_pct": r.get("Diff %"),
            "vwap": r.get("VWAP"),
            "d120": r.get("120 Days"),
            "d180": r.get("180 Days"),
            "w52h": r.get("52 Weeks High"),
            "w52l": r.get("52 Weeks Low"),
            "turnover": r.get("Turnover"),
            "vol": r.get("Vol"),
        }

    candidates = preds.get("alpha_candidates", [])[:15]
    enriched = []
    for c in candidates:
        e = enrich(c["symbol"])
        e["quant_score"] = c.get("combined_score")
        e["signals"] = c.get("signal_types")
        enriched.append(e)

    return {
        "date": index_data.get("date") or date.today().isoformat(),
        "primary_indices": index_data.get("primary", []),
        "top_gainers": summary.get("top_gainers", []),
        "top_losers": summary.get("top_losers", []),
        "nepse_forecast": preds.get("nepse_index_forecast", {}),
        "candidates": enriched,
        "universe_size": len(rows),
    }


def gemini_recommend(context):
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL, system_instruction=SYSTEM_PROMPT
    )
    resp = model.generate_content(
        "Market data (JSON):\n" + json.dumps(context, default=str),
        generation_config=genai.GenerationConfig(temperature=0.6, max_output_tokens=4096),
    )
    return _extract_json(resp.text.strip())


def quant_fallback(context):
    """No Gemini available — synthesize a plain recommendation list from scores."""
    recs = []
    for c in context["candidates"][:8]:
        score = c.get("quant_score") or 0
        action = "BUY" if score >= 1.4 else "ACCUMULATE" if score >= 1.0 else "WATCH"
        sig = ", ".join(c.get("signals") or [])
        recs.append({
            "symbol": c["symbol"],
            "action": action,
            "conviction": "high" if score >= 1.4 else "medium" if score >= 1.0 else "low",
            "rationale": f"Quant score {score} from {sig}; LTP {c.get('ltp')} vs 120d {c.get('d120')}.",
            "risk": "Screen-only signal — no fundamental review.",
        })
    return {
        "market_summary": f"{context['universe_size']} scrips traded on "
                          f"{context['date']}. Ranked by the quantitative screen "
                          f"(momentum / liquidity / value-bounce).",
        "recommendations": recs,
        "outlook": "Watch breadth and turnover leaders into the next session.",
    }


def main():
    # When no key is available (e.g. CI without the secret), keep the last
    # committed recommendations.json instead of clobbering it with the quant
    # fallback — so a locally-generated Gemini file survives scheduled runs.
    if not GEMINI_API_KEY and os.path.exists(f"{DOCS}/recommendations.json"):
        print("[recommend] no GEMINI_API_KEY; keeping existing recommendations.json")
        return

    context = build_context()
    used = "gemini:" + GEMINI_MODEL
    try:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not set")
        result = gemini_recommend(context)
        if not isinstance(result, dict) or "recommendations" not in result:
            raise RuntimeError("unexpected Gemini response shape")
    except Exception as e:
        print(f"[recommend] Gemini unavailable ({e}); using quant fallback")
        result = quant_fallback(context)
        used = "quant-fallback"

    result["date"] = context["date"]
    result["generated_by"] = used
    result["disclaimer"] = (
        "Auto-generated from public NEPSE data for educational purposes. "
        "Not investment advice. Do your own research."
    )
    with open(f"{DOCS}/recommendations.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"[recommend] wrote docs/recommendations.json "
          f"({len(result.get('recommendations', []))} recs, via {used})")


if __name__ == "__main__":
    main()
