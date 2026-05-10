import streamlit as st


def init_state():
    """Initialise all Streamlit session-state keys with safe defaults."""
    defaults = {
        "image_list": [],
        "current_img_idx": 0,
        "annotations": [],
        "current_font": "Naskh",
        "crop_counters": {},
        "output_folder": "",
        "canvas_version": 0,
        "edit_target": None,
        "canvas_drawing_mode": "rect",
        "has_canvas_objects": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

