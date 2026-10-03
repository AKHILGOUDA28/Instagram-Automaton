"""
template_04.py — 4 Alternating Wide Cards.

Layout:
┌────────────────────────────┐
│ [IMG] │ Text  (story 1)    │
├────────────────────────────┤
│ Text  │ [IMG] (story 2)    │
├────────────────────────────┤
│ [IMG] │ Text  (story 3)    │
├────────────────────────────┤
│ Text  │ [IMG] (story 4)    │
└────────────────────────────┘
"""
import textwrap
from .theme import *


def render(post_data: dict, output_path: str) -> str:
    updates  = post_data.get("updates", [])
    date_str = post_data.get("date", "")

    img, draw = new_canvas()
    draw_header(img, draw, date_str, "4 STORIES IN FOCUS TODAY")

    CARD_W  = 990
    CARD_H  = 245
    GAP     = 22
    START_X = 45
    START_Y = 225
    IMG_W   = 300
    IMG_H   = CARD_H - 24

    for i in range(min(4, len(updates))):
        item    = updates[i]
        cx      = START_X
        cy      = START_Y + i * (CARD_H + GAP)
        img_left = (i % 2 == 0)  # Alternate image side

        # Shadow + card
        rounded_rect(draw, [cx + 3, cy + 3, cx + CARD_W + 3, cy + CARD_H + 3],
                     radius=20, fill="#CDD9EA")
        rounded_rect(draw, [cx, cy, cx + CARD_W, cy + CARD_H],
                     radius=20, fill=CARD_BG, outline=CARD_BORDER, width=1)

        # Position image
        thumb = fetch_thumb(item.get("image_url", ""), size=(IMG_W, IMG_H))
        if img_left:
            img_x = cx + 12
            txt_x = cx + IMG_W + 26
        else:
            img_x = cx + CARD_W - IMG_W - 12
            txt_x = cx + 20

        img.paste(thumb, (img_x, cy + 12), thumb)

        # Accent bar on the image side (left or right)
        bar_x = cx if img_left else cx + CARD_W - 6
        draw.rectangle([bar_x, cy, bar_x + 6, cy + CARD_H], fill=BLUE)

        # Number + category
        ty = cy + 14
        number_circle(draw, txt_x, ty, i + 1, size=40)
        cat = item.get("category", "NEWS")
        cat_pill(draw, txt_x + 50, ty + 7, cat)

        # Headline
        hy = ty + 52
        txt_width = CARD_W - IMG_W - 50
        max_chars = int(txt_width / 9)
        headline = textwrap.fill(item.get("headline", ""), width=max_chars)
        draw.multiline_text((txt_x, hy), headline, fill=TEXT_DARK,
                            font=font(20, bold=True), spacing=5)
        bbox = draw.multiline_textbbox((txt_x, hy), headline,
                                       font=font(20, bold=True), spacing=5)

        # Bullets
        by = bbox[3] + 10
        for pt in item.get("points", [])[:3]:
            line = textwrap.fill("• " + pt, width=max_chars + 4)
            draw.multiline_text((txt_x, by), line, fill=TEXT_GRAY,
                                font=font(13), spacing=4)
            bb = draw.multiline_textbbox((txt_x, by), line, font=font(13), spacing=4)
            by = bb[3] + 6
            if by > cy + CARD_H - 12:
                break

    draw_footer(draw, y_start=1262)
    return save_canvas(img, output_path)
