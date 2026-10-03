"""
theme.py — Shared brand constants and drawing helpers for all templates.
"""
import os
import logging
import requests
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1080, 1350

# ── Brand Colors ──────────────────────────────────────────────────────────────
NAVY        = "#132B4F"
BLUE        = "#1769D2"
BG_COLOR    = "#F5F8FC"
BG_BOTTOM   = "#EEF4FA"
CARD_BG     = "#FFFFFF"
CARD_BORDER = "#E2EAF2"
TEXT_DARK   = "#132B4F"
TEXT_GRAY   = "#455A70"
TEXT_MID    = "#2E4A65"
PILL_DARK   = "#17375E"

# ── Category Color System ─────────────────────────────────────────────────────
CAT_COLORS = {
    "INDIA":        ("#E6F1FF", "#1557A6"),
    "NATIONAL":     ("#E6F1FF", "#1557A6"),
    "WORLD":        ("#ECE9FF", "#5145A6"),
    "INTERNATIONAL":("#ECE9FF", "#5145A6"),
    "ECONOMY":      ("#E2F6F1", "#087A68"),
    "BANKING":      ("#E2F6F1", "#087A68"),
    "SCIENCE":      ("#FFF0DE", "#D56512"),
    "TECH":         ("#FFF0DE", "#D56512"),
    "DEFENCE":      ("#FFE5E5", "#C73535"),
    "ENVIRONMENT":  ("#E3F6E8", "#198044"),
    "SPORTS":       ("#FFF4E5", "#C45E00"),
    "AWARDS":       ("#F5E6FF", "#7B2FBE"),
    "APPOINTMENTS": ("#E6F1FF", "#1557A6"),
}

# ── Asset Paths ───────────────────────────────────────────────────────────────
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
FONTS_DIR  = os.path.join(ASSETS_DIR, "fonts")
LOGO_PATH  = os.path.join(ASSETS_DIR, "logo", "logo.png")

FONT_BOLD  = os.path.join(FONTS_DIR, "NotoSans-Bold.ttf")
FONT_REG   = os.path.join(FONTS_DIR, "NotoSans-Regular.ttf")


# ── Font Helper ───────────────────────────────────────────────────────────────
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()


# ── Drawing Helpers ───────────────────────────────────────────────────────────
def rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int,
                 fill=None, outline=None, width: int = 1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def centered_text(draw: ImageDraw.ImageDraw, text: str, y: int, fnt, color: str,
                  canvas_w: int = W):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = (canvas_w - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, fill=color, font=fnt)


