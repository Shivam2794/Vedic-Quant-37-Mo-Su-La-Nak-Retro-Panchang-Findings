INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Saturn-Venus Combination' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Venus_Combination` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Venus Combination' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Venus_Combination` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Venus Combination' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Venus_Combination` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Venus Combination' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Venus_Combination` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Venus Combination' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Venus_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_Venus_Combination` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Venus_Combination` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Venus_Combination` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon-Saturn Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_Saturn_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Saturn_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon-Mercury Combination In 2nd To Sun' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon-Mercury Combination In 2nd To Sun' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon-Mercury Combination In 2nd To Sun' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon-Mercury Combination In 2nd To Sun' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon-Mercury Combination In 2nd To Sun' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Mercury_Combination_In_2nd_To_Sun` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Rahu-Venus In Capricorn' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Rahu-Venus In Capricorn' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Rahu-Venus In Capricorn' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Rahu-Venus In Capricorn' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Rahu-Venus In Capricorn' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Rahu_Venus_In_Capricorn` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Rahu_Venus_In_Capricorn` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Mercury In Aquarius' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Mercury In Aquarius' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Mercury In Aquarius' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Mercury In Aquarius' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Mercury In Aquarius' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Mercury_In_Aquarius` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Mercury_In_Aquarius` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Aspecting Jupiter' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Aspecting Jupiter' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Aspecting Jupiter' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Aspecting Jupiter' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Aspecting Jupiter' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Aspecting_Jupiter` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Aspecting_Jupiter` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu Behind Moon In Capricorn' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu Behind Moon In Capricorn' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu Behind Moon In Capricorn' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu Behind Moon In Capricorn' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu Behind Moon In Capricorn' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Behind_Moon_In_Capricorn` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Behind_Moon_In_Capricorn` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus in Cancer Placement' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Cancer_Placement` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus in Cancer Placement' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Cancer_Placement` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus in Cancer Placement' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Cancer_Placement` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus in Cancer Placement' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Cancer_Placement` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus in Cancer Placement' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Cancer_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_in_Cancer_Placement` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Cancer_Placement` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Cancer_Placement` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars And Saturn With Mercury In The Second House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars And Saturn With Mercury In The Second House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars And Saturn With Mercury In The Second House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars And Saturn With Mercury In The Second House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars And Saturn With Mercury In The Second House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_And_Saturn_With_Mercury_In_The_Second_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury In Leo' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_Leo` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury In Leo' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_Leo` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury In Leo' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_Leo` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury In Leo' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_Leo` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury In Leo' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_In_Leo` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_In_Leo` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_In_Leo` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL