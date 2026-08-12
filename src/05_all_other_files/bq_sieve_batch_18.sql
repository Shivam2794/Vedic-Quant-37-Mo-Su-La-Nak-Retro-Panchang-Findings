INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Retrograde Saturn Aspect on Mars (Chart 254)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect on Mars (Chart 254)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect on Mars (Chart 254)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect on Mars (Chart 254)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect on Mars (Chart 254)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_on_Mars__Chart_254_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 12th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_12th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 12th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_12th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 12th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_12th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 12th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_12th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 12th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_In_12th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_12th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_12th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury In 12th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_12th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury In 12th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_12th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury In 12th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_12th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury In 12th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_12th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury In 12th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_In_12th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_12th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_12th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars In Taurus With Saturn And Rahu' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars In Taurus With Saturn And Rahu' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars In Taurus With Saturn And Rahu' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars In Taurus With Saturn And Rahu' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars In Taurus With Saturn And Rahu' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Taurus_With_Saturn_And_Rahu` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon in Leo with Ketu' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Leo_with_Ketu` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon in Leo with Ketu' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Leo_with_Ketu` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon in Leo with Ketu' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Leo_with_Ketu` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon in Leo with Ketu' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Leo_with_Ketu` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon in Leo with Ketu' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Leo_with_Ketu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Leo_with_Ketu` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Leo_with_Ketu` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Pisces Contacting Mars and Jupiter' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Pisces Contacting Mars and Jupiter' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Pisces Contacting Mars and Jupiter' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Pisces Contacting Mars and Jupiter' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Pisces Contacting Mars and Jupiter' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Pisces_Contacting_Mars_and_Jupiter` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon In 2nd House Of Karakamsa' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon In 2nd House Of Karakamsa' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon In 2nd House Of Karakamsa' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon In 2nd House Of Karakamsa' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon In 2nd House Of Karakamsa' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 2nd House Of Karakamsa' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 2nd House Of Karakamsa' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 2nd House Of Karakamsa' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 2nd House Of Karakamsa' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 2nd House Of Karakamsa' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 2nd House Of Karakamsa' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 2nd House Of Karakamsa' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 2nd House Of Karakamsa' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 2nd House Of Karakamsa' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 2nd House Of Karakamsa' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_2nd_House_Of_Karakamsa` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_2nd_House_Of_Karakamsa` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 7th House Prediction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_7th_House_Prediction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 7th House Prediction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_7th_House_Prediction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 7th House Prediction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_7th_House_Prediction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 7th House Prediction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_7th_House_Prediction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn In 7th House Prediction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_7th_House_Prediction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_7th_House_Prediction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_7th_House_Prediction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL