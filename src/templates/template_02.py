"""
template_02.py — Featured Hero + 4 Compact Cards

Layout:
┌──────────────────────────────┐
│      FEATURED STORY 1        │  (large, image left, big text right)
└──────────────────────────────┘
┌──────┬──────┬──────┬──────┐
│  2   │  3   │  4   │  5   │  (compact, image top, text below)
└──────┴──────┴──────┴──────┘
"""
import textwrap
from .theme import *


def render(post_data: dict, output_path: str) -> str:
    updates  = post_data.get("updates", [])
    date_str = post_data.get("date", "")

    img, draw = new_canvas()
    draw_header(img, draw, date_str, "TODAY'S TOP STORY + 4 UPDATES")

    # ── HERO CARD ─────────────────────────────────────────────────────────────
    HERO_X, HERO_Y = 45, 225
    HERO_W, HERO_H = 990, 370

    rounded_rect(draw, [HERO_X + 3, HERO_Y + 3, HERO_X + HERO_W + 3, HERO_Y + HERO_H + 3],
                 radius=22, fill="#D0DFEE")
    rounded_rect(draw, [HERO_X, HERO_Y, HERO_X + HERO_W, HERO_Y + HERO_H],
                 radius=22, fill=CARD_BG, outline=CARD_BORDER, width=1)

    if updates:
        hero = updates[0]
        # Number + category
        number_circle(draw, HERO_X + 16, HERO_Y + 16, 1, size=48)
        cat_pill(draw, HERO_X + 76, HERO_Y + 22, hero.get("category", "NEWS"))

        # Large image
        thumb = fetch_thumb(hero.get("image_url", ""), size=(310, 290))
        img.paste(thumb, (HERO_X + 16, HERO_Y + 70), thumb)

        # Text area
        tx, ty = HERO_X + 345, HERO_Y + 70

        # Headline — larger font for hero
        headline = textwrap.fill(hero.get("headline", ""), width=30)
        draw.multiline_text((tx, ty), headline, fill=TEXT_DARK,
                            font=font(26, bold=True), spacing=7)
        bbox = draw.multiline_textbbox((tx, ty), headline,
                                       font=font(26, bold=True), spacing=7)

        # Key facts label
        by = bbox[3] + 18
        draw.text((tx, by), "KEY FACTS", fill=BLUE, font=font(13, bold=True))
        by += 22

        # Bullets
        for pt in hero.get("points", [])[:3]:
            line = textwrap.fill("• " + pt, width=42)
            draw.multiline_text((tx, by), line, fill=TEXT_GRAY,
                                font=font(14), spacing=5)
            bb = draw.multiline_textbbox((tx, by), line, font=font(14), spacing=5)
            by = bb[3] + 8

    # ── 4 COMPACT CARDS ───────────────────────────────────────────────────────
    COMP_Y   = HERO_Y + HERO_H + 30
    COMP_W   = 228
    COMP_H   = 570
    GAP      = 14
    START_X  = 45

    for i in range(1, min(5, len(updates))):
        item = updates[i]
        cx   = START_X + (i - 1) * (COMP_W + GAP)

        rounded_rect(draw, [cx + 2, COMP_Y + 2, cx + COMP_W + 2, COMP_Y + COMP_H + 2],
                     radius=18, fill="#D0DFEE")
        rounded_rect(draw, [cx, COMP_Y, cx + COMP_W, COMP_Y + COMP_H],
                     radius=18, fill=CARD_BG, outline=CARD_BORDER, width=1)

        # Number circle (small)
        number_circle(draw, cx + 10, COMP_Y + 10, i + 1, size=36)

        # Category pill
        cat = item.get("category", "NEWS")
        c_bg, c_fg = CAT_COLORS.get(cat.upper(), ("#E8F2FF", "#1759A5"))
        rounded_rect(draw, [cx + 52, COMP_Y + 14, cx + COMP_W - 8, COMP_Y + 36],
                     radius=10, fill=c_bg)
        draw.text((cx + 58, COMP_Y + 18), cat.upper()[:10],
                  fill=c_fg, font=font(11, bold=True))

        # Compact image (full width of card)
        thumb = fetch_thumb(item.get("image_url", ""), size=(COMP_W - 20, 130))
        img.paste(thumb, (cx + 10, COMP_Y + 46), thumb)

        # Headline
        ty = COMP_Y + 185
        headline = textwrap.fill(item.get("headline", ""), width=18)
        draw.multiline_text((cx + 10, ty), headline, fill=TEXT_DARK,
                            font=font(15, bold=True), spacing=5)
        bbox = draw.multiline_textbbox((cx + 10, ty), headline,
                                       font=font(15, bold=True), spacing=5)

        # Bullets
        by = bbox[3] + 10
        for pt in item.get("points", [])[:3]:
            line = textwrap.fill("• " + pt, width=20)
            draw.multiline_text((cx + 10, by), line, fill=TEXT_GRAY,
                                font=font(12), spacing=4)
            bb = draw.multiline_textbbox((cx + 10, by), line,
                                         font=font(12), spacing=4)
            by = bb[3] + 6
            if by > COMP_Y + COMP_H - 20:
                break

    draw_footer(draw, y_start=1262)
    return save_canvas(img, output_path)
