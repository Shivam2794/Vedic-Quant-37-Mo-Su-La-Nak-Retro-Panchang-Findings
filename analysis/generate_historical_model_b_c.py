import sys, re, math, os, shutil
sys.stdout.reconfigure(encoding='utf-8')
"""
generate_historical_model_b_c.py
=================================
Historical backtest version (2024-2026) of the Model B/C report generator.

Parses master_trading_plan_2024_2026.md, extracts every signal per day,
re-runs Model B (Time-Decay) and Model C (Two-Factor Orthogonal) aggregation,
then writes new report copies for all 8 documents stamped as HISTORICAL BACKTEST.

CRITICAL WARNINGS (displayed in all reports):
  ⚠️  The 37 Findings were derived from 141-year DJIA/SPY data (1880-2021).
  ⚠️  The 2024-2026 period PARTIALLY OVERLAPS the training window.
  ⚠️  This is an in-sample/near-OOS validation — treat accuracy with caution.

Output files (2024-2026):
  master_trading_plan_2024_2026_Model_B.md
"""

# Workspace directories
WORKSPACE = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a"
BASE2 = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\35732b90-976f-4cc4-b3fe-7fc24c167fe0"

IN_SAMPLE_WARNING = """> ⚠️ **IN-SAMPLE OVERLAP WARNING:** The 37 Vedic Quant Findings were derived
> from 141 years of DJIA/SPY data (1880–2021). The tested period partially
> falls within the TRAINING window. Therefore, accuracy figures for this period
> are likely **OVERSTATED** relative to true out-of-sample performance. Use this
> backtest as a consistency check, not as a proof of generalization.
> A fully clean OOS test would require data from 2022 onwards ONLY.
"""

# ─────────────────────────────────────────────────────────────────────────────
# MODEL IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────────────────────

# C1 FIX: TOXIC_FINDINGS must be filtered in B/C too (matches signal_aggregator.py)
TOXIC_FINDINGS = {16, 25}

def _log_weight(n_size):
    return math.log10(max(2, n_size)) / 2.0

def _sigmoid(x, k):
    arg = -k * x
    if arg > 700: return 0.0
    if arg < -700: return 1.0
    return 1.0 / (1.0 + math.exp(arg))

def _resolve_tier1(signals):
    t1 = [s for s in signals if s.get("tier", 3) == 1]
    if not t1: return None
    # Model A: Take the one with highest absolute yield.
    dominant = max(t1, key=lambda x: abs(x.get("yield_pct", 0.0)))
    direction = dominant.get("direction", "SHORT")
    
    if direction == "LONG":
        return (0.999, "TIER 1 OVERRIDE", "LONG")
    else:
        return (0.001, "TIER 1 OVERRIDE", "SHORT")

def model_b_time_decay(signals):
    t1 = _resolve_tier1(signals)
    if t1: return t1
    active = [s for s in signals if s["direction"] != "CASH" and s.get("finding") not in TOXIC_FINDINGS]  # C1 FIX
    if not active: return (0.5, "FLAT", "CASH")
    net = 0.0
    for s in active:
        d = 1.0 if s["direction"] == "LONG" else -1.0
        hold = max(1, s.get("hold_days", 20))
        dr = s["yield_pct"] / hold
        net += d * abs(dr) * _log_weight(s["n_size"])
    p = _sigmoid(net, 8.0)
    direction = "LONG" if p >= 0.5 else "SHORT"
    if abs(p - 0.5) < 1e-9: direction = "CASH"
    label = _bias_label(p, direction)
    return (p, label, direction)

def model_c_two_factor(signals):
    t1 = _resolve_tier1(signals)
    if t1: return t1
    active = [s for s in signals if s["direction"] != "CASH" and s.get("finding") not in TOXIC_FINDINGS]  # C1 FIX
    if not active: return (0.5, "FLAT", "CASH")

    macro_sigs = [s for s in active if s.get("hold_days", 20) >= 7]
    micro_sigs = [s for s in active if s.get("hold_days", 20) < 7]

    def _engine(sigs):
        if not sigs: return 0.5, 0.0
        net_daily = 0.0
        for s in sigs:
            d = 1.0 if s["direction"] == "LONG" else -1.0
            hold = max(1, s.get("hold_days", 20))
            dr = s["yield_pct"] / hold
            net_daily += d * abs(dr) * _log_weight(s["n_size"])
        return _sigmoid(net_daily, 8.0), net_daily

    p_macro, net_macro = _engine(macro_sigs)
    p_micro, net_micro = _engine(micro_sigs)

    if not macro_sigs:   p, net_dir = p_micro, net_micro; regime = "MICRO_ONLY"
    elif not micro_sigs: p, net_dir = p_macro, net_macro; regime = "MACRO_ONLY"
    else:
        macro_bull = p_macro >= 0.5
        micro_bull = p_micro >= 0.5
        if macro_bull == micro_bull:
            total = abs(net_macro) + abs(net_micro)
            if total == 0: w_mac = w_mic = 0.5
            else: w_mac = abs(net_macro)/total; w_mic = abs(net_micro)/total
            p = w_mac * p_macro + w_mic * p_micro
            regime = "ALIGNED_LONG" if macro_bull else "ALIGNED_SHORT"
        else:
            denom = net_macro**2 + net_micro**2
            if denom == 0: w_mic = 0.5
            else: w_mic = net_micro**2 / denom
            w_mac = 1.0 - w_mic
            p = w_mac * p_macro + w_mic * p_micro
            regime = "COUNTER_TREND_RALLY" if (not macro_bull and micro_bull) else "COUNTER_TREND_DIP"

    direction = "LONG" if p >= 0.5 else "SHORT"
    if p == 0.5: direction = "CASH"
    label = _bias_label(p, direction)
    return (p, f"{label} [{regime}]", direction)

def _bias_label(p, direction):
    if direction in ("CASH", "NEUTRAL"): return "FLAT / NEUTRAL"
    if direction == "LONG":
        if p >= 0.95: return "ABSOLUTE MAX LONG"
        if p >= 0.80: return "EXTREME LONG CONVICTION"
        if p >= 0.65: return "STRONG LONG"
        if p >= 0.55: return "MILD LONG"
        return "MARGINAL LONG"
    else:
        if p <= 0.05: return "ABSOLUTE MAX SHORT"
        if p <= 0.20: return "EXTREME SHORT CONVICTION"
        if p <= 0.35: return "STRONG SHORT"
        if p <= 0.45: return "MILD SHORT"
        return "MARGINAL SHORT"

def _net_yield_daily(signals):
    net = 0.0
    for s in signals:
        if s["direction"] in ("LONG", "SHORT"):
            d = 1.0 if s["direction"] == "LONG" else -1.0
            hold = max(1, s.get("hold_days", 20))
            dr = s["yield_pct"] / hold
            net += d * abs(dr) * _log_weight(s["n_size"])
    return net

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

DIRECTION_RE  = re.compile(r'\|\s+\*\*Direction\*\*\s+\|\s+\*\*([A-Z]+)\*\*\s+\|')
YIELD_RE      = re.compile(r'Historical Return.*?([0-9]+\.[0-9]+)%')
HOLD_RE       = re.compile(r'Hold Period.*?(\d+)\s+trading')
FINDING_RE    = re.compile(r'Finding #(\d+)')
DATE_RE       = re.compile(r'###\s+☀️\s+(.+?)\s+—\s+DAILY MATH AGGREGATE')
SIGNAL_HDR_RE = re.compile(r'###\s+\[(\d+)/\d+\]')

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.master_trading_plan import FINDING_META

N_SIZE_MAP = {k: v["n_size"] for k, v in FINDING_META.items()}
TIER_MAP = {k: v["tier"] for k, v in FINDING_META.items()}

def parse_master_plan(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    days, day_order, current_date, current_signal = {}, [], None, None
    for line in lines:
        if dm := DATE_RE.search(line):
            if current_signal and current_date:
                days.setdefault(current_date, []).append(current_signal)
            current_date = dm.group(1).strip()
            if current_date not in days:
                days[current_date] = []
                day_order.append(current_date)
            current_signal = None
        elif sm := SIGNAL_HDR_RE.search(line):
            if current_signal: days[current_date].append(current_signal)
            current_signal = {"finding": None, "direction": None, "yield_pct": 0.0, "hold_days": 20, "n_size": 1000, "tier": 3}
            if fn_m := FINDING_RE.search(line):
                fn = int(fn_m.group(1))
                current_signal.update({"finding": fn, "n_size": N_SIZE_MAP.get(fn, 1000), "tier": TIER_MAP.get(fn, 3)})
        elif current_signal:
            if dm2 := DIRECTION_RE.search(line): current_signal["direction"] = dm2.group(1).strip()
            if ym := YIELD_RE.search(line): current_signal["yield_pct"] = float(ym.group(1))
            if hm := HOLD_RE.search(line): current_signal["hold_days"] = int(hm.group(1))
    if current_signal and current_date: days[current_date].append(current_signal)
    return days, day_order, lines

def rebuild_plan(src_lines, days, day_order, model_fn, model_name, suffix):
    content = ''.join(src_lines)
    content = re.sub(r'# MASTER VEDIC-QUANT TRADING PLAN \d{4}-\d{4}', f"# MASTER VEDIC-QUANT TRADING PLAN {suffix} — {model_name} [HISTORICAL BACKTEST]", content)
    content = re.sub(r'## All 37 Proven Findings \| SPY / ES1! \| Swiss Ephemeris \(Lahiri Sidereal\)', f"## All 37 Proven Findings | SPY / ES1! | Swiss Ephemeris (Lahiri Sidereal) | Aggregator: {model_name} | {suffix} HISTORICAL BACKTEST", content)
    content = content.replace("---\n\n## HOW TO USE THIS PLAN", f"---\n\n{IN_SAMPLE_WARNING}\n---\n\n## HOW TO USE THIS PLAN")
    
    def make_agg_block(date_str):
        sigs = days.get(date_str, [])
        p, label, direction, net_y = aggregate_day(sigs, model_fn)
        tier1 = _resolve_tier1(sigs)
        t1_line = "> 🚨 **TIER 1 OVERRIDE ACTIVE** 🚨\n" if (tier1 and tier1[0] != 0.5) else ("> ⚖️ **TIER 1 CONFLICT — NEUTRAL** ⚖️\n" if (tier1 and tier1[0] == 0.5) else "")
        return f"> **Net System Bias [{model_name}]:** {label}\n{t1_line}> **P(Long):** {p*100:.1f}% | **P(Short):** {(1-p)*100:.1f}% | **Expected Daily Force:** {net_y:+.3f}% / day\n"

    return re.sub(r'(###\s+☀️\s+.+?—\s+DAILY MATH AGGREGATE\n)((?:>.*\n)*)', lambda m: m.group(1) + make_agg_block(DATE_RE.search(m.group(1)).group(1).strip()), content)

def aggregate_day(signals, model_fn):
    if not signals: return 0.5, "FLAT / NEUTRAL", "CASH", 0.0
    p, label, direction = model_fn(signals)
    return p, label, direction, _net_yield_daily(signals)

def build_summary(days, day_order, model_fn, model_name, suffix):
    total_long = total_short = total_cash = 0
        with open(out_plan, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        size_mb = os.path.getsize(out_plan) / 1024 / 1024
        print(f"  Written: {out_plan}  ({size_mb:.2f} MB)")

        # 2. Trading Plan Summary
        out_summary = os.path.join(OUT_BASE, f"TRADING_PLAN_SUMMARY_{YEAR_LABEL}_{model_name}.md")
        print(f"  Building {model_name} historical summary...")
        summary_content = build_summary(days, day_order, model_fn, model_name)
        with open(out_summary, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        print(f"  Written: {out_summary}")

        # 3. Vedic Quant Findings
        out_findings = os.path.join(OUT_BASE, f"vedic_quant_findings_{YEAR_LABEL}_{model_name}.md")
        print(f"  Building {model_name} findings...")
        findings_content = build_findings(model_name)
        with open(out_findings, 'w', encoding='utf-8') as f:
            f.write(findings_content)
        print(f"  Written: {out_findings}")

        # 4. Historical Trading Calendar
        out_calendar = os.path.join(OUT_BASE, f"historical_trading_calendar_{YEAR_LABEL}_{model_name}.md")
        print(f"  Building {model_name} historical calendar...")
        cal_content = build_calendar(days, day_order, model_fn, model_name)
        with open(out_calendar, 'w', encoding='utf-8') as f:
            f.write(cal_content)
        print(f"  Written: {out_calendar}")

    print("\n" + "="*60)
    print("ALL 8 HISTORICAL REPORTS GENERATED SUCCESSFULLY")
    print("="*60)

    # Quick stats comparison
    print(f"\n📊 MODEL COMPARISON ({COVERAGE}):")
    for model_fn, model_name in [(model_b_time_decay,"Model_B"),(model_c_two_factor,"Model_C")]:
        counts = {"LONG":0,"SHORT":0,"CASH":0}
        for d in day_order:
            sigs = days.get(d,[])
            if not sigs: continue
            p, label, direction, _ = aggregate_day(sigs, model_fn)
            counts[direction if direction in counts else "CASH"] += 1
        total = sum(counts.values())
        print(f"  {model_name}: LONG={counts['LONG']}({counts['LONG']/max(1,total)*100:.0f}%) "
              f"SHORT={counts['SHORT']}({counts['SHORT']/max(1,total)*100:.0f}%) "
              f"CASH={counts['CASH']}({counts['CASH']/max(1,total)*100:.0f}%)")

    print("\n⚠️  NEXT STEP: Download SPY historical OHLC data for the period")
    print(f"    {COVERAGE}")
    print("    then run accuracy_validator.py to compare predictions vs actual market moves.")

if __name__ == "__main__":
    main()
