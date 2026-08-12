INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Venus Period (34-44)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Period__34_44_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus Period (34-44)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Period__34_44_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus Period (34-44)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Period__34_44_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus Period (34-44)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Period__34_44_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus Period (34-44)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Period__34_44_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_Period__34_44_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Period__34_44_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Period__34_44_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars and Rahu in Leo in 12th House' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars and Rahu in Leo in 12th House' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars and Rahu in Leo in 12th House' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars and Rahu in Leo in 12th House' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars and Rahu in Leo in 12th House' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_and_Rahu_in_Leo_in_12th_House` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_and_Rahu_in_Leo_in_12th_House` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Ketu In 3Rd House Chart 329' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Ketu In 3Rd House Chart 329' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Ketu In 3Rd House Chart 329' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Ketu In 3Rd House Chart 329' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Ketu In 3Rd House Chart 329' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Ketu_In_3Rd_House_Chart_329` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Sun In Taurus Chart 329' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Sun In Taurus Chart 329' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Sun In Taurus Chart 329' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Sun In Taurus Chart 329' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Sun In Taurus Chart 329' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Sun_In_Taurus_Chart_329` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Sun_In_Taurus_Chart_329` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Venus Mercury Ketu In Virgo Chart 331' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Venus Mercury Ketu In Virgo Chart 331' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Venus Mercury Ketu In Virgo Chart 331' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Venus Mercury Ketu In Virgo Chart 331' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Placement Of Venus Mercury Ketu In Virgo Chart 331' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Placement_Of_Venus_Mercury_Ketu_In_Virgo_Chart_331` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun Aspect On Moon Chart 329' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun Aspect On Moon Chart 329' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun Aspect On Moon Chart 329' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun Aspect On Moon Chart 329' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun Aspect On Moon Chart 329' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Aspect_On_Moon_Chart_329` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Aspect_On_Moon_Chart_329` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Budha/Mercury Period' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Budha_Mercury_Period` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Budha/Mercury Period' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Budha_Mercury_Period` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Budha/Mercury Period' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Budha_Mercury_Period` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Budha/Mercury Period' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Budha_Mercury_Period` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Budha/Mercury Period' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Budha_Mercury_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Budha_Mercury_Period` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Budha_Mercury_Period` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Budha_Mercury_Period` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Chandra/Moon Period' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Chandra_Moon_Period` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Chandra/Moon Period' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Chandra_Moon_Period` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Chandra/Moon Period' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Chandra_Moon_Period` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Chandra/Moon Period' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Chandra_Moon_Period` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Chandra/Moon Period' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Chandra_Moon_Period` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Chandra_Moon_Period` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Chandra_Moon_Period` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Chandra_Moon_Period` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon In Sagittarius (Chart 110)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon In Sagittarius (Chart 110)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon In Sagittarius (Chart 110)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon In Sagittarius (Chart 110)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon In Sagittarius (Chart 110)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_In_Sagittarius__Chart_110_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_In_Sagittarius__Chart_110_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Pisces (Chart 111)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Pisces (Chart 111)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Pisces (Chart 111)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Pisces (Chart 111)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Pisces (Chart 111)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL