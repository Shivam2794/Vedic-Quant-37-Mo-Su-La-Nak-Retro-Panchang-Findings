INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Moon-Venus Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Venus_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon-Venus Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Venus_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon-Venus Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Venus_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon-Venus Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Venus_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon-Venus Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Venus_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Venus_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Mars Combination' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Mars_Combination` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Mars Combination' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Mars_Combination` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Mars Combination' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Mars_Combination` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Mars Combination' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Mars_Combination` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Mars Combination' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Mars_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_Mars_Combination` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Mars_Combination` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Mars_Combination` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn-Rahu Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn-Rahu Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn-Rahu Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn-Rahu Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn-Rahu Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Rahu_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus-Jupiter Combination (Chart 459)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus-Jupiter Combination (Chart 459)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus-Jupiter Combination (Chart 459)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus-Jupiter Combination (Chart 459)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus-Jupiter Combination (Chart 459)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Jupiter_Combination__Chart_459_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Jupiter_Combination__Chart_459_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jaimini Rule (Moon in Aries, Taurus, Gemini)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jaimini Rule (Moon in Aries, Taurus, Gemini)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jaimini Rule (Moon in Aries, Taurus, Gemini)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jaimini Rule (Moon in Aries, Taurus, Gemini)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jaimini Rule (Moon in Aries, Taurus, Gemini)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jaimini_Rule__Moon_in_Aries__Taurus__Gemini_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Venus Conjunction in Aquarius (Introductory)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Venus Conjunction in Aquarius (Introductory)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Venus Conjunction in Aquarius (Introductory)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Venus Conjunction in Aquarius (Introductory)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Venus Conjunction in Aquarius (Introductory)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Venus_Conjunction_in_Aquarius__Introductory_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn in 1st House in Leo (Introductory)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn in 1st House in Leo (Introductory)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn in 1st House in Leo (Introductory)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn in 1st House in Leo (Introductory)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn in 1st House in Leo (Introductory)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_1st_House_in_Leo__Introductory_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_1st_House_in_Leo__Introductory_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Aquarius with Saturn in 7th in Leo (Chart 460)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Aquarius with Saturn in 7th in Leo (Chart 460)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Aquarius with Saturn in 7th in Leo (Chart 460)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Aquarius with Saturn in 7th in Leo (Chart 460)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Aquarius with Saturn in 7th in Leo (Chart 460)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Aquarius_with_Saturn_in_7th_in_Leo__Chart_460_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter has Venus in 3rd House (Chart 460)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter has Venus in 3rd House (Chart 460)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter has Venus in 3rd House (Chart 460)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter has Venus in 3rd House (Chart 460)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter has Venus in 3rd House (Chart 460)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_has_Venus_in_3rd_House__Chart_460_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn in Leo (Chart 461)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn in Leo (Chart 461)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn in Leo (Chart 461)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn in Leo (Chart 461)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn in Leo (Chart 461)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_in_Leo__Chart_461_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_in_Leo__Chart_461_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL