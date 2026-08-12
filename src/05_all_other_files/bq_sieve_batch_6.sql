INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Mercury-Moon Conjunction (Chart 306)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Conjunction (Chart 306)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Conjunction (Chart 306)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Conjunction (Chart 306)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury-Moon Conjunction (Chart 306)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_Moon_Conjunction__Chart_306_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_Moon_Conjunction__Chart_306_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun in Leo Chart 172' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Leo_Chart_172` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun in Leo Chart 172' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Leo_Chart_172` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun in Leo Chart 172' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Leo_Chart_172` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun in Leo Chart 172' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Leo_Chart_172` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun in Leo Chart 172' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_in_Leo_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_in_Leo_Chart_172` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_in_Leo_Chart_172` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_in_Leo_Chart_172` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Aquarius Chart 172' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Aquarius Chart 172' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Aquarius Chart 172' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Aquarius Chart 172' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Aquarius Chart 172' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Aquarius_Chart_172` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Aquarius_Chart_172` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Rahu-Saturn Dasha Sequence Chart 172' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Rahu-Saturn Dasha Sequence Chart 172' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Rahu-Saturn Dasha Sequence Chart 172' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Rahu-Saturn Dasha Sequence Chart 172' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter-Rahu-Saturn Dasha Sequence Chart 172' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Rahu_Saturn_Dasha_Sequence_Chart_172` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars in Cancer Chart 173' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_Cancer_Chart_173` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars in Cancer Chart 173' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_Cancer_Chart_173` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars in Cancer Chart 173' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_Cancer_Chart_173` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars in Cancer Chart 173' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_Cancer_Chart_173` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars in Cancer Chart 173' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_Cancer_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_Cancer_Chart_173` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_Cancer_Chart_173` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Gemini Chart 173' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Gemini_Chart_173` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Gemini Chart 173' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Gemini_Chart_173` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Gemini Chart 173' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Gemini_Chart_173` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Gemini Chart 173' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Gemini_Chart_173` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Gemini Chart 173' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Gemini_Chart_173` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Gemini_Chart_173` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Gemini_Chart_173` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu Moving Towards Mars In Sagittarius' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu Moving Towards Mars In Sagittarius' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu Moving Towards Mars In Sagittarius' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu Moving Towards Mars In Sagittarius' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu Moving Towards Mars In Sagittarius' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moving_Towards_Mars_In_Sagittarius` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars In Leo (Chart 174)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Leo__Chart_174_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars In Leo (Chart 174)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Leo__Chart_174_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars In Leo (Chart 174)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Leo__Chart_174_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars In Leo (Chart 174)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Leo__Chart_174_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars In Leo (Chart 174)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Leo__Chart_174_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Leo__Chart_174_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Leo__Chart_174_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars In Virgo (Chart 175)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Virgo__Chart_175_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars In Virgo (Chart 175)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Virgo__Chart_175_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars In Virgo (Chart 175)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Virgo__Chart_175_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars In Virgo (Chart 175)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Virgo__Chart_175_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars In Virgo (Chart 175)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_In_Virgo__Chart_175_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_In_Virgo__Chart_175_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_In_Virgo__Chart_175_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Libra Placement' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Libra_Placement` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Libra Placement' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Libra_Placement` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Libra Placement' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Libra_Placement` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Libra Placement' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Libra_Placement` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mercury in Libra Placement' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mercury_in_Libra_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mercury_in_Libra_Placement` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mercury_in_Libra_Placement` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mercury_in_Libra_Placement` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL