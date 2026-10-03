"""
template_03.py — 3 Tall Cards with large image banners.

Layout:
┌────────────────────────────────────────────┐
│  [IMAGE BANNER]  Story 1                   │
│  Headline + Key facts below                │
├────────────────────────────────────────────┤
│  [IMAGE BANNER]  Story 2                   │
├────────────────────────────────────────────┤
│  [IMAGE BANNER]  Story 3                   │
└────────────────────────────────────────────┘
"""
import textwrap
from .theme import *


def render(post_data: dict, output_path: str) -> str:
    updates  = post_data.get("updates", [])
    date_str = post_data.get("date", "")

    img, draw = new_canvas()
    draw_header(img, draw, date_str, "3 DEEP DIVES YOU SHOULD KNOW")

    CARD_W  = 990
    CARD_H  = 320
    GAP     = 22
    START_X = 45
    START_Y = 225

    for i in range(min(3, len(updates))):
        item = updates[i]
        cx   = START_X
        cy   = START_Y + i * (CARD_H + GAP)

        # Shadow + card
        rounded_rect(draw, [cx + 3, cy + 3, cx + CARD_W + 3, cy + CARD_H + 3],
                     radius=22, fill="#CDD9EA")
        rounded_rect(draw, [cx, cy, cx + CARD_W, cy + CARD_H],
                     radius=22, fill=CARD_BG, outline=CARD_BORDER, width=1)

        # Large image on the left (tall)
        thumb = fetch_thumb(item.get("image_url", ""), size=(268, CARD_H - 24))
        img.paste(thumb, (cx + 12, cy + 12), thumb)

        # Right text area
        tx, ty = cx + 295, cy + 16

        # Number + category inline
        number_circle(draw, tx, ty, i + 1, size=44)
        cat = item.get("category", "NEWS")
        cat_pill(draw, tx + 54, ty + 9, cat)

        # Headline
        hy = ty + 58
        headline = textwrap.fill(item.get("headline", ""), width=38)
        draw.multiline_text((tx, hy), headline, fill=TEXT_DARK,
                            font=font(22, bold=True), spacing=6)
        bbox = draw.multiline_textbbox((tx, hy), headline,
                                       font=font(22, bold=True), spacing=6)

        # KEY FACTS label
        by = bbox[3] + 16
        rounded_rect(draw, [tx, by, tx + 100, by + 24], radius=8, fill=BLUE)
        draw.text((tx + 8, by + 4), "KEY FACTS", fill="#FFFFFF", font=font(12, bold=True))
        by += 34

        # Bullets (up to 4 for this spacious layout)
        for pt in item.get("points", [])[:4]:
            line = textwrap.fill("• " + pt, width=50)
            draw.multiline_text((tx, by), line, fill=TEXT_GRAY,
                                font=font(14), spacing=5)
            bb = draw.multiline_textbbox((tx, by), line, font=font(14), spacing=5)
            by = bb[3] + 8
            if by > cy + CARD_H - 12:
                break

    draw_footer(draw, y_start=1262)
    return save_canvas(img, output_path)
