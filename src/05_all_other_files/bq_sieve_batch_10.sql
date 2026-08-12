INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Mars In 12th To Mercury-Rahu Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars In 12th To Mercury-Rahu Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars In 12th To Mercury-Rahu Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars In 12th To Mercury-Rahu Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars In 12th To Mercury-Rahu Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_12th_To_Mercury_Rahu_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon in Scorpio' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Scorpio` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon in Scorpio' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Scorpio` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon in Scorpio' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Scorpio` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon in Scorpio' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Scorpio` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon in Scorpio' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_in_Scorpio` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Scorpio` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Scorpio` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Libra' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Libra` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Libra' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Libra` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Libra' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Libra` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Libra' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Libra` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Libra' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Libra` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_in_Libra` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Libra` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Libra` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus in Taurus' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Taurus` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus in Taurus' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Taurus` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus in Taurus' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Taurus` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus in Taurus' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Taurus` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus in Taurus' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_in_Taurus` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_in_Taurus` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_in_Taurus` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Gemini' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Gemini` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Gemini' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Gemini` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Gemini' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Gemini` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Gemini' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Gemini` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Gemini' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_in_Gemini` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Gemini` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Gemini` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun in Gemini' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Gemini` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun in Gemini' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Gemini` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun in Gemini' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Gemini` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun in Gemini' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Gemini` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun in Gemini' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_in_Gemini` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Gemini` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Gemini` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury Has Jupiter In 2nd House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury Has Jupiter In 2nd House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury Has Jupiter In 2nd House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury Has Jupiter In 2nd House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury Has Jupiter In 2nd House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Has_Jupiter_In_2nd_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Has_Jupiter_In_2nd_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Ketu In 4th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_4th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Ketu In 4th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_4th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Ketu In 4th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_4th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Ketu In 4th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_4th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Ketu In 4th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_4th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Ketu_In_4th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_4th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_4th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon And Saturn In Pisces' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_And_Saturn_In_Pisces` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon And Saturn In Pisces' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_And_Saturn_In_Pisces` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon And Saturn In Pisces' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_And_Saturn_In_Pisces` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon And Saturn In Pisces' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_And_Saturn_In_Pisces` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon And Saturn In Pisces' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_And_Saturn_In_Pisces` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_And_Saturn_In_Pisces` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_And_Saturn_In_Pisces` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars Conjunct Mercury (Chart 326)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars Conjunct Mercury (Chart 326)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars Conjunct Mercury (Chart 326)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars Conjunct Mercury (Chart 326)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars Conjunct Mercury (Chart 326)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Conjunct_Mercury__Chart_326_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Conjunct_Mercury__Chart_326_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL