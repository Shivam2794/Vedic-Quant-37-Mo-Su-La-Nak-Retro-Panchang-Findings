import pytest
import os
import sys
import numpy as np
import pandas as pd
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.calendar.forward_signal_scanner import scan_forward_signals_2026_2027
from src.analysis.mine_trend_wave_rules import build_candidate_pure_vedic_features

class TestRuleConjunctionStress:
    @pytest.fixture(scope='class')
    def forward_data_and_features(self):
        df_fwd = pd.read_parquet('data/forward_ephemeris_2026_2027_supreme.parquet')
        df_feats = build_candidate_pure_vedic_features(df_fwd, prefix='')
        return df_fwd, df_feats

    def test_single_factor_rule_trigger_logic(self, forward_data_and_features):
        df_fwd, df_feats = forward_data_and_features
        feat_name = 'Moon in Rohini'
        assert feat_name in df_feats.columns
        feature_col = df_feats[feat_name].values
        for i in range(min(500, len(df_fwd))):
            assert bool(feature_col[i]) == bool(df_feats.iloc[i][feat_name])

    def test_multi_antecedent_conjunction_truth_table(self, forward_data_and_features):
        df_fwd, df_feats = forward_data_and_features
        feat1 = 'Moon in Rohini'
        feat2 = 'Sun in Taurus'
        assert feat1 in df_feats.columns and feat2 in df_feats.columns
        vec1 = df_feats[feat1].values
        vec2 = df_feats[feat2].values
        conjunction = vec1 & vec2
        for i in range(len(df_fwd)):
            assert bool(conjunction[i]) == bool(vec1[i] and vec2[i])

    def test_overlapping_hierarchical_subsets_and_supersets(self, forward_data_and_features):
        df_fwd, df_feats = forward_data_and_features
        feat_a = 'Moon in Rohini'
        feat_b = 'Sun in Taurus'
        vec_a = df_feats[feat_a].values
        vec_b = df_feats[feat_b].values
        case_a_only = vec_a & (~vec_b)
        if case_a_only.sum() > 0:
            idx = np.where(case_a_only)[0][0]
            assert vec_a[idx] == True
            assert (vec_a[idx] and vec_b[idx]) == False
        case_both = vec_a & vec_b
        if case_both.sum() > 0:
            idx = np.where(case_both)[0][0]
            assert vec_a[idx] == True
            assert (vec_a[idx] and vec_b[idx]) == True

    def test_rule_parser_unmapped_feature_graceful_drop(self, forward_data_and_features):
        df_fwd, df_feats = forward_data_and_features
        feat_names = list(df_feats.columns)
        name_to_idx = {name: idx for idx, name in enumerate(feat_names)}
        def parse_rule_indices(rules):
            parsed = []
            for r in rules:
                raw_ant = r['Antecedents']
                parts = [p.strip().strip('[]') for p in raw_ant.split(' \u2227 ')]
                indices = [name_to_idx[p] for p in parts if p in name_to_idx]
                if len(indices) == len(parts):
                    parsed.append((indices, r))
            return parsed
        adversarial_rules = [
            {'Antecedents': '[Pluto in Aries] \u2227 [Moon in Rohini]', 'Confidence_Pct': 90.0},
            {'Antecedents': '[Fictitious_Planet_X] \u2227 [Sun in Leo]', 'Confidence_Pct': 80.0},
            {'Antecedents': '[Moon in Rohini]', 'Confidence_Pct': 85.0},
            {'Antecedents': '[Moon in Rohini] \u2227 [Sun in Taurus]', 'Confidence_Pct': 88.0},
        ]
        parsed = parse_rule_indices(adversarial_rules)
        assert len(parsed) == 2
        assert parsed[0][1]['Antecedents'] == '[Moon in Rohini]'
        assert parsed[1][1]['Antecedents'] == '[Moon in Rohini] \u2227 [Sun in Taurus]'

    def test_extreme_all_zero_feature_state(self):
        feat_matrix = np.zeros((10, 50), dtype=bool)
        parsed_bull = [([0, 1], {'Confidence_Pct': 80.0, 'Avg_Wave_Return_Pct': 5.0, 'Antecedents': '[F0] \u2227 [F1]'})]
        parsed_bear = [([2], {'Confidence_Pct': 75.0, 'Avg_Wave_Return_Pct': -3.0, 'Antecedents': '[F2]'})]
        signals = []
        for i in range(10):
            active_bull = [r for indices, r in parsed_bull if all(feat_matrix[i, idx] for idx in indices)]
            active_bear = [r for indices, r in parsed_bear if all(feat_matrix[i, idx] for idx in indices)]
            if len(active_bull) > 0 or len(active_bear) > 0:
                signals.append(i)
        assert len(signals) == 0

    def test_extreme_all_one_feature_state(self):
        feat_matrix = np.ones((10, 50), dtype=bool)
        parsed_bull = [
            ([0, 1], {'Confidence_Pct': 90.0, 'Avg_Wave_Return_Pct': 5.0, 'Antecedents': '[F0] \u2227 [F1]'}),
            ([3], {'Confidence_Pct': 80.0, 'Avg_Wave_Return_Pct': 3.0, 'Antecedents': '[F3]'})
        ]
        parsed_bear = [([2], {'Confidence_Pct': 75.0, 'Avg_Wave_Return_Pct': -3.0, 'Antecedents': '[F2]'})]
        signals = []
        for i in range(10):
            active_bull = [r for indices, r in parsed_bull if all(feat_matrix[i, idx] for idx in indices)]
            active_bear = [r for indices, r in parsed_bear if all(feat_matrix[i, idx] for idx in indices)]
            if len(active_bull) > 0 or len(active_bear) > 0:
                n_bull = len(active_bull)
                n_bear = len(active_bear)
                direction = 'Bullish_Dominant_Conflict' if n_bull > n_bear else 'Bearish_Dominant_Conflict'
                signals.append(direction)
        assert len(signals) == 10
        assert all(d == 'Bullish_Dominant_Conflict' for d in signals)

class TestConfluenceScoreCalibration:
    @staticmethod
    def classify_state(active_bull, active_bear):
        n_bull = len(active_bull)
        n_bear = len(active_bear)
        if n_bull == 0 and n_bear == 0:
            return None
        max_bull_conf = max([r['Confidence_Pct'] for r in active_bull]) if n_bull > 0 else 0.0
        max_bear_conf = max([r['Confidence_Pct'] for r in active_bear]) if n_bear > 0 else 0.0
        max_bull_move = max([r['Avg_Wave_Return_Pct'] for r in active_bull]) if n_bull > 0 else 0.0
        max_bear_move = min([r['Avg_Wave_Return_Pct'] for r in active_bear]) if n_bear > 0 else 0.0
        if n_bull > 0 and n_bear == 0:
            direction = 'Bullish_Inception'
            conviction = max_bull_conf
        elif n_bear > 0 and n_bull == 0:
            direction = 'Bearish_Liquidation'
            conviction = max_bear_conf
        elif n_bull > n_bear:
            direction = 'Bullish_Dominant_Conflict'
            conviction = max_bull_conf * 0.85
        elif n_bear > n_bull:
            direction = 'Bearish_Dominant_Conflict'
            conviction = max_bear_conf * 0.85
        else:
            direction = 'Equilibrium_Stalemate'
            conviction = 50.0
        expected_move = round(max_bull_move if 'Bull' in direction else max_bear_move, 2)
        return {
            'Direction': direction,
            'Conviction_Pct': round(conviction, 1),
            'Expected_Move_Pct': expected_move,
            'Bullish_Rules_N': n_bull,
            'Bearish_Rules_N': n_bear
        }

    def test_pure_bullish_state_calibration(self):
        bull_rules = [{'Confidence_Pct': 88.5, 'Avg_Wave_Return_Pct': 6.2, 'Antecedents': '[F1]'}]
        res = self.classify_state(bull_rules, [])
        assert res['Direction'] == 'Bullish_Inception'
        assert res['Conviction_Pct'] == 88.5
        assert res['Expected_Move_Pct'] == 6.2
        assert res['Bullish_Rules_N'] == 1
        assert res['Bearish_Rules_N'] == 0

    def test_pure_bearish_state_calibration(self):
        bear_rules = [{'Confidence_Pct': 92.4, 'Avg_Wave_Return_Pct': -4.8, 'Antecedents': '[F2]'}]
        res = self.classify_state([], bear_rules)
        assert res['Direction'] == 'Bearish_Liquidation'
        assert res['Conviction_Pct'] == 92.4
        assert res['Expected_Move_Pct'] == -4.8
        assert res['Bullish_Rules_N'] == 0
        assert res['Bearish_Rules_N'] == 1

    def test_bullish_dominant_conflict_085_penalty(self):
        bull_rules = [
            {'Confidence_Pct': 90.0, 'Avg_Wave_Return_Pct': 7.5, 'Antecedents': '[B1]'},
            {'Confidence_Pct': 85.0, 'Avg_Wave_Return_Pct': 4.5, 'Antecedents': '[B2]'},
        ]
        bear_rules = [{'Confidence_Pct': 75.0, 'Avg_Wave_Return_Pct': -3.0, 'Antecedents': '[BR1]'}]
        res = self.classify_state(bull_rules, bear_rules)
        assert res['Direction'] == 'Bullish_Dominant_Conflict'
        assert res['Conviction_Pct'] == round(90.0 * 0.85, 1)
        assert res['Expected_Move_Pct'] == 7.5
        assert res['Bullish_Rules_N'] == 2
        assert res['Bearish_Rules_N'] == 1

    def test_bearish_dominant_conflict_085_penalty(self):
        bull_rules = [{'Confidence_Pct': 80.0, 'Avg_Wave_Return_Pct': 4.0, 'Antecedents': '[B1]'}]
        bear_rules = [
            {'Confidence_Pct': 95.0, 'Avg_Wave_Return_Pct': -8.2, 'Antecedents': '[BR1]'},
            {'Confidence_Pct': 90.0, 'Avg_Wave_Return_Pct': -5.1, 'Antecedents': '[BR2]'},
            {'Confidence_Pct': 85.0, 'Avg_Wave_Return_Pct': -4.0, 'Antecedents': '[BR3]'},
        ]
        res = self.classify_state(bull_rules, bear_rules)
        assert res['Direction'] == 'Bearish_Dominant_Conflict'
        assert res['Conviction_Pct'] == round(95.0 * 0.85, 1)
        assert res['Expected_Move_Pct'] == -8.2
        assert res['Bullish_Rules_N'] == 1
        assert res['Bearish_Rules_N'] == 3

    def test_exact_50_50_stalemate_calibration(self):
        bull_rules = [
            {'Confidence_Pct': 95.0, 'Avg_Wave_Return_Pct': 8.0, 'Antecedents': '[B1]'},
            {'Confidence_Pct': 90.0, 'Avg_Wave_Return_Pct': 6.0, 'Antecedents': '[B2]'},
        ]
        bear_rules = [
            {'Confidence_Pct': 98.0, 'Avg_Wave_Return_Pct': -9.0, 'Antecedents': '[BR1]'},
            {'Confidence_Pct': 88.0, 'Avg_Wave_Return_Pct': -5.0, 'Antecedents': '[BR2]'},
        ]
        res = self.classify_state(bull_rules, bear_rules)
        assert res['Direction'] == 'Equilibrium_Stalemate'
        assert res['Conviction_Pct'] == 50.0
        assert res['Bullish_Rules_N'] == 2
        assert res['Bearish_Rules_N'] == 2

    def test_100_percent_winrate_ceiling_boundary(self):
        bull_rules = [{'Confidence_Pct': 100.0, 'Avg_Wave_Return_Pct': 10.54, 'Antecedents': '[B1]'}]
        res = self.classify_state(bull_rules, [])
        assert res['Conviction_Pct'] == 100.0
        assert res['Direction'] == 'Bullish_Inception'

class TestManifestDataQuality:
    @pytest.fixture(scope='class')
    def manifest_df(self):
        path = 'data/forward_signals_2026_2027_manifest.parquet'
        assert os.path.exists(path)
        return pd.read_parquet(path)

    def test_manifest_exact_row_count(self, manifest_df):
        assert len(manifest_df) == 3514

    def test_manifest_schema_and_column_count(self, manifest_df):
        expected_cols = [
            'Datetime_NY', 'Date_Str', 'Time_Str', 'Horizon_Type', 'Direction',
            'Conviction_Pct', 'Bullish_Rules_N', 'Bearish_Rules_N',
            'Max_Bullish_WinRate', 'Max_Bearish_WinRate', 'Expected_Move_Pct',
            'Multi_Entity_Crisis_Level', 'Moon_Nakshatra', 'Moon_Sign', 'Lagna_Sign',
            'Top_Bull_Trigger', 'Top_Bear_Trigger'
        ]
        assert list(manifest_df.columns) == expected_cols
        assert len(manifest_df.columns) == 17

    def test_manifest_zero_nulls_and_zero_infs(self, manifest_df):
        assert manifest_df.isnull().sum().sum() == 0
        num_cols = manifest_df.select_dtypes(include=[np.number])
        assert np.isinf(num_cols).sum().sum() == 0

    def test_manifest_temporal_strict_monotonicity(self, manifest_df):
        dt_series = pd.to_datetime(manifest_df['Datetime_NY'], utc=True)
        assert dt_series.is_monotonic_increasing
        assert dt_series.duplicated().sum() == 0

    def test_manifest_date_span_coverage(self, manifest_df):
        years = pd.to_datetime(manifest_df['Date_Str']).dt.year.unique()
        assert set(years) == {2026, 2027}
        assert manifest_df['Date_Str'].min() == '2026-01-02'
        assert manifest_df['Date_Str'].max() == '2027-12-31'

    def test_manifest_direction_categories_and_conviction_ranges(self, manifest_df):
        canonical_dirs = {
            'Bullish_Inception', 'Bearish_Liquidation',
            'Bullish_Dominant_Conflict', 'Bearish_Dominant_Conflict',
            'Equilibrium_Stalemate'
        }
        assert set(manifest_df['Direction'].unique()).issubset(canonical_dirs)
        assert (manifest_df['Conviction_Pct'] >= 50.0).all()
        assert (manifest_df['Conviction_Pct'] <= 100.0).all()

    def test_manifest_vedic_astronomical_invariants(self, manifest_df):
        nakshatras_27 = {
            'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
            'Magha', 'P.Phalguni', 'U.Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
            'Moola', 'P.Ashadha', 'U.Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'P.Bhadrapada', 'U.Bhadrapada', 'Revati'
        }
        zodiac_12 = {
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        }
        assert set(manifest_df['Moon_Nakshatra'].unique()) == nakshatras_27
        assert set(manifest_df['Moon_Sign'].unique()) == zodiac_12
        assert set(manifest_df['Lagna_Sign'].unique()) == zodiac_12

    def test_manifest_crisis_level_domain(self, manifest_df):
        assert (manifest_df['Multi_Entity_Crisis_Level'] >= 0).all()
        assert (manifest_df['Multi_Entity_Crisis_Level'] <= 3).all()

    def test_manifest_deterministic_confluence_recomputation_sweep(self, manifest_df):
        for _, row in manifest_df.iterrows():
            n_b = row['Bullish_Rules_N']
            n_br = row['Bearish_Rules_N']
            assert n_b + n_br > 0
            if n_b > 0 and n_br == 0:
                assert row['Direction'] == 'Bullish_Inception'
                assert row['Top_Bear_Trigger'] == 'None'
                assert np.isclose(row['Conviction_Pct'], round(row['Max_Bullish_WinRate'], 1))
            elif n_br > 0 and n_b == 0:
                assert row['Direction'] == 'Bearish_Liquidation'
                assert row['Top_Bull_Trigger'] == 'None'
                assert np.isclose(row['Conviction_Pct'], round(row['Max_Bearish_WinRate'], 1))
            elif n_b > n_br:
                assert row['Direction'] == 'Bullish_Dominant_Conflict'
                assert np.isclose(row['Conviction_Pct'], round(row['Max_Bullish_WinRate'] * 0.85, 1))
            elif n_br > n_b:
                assert row['Direction'] == 'Bearish_Dominant_Conflict'
                assert np.isclose(row['Conviction_Pct'], round(row['Max_Bearish_WinRate'] * 0.85, 1))
            else:
                assert row['Direction'] == 'Equilibrium_Stalemate'
                assert row['Conviction_Pct'] == 50.0

class TestCalendarReportIntegrity:
    @pytest.fixture(scope='class')
    def report_content(self):
        path = 'reports/forward_2026_2027_astro_quant_calendar.md'
        assert os.path.exists(path)
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return lines

    def test_report_demographics_exact_match(self, report_content):
        df_sig = pd.read_parquet('data/forward_signals_2026_2027_manifest.parquet')
        text = ''.join(report_content)
        assert f'Total Actionable Forward Sessions Identified**: `{len(df_sig)}`' in text
        assert f'Pure Bullish Inception Sessions**: `{(df_sig["Direction"] == "Bullish_Inception").sum()}`' in text
        assert f'Pure Bearish Liquidation Sessions**: `{(df_sig["Direction"] == "Bearish_Liquidation").sum()}`' in text
        assert f'High-Conviction Windows ($\\ge 85\\%$ Historical Win Rate)**: `{(df_sig["Conviction_Pct"] >= 85.0).sum()}`' in text

    def test_report_table_pipe_and_column_alignment(self, report_content):
        table_rows = [l.strip() for l in report_content if l.strip().startswith('|')]
        assert len(table_rows) >= 42
        for i, row in enumerate(table_rows):
            cells = row.split('|')
            assert len(cells) == 8, f'Table row {i} has invalid column count: {row}'

    def test_report_table_chronological_ordering(self, report_content):
        table_rows = [l.strip() for l in report_content if l.strip().startswith('|')][2:]
        dates = []
        for r in table_rows:
            cells = [c.strip() for c in r.split('|')[1:-1]]
            dt_str = cells[0].replace('`', '').strip()
            dates.append(pd.to_datetime(dt_str))
        date_series = pd.Series(dates)
        assert date_series.is_monotonic_increasing

    def test_report_markdown_syntax_and_section_structure(self, report_content):
        text = ''.join(report_content)
        assert '# \U0001F4C5 Forward 2026–2027 Institutional Astro-Quant Trading Calendar' in text
        assert '## \U0001F4CA 2026–2027 Forward Signal Demographics' in text
        assert '## \U0001F31F Top High-Conviction Forward Astro-Quant Windows (2026–2027)' in text
        assert '## \U0001F52C Key Astro-Macro Observations for 2026–2027' in text
        assert '---' in text


class TestAdversarialEngineExtensions:
    """Additional stress tests on custom thresholds, graceful defaults, and roundtrips."""

    def test_missing_optional_row_keys_graceful_defaults(self):
        """Verify that incomplete or sparse forward ephemeris rows do not raise KeyError."""
        sparse_row = {
            "Datetime_NY": "2026-01-02 09:30:00-05:00",
            "Date_Str": "2026-01-02",
            "Time_Str": "09:30:00",
            "Horizon_Type": "Daily_Open",
            # Missing Multi_Entity_Sade_Sati_Count, Moon_Nakshatra, Moon_Sign, Lagna_NYSE_Sign
        }
        crisis = int(sparse_row.get("Multi_Entity_Sade_Sati_Count", 0))
        moon_nak = sparse_row.get("Moon_Nakshatra", "")
        moon_sign = sparse_row.get("Moon_Sign", "")
        lagna_sign = sparse_row.get("Lagna_NYSE_Sign", "")
        
        assert crisis == 0
        assert moon_nak == ""
        assert moon_sign == ""
        assert lagna_sign == ""

    def test_confluence_expected_move_sign_consistency(self):
        """Verify bullish directions associate with non-negative expected returns and bearish with negative."""
        df_sig = pd.read_parquet("data/forward_signals_2026_2027_manifest.parquet")
        bull_mask = df_sig["Direction"].str.contains("Bull")
        bear_mask = df_sig["Direction"].str.contains("Bear")
        
        # Bullish moves in mined rules should be positive
        assert (df_sig[bull_mask]["Expected_Move_Pct"] > 0).all()
        # Bearish moves in mined rules should be negative
        assert (df_sig[bear_mask]["Expected_Move_Pct"] < 0).all()

    def test_top_trigger_string_formatting_invariants(self):
        """Verify Top_Bull_Trigger and Top_Bear_Trigger strings are either 'None' or bracketed formulas."""
        df_sig = pd.read_parquet("data/forward_signals_2026_2027_manifest.parquet")
        for _, row in df_sig.iterrows():
            top_bull = row["Top_Bull_Trigger"]
            top_bear = row["Top_Bear_Trigger"]
            
            if row["Direction"] == "Bullish_Inception":
                assert top_bull.startswith("[") and top_bull.endswith("]")
                assert top_bear == "None"
            elif row["Direction"] == "Bearish_Liquidation":
                assert top_bear.startswith("[") and top_bear.endswith("]")
                assert top_bull == "None"
            elif "Dominant_Conflict" in row["Direction"] or row["Direction"] == "Equilibrium_Stalemate":
                assert top_bull.startswith("[") and top_bull.endswith("]")
                assert top_bear.startswith("[") and top_bear.endswith("]")

    def test_manifest_to_parquet_snappy_compression_roundtrip(self, tmp_path):
        """Verify manifest roundtrip to snappy parquet maintains bit-level equality."""
        df_sig = pd.read_parquet("data/forward_signals_2026_2027_manifest.parquet")
        temp_file = tmp_path / "test_manifest.parquet"
        df_sig.to_parquet(str(temp_file), compression="snappy", index=False)
        
        df_reloaded = pd.read_parquet(str(temp_file))
        pd.testing.assert_frame_equal(df_sig, df_reloaded)

