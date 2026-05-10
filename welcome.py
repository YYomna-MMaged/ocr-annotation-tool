import streamlit as st


def render_welcome():
    """Landing screen shown before any images are loaded."""
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 0 2rem">
            <div style="font-size:5rem">📜</div>
            <h2 style="font-family:'Cinzel',serif;color:#e07b39">
                Arabic Manuscript OCR Annotator
            </h2>
            <p style="color:#8a7b6a;font-size:1.1rem;max-width:560px;margin:auto">
                Prepare high-quality line-level datasets for Arabic OCR model fine-tuning.
                Draw bounding boxes, transcribe text, and export to Excel in one workflow.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="ann-card">
                <h4>1️⃣ Load Images</h4>
                <p style="color:#8a7b6a;font-size:0.9rem">
                Enter the path to your manuscript image folder in the sidebar and click
                <strong>Load Images</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="ann-card">
                <h4>2️⃣ Draw & Crop</h4>
                <p style="color:#8a7b6a;font-size:0.9rem">
                Click and drag on the image to draw a bounding box around a text line.
                A live crop preview appears instantly.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="ann-card">
                <h4>3️⃣ Label & Export</h4>
                <p style="color:#8a7b6a;font-size:0.9rem">
                Enter the Arabic transcription, select the script type, and save.
                Download the annotation Excel file from the sidebar.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        """
        ### 📁 Expected Project Structure
        ```
        your_project/
        ├── input_images/
        │   ├── manuscript_01.jpg
        │   └── manuscript_02.jpg
        ├── cropped_images/         ← auto-created
        │   ├── manuscript_01_crop_001.png
        │   └── manuscript_01_crop_002.png
        └── annotations_output.xlsx ← auto-saved
        ```
        """
    )

