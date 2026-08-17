# Omni-Vedic Supreme Fusion Engine Package
import pandas as pd
from typing import List
from .omni_vedic_fusion import extract_omni_vedic_row

def calculate_all_vedic_features(jds: List[float], **kwargs) -> pd.DataFrame:
    rows = [extract_omni_vedic_row(jd) for jd in jds]
    df = pd.DataFrame(rows)
    df.insert(0, "Julian_Date_UT", jds)
    return df
