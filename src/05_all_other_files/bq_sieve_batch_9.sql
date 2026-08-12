INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Rahu-Sun Conjunction (Chart 105)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Sun Conjunction (Chart 105)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Sun Conjunction (Chart 105)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Sun Conjunction (Chart 105)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Sun Conjunction (Chart 105)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Sun_Conjunction__Chart_105_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Sun_Conjunction__Chart_105_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Mars Combination in Scorpio' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Mars Combination in Scorpio' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Mars Combination in Scorpio' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Mars Combination in Scorpio' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Mars Combination in Scorpio' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Mars_Combination_in_Scorpio` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Mars_Combination_in_Scorpio` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Sagittarius Opposed by Venus in Gemini with Rahu and Mars in 12th' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Sagittarius Opposed by Venus in Gemini with Rahu and Mars in 12th' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Sagittarius Opposed by Venus in Gemini with Rahu and Mars in 12th' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Sagittarius Opposed by Venus in Gemini with Rahu and Mars in 12th' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter in Sagittarius Opposed by Venus in Gemini with Rahu and Mars in 12th' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_in_Sagittarius_Opposed_by_Venus_in_Gemini_with_Rahu_and_Mars_in_12th` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Ketu in Taurus' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Ketu in Taurus' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Ketu in Taurus' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Ketu in Taurus' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Ketu in Taurus' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Ketu_in_Taurus` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Ketu_in_Taurus` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Venus in Mercury\'s House and the Sun in Cancer' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Venus in Mercury\'s House and the Sun in Cancer' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Venus in Mercury\'s House and the Sun in Cancer' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Venus in Mercury\'s House and the Sun in Cancer' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn Contacts Venus in Mercury\'s House and the Sun in Cancer' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Contacts_Venus_in_Mercury_s_House_and_the_Sun_in_Cancer` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Scorpio' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Scorpio` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Scorpio' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Scorpio` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Scorpio' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Scorpio` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Scorpio' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Scorpio` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Ketu in Scorpio' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_in_Scorpio` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Ketu_in_Scorpio` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_in_Scorpio` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_in_Scorpio` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspects Venus' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspects_Venus` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspects Venus' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspects_Venus` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspects Venus' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspects_Venus` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspects Venus' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspects_Venus` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspects Venus' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspects_Venus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_Aspects_Venus` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspects_Venus` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspects_Venus` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon in Pisces with Saturn' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Pisces_with_Saturn` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon in Pisces with Saturn' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Pisces_with_Saturn` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon in Pisces with Saturn' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Pisces_with_Saturn` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon in Pisces with Saturn' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Pisces_with_Saturn` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon in Pisces with Saturn' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Pisces_with_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Pisces_with_Saturn` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Pisces_with_Saturn` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Moon Combination' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moon_Combination` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Moon Combination' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moon_Combination` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Moon Combination' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moon_Combination` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Moon Combination' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moon_Combination` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu-Moon Combination' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_Moon_Combination` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_Moon_Combination` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_Moon_Combination` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_Moon_Combination` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Venus Conjunction' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Venus_Conjunction` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Venus Conjunction' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Venus_Conjunction` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Venus Conjunction' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Venus_Conjunction` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Venus Conjunction' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Venus_Conjunction` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mars-Venus Conjunction' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mars_Venus_Conjunction` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mars_Venus_Conjunction` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mars_Venus_Conjunction` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL