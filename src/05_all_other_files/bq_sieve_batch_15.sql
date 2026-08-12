INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Venus In 12th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_12th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus In 12th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_12th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus In 12th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_12th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus In 12th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_12th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus In 12th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_In_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_In_12th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_In_12th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_In_12th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect On Mercury' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect On Mercury' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect On Mercury' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect On Mercury' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Retrograde Saturn Aspect On Mercury' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Retrograde_Saturn_Aspect_On_Mercury` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Retrograde_Saturn_Aspect_On_Mercury` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Transit Over Sun In Virgo' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Transit Over Sun In Virgo' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Transit Over Sun In Virgo' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Transit Over Sun In Virgo' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Transit Over Sun In Virgo' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Transit_Over_Sun_In_Virgo` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Transit_Over_Sun_In_Virgo` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars In Gemini' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Gemini` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars In Gemini' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Gemini` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars In Gemini' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Gemini` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars In Gemini' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Gemini` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars In Gemini' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Gemini` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_In_Gemini` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Gemini` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Gemini` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury in 5th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_5th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury in 5th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_5th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury in 5th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_5th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury in 5th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_5th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury in 5th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_5th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_in_5th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_5th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_5th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Virgo Transit' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Virgo_Transit` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Virgo Transit' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Virgo_Transit` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Virgo Transit' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Virgo_Transit` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Virgo Transit' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Virgo_Transit` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Virgo Transit' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Virgo_Transit` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Virgo_Transit` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Virgo_Transit` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars Aspect On Jupiter' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars Aspect On Jupiter' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars Aspect On Jupiter' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars Aspect On Jupiter' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars Aspect On Jupiter' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn Aspect On Jupiter' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn Aspect On Jupiter' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn Aspect On Jupiter' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn Aspect On Jupiter' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn Aspect On Jupiter' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Aspect_On_Jupiter` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Aspect_On_Jupiter` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Aspect_On_Jupiter` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus-Mercury In 3rd House From Saturn' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus-Mercury In 3rd House From Saturn' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus-Mercury In 3rd House From Saturn' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus-Mercury In 3rd House From Saturn' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun-Venus-Mercury In 3rd House From Saturn' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Venus_Mercury_In_3rd_House_From_Saturn` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Ketu-Mars Conjunction in Leo' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Ketu-Mars Conjunction in Leo' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Ketu-Mars Conjunction in Leo' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Ketu-Mars Conjunction in Leo' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Ketu-Mars Conjunction in Leo' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Ketu_Mars_Conjunction_in_Leo` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL