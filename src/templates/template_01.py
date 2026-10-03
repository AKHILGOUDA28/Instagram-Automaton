"""
template_01.py — 2×3 Grid Layout (the original premium design).

Layout:
┌─────┬─────┐
│  1  │  2  │
├─────┼─────┤
│  3  │  4  │
├─────┼─────┤
│  5  │  6  │
└─────┴─────┘
Each card: image left, headline + bullets right.
"""
import textwrap
from .theme import *


def render(post_data: dict, output_path: str) -> str:
    updates = post_data.get("updates", [])
    date_str = post_data.get("date", "")

    img, draw = new_canvas()
    draw_header(img, draw, date_str, "6 KEY UPDATES YOU SHOULD KNOW")

    # Grid constants
    COL_W   = 476
    CARD_H  = 270
    GAP_X   = 38
    GAP_Y   = 28
    START_X = 45
    START_Y = 225

    for i in range(min(6, len(updates))):
        item = updates[i]
        row  = i // 2
        col  = i % 2
        cx   = START_X + col * (COL_W + GAP_X)
        cy   = START_Y + row * (CARD_H + GAP_Y)

        # Card bg + shadow effect (slightly offset rect)
        rounded_rect(draw, [cx + 3, cy + 3, cx + COL_W + 3, cy + CARD_H + 3],
                     radius=20, fill="#D8E4F0")
        rounded_rect(draw, [cx, cy, cx + COL_W, cy + CARD_H],
                     radius=20, fill=CARD_BG, outline=CARD_BORDER, width=1)

        # Number circle
        number_circle(draw, cx + 14, cy + 14, i + 1, size=42)

        # Category pill
        cat = item.get("category", "NEWS")
        cat_pill(draw, cx + 64, cy + 20, cat)

        # Image (left side)
        thumb = fetch_thumb(item.get("image_url", ""), size=(178, 198))
        img.paste(thumb, (cx + 14, cy + 64), thumb)

        # Headline (right of image)
        tx = cx + 205
        ty = cy + 64
        headline = textwrap.fill(item.get("headline", ""), width=23)
        draw.multiline_text((tx, ty), headline, fill=TEXT_DARK,
                            font=font(19, bold=True), spacing=5)
        bbox = draw.multiline_textbbox((tx, ty), headline,
                                       font=font(19, bold=True), spacing=5)

        # Bullets
        by = bbox[3] + 12
        for pt in item.get("points", [])[:3]:
            line = textwrap.fill("• " + pt, width=30)
            draw.multiline_text((tx, by), line, fill=TEXT_GRAY,
                                font=font(13), spacing=4)
            bb = draw.multiline_textbbox((tx, by), line, font=font(13), spacing=4)
            by = bb[3] + 6

    draw_footer(draw, y_start=1262)
    return save_canvas(img, output_path)
