import streamlit as st

from annotations_table import render_annotation_table
from canvas_section import render_canvas_section
from sidebar import auto_sync_images, render_sidebar
from state import init_state
from styles import configure_page
from welcome import render_welcome


def main():
    configure_page()
    init_state()
    render_sidebar()
    auto_sync_images()

    st.markdown("# 📜 Arabic Manuscript OCR Annotator")

    if not st.session_state.image_list:
        render_welcome()
        return

    render_canvas_section()
    render_annotation_table()


if __name__ == "__main__":
    main()

