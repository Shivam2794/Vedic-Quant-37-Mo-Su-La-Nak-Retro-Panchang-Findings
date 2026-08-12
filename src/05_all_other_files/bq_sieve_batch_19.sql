INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Moon In 5th House Of Upapada' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon In 5th House Of Upapada' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon In 5th House Of Upapada' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon In 5th House Of Upapada' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon In 5th House Of Upapada' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_5th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_5th_House_Of_Upapada` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus In 11th House Of Upapada' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus In 11th House Of Upapada' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus In 11th House Of Upapada' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus In 11th House Of Upapada' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus In 11th House Of Upapada' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_11th_House_Of_Upapada` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_11th_House_Of_Upapada` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon In Taurus' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Taurus` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon In Taurus' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Taurus` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon In Taurus' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Taurus` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon In Taurus' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Taurus` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon In Taurus' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_In_Taurus` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Taurus` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Taurus` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter, Moon, Rahu in 11th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter, Moon, Rahu in 11th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter, Moon, Rahu in 11th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter, Moon, Rahu in 11th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter, Moon, Rahu in 11th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter__Moon__Rahu_in_11th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter__Moon__Rahu_in_11th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun in Aquarius, Capricorn, or Cancer in 11th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun in Aquarius, Capricorn, or Cancer in 11th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun in Aquarius, Capricorn, or Cancer in 11th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun in Aquarius, Capricorn, or Cancer in 11th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun in Aquarius, Capricorn, or Cancer in 11th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Aquarius__Capricorn__or_Cancer_in_11th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury, Saturn in 11th House Aspected by Rahu' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury, Saturn in 11th House Aspected by Rahu' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury, Saturn in 11th House Aspected by Rahu' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury, Saturn in 11th House Aspected by Rahu' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury, Saturn in 11th House Aspected by Rahu' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury__Saturn_in_11th_House_Aspected_by_Rahu` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in 11th House Debilitated in Navamsa or Drekkana' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in 11th House Debilitated in Navamsa or Drekkana' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in 11th House Debilitated in Navamsa or Drekkana' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in 11th House Debilitated in Navamsa or Drekkana' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in 11th House Debilitated in Navamsa or Drekkana' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_11th_House_Debilitated_in_Navamsa_or_Drekkana` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury and Moon in 11th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_and_Moon_in_11th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury and Moon in 11th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_and_Moon_in_11th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury and Moon in 11th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_and_Moon_in_11th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury and Moon in 11th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_and_Moon_in_11th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury and Moon in 11th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_and_Moon_in_11th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_and_Moon_in_11th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_and_Moon_in_11th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 8th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_8th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 8th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_8th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 8th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_8th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 8th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_8th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu In 8th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_8th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_In_8th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_8th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_8th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon In 8th House Aspected By Mars' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon In 8th House Aspected By Mars' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon In 8th House Aspected By Mars' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon In 8th House Aspected By Mars' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon In 8th House Aspected By Mars' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_8th_House_Aspected_By_Mars` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_8th_House_Aspected_By_Mars` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL