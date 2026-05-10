import os
from pathlib import Path

import streamlit as st

from constants import FONT_TYPES
from file_helpers import sanitize_crop_filename
from persistence import annotations_df, autosave_excel


def render_annotation_table():
    """Render tabs for current-image annotations and all annotations."""
    st.divider()
    st.markdown("### 📋 Annotations")

    all_anns = st.session_state.annotations
    if not all_anns:
        st.info("No annotations yet. Draw boxes on the image above to start.")
        return

    idx = st.session_state.current_img_idx
    image_list = st.session_state.image_list
    current_stem = Path(image_list[idx]).stem if image_list else ""

    current_anns = [
        (i, a) for i, a in enumerate(all_anns)
        if a.get("source_stem", "") == current_stem
        or a.get("img_name", "").startswith(current_stem)
    ]

    tab_cur, tab_all = st.tabs([
        f"🖼️ Current Image ({len(current_anns)} crops)",
        f"📚 All Images ({len(all_anns)} total)",
    ])

    with tab_cur:
        _render_current_image_anns(current_anns)

    with tab_all:
        _render_all_anns_table()


def _render_current_image_anns(current_anns: list[tuple]):
    if not current_anns:
        st.info("No crops annotated for this image yet.")
        return

    for _local_i, (global_i, ann) in enumerate(current_anns):
        with st.expander(
            f"🔖 {ann['img_name']}  ·  {ann['font_type']}",
            expanded=False,
        ):
            col_img, col_form, col_del = st.columns([2, 3, 1])

            with col_img:
                crop_path = ann.get("crop_path", "")
                if os.path.isfile(crop_path):
                    st.image(crop_path, use_container_width=True)
                else:
                    st.caption("*(file not found)*")

            with col_form:
                new_label = st.text_area(
                    "Label",
                    value=ann["label"],
                    key=f"edit_label_{global_i}",
                    height=140,
                )
                new_font = st.selectbox(
                    "Script Type",
                    FONT_TYPES,
                    index=FONT_TYPES.index(ann["font_type"]) if ann["font_type"] in FONT_TYPES else 3,
                    key=f"edit_font_{global_i}",
                )
                new_img_name = st.text_input(
                    "Crop Filename",
                    value=ann["img_name"],
                    key=f"edit_img_name_{global_i}",
                )
                if st.button("✏️ Update", key=f"btn_update_{global_i}", use_container_width=True):
                    if not _rename_crop_file(global_i, new_img_name):
                        return
                    st.session_state.annotations[global_i]["label"] = new_label.strip()
                    st.session_state.annotations[global_i]["font_type"] = new_font
                    autosave_excel()
                    st.success("✅ Annotation updated.")
                    st.rerun()

            with col_del:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"btn_del_{global_i}", help="Delete this annotation"):
                    _delete_annotation(global_i)
                    st.rerun()


def _delete_annotation(global_i: int):
    ann = st.session_state.annotations[global_i]
    crop_path = ann.get("crop_path", "")

    if os.path.isfile(crop_path):
        try:
            os.remove(crop_path)
        except OSError:
            pass

    st.session_state.annotations.pop(global_i)
    autosave_excel()
    st.success("🗑️ Annotation deleted.")


def _rename_crop_file(global_i: int, new_img_name: str) -> bool:
    ann = st.session_state.annotations[global_i]

    try:
        safe_name = sanitize_crop_filename(new_img_name)
    except ValueError as exc:
        st.error(str(exc))
        return False

    if safe_name == ann.get("img_name"):
        return True

    old_path = ann.get("crop_path", "")
    output_dir = st.session_state.output_folder
    new_path = os.path.join(output_dir, safe_name)

    if os.path.exists(new_path):
        st.error(f"A file named `{safe_name}` already exists. Choose another name.")
        return False

    if old_path and os.path.isfile(old_path):
        try:
            os.rename(old_path, new_path)
        except OSError as exc:
            st.error(f"Could not rename crop file: {exc}")
            return False

    st.session_state.annotations[global_i]["img_name"] = safe_name
    st.session_state.annotations[global_i]["crop_path"] = new_path
    return True


def _render_all_anns_table():
    df = annotations_df()
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "font_type": st.column_config.TextColumn("Font Type", width="small"),
            "img_name": st.column_config.TextColumn("Crop Filename"),
            "label": st.column_config.TextColumn("Arabic Label"),
        },
    )
    st.caption(f"Total crops annotated: **{len(df)}**")
