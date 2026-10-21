import pandas as pd
import pytest
from src.data_loader import read_dataset

def test_read_csv():
    df = read_dataset(b"a,b\n1,2\n", "sample.csv")
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 1

def test_excel_multiple_sheets(tmp_path):
    path = tmp_path / "multi.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame({"x":[1]}).to_excel(writer, sheet_name="Satu", index=False)
        pd.DataFrame({"y":[2]}).to_excel(writer, sheet_name="Dua", index=False)
    raw = path.read_bytes()
    assert read_dataset(raw, "multi.xlsx", "Dua").iloc[0,0] == 2

def test_empty_and_unsupported():
    with pytest.raises(ValueError): read_dataset(b"", "a.csv")
    with pytest.raises(ValueError): read_dataset(b"x", "a.txt")

def test_duplicate_columns_get_unique_names():
    df = read_dataset(b"x,x\n1,2\n", "dupe.csv")
    assert len(set(df.columns)) == 2
