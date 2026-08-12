CREATE OR REPLACE TABLE `antigravity_quant.sieve_results` AS
SELECT
    'Sun-Mercury-Venus Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury-Venus Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury-Venus Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury-Venus Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury-Venus Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_Venus_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_Venus_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus-Ketu Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Ketu_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus-Ketu Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Ketu_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus-Ketu Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Ketu_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus-Ketu Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Ketu_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus-Ketu Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Ketu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_Ketu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Ketu_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Ketu_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus-Saturn Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Saturn_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus-Saturn Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Saturn_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus-Saturn Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Saturn_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus-Saturn Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Saturn_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus-Saturn Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_Saturn_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Saturn_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus with Sun Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Sun_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus with Sun Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Sun_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus with Sun Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Sun_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus with Sun Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Sun_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus with Sun Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Sun_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_with_Sun_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Sun_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Sun_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus with Moon Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Moon_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus with Moon Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Moon_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus with Moon Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Moon_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus with Moon Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Moon_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus with Moon Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_with_Moon_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Moon_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Moon_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mars Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mars_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mars Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mars_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mars Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mars_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mars Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mars_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mars Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mars_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_with_Mars_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mars_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mars_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mercury Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mercury_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mercury Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mercury_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mercury Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mercury_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mercury Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mercury_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus with Mercury Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Mercury_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Mercury_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Mercury_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus with Rahu Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Rahu_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus with Rahu Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Rahu_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus with Rahu Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Rahu_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus with Rahu Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Rahu_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus with Rahu Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_with_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_with_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_with_Rahu_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Conjunction of Sun and Rahu' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Conjunction of Sun and Rahu' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Conjunction of Sun and Rahu' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Conjunction of Sun and Rahu' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Conjunction of Sun and Rahu' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Conjunction_of_Sun_and_Rahu` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Conjunction_of_Sun_and_Rahu` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL