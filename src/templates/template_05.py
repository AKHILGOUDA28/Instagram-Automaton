"""
template_05.py — Exam Focus 2x3 Grid (SSC/UPSC style, no images).

Layout: Same 2x3 grid as Template 01 but text-only with Exam Angle box.
┌──────────────────────┬──────────────────────┐
│ CATEGORY             │ CATEGORY             │
│ Headline             │ Headline             │
│ • Key fact 1         │ • Key fact 1         │
│ • Key fact 2         │ • Key fact 2         │
│ ┌─ EXAM ANGLE ─────┐ │ ┌─ EXAM ANGLE ─────┐ │
│ │ Q: ...?  A: ...  │ │ │ Q: ...?  A: ...  │ │
│ └──────────────────┘ │ └──────────────────┘ │
└──────────────────────┴──────────────────────┘
"""
import textwrap
from .theme import *


EXAM_RELEVANCE = ["SSC", "UPSC", "STATE PSC", "BANKING", "RAILWAYS"]


def render(post_data: dict, output_path: str) -> str:
    updates  = post_data.get("updates", [])
    date_str = post_data.get("date", "")

    img, draw = new_canvas()

    # Custom header subtitle for exam focus
    draw_header(img, draw, date_str, "DAILY EXAM CURRENT AFFAIRS")

    # Exam tag line below pill
    exam_line = "  •  ".join(EXAM_RELEVANCE)
    centered_text(draw, exam_line, 215, font(12, bold=True), "#4F6B86")

    # Grid constants
    COL_W   = 476
    CARD_H  = 278
    GAP_X   = 38
    GAP_Y   = 22
    START_X = 45
    START_Y = 238

    for i in range(min(6, len(updates))):
        item = updates[i]
        row  = i // 2
        col  = i % 2
        cx   = START_X + col * (COL_W + GAP_X)
        cy   = START_Y + row * (CARD_H + GAP_Y)

        # Card shadow + bg
        rounded_rect(draw, [cx + 3, cy + 3, cx + COL_W + 3, cy + CARD_H + 3],
                     radius=20, fill="#CDD9EA")
        rounded_rect(draw, [cx, cy, cx + COL_W, cy + CARD_H],
                     radius=20, fill=CARD_BG, outline=CARD_BORDER, width=1)

        # Left colored accent strip
        cat = item.get("category", "NEWS")
        _, c_fg = CAT_COLORS.get(cat.upper(), ("#E8F2FF", "#1759A5"))
        draw.rectangle([cx, cy + 30, cx + 5, cy + CARD_H - 30], fill=c_fg)

        # Number circle (small)
        number_circle(draw, cx + 14, cy + 14, i + 1, size=38)

        # Category pill
        cat_pill(draw, cx + 60, cy + 20, cat)

        # --- IMAGE ---
        thumb = fetch_thumb(item.get("image_url", ""), size=(130, 130))
        img.paste(thumb, (cx + 16, cy + 62), thumb)

        tx = cx + 158

        # --- HEADLINE ---
        hy = cy + 62
        headline = textwrap.fill(item.get("headline", ""), width=26)
        draw.multiline_text((tx, hy), headline, fill=TEXT_DARK,
                            font=font(17, bold=True), spacing=4)
        bbox = draw.multiline_textbbox((tx, hy), headline,
                                       font=font(17, bold=True), spacing=4)

        # --- BULLETS ---
        by = bbox[3] + 8
        for pt in item.get("points", [])[:2]:
            line = textwrap.fill("• " + pt, width=35)
            draw.multiline_text((tx, by), line, fill=TEXT_GRAY,
                                font=font(12), spacing=3)
            bb = draw.multiline_textbbox((tx, by), line, font=font(12), spacing=3)
            by = bb[3] + 5

        # --- EXAM ANGLE BOX ---
        exam_box_y = cy + CARD_H - 74
        rounded_rect(draw,
                     [cx + 10, exam_box_y, cx + COL_W - 10, cy + CARD_H - 10],
                     radius=10, fill="#EEF4FF")
        draw.text((cx + 18, exam_box_y + 6), "EXAM ANGLE",
                  fill=BLUE, font=font(11, bold=True))

        actual_q = item.get("question", "")
        actual_a = item.get("answer", "")
        if not actual_q:
            actual_q = f"What is related to {item.get('headline', '')[:30]}?"
        
        q_line = textwrap.fill(f"Q: {actual_q}", width=66)
        
        # We need to print Q and A separately or together if it fits
        draw.multiline_text((cx + 18, exam_box_y + 20), q_line,
                            fill=TEXT_DARK, font=font(11, bold=True), spacing=2)
        
        # Figure out where to put the answer
        q_bbox = draw.multiline_textbbox((cx + 18, exam_box_y + 20), q_line, font=font(11, bold=True), spacing=2)
        ans_line = textwrap.fill(f"Ans: {actual_a}", width=66)
        draw.multiline_text((cx + 18, q_bbox[3] + 2), ans_line,
                            fill="#0A6B29", font=font(11, bold=True), spacing=2) # Green for answer

    draw_footer(draw, y_start=1262)
    return save_canvas(img, output_path)
