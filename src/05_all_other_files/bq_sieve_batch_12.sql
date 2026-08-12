INSERT INTO `antigravity_quant.sieve_results`
SELECT
    'Ketu In Pisces (Chart 111)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Ketu In Pisces (Chart 111)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Ketu In Pisces (Chart 111)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Ketu In Pisces (Chart 111)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Ketu In Pisces (Chart 111)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Ketu_In_Pisces__Chart_111_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Ketu_In_Pisces__Chart_111_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun In Libra Debilitated With Mercury And Rahu (Chart 111)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun In Libra Debilitated With Mercury And Rahu (Chart 111)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun In Libra Debilitated With Mercury And Rahu (Chart 111)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun In Libra Debilitated With Mercury And Rahu (Chart 111)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun In Libra Debilitated With Mercury And Rahu (Chart 111)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_In_Libra_Debilitated_With_Mercury_And_Rahu__Chart_111_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Contact of Saturn and Venus in Virgo' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Contact of Saturn and Venus in Virgo' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Contact of Saturn and Venus in Virgo' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Contact of Saturn and Venus in Virgo' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Contact of Saturn and Venus in Virgo' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Contact_of_Saturn_and_Venus_in_Virgo` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Contact_of_Saturn_and_Venus_in_Virgo` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Rahu In Pisces And Moon In Aries Configuration (Chart 337)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Rahu In Pisces And Moon In Aries Configuration (Chart 337)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Rahu In Pisces And Moon In Aries Configuration (Chart 337)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Rahu In Pisces And Moon In Aries Configuration (Chart 337)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Rahu In Pisces And Moon In Aries Configuration (Chart 337)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Rahu_In_Pisces_And_Moon_In_Aries_Configuration__Chart_337_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Jupiter And Moon' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Jupiter And Moon' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Jupiter And Moon' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Jupiter And Moon' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Jupiter And Moon' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Jupiter_And_Moon` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Jupiter_And_Moon` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn In Virgo Transit (Chart 116)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn In Virgo Transit (Chart 116)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn In Virgo Transit (Chart 116)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn In Virgo Transit (Chart 116)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn In Virgo Transit (Chart 116)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_In_Virgo_Transit__Chart_116_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_In_Virgo_Transit__Chart_116_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Moon And Venus Effect (Chart 116)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Moon And Venus Effect (Chart 116)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Moon And Venus Effect (Chart 116)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Moon And Venus Effect (Chart 116)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Sun Conjunct Moon And Venus Effect (Chart 116)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Sun_Conjunct_Moon_And_Venus_Effect__Chart_116_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Mars in 2nd house' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_2nd_house` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Mars in 2nd house' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_2nd_house` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Mars in 2nd house' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_2nd_house` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Mars in 2nd house' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_2nd_house` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Mars in 2nd house' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Mars_in_2nd_house` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Mars_in_2nd_house` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Mars_in_2nd_house` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Mars_in_2nd_house` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn, Venus, Mercury in 2nd House from Sun (Chart 119)' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn, Venus, Mercury in 2nd House from Sun (Chart 119)' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn, Venus, Mercury in 2nd House from Sun (Chart 119)' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn, Venus, Mercury in 2nd House from Sun (Chart 119)' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn, Venus, Mercury in 2nd House from Sun (Chart 119)' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn__Venus__Mercury_in_2nd_House_from_Sun__Chart_119_` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Jupiter Conjunction in Virgo' AS rule_name,
    '1D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_1d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_1d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_1d, NULL)) - AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_1d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_1d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_1d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_1d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS FLOAT64), r.fwd_return_1d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_1d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Jupiter Conjunction in Virgo' AS rule_name,
    '5D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_5d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_5d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_5d, NULL)) - AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_5d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_5d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_5d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_5d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS FLOAT64), r.fwd_return_5d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_5d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Jupiter Conjunction in Virgo' AS rule_name,
    '10D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_10d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_10d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_10d, NULL)) - AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_10d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_10d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_10d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_10d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS FLOAT64), r.fwd_return_10d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_10d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Jupiter Conjunction in Virgo' AS rule_name,
    '21D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_21d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_21d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_21d, NULL)) - AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_21d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_21d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_21d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_21d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS FLOAT64), r.fwd_return_21d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_21d IS NOT NULL
UNION ALL
SELECT
    'Saturn-Jupiter Conjunction in Virgo' AS rule_name,
    '63D' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_63d, NULL)) AS mean_return_active,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_63d, NULL)) AS mean_return_inactive,
    AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_63d, NULL)) - AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 0, r.fwd_return_63d, NULL)) AS differential_return,
    STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_63d, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_63d, NULL)) - 0.0005,
      STDDEV(IF(`rule_Saturn_Jupiter_Conjunction_in_Virgo` = 1, r.fwd_return_63d, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`rule_Saturn_Jupiter_Conjunction_in_Virgo` AS FLOAT64), r.fwd_return_63d) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.fwd_return_63d IS NOT NULL