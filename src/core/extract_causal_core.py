"""
Post-Sieve Causal Core Extractor
=================================
Runs after sector_sieve_candidates.csv is fully populated.
Applies multi-criteria filters to extract the "Causal Core" —
the set of features with genuine, robust, cross-validated alpha.

Criteria:
  1. cost_adjusted_ir  > 0.3  (>0.3 Sharpe-like ratio after 5bps cost)
  2. n_active          > 100  (sufficient observations)
  3. differential_return > 0.001  (>0.1% raw edge)
  4. pearson_corr  != NaN and != 0
  5. Appears in >= 2 horizons OR >= 2 sectors  (cross-validation)
  6. Activation rate: 0.01 <= rate <= 0.99  (not degenerate)

Output:
  - causal_core.csv          (filtered survivors)
  - causal_core_summary.md   (human-readable report)
  - top_signals_by_type.csv  (breakdown by feature type)
"""
import csv
import math
from collections import defaultdict
import os

SIEVE_CSV = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\sector_sieve_candidates.csv'
OUTPUT_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch'

def safe_float(x, default=0.0):
    try:
        v = float(x)
        return v if math.isfinite(v) else default
    except:
        return default

def get_feature_type(rule_name):
    """Classify rule name into high-level feature type."""
    if rule_name.startswith('ton_'):
        return 'TransitOverNatal'
    elif rule_name.startswith('asp_'):
        return 'Aspect'
    elif rule_name.startswith('rule_'):
        return 'KnowledgeRule'
    elif rule_name.startswith('house_'):
        return 'House'
    elif rule_name.startswith('parashari_'):
        return 'ParashariAspect'
    elif any(rule_name.startswith(d) for d in ['D1_', 'D2_', 'D3_', 'D4_', 'D7_', 'D9_',
                                                  'D10_', 'D12_', 'D16_', 'D20_', 'D24_',
                                                  'D27_', 'D30_', 'D40_', 'D45_', 'D60_']):
        varga = rule_name.split('_')[0]
        return f'DivisionalChart_{varga}'
    elif rule_name.startswith('dasha_'):
        return 'Dasha'
    elif rule_name.startswith('jaimini_'):
        return 'JaiminiKaraka'
    elif rule_name.startswith('ashtakavarga_'):
        return 'Ashtakavarga'
    elif rule_name in ['tithi', 'vaara', 'yoga_panchang', 'karana']:
        return 'Panchang'
    elif rule_name in ['sade_sati_active', 'rahu_over_natal_moon']:
        return 'SpecialPattern'
    else:
        return 'Other'

def main():
    print("=" * 60)
    print("POST-SIEVE CAUSAL CORE EXTRACTOR")
    print("=" * 60)
    
    if not os.path.exists(SIEVE_CSV):
        print(f"ERROR: Sieve CSV not found at {SIEVE_CSV}")
        return
    
    rows = list(csv.DictReader(open(SIEVE_CSV, encoding='utf-8')))
    print(f"Total Sieve rows: {len(rows):,}")
    
    # ── STEP 1: Apply individual filters ──────────────────────────
    survivors = []
    filter_stats = defaultdict(int)
    
    for r in rows:
        rule = r['rule_name']
        horizon = r['horizon']
        sector = r.get('sector', 'Unknown')
        
        ir = safe_float(r.get('cost_adjusted_ir', 0))
        n = safe_float(r.get('n_active', 0))
        dr = safe_float(r.get('differential_return', 0))
        corr = safe_float(r.get('pearson_corr', 0))
        rate = safe_float(r.get('activation_rate', 0))
        
        filter_stats['total'] += 1
        
        if abs(ir) < 0.3:
            filter_stats['fail_ir'] += 1
            continue
        if n < 100:
            filter_stats['fail_n'] += 1
            continue
        if abs(dr) < 0.001:
            filter_stats['fail_dr'] += 1
            continue
        if corr == 0.0:
            filter_stats['fail_corr'] += 1
            continue
        if rate < 0.01 or rate > 0.99:
            filter_stats['fail_rate'] += 1
            continue
        
        survivors.append({
            'rule_name': rule,
            'horizon': horizon,
            'sector': sector,
            'cost_adjusted_ir': ir,
            'differential_return': dr,
            'pearson_corr': corr,
            'n_active': int(n),
            'activation_rate': rate,
            'feature_type': get_feature_type(rule),
        })
        filter_stats['pass'] += 1
    
    print(f"\nFilter Results:")
    print(f"  Total rows:           {filter_stats['total']:,}")
    print(f"  Failed |IR| < 0.3:    {filter_stats['fail_ir']:,}")
    print(f"  Failed n < 100:       {filter_stats['fail_n']:,}")
    print(f"  Failed |dr| < 0.001:  {filter_stats['fail_dr']:,}")
    print(f"  Failed corr == 0:     {filter_stats['fail_corr']:,}")
    print(f"  Failed rate OOB:      {filter_stats['fail_rate']:,}")
    print(f"  PASSED (survivors):   {filter_stats['pass']:,}")
    
    # ── STEP 2: Cross-validation filter (≥2 horizons OR ≥2 sectors) ──
    rule_horizons = defaultdict(set)
    rule_sectors = defaultdict(set)
    for s in survivors:
        rule_horizons[s['rule_name']].add(s['horizon'])
        rule_sectors[s['rule_name']].add(s['sector'])
    
    causal_core = [
        s for s in survivors
        if len(rule_horizons[s['rule_name']]) >= 2 or len(rule_sectors[s['rule_name']]) >= 2
    ]
    
    print(f"\n  After cross-validation (>=2 horizons or sectors): {len(causal_core):,}")
    
    # ── STEP 3: Sort by |IR| descending ───────────────────────────
    causal_core.sort(key=lambda x: abs(x['cost_adjusted_ir']), reverse=True)
    
    # ── STEP 4: Write outputs ──────────────────────────────────────
    core_path = os.path.join(OUTPUT_DIR, 'causal_core.csv')
    with open(core_path, 'w', newline='', encoding='utf-8') as f:
        if causal_core:
            writer = csv.DictWriter(f, fieldnames=causal_core[0].keys())
            writer.writeheader()
            writer.writerows(causal_core)
    print(f"\nWrote causal_core.csv: {len(causal_core):,} rows")
    
    # ── STEP 5: Summary by feature type ───────────────────────────
    type_stats = defaultdict(lambda: {'count': 0, 'best_ir': 0.0, 'examples': []})
    for s in causal_core:
        ft = s['feature_type']
        type_stats[ft]['count'] += 1
        if abs(s['cost_adjusted_ir']) > abs(type_stats[ft]['best_ir']):
            type_stats[ft]['best_ir'] = s['cost_adjusted_ir']
        if len(type_stats[ft]['examples']) < 3:
            type_stats[ft]['examples'].append(s['rule_name'])
    
    print("\nCausal Core by Feature Type:")
    print(f"{'Type':<25} {'Count':>6} {'Best IR':>8}  Top Examples")
    print("-" * 80)
    for ft, stats in sorted(type_stats.items(), key=lambda x: -x[1]['count']):
        examples = ', '.join(set(stats['examples']))[:50]
        print(f"  {ft:<23} {stats['count']:>6} {stats['best_ir']:>+8.4f}  {examples}")
    
    # ── STEP 6: Top 30 signals overall ────────────────────────────
    print(f"\nTop 30 Signals (Causal Core):")
    print(f"{'IR':>8} {'DR':>8} {'n':>8} {'Type':<20} {'Signal':<50} Sector/Horizon")
    print("-" * 130)
    for s in causal_core[:30]:
        print(
            f"  {s['cost_adjusted_ir']:>+6.4f}"
            f"  {s['differential_return']:>+8.5f}"
            f"  {s['n_active']:>8,}"
            f"  {s['feature_type']:<20}"
            f"  {s['rule_name'][:48]:<50}"
            f"  [{s['sector']}] [{s['horizon']}]"
        )
    
    # ── STEP 7: Write markdown report ─────────────────────────────
    md_path = os.path.join(OUTPUT_DIR, 'causal_core_summary.md')
    unique_rules = set(s['rule_name'] for s in causal_core)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Causal Core Summary\n\n")
        f.write(f"- **Total Sieve rows tested:** {len(rows):,}\n")
        f.write(f"- **Survivors (single-pass):** {filter_stats['pass']:,}\n")
        f.write(f"- **Causal Core (cross-validated):** {len(causal_core):,} rows\n")
        f.write(f"- **Unique rule names in Core:** {len(unique_rules)}\n\n")
        
        f.write(f"## Feature Type Breakdown\n\n")
        f.write(f"| Feature Type | Count | Best IR |\n|---|---|---|\n")
        for ft, stats in sorted(type_stats.items(), key=lambda x: -x[1]['count']):
            f.write(f"| {ft} | {stats['count']} | {stats['best_ir']:+.4f} |\n")
        
        f.write(f"\n## Top 50 Signals\n\n")
        f.write(f"| IR | DR | n | Type | Signal | Sector | Horizon |\n")
        f.write(f"|---|---|---|---|---|---|---|\n")
        for s in causal_core[:50]:
            f.write(
                f"| {s['cost_adjusted_ir']:+.4f} | {s['differential_return']:+.5f}"
                f" | {s['n_active']:,} | {s['feature_type']} | {s['rule_name']}"
                f" | {s['sector']} | {s['horizon']} |\n"
            )
    
    print(f"\nWrote causal_core_summary.md")
    print(f"\n{'='*60}")
    print(f"CAUSAL CORE: {len(unique_rules)} unique features ready for PCMCI + ML")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
