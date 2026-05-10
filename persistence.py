from pathlib import Path

import pandas as pd
import streamlit as st

from constants import EXCEL_FILENAME


def annotations_df() -> pd.DataFrame:
    """Return a clean DataFrame from session annotations."""
    rows = [
        {"font_type": a["font_type"], "img_name": a["img_name"], "label": a["label"]}
        for a in st.session_state.annotations
    ]
    return pd.DataFrame(rows, columns=["font_type", "img_name", "label"])


def autosave_excel():
    """Write annotations to Excel beside the output folder."""
    out_dir = st.session_state.output_folder
    if not out_dir:
        return
    excel_path = Path(out_dir).parent / EXCEL_FILENAME
    df = annotations_df()
    if not df.empty:
        df.to_excel(str(excel_path), index=False, engine="openpyxl")
    elif excel_path.exists():
        excel_path.unlink()


def load_session_from_excel(output_folder: str) -> list[dict]:
    """Load a previous session from annotations_output.xlsx if it exists."""
    excel_path = Path(output_folder).parent / EXCEL_FILENAME
    if not excel_path.exists():
        return []

    df = pd.read_excel(str(excel_path), engine="openpyxl")
    annotations = []
    for _, row in df.iterrows():
        img_name = str(row.get("img_name", ""))
        crop_path = str(Path(output_folder) / img_name)
        source_stem = img_name.rsplit("_crop_", 1)[0] if "_crop_" in img_name else img_name
        annotations.append({
            "font_type": str(row.get("font_type", "Naskh")),
            "img_name": img_name,
            "label": str(row.get("label", "")),
            "crop_path": crop_path,
            "source_stem": source_stem,
        })
    return annotations


def rebuild_counters_from_annotations(annotations: list[dict]):
    """Re-populate crop counters from loaded annotations for display continuity."""
    counters = {}
    for ann in annotations:
        img_name = ann.get("img_name", "")
        if "_crop_" in img_name:
            stem, rest = img_name.rsplit("_crop_", 1)
            try:
                num = int(rest.replace(".png", "").replace(".jpg", ""))
                counters[stem] = max(counters.get(stem, 0), num)
            except ValueError:
                pass
    st.session_state.crop_counters = counters

