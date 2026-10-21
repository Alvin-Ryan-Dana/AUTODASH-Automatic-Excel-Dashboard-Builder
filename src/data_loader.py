"""Loading and normalizing user-provided tabular data."""
from __future__ import annotations
from io import BytesIO, StringIO
from pathlib import Path
import pandas as pd

SUPPORTED = {".csv", ".xlsx", ".xls"}

def read_dataset(data: bytes, filename: str, sheet_name: str | None = None) -> pd.DataFrame:
    """Read a CSV or Excel workbook from bytes without executing spreadsheet formulas."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Format {suffix or '(tanpa ekstensi)'} tidak didukung. Gunakan CSV, XLSX, atau XLS.")
    if not data:
        raise ValueError("File kosong. Pilih file yang berisi data.")
    try:
        if suffix == ".csv":
            last_error = None
            for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
                try:
                    frame = pd.read_csv(BytesIO(data), encoding=encoding, low_memory=False)
                    break
                except UnicodeDecodeError as exc:
                    last_error = exc
            else:
                raise ValueError("Encoding CSV tidak dikenali.") from last_error
        else:
            engine = "openpyxl" if suffix == ".xlsx" else "xlrd"
            frame = pd.read_excel(BytesIO(data), sheet_name=sheet_name or 0, engine=engine)
    except ImportError as exc:
        raise ValueError("Untuk membaca file .xls, instal dependensi xlrd: pip install xlrd.") from exc
    except (pd.errors.ParserError, ValueError, OSError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("Untuk membaca"):
            raise
        raise ValueError(f"File tidak dapat dibaca. Periksa apakah file rusak atau formatnya sesuai. Detail: {exc}") from exc
    if isinstance(frame, dict):
        raise ValueError("Pilih satu sheet Excel terlebih dahulu.")
    if frame.empty and len(frame.columns) == 0:
        raise ValueError("Dataset tidak memiliki baris maupun kolom.")
    # Keep original labels readable, but make duplicate labels unique and traceable.
    cols, seen = [], {}
    for i, col in enumerate(frame.columns):
        name = str(col).strip() or f"Kolom_{i+1}"
        seen[name] = seen.get(name, 0) + 1
        cols.append(name if seen[name] == 1 else f"{name} ({seen[name]})")
    frame.columns = cols
    return frame
