import math

TOXIC_FINDINGS = {16, 1, 11, 27, 20, 2, 4, 26, 6}

def compute_daily_probability(signals):
    """
    Takes a list of signal dictionaries for a single day.
    Returns:
      - p_long (float): Probability of the day being a profitable LONG (0.0 to 1.0)
      - p_short (float): Probability of the day being a profitable SHORT (1.0 - p_long)
      - expected_net_yield (float): The mathematical expected yield of the day
      - net_bias (str): Human readable bias string
      - is_crash_override (bool): True if a Tier 1 signal overrode the math
    """
    
    # ML OPTIMIZATION: Filter out all toxic findings mathematically proven to destroy capital
    if signals:
        signals = [s for s in signals if s.get("finding") not in TOXIC_FINDINGS]
    
    if not signals:
        return 0.50, 0.50, 0.0, "FLAT (NO EDGE)", False

    # 1. Check for Crash / Tier 1 Overrides
    tier1_signals = [s for s in signals if s.get("tier", 3) == 1]
    if tier1_signals:
        # If multiple Tier 1, take the one with the highest absolute yield
        dominant = max(tier1_signals, key=lambda x: abs(x.get("historical_yield", 0)))
        direction = dominant.get("direction", "SHORT")
        
        # Absolute Override
        if direction == "LONG":
            return 0.999, 0.001, dominant.get("historical_yield", 15.0), "ABSOLUTE MAX LONG (TIER 1 OVERRIDE)", True
        else:
            return 0.001, 0.999, -abs(dominant.get("historical_yield", 15.0)), "ABSOLUTE MAX SHORT (TIER 1 OVERRIDE)", True

    # 2. Additive Mathematical Probability
    # For non-crash days, we aggregate the EV tensors
    net_yield = 0.0
    
    for s in signals:
        raw_yield = s.get("historical_yield", 0.0)
        n_size = s.get("n_size", 100)
        direction = s.get("direction", "LONG")
        
        # Calculate Direction Multiplier
        if direction == "LONG":
            d = 1.0
        elif direction == "SHORT":
            d = -1.0
        else:
            d = 0.0 # CASH
            
        # Logarithmic N-Size Weighting
        # Normalized so that N=100 gives a weight of 1.0
        # N=10 gives 0.5, N=1000 gives 1.5
        # We ensure minimum n_size of 2 to avoid log10(1) = 0 or log10(0) error
        safe_n = max(2, n_size)
        weight_n = math.log10(safe_n) / 2.0 
        
        # Yield contribution
        contribution = d * abs(raw_yield) * weight_n
        net_yield += contribution
        
    # Phase 3: Sigmoid Probability Mapping
    # Base formula: P(Long) = 1 / (1 + e^(-k * net_yield))
    # 'k' controls the steepness. We use k=0.55 to ensure that strong conviction
    # days (Yield > 9%) cross the 99% probability threshold.
    k = 0.55
    p_long = 1.0 / (1.0 + math.exp(-k * net_yield))
    p_short = 1.0 - p_long
    
    # 4. Human Readable Bias
    bias = "FLAT"
    if p_long >= 0.90:
        bias = "EXTREME LONG CONVICTION"
    elif p_long >= 0.75:
        bias = "HEAVY LONG"
    elif p_long >= 0.60:
        bias = "MILD LONG"
    elif p_short >= 0.90:
        bias = "EXTREME SHORT CONVICTION"
    elif p_short >= 0.75:
        bias = "HEAVY SHORT"
    elif p_short >= 0.60:
        bias = "MILD SHORT"
        
    return p_long, p_short, net_yield, bias, False

# Quick test if run directly
if __name__ == "__main__":
    test_signals = [
        {"direction": "LONG", "historical_yield": 2.0, "n_size": 900, "tier": 3},
        {"direction": "SHORT", "historical_yield": 4.0, "n_size": 50, "tier": 2}
    ]
    p_long, p_short, net_yield, bias, _ = compute_daily_probability(test_signals)
    print(f"Test Expected Yield: {net_yield:.2f}% | P(Long): {p_long:.1%} | Bias: {bias}")
