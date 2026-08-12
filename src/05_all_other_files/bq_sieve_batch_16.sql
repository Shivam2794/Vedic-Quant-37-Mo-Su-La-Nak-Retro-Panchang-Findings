INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Sun-Mercury in Cancer (House of Mind)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury in Cancer (House of Mind)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury in Cancer (House of Mind)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury in Cancer (House of Mind)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun-Mercury in Cancer (House of Mind)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Mercury_in_Cancer__House_of_Mind_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Capricorn (Page 92)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Capricorn (Page 92)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Capricorn (Page 92)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Capricorn (Page 92)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn in Capricorn (Page 92)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_in_Capricorn__Page_92_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_in_Capricorn__Page_92_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Aquarius (Page 92)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Aquarius (Page 92)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Aquarius (Page 92)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Aquarius (Page 92)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu in Aquarius (Page 92)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_in_Aquarius__Page_92_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_in_Aquarius__Page_92_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Taurus' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Taurus` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Taurus' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Taurus` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Taurus' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Taurus` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Taurus' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Taurus` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Taurus' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Taurus` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_In_Taurus` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Taurus` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Taurus` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Gemini Placement' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Gemini_Placement` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Gemini Placement' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Gemini_Placement` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Gemini Placement' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Gemini_Placement` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Gemini Placement' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Gemini_Placement` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Gemini Placement' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Gemini_Placement` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Gemini_Placement` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Gemini_Placement` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect On Saturn' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect On Saturn' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect On Saturn' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect On Saturn' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter Aspect On Saturn' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus Aspect On Saturn' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus Aspect On Saturn' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus Aspect On Saturn' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus Aspect On Saturn' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus Aspect On Saturn' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Aspect_On_Saturn` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_Aspect_On_Saturn` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Aspect_On_Saturn` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Aspect_On_Saturn` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Moon in Cancer (Chart 380)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Cancer__Chart_380_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Moon in Cancer (Chart 380)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Cancer__Chart_380_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Moon in Cancer (Chart 380)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Cancer__Chart_380_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Moon in Cancer (Chart 380)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Cancer__Chart_380_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Moon in Cancer (Chart 380)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Moon_in_Cancer__Chart_380_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Moon_in_Cancer__Chart_380_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Moon_in_Cancer__Chart_380_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Venus-Mars Exchange with Saturn in Aries (Chart 221)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Venus-Mars Exchange with Saturn in Aries (Chart 221)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Venus-Mars Exchange with Saturn in Aries (Chart 221)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Venus-Mars Exchange with Saturn in Aries (Chart 221)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Venus-Mars Exchange with Saturn in Aries (Chart 221)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Venus_Mars_Exchange_with_Saturn_in_Aries__Chart_221_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Leo' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Leo` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Leo' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Leo` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Leo' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Leo` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Leo' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Leo` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Jupiter In Leo' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Jupiter_In_Leo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Jupiter_In_Leo` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Jupiter_In_Leo` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Jupiter_In_Leo` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL