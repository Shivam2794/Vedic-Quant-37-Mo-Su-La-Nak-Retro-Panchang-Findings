INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Saturn in Taurus' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Taurus` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Taurus' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Taurus` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Taurus' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Taurus` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Taurus' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Taurus` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Taurus' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_in_Taurus` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Taurus` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Taurus` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn and Venus in Leo' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_and_Venus_in_Leo` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn and Venus in Leo' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_and_Venus_in_Leo` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn and Venus in Leo' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_and_Venus_in_Leo` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn and Venus in Leo' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_and_Venus_in_Leo` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn and Venus in Leo' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_and_Venus_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_and_Venus_in_Leo` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_and_Venus_in_Leo` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars-Jupiter Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Jupiter_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars-Jupiter Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Jupiter_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars-Jupiter Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Jupiter_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars-Jupiter Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Jupiter_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars-Jupiter Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Jupiter_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_Jupiter_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Jupiter_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Jupiter_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars-Rahu Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Rahu_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars-Rahu Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Rahu_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars-Rahu Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Rahu_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars-Rahu Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Rahu_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars-Rahu Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Rahu_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_Rahu_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Rahu_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Rahu_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars-Moon Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Moon_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars-Moon Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Moon_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars-Moon Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Moon_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars-Moon Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Moon_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars-Moon Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Moon_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_Moon_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Moon_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Moon_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars-Saturn Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Saturn_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars-Saturn Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Saturn_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars-Saturn Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Saturn_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars-Saturn Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Saturn_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars-Saturn Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Saturn_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_Saturn_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Saturn_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Saturn_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars Dasha' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Dasha` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Dasha` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Dasha` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars Dasha' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Dasha` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Dasha` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Dasha` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars Dasha' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Dasha` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Dasha` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Dasha` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars Dasha' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Dasha` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Dasha` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Dasha` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars Dasha' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Dasha` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Dasha` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_Dasha` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Dasha` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Dasha` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Dasha` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect on Mercury (Chart 103)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect on Mercury (Chart 103)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect on Mercury (Chart 103)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect on Mercury (Chart 103)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect on Mercury (Chart 103)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_on_Mercury__Chart_103_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon-Jupiter-Rahu Conjunction in Sagittarius (Chart 104)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon-Jupiter-Rahu Conjunction in Sagittarius (Chart 104)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon-Jupiter-Rahu Conjunction in Sagittarius (Chart 104)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon-Jupiter-Rahu Conjunction in Sagittarius (Chart 104)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon-Jupiter-Rahu Conjunction in Sagittarius (Chart 104)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_Jupiter_Rahu_Conjunction_in_Sagittarius__Chart_104_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Capricorn and Transiting to Sagittarius (Chart 105)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Capricorn and Transiting to Sagittarius (Chart 105)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Capricorn and Transiting to Sagittarius (Chart 105)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Capricorn and Transiting to Sagittarius (Chart 105)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Capricorn and Transiting to Sagittarius (Chart 105)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Capricorn_and_Transiting_to_Sagittarius__Chart_105_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL