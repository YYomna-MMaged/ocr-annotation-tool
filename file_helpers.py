import re
from pathlib import Path

import streamlit as st
from PIL import Image

from constants import SUPPORTED_EXTENSIONS


def collect_images(folder: str) -> list[str]:
    """Return a sorted list of supported image file paths from folder."""
    p = Path(folder)
    found = []
    for ext in SUPPORTED_EXTENSIONS:
        found.extend(p.glob(f"*{ext}"))
        found.extend(p.glob(f"*{ext.upper()}"))
    return sorted({str(f) for f in found})


def sanitize_crop_filename(raw_name: str) -> str:
    """Clean a user-supplied crop filename while keeping Arabic characters."""
    safe_name = raw_name.strip().replace(" ", "_")
    safe_name = re.sub(r'[<>:"/\\\\|?*]+', "_", safe_name)
    safe_name = safe_name.strip("._")
    if not safe_name:
        raise ValueError("Please enter a valid file name.")
    if not safe_name.lower().endswith(".png"):
        safe_name += ".png"
    return safe_name


def next_crop_name(image_path: str, output_folder: str) -> str:
    """
    Generate the next sequential crop filename from files currently on disk.

    This deliberately re-scans output_folder on every save, so manual deletion,
    rename, or edits inside the folder are reflected before choosing the number.
    """
    stem = Path(image_path).stem
    pattern = re.compile(rf"^{re.escape(stem)}_crop_(\d+)\.png$", re.IGNORECASE)
    max_seen = 0

    out_dir = Path(output_folder)
    if out_dir.exists():
        for file_path in out_dir.iterdir():
            if not file_path.is_file():
                continue
            match = pattern.match(file_path.name)
            if match:
                max_seen = max(max_seen, int(match.group(1)))

    next_idx = max_seen + 1
    st.session_state.crop_counters[stem] = next_idx
    return f"{stem}_crop_{next_idx:03d}.png"


def save_crop(
    image_pil: Image.Image,
    box: dict,
    output_folder: str,
    filename: str,
) -> tuple[Image.Image, str]:
    """Crop image_pil using original-image coordinates and save as PNG."""
    x = max(0, int(box["left"]))
    y = max(0, int(box["top"]))
    x2 = min(image_pil.width, x + max(1, int(box["width"])))
    y2 = min(image_pil.height, y + max(1, int(box["height"])))

    cropped = image_pil.crop((x, y, x2, y2))
    out_path = Path(output_folder) / filename
    cropped.save(out_path, "PNG")
    return cropped, str(out_path)


def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritical marks (tashkeel) from text and normalize whitespace."""
    # Remove all Arabic diacritics using explicit Unicode ranges:
    # U+0610–U+061A : Arabic extended marks (e.g. ؐ–ؚ)
    # U+064B–U+065F : Core tashkeel (fathah, dammah, kasrah, tanwin, shadda, sukun …)
    # U+0670       : Arabic letter superscript alef (alef wasl mark)
    # U+06D6–U+06DC: Quranic annotation signs
    # U+06DF–U+06E4: More Quranic marks
    # U+06E7–U+06E8: Arabic small high yeh / noon
    # U+06EA–U+06ED: Arabic empty centre / rounded high stop …
    arabic_diacritics = re.compile(
        r'[\u0610-\u061A\u064B-\u065F\u0670'
        r'\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]'
    )
    text = arabic_diacritics.sub('', text)

    # Collapse multiple spaces / tabs on the same line into a single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Collapse 3+ consecutive newlines down to at most 2 (preserve paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()