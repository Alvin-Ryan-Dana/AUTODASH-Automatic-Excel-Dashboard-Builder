import pandas as pd
from src.data_profiler import profile_dataset

def test_profile_missing_duplicates_and_numeric():
    df = pd.DataFrame({"n":[1,None,3,3], "cat":["a","a",None,None]})
    profile, summary = profile_dataset(df)
    assert summary["baris_duplikat"] == 1
    assert summary["sel_kosong"] == 3
    assert profile.set_index("kolom").loc["n","tipe_terdeteksi"] == "numerik"

def test_empty_dataframe():
    profile, summary = profile_dataset(pd.DataFrame())
    assert profile.empty and summary["baris"] == 0

def test_numeric_missing_is_supported():
    profile, _ = profile_dataset(pd.DataFrame({"value":[1.0,None,3.0]}))
    assert int(profile.iloc[0]["nilai_kosong"]) == 1
