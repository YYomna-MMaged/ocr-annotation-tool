import streamlit as st
from streamlit.components.v1 import html


def configure_page():
    """Set Streamlit page config and inject custom CSS."""
    st.set_page_config(
        page_title="Arabic Manuscript Annotator",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');

        :root {
            --bg-dark:     #0e0c0a;
            --bg-card:     #1a1612;
            --bg-card2:    #221e19;
            --accent:      #e07b39;
            --accent-dim:  #9e5526;
            --accent-glow: rgba(224,123,57,0.25);
            --text-main:   #f0e8d8;
            --text-muted:  #8a7b6a;
            --border:      #3a3028;
            --success:     #4caf78;
            --danger:      #d94f4f;
        }

        .stApp {
            background: var(--bg-dark);
            color: var(--text-main);
        }
        .block-container { padding-top: 1.5rem !important; }

        h1 {
            font-family: 'Cinzel', serif !important;
            color: var(--accent) !important;
            letter-spacing: 0.05em;
            font-size: 2rem !important;
        }
        h2, h3 { font-family: 'Cinzel', serif !important; color: var(--text-main) !important; }

        [data-testid="stSidebar"] {
            background: var(--bg-card) !important;
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] .stButton > button {
            background: var(--bg-card2);
            border: 1px solid var(--border);
            color: var(--text-main);
            border-radius: 6px;
            transition: all 0.2s;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: var(--accent);
            color: var(--accent);
        }

        .stButton > button[kind="primary"] {
            background: var(--accent) !important;
            border: none !important;
            color: #1a1612 !important;
            font-weight: 700 !important;
            border-radius: 6px !important;
            transition: all 0.2s !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #f5905a !important;
            box-shadow: 0 0 18px var(--accent-glow) !important;
        }

        .stButton > button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid var(--border) !important;
            color: var(--text-muted) !important;
            border-radius: 6px !important;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: var(--danger) !important;
            color: var(--danger) !important;
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: var(--bg-card2) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-main) !important;
            border-radius: 6px !important;
            font-family: 'Amiri', serif;
            font-size: 1.1rem;
            direction: rtl;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px var(--accent-glow) !important;
        }

        .large-arabic-input textarea {
            min-height: 260px !important;
            line-height: 1.9 !important;
            resize: vertical !important;
            white-space: pre-wrap !important;
        }

        .stSelectbox > div > div {
            background: var(--bg-card2) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-main) !important;
            border-radius: 6px !important;
        }

        [data-baseweb="tab-list"] {
            background: var(--bg-card) !important;
            border-radius: 8px 8px 0 0;
            border-bottom: 1px solid var(--border) !important;
        }
        [data-baseweb="tab"] {
            color: var(--text-muted) !important;
            font-family: 'Cinzel', serif !important;
        }
        [aria-selected="true"] {
            color: var(--accent) !important;
            border-bottom: 2px solid var(--accent) !important;
        }

        .stDataFrame { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }

        [data-testid="stExpander"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }

        .ann-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        .ann-badge {
            display: inline-block;
            background: var(--accent-dim);
            color: var(--text-main);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-family: monospace;
        }
        .arabic-label {
            font-family: 'Amiri', serif;
            font-size: 1.2rem;
            direction: rtl;
            text-align: right;
            color: var(--text-main);
        }

        [data-testid="stAlert"] {
            border-radius: 8px !important;
            border: 1px solid var(--border) !important;
        }

        .stSlider > div > div > div { color: var(--accent) !important; }
        hr { border-color: var(--border) !important; }
        .stCaption { color: var(--text-muted) !important; }

        [data-testid="stImage"] img {
            border: 1px solid var(--border);
            border-radius: 6px;
        }

        .nav-pill {
            display: inline-block;
            background: var(--bg-card2);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 4px 14px;
            font-family: 'Cinzel', serif;
            font-size: 0.82rem;
            color: var(--text-muted);
            margin: 0 4px;
        }

        /* streamlit-drawable-canvas toolbar: keep undo/redo visible on dark UI. */
        div[data-testid="stVerticalBlock"] button[title*="Undo"],
        div[data-testid="stVerticalBlock"] button[title*="Redo"],
        div[data-testid="stVerticalBlock"] button[title*="Delete"],
        div[data-testid="stVerticalBlock"] button[title*="Remove"] {
            background: var(--bg-card2) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-main) !important;
        }
        div[data-testid="stVerticalBlock"] button[title*="Undo"] svg,
        div[data-testid="stVerticalBlock"] button[title*="Redo"] svg,
        div[data-testid="stVerticalBlock"] button[title*="Delete"] svg,
        div[data-testid="stVerticalBlock"] button[title*="Remove"] svg {
            fill: var(--text-main) !important;
            stroke: var(--text-main) !important;
        }
        div[data-testid="stVerticalBlock"] button[title*="Undo"]:hover,
        div[data-testid="stVerticalBlock"] button[title*="Redo"]:hover {
            border-color: var(--accent) !important;
            color: var(--accent) !important;
        }

        /* Image selector - make it bigger and button-like */
        #image_selector {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            padding: 12px 16px !important;
            height: auto !important;
            min-height: 48px !important;
        }

        /* 1. ضبط الحاوية الأساسية للـ Selectbox */
        div[data-testid="stSelectbox"] > div {
            background-color: var(--bg-card2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            height: 45px !important;
            display: flex !important;
            align-items: center !important;
        }

        /* 2. دمج الأجزاء الـ 3 في جزء واحد متناسق */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: transparent !important;
            border: none !important;
            padding: 0 12px !important;
            width: 100% !important;
            display: flex !important;
        }

        /* 3. تنظيف النص وجعله واضح وفي المنتصف */
        div[data-testid="stSelectbox"] .st-ae, 
        div[data-testid="stSelectbox"] [data-testid="stMarkdownContainer"] p {
            color: var(--text-main) !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
        }

        /* 4. إخفاء الخطوط الفاصلة */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div:nth-child(2) {
            display: none !important;
        }

        /* 5. ضبط شكل ولون سهم الاختيار */
        div[data-testid="stSelectbox"] svg {
            fill: var(--accent) !important;
        }

        /* 6. تنسيق القائمة اللي بتفتح (Dropdown Menu) */
        [role="listbox"] {
            background-color: var(--bg-card2) !important;
            border: 1px solid var(--border) !important;
        }
        [role="option"] {
            color: var(--text-main) !important;
            background-color: transparent !important;
        }
        [role="option"]:hover {
            background-color: var(--bg-card) !important;
            color: var(--accent) !important;
        }
        [role="option"][aria-selected="true"] {
            background-color: var(--accent-dim) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _inject_canvas_toolbar_styles()


def _inject_canvas_toolbar_styles():
    """Try to style drawable-canvas toolbar buttons rendered inside iframes."""
    html(
        """
        <script>
        const toolbarCss = `
            button[title*="Undo"], button[title*="Redo"],
            button[aria-label*="Undo"], button[aria-label*="Redo"],
            button[title*="Delete"], button[aria-label*="Delete"],
            button[title*="Remove"], button[aria-label*="Remove"] {
                background: #221e19 !important;
                border: 1px solid #3a3028 !important;
                color: #f0e8d8 !important;
            }
            button[title*="Undo"] svg, button[title*="Redo"] svg,
            button[aria-label*="Undo"] svg, button[aria-label*="Redo"] svg,
            button[title*="Delete"] svg, button[aria-label*="Delete"] svg,
            button[title*="Remove"] svg, button[aria-label*="Remove"] svg,
            button[title*="Undo"] path, button[title*="Redo"] path,
            button[aria-label*="Undo"] path, button[aria-label*="Redo"] path,
            button[title*="Delete"] path, button[aria-label*="Delete"] path,
            button[title*="Remove"] path, button[aria-label*="Remove"] path {
                fill: #f0e8d8 !important;
                stroke: #f0e8d8 !important;
            }
            button[title*="Undo"]:hover, button[title*="Redo"]:hover,
            button[aria-label*="Undo"]:hover, button[aria-label*="Redo"]:hover {
                border-color: #e07b39 !important;
                color: #e07b39 !important;
            }
        `;

        function injectInto(doc) {
            if (!doc || doc.getElementById("canvas-toolbar-dark-fix")) return;
            const style = doc.createElement("style");
            style.id = "canvas-toolbar-dark-fix";
            style.textContent = toolbarCss;
            doc.head.appendChild(style);
        }

        function run() {
            try { injectInto(window.parent.document); } catch (e) {}
            try {
                const iframes = window.parent.document.querySelectorAll("iframe");
                iframes.forEach((frame) => {
                    try { injectInto(frame.contentDocument); } catch (e) {}
                });
            } catch (e) {}
        }

        run();
        setInterval(run, 800);
        </script>
        """,
        height=0,
        width=0,
    )
