import os
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from streamlit.components.v1 import html

from canvas_helpers import extract_rects, scale_rect_to_original
from constants import BOX_FILL_COLOR, BOX_STROKE_COLOR, FONT_TYPES, MAX_CANVAS_WIDTH
from file_helpers import next_crop_name, sanitize_crop_filename, save_crop
from persistence import autosave_excel


def render_canvas_section():
    """Render the image canvas and the live crop/annotation panel."""
    image_list = st.session_state.image_list
    idx = st.session_state.current_img_idx
    output_dir = st.session_state.output_folder
    current_path = image_list[idx]

    try:
        image_pil = Image.open(current_path).convert("RGB")
    except Exception as exc:
        st.error(f"❌ Could not open image: {exc}")
        return

    orig_w, orig_h = image_pil.size
    _render_navigation(idx, image_list, current_path, orig_w, orig_h)

    st.markdown("<br>", unsafe_allow_html=True)
    zoom_pct = st.slider(
        "🔍 Zoom level", min_value=25, max_value=200, value=75, step=25, format="%d%%"
    )

    display_w = int(orig_w * zoom_pct / 100)
    display_h = int(orig_h * zoom_pct / 100)
    if display_w > MAX_CANVAS_WIDTH:
        scale = MAX_CANVAS_WIDTH / display_w
        display_w = MAX_CANVAS_WIDTH
        display_h = int(display_h * scale)

    display_img = image_pil.resize((display_w, display_h), Image.LANCZOS)
    col_canvas, col_panel = st.columns([3, 1], gap="medium")

    with col_canvas:
    # Auto-switch mode based on whether boxes exist on canvas
        has_rects = st.session_state.get("has_rects_on_canvas", False)
        drawing_mode = "transform" if has_rects else "rect"

        canvas_key = f"canvas_{idx}_{st.session_state.canvas_version}"
        canvas_result = st_canvas(
            fill_color=BOX_FILL_COLOR,
            stroke_width=2,
            stroke_color=BOX_STROKE_COLOR,
            background_image=display_img,
            update_streamlit=True,
            height=display_h,
            width=display_w,
            drawing_mode=drawing_mode,
            key=canvas_key,
        )

        # Detect if rects appeared/disappeared and switch mode automatically
        rects_now = extract_rects(canvas_result.json_data) if canvas_result.json_data else []
        new_has_rects = len(rects_now) > 0
        if new_has_rects != has_rects:
            st.session_state.has_rects_on_canvas = new_has_rects
            st.rerun()

        if st.button("🔄 Clear Canvas", help="Remove all drawn boxes"):
            st.session_state.canvas_version += 1
            st.session_state.has_rects_on_canvas = False  # ← reset mode too
            st.rerun()

    with col_panel:
        _render_crop_panel(
            canvas_result=canvas_result,
            image_pil=image_pil,
            current_path=current_path,
            output_dir=output_dir,
            idx=idx,
            display_w=display_w,
            display_h=display_h,
            orig_w=orig_w,
            orig_h=orig_h,
        )