def gradient_bg(img: Image.Image):
    """Apply a very subtle vertical gradient to background."""
    draw = ImageDraw.Draw(img)
    top_c    = (248, 250, 253)
    bottom_c = (238, 244, 250)
    for y in range(H):
        t = y / H
        r = int(top_c[0] + (bottom_c[0] - top_c[0]) * t)
        g = int(top_c[1] + (bottom_c[1] - top_c[1]) * t)
        b = int(top_c[2] + (bottom_c[2] - top_c[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def draw_header(img: Image.Image, draw: ImageDraw.ImageDraw, date_str: str,
                subtitle: str = "6 KEY UPDATES YOU SHOULD KNOW"):
    """Draw the shared brand header: logo, DAILY/CURRENT AFFAIRS, date card."""
    # Logo
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            lw, lh = logo.size
            target_lw = 130
            target_lh = int(lh * (target_lw / lw))
            logo = logo.resize((target_lw, target_lh), Image.Resampling.LANCZOS)
            img.paste(logo, (45, 35), logo)
        except Exception as e:
            log.warning(f"Logo load failed: {e}")

    # Tagline
    draw.text((45, 88), "KNOW TODAY  |  THINK DEEPER  |  STAY AHEAD",
              fill="#52657A", font=font(12))

    # Main Titles — centered
    f_daily = font(38, bold=True)
    f_ca    = font(44, bold=True)
    centered_text(draw, "DAILY", 38, f_daily, NAVY)
    centered_text(draw, "CURRENT AFFAIRS", 83, f_ca, BLUE)

    # Date card (top-right)
    rounded_rect(draw, [848, 33, 1035, 112], radius=14, fill="#E8F1FC")
    parts = date_str.upper().split(" ")
    d1 = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else date_str
    d2 = parts[2] if len(parts) >= 3 else ""
    draw.text((864, 48), d1, fill="#173A63", font=font(17, bold=True))
    draw.text((864, 75), d2, fill="#4F6B86", font=font(14))

    # Separator pill
    pill_w = 740
    pill_x = (W - pill_w) // 2
    rounded_rect(draw, [pill_x, 158, pill_x + pill_w, 208],
                 radius=25, fill=PILL_DARK)
    centered_text(draw, subtitle, 170, font(19, bold=True), "#FFFFFF")


def draw_footer(draw: ImageDraw.ImageDraw, y_start: int = 1262):
    """Draw the shared brand footer."""
    draw.rectangle([0, y_start, W, H], fill=NAVY)
    draw.text((45, y_start + 22),
              "A more informed you builds a better tomorrow.",
              fill="#FFFFFF", font=font(16))
    draw.text((W // 2 - 100, y_start + 22),
              "@currently_in_india", fill="#FFFFFF", font=font(16, bold=True))
    draw.text((W - 185, y_start + 22), "Save for later", fill="#AABFCF", font=font(15))


def cat_pill(draw: ImageDraw.ImageDraw, x: int, y: int, cat: str):
    """Draw a category pill and return its right edge x."""
    c_bg, c_fg = CAT_COLORS.get(cat.upper(), ("#E8F2FF", "#1759A5"))
    f_cat = font(12, bold=True)
    bbox = draw.textbbox((0, 0), cat.upper(), font=f_cat)
    pw = bbox[2] - bbox[0] + 20
    rounded_rect(draw, [x, y, x + pw, y + 26], radius=10, fill=c_bg)
    draw.text((x + 10, y + 5), cat.upper(), fill=c_fg, font=f_cat)
    return x + pw


def number_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, num: int, size: int = 44):
    """Draw the numbered circle for a card."""
    draw.ellipse([cx, cy, cx + size, cy + size], fill=BLUE)
    f_num = font(20, bold=True)
    txt = str(num)
    bbox = draw.textbbox((0, 0), txt, font=f_num)
    tx = cx + (size - (bbox[2] - bbox[0])) // 2
    ty = cy + (size - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), txt, fill="#FFFFFF", font=f_num)


def fetch_thumb(url: str, size=(185, 170), radius: int = 12) -> Image.Image:
    """Download, crop, and round-corner an image. Returns a placeholder on failure."""
    try:
        if not url:
            raise ValueError("no url")
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        # Center crop
        iw, ih = img.size
        tw, th = size
        if (iw / ih) > (tw / th):
            new_w = int(ih * tw / th)
            left  = (iw - new_w) // 2
            img   = img.crop((left, 0, left + new_w, ih))
        else:
            new_h = int(iw * th / tw)
            top   = (ih - new_h) // 2
            img   = img.crop((0, top, iw, top + new_h))
        img = img.resize(size, Image.Resampling.LANCZOS)
        # Round corners
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0], size[1]],
                                                radius=radius, fill=255)
        img.putalpha(mask)
        return img
    except Exception as e:
        log.warning(f"Image fetch failed ({url[:60]}...): {e}")
        ph = Image.new("RGBA", size, (226, 234, 245, 255))
        ImageDraw.Draw(ph).rounded_rectangle(
            [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill="#DCE8F5")
        return ph


def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img  = Image.new("RGBA", (W, H), BG_COLOR)
    gradient_bg(img)
    draw = ImageDraw.Draw(img)
    return img, draw


def save_canvas(img: Image.Image, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.convert("RGB").save(output_path, "JPEG", quality=95)
    log.info(f"Image saved: {output_path}")
    return output_path
