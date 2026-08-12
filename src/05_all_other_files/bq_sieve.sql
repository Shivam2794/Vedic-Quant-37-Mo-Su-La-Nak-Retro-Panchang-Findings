-- BigQuery Statistical Sieve for Astrological Rule Features (Phase 1)
-- ===================================================================
-- This script evaluates the predictive power of the 611 compiled AST rules
-- against N-day forward returns. 
-- It computes three core metrics to filter noise from the causal core:
--   1. Activation Rate (Must trigger often enough to be tradable)
--   2. Cost-Adjusted Information Ratio (Mean Return / Std Dev of Return)
--   3. Spearman Rank Correlation (Monotonic relationship with future returns)

-- Assumes a flat table `antigravity_quant.feature_matrix`
-- and `antigravity_quant.stock_returns`

-- 1. Combine Returns with Rule Activations
WITH rule_activations AS (
    SELECT 
        f.ticker,
        f.date,
        -- Forward 5-day return (simplified close-to-close)
        r.fwd_return_5d,
        -- Example of dynamically unpivoting the rules if they were stored in an array 
        -- or querying specific rule columns directly. Assuming wide format here.
        f.rule_Sun_Venus_Conjunction,
        f.rule_Venus_Ketu_Conjunction,
        f.rule_Saturn_Moon_Conjunction,
        f.rule_Jupiter_in_5th_House,
        f.rule_Venus_Mahadasha
        -- ... (All 611 compiled rules)
    FROM `antigravity_quant.feature_matrix` f
    JOIN `antigravity_quant.stock_returns` r 
      ON f.ticker = r.ticker AND f.date = r.date
),

-- 2. Compute the Sieve Metrics per Rule
-- We UNPIVOT the wide table to group by Rule Name easily
unpivoted_rules AS (
    SELECT 
        ticker,
        date,
        fwd_return_5d,
        rule_name,
        rule_active
    FROM rule_activations
    UNPIVOT (
        rule_active FOR rule_name IN (
            rule_Sun_Venus_Conjunction,
            rule_Venus_Ketu_Conjunction,
            rule_Saturn_Moon_Conjunction,
            rule_Jupiter_in_5th_House,
            rule_Venus_Mahadasha
            -- ... 
        )
    )
),

sieve_metrics AS (
    SELECT
        rule_name,
        
        -- A. Activation Rate (Total Active Days / Total Possible Days)
        SUM(rule_active) / COUNT(*) AS activation_rate,
        
        -- B. Information Ratio (IR) of the Rule
        -- Mean forward return when rule is active
        AVG(IF(rule_active = 1, fwd_return_5d, NULL)) AS mean_fwd_return_when_active,
        STDDEV(IF(rule_active = 1, fwd_return_5d, NULL)) AS stddev_fwd_return_when_active,
        
        -- C. Spearman Rank Correlation Components
        -- BigQuery natively supports CORR() for Pearson, but for Spearman we need ranks.
        -- As an approximation for the sieve, we use Pearson on the binary indicator.
        CORR(rule_active, fwd_return_5d) AS pearson_correlation
        
    FROM unpivoted_rules
    GROUP BY rule_name
)

-- 3. Final Filtered Causal Candidates
SELECT 
    rule_name,
    activation_rate,
    mean_fwd_return_when_active,
    (mean_fwd_return_when_active - 0.0005) / NULLIF(stddev_fwd_return_when_active, 0) AS cost_adjusted_ir,
    pearson_correlation
FROM sieve_metrics
WHERE 
    -- Sieve Conditions:
    activation_rate > 0.01          -- Must activate at least 1% of the time (avoid extreme outliers)
    AND activation_rate < 0.50      -- Must not be active all the time (avoid meaningless baselines)
    AND (
        ABS(mean_fwd_return_when_active) > 0.005  -- Must generate at least 50bps expected return
        OR ABS(pearson_correlation) > 0.02        -- Or have a statistically significant correlation
    )
ORDER BY cost_adjusted_ir DESC;