def _render_navigation(idx, image_list, current_path, orig_w, orig_h):
    nav_l, nav_c, nav_r = st.columns([1, 3, 1], vertical_alignment="center")

    with nav_l:
        if st.button("◀ Prev", disabled=(idx == 0), use_container_width=True, key="prev_btn"):
            st.session_state.current_img_idx -= 1
            st.session_state.canvas_version += 1
            st.session_state.has_rects_on_canvas = False  # ← add this
            st.rerun()
            
    with nav_c:
        image_names = [Path(img).name for img in image_list]
        selected_image_name = st.selectbox(
            "Select Image",
            options=image_names,
            index=idx,
            label_visibility="collapsed",
            key="image_selector"
        )
        # التحديث في حالة التغيير
        if selected_image_name != image_names[idx]:
            st.session_state.current_img_idx = image_names.index(selected_image_name)
            st.session_state.canvas_version += 1
            st.session_state.has_rects_on_canvas = False  # ← add this
            st.rerun()
    
    with nav_r:
        if st.button("Next ▶", disabled=(idx == len(image_list) - 1), use_container_width=True, key="next_btn"):
            st.session_state.current_img_idx += 1
            st.session_state.canvas_version += 1
            st.session_state.has_rects_on_canvas = False  # ← add this
            st.rerun()

    # المعلومات والـ Progress Bar نخليهم "تحت" الـ Columns مش جواها عشان ميبوظوش المحاذاة
    pct = (idx + 1) / len(image_list) * 100
    st.markdown(
        f"<div style='text-align:center; margin-top: -10px;'>"
        f"<span class='nav-pill'>Image {idx + 1} / {len(image_list)}</span>"
        f"<span class='nav-pill'>{orig_w}×{orig_h} px</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.progress(pct / 100)


def _render_crop_panel(
    canvas_result,
    image_pil: Image.Image,
    current_path: str,
    output_dir: str,
    idx: int,
    display_w: int,
    display_h: int,
    orig_w: int,
    orig_h: int,
):
    st.markdown("#### ✂️ Crop & Annotate")
    rects = extract_rects(canvas_result.json_data)

    if not rects:
        st.info("Draw a rectangle on the image to begin.")
        return

    last_rect = rects[-1]
    box = scale_rect_to_original(last_rect, display_w, display_h, orig_w, orig_h)

    if box["width"] < 5 or box["height"] < 5:
        st.warning("Box is too small. Draw a larger rectangle.")
        return

    try:
        x = max(0, int(box["left"]))
        y = max(0, int(box["top"]))
        x2 = min(orig_w, x + int(box["width"]))
        y2 = min(orig_h, y + int(box["height"]))
        preview = image_pil.crop((x, y, x2, y2))
        st.image(preview, caption="Crop Preview", use_container_width=True)
        st.caption(f"Size: {x2 - x} × {y2 - y} px")
    except Exception as exc:
        st.error(f"Preview error: {exc}")
        return

    default_auto_name = next_crop_name(current_path, output_dir)
    stem = Path(current_path).stem
    st.caption(f"Next auto name from folder: `{default_auto_name}`")

    rect_count = len(rects)
    label_key = f"label_input_{idx}_{rect_count}"
    font_key = f"crop_font_{idx}_{rect_count}"
    name_key = f"custom_name_{idx}_{rect_count}"

    st.markdown('<div class="large-arabic-input">', unsafe_allow_html=True)
    label = st.text_area(
        "📝 Transcription (Arabic)",
        placeholder="أدخل النص هنا...",
        key=label_key,
        height=260,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    crop_font_idx = (
        FONT_TYPES.index(st.session_state.current_font)
        if st.session_state.current_font in FONT_TYPES
        else 3
    )
    crop_font = st.selectbox(
        "🖋️ Script Type",
        FONT_TYPES,
        index=crop_font_idx,
        key=font_key,
    )

    custom_crop_name = st.text_input(
        "📁 Crop File Name",
        value=default_auto_name,
        key=name_key,
        help="You can edit this name. Ctrl + Enter saves while your cursor is in the text box.",
    )

    _install_ctrl_enter_submitter()

    save_clicked = st.button(
        "💾 Save Crop",
        type="primary",
        use_container_width=True,
        key=f"save_crop_{idx}_{rect_count}",
    )

    if save_clicked:
        _save_current_crop(
            label=st.session_state.get(label_key, label),
            crop_font=st.session_state.get(font_key, crop_font),
            custom_crop_name=st.session_state.get(name_key, custom_crop_name),
            image_pil=image_pil,
            box=box,
            output_dir=output_dir,
            current_path=current_path,
            stem=stem,
            rendered_auto_name=default_auto_name,
        )


def _save_current_crop(
    label: str,
    crop_font: str,
    custom_crop_name: str,
    image_pil: Image.Image,
    box: dict,
    output_dir: str,
    current_path: str,
    stem: str,
    rendered_auto_name: str,
):
    if not label.strip():
        st.error("Please enter a transcription before saving.")
        return

    if custom_crop_name.strip() == rendered_auto_name:
        crop_name = next_crop_name(current_path, output_dir)
    else:
        try:
            crop_name = sanitize_crop_filename(custom_crop_name)
        except ValueError as exc:
            st.error(str(exc))
            return

    out_path = Path(output_dir) / crop_name
    if os.path.exists(out_path):
        st.error(f"A file named `{crop_name}` already exists. Choose another name.")
        return

    _, crop_path = save_crop(image_pil, box, output_dir, crop_name)
    st.session_state.current_font = crop_font
    st.session_state.annotations.append({
        "font_type": crop_font,
        "img_name": crop_name,
        "label": label.strip(),
        "crop_path": crop_path,
        "source_stem": stem,
    })

    autosave_excel()
    st.session_state.canvas_version += 1
    st.success(f"✅ Saved **{crop_name}**")
    st.rerun()


def _install_ctrl_enter_submitter():
    """Make Ctrl+Enter save reliably after textarea edits."""
    html(
        """
        <script>
        function findSaveButton(doc) {
            const buttons = Array.from(doc.querySelectorAll("button"));
            return buttons.find((button) => button.innerText.includes("Save Crop"));
        }

        function submitFromTextarea(event) {
            if (!(event.ctrlKey || event.metaKey) || event.key !== "Enter") return;
            const target = event.target;
            if (!target || target.tagName !== "TEXTAREA") return;

            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();

            target.dispatchEvent(new Event("input", { bubbles: true }));
            target.dispatchEvent(new Event("change", { bubbles: true }));
            target.blur();

            window.setTimeout(() => {
                const button = findSaveButton(window.parent.document);
                if (button) button.click();
            }, 350);
        }

        function bindShortcut() {
            try {
                const doc = window.parent.document;
                if (doc.__arabicCropCtrlEnterBound) return;
                doc.__arabicCropCtrlEnterBound = true;
                doc.addEventListener("keydown", submitFromTextarea, true);
            } catch (error) {}
        }

        bindShortcut();
        </script>
        """,
        height=0,
        width=0,
    )