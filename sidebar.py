import io
import os

import streamlit as st

from constants import CSV_FILENAME, EXCEL_FILENAME, FONT_TYPES
from file_helpers import collect_images
from persistence import annotations_df, load_session_from_excel, rebuild_counters_from_annotations


def render_sidebar():
    """Render the left sidebar: folder config, font selector, export, shortcuts."""
    with st.sidebar:
        st.markdown("## 📜 Manuscript Annotator")
        st.caption("Arabic OCR Dataset Preparation Tool")
        st.divider()

        st.markdown("### ⚙️ Workspace")
        input_folder = st.text_input(
            "📁 Input Images Folder",
            value=st.session_state.get("_input_folder", "input_images"),
            help="Folder containing your manuscript .jpg/.png images",
        )
        st.session_state["_input_folder"] = input_folder

        output_folder = st.text_input(
            "💾 Crops Output Folder",
            value=st.session_state.get("_output_folder_ui", "cropped_images"),
            help="Cropped image files will be saved here",
        )
        st.session_state["_output_folder_ui"] = output_folder

        if st.button("🔄 Load / Refresh Images", use_container_width=True):
            _load_images(input_folder, output_folder)

        st.divider()
        st.markdown("### 🖋️ Default Script Type")
        st.caption("This persists between crops — change only when needed.")

        curr_font_idx = (
            FONT_TYPES.index(st.session_state.current_font)
            if st.session_state.current_font in FONT_TYPES
            else 3
        )

        chosen_font = st.selectbox(
            "Script / Font Type",
            FONT_TYPES,
            index=curr_font_idx,
            label_visibility="collapsed",
        )
        if chosen_font != st.session_state.current_font:
            st.session_state.current_font = chosen_font

        n_imgs = len(st.session_state.image_list)
        n_anns = len(st.session_state.annotations)
        if n_imgs:
            st.divider()
            st.markdown("### 📊 Session Stats")
            col_a, col_b = st.columns(2)
            col_a.metric("Images", n_imgs)
            col_b.metric("Crops", n_anns)

        if n_anns:
            st.divider()
            st.markdown("### 💾 Export Annotations")

            excel_buf = io.BytesIO()
            annotations_df().to_excel(excel_buf, index=False, engine="openpyxl")
            st.download_button(
                "⬇️ Download Excel (.xlsx)",
                data=excel_buf.getvalue(),
                file_name=EXCEL_FILENAME,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            csv_bytes = annotations_df().to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇️ Download CSV",
                data=csv_bytes,
                file_name=CSV_FILENAME,
                mime="text/csv",
                use_container_width=True,
            )

        st.divider()
        st.markdown("### ⌨️ Shortcuts & Tips")
        st.markdown(
            """
            - **Draw box**: click & drag on canvas
            - **Save crop**: **Ctrl + Enter** while editing the transcription
            - **Next / Prev image**: buttons above canvas
            - **Reset canvas**: click *Clear Canvas*
            - **Zoom**: use the zoom slider
            - **Resume session**: reload the same folder
            """,
            unsafe_allow_html=False,
        )


def _load_images(input_folder: str, output_folder: str):
    """Load images from disk and optionally resume a previous session."""
    if not os.path.isdir(input_folder):
        st.sidebar.error(f"❌ Folder not found: `{input_folder}`")
        return

    os.makedirs(output_folder, exist_ok=True)
    images = collect_images(input_folder)

    if not images:
        st.sidebar.warning("⚠️ No supported images found in that folder.")
        return

    st.session_state.image_list = images
    st.session_state.current_img_idx = 0
    st.session_state.output_folder = output_folder
    st.session_state.canvas_version = 0

    loaded = load_session_from_excel(output_folder)
    if loaded:
        st.session_state.annotations = loaded
        rebuild_counters_from_annotations(loaded)
        st.sidebar.success(
            f"✅ Loaded {len(images)} images.\n"
            f"🔁 Resumed session — {len(loaded)} existing annotations restored."
        )
    else:
        st.session_state.annotations = []
        st.session_state.crop_counters = {}
        st.sidebar.success(f"✅ Loaded {len(images)} images.")

    st.rerun()


def auto_sync_images():
    """Automatically detect newly added or removed images in the input folder."""
    input_folder = st.session_state.get("_input_folder", "input_images")
    output_folder = st.session_state.get("_output_folder_ui", "cropped_images")

    if not os.path.isdir(input_folder):
        return

    os.makedirs(output_folder, exist_ok=True)
    latest_images = collect_images(input_folder)
    if not latest_images:
        return

    old_images = st.session_state.image_list
    if not old_images:
        st.session_state.image_list = latest_images
        st.session_state.current_img_idx = 0
        st.session_state.output_folder = output_folder
        return

    if set(latest_images) != set(old_images):
        current_image = old_images[st.session_state.current_img_idx] if old_images else None
        st.session_state.image_list = latest_images
        st.session_state.output_folder = output_folder

        if current_image in latest_images:
            st.session_state.current_img_idx = latest_images.index(current_image)
        else:
            st.session_state.current_img_idx = 0

