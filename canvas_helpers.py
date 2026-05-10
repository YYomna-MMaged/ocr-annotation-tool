def extract_rects(json_data: dict) -> list[dict]:
    """Pull rectangle objects from the canvas JSON payload."""
    if not json_data:
        return []
    return [obj for obj in json_data.get("objects", []) if obj.get("type") == "rect"]


def scale_rect_to_original(
    rect: dict,
    display_w: int,
    display_h: int,
    orig_w: int,
    orig_h: int,
) -> dict:
    """Convert canvas-space rectangle coordinates back to original image space."""
    sx = orig_w / display_w
    sy = orig_h / display_h
    return {
        "left": rect["left"] * sx,
        "top": rect["top"] * sy,
        "width": rect["width"] * rect.get("scaleX", 1) * sx,
        "height": rect["height"] * rect.get("scaleY", 1) * sy,
    }

