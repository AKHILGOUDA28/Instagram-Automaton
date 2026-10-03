"""
image_generator.py — Thin wrapper that delegates to the template manager.

The actual rendering logic lives in src/templates/template_0N.py files.
"""

import os
import logging
from datetime import datetime
from src.templates import template_manager

log = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def generate_image(post_data: dict, template_override: int | None = None) -> str:
    """
    Generate the Instagram image using the selected template.

    Args:
        post_data:          Structured dict from summarizer (has 'updates', 'date', etc.)
        template_override:  Force a specific template (1-5). None = auto by weekday.

    Returns:
        Absolute path to the saved JPEG file.
    """
    date_tag    = datetime.now().strftime("%Y_%m_%d")
    output_path = os.path.join(OUTPUT_DIR, f"current_affairs_{date_tag}.jpg")

    log.info("Generating Instagram image via template manager...")
    result = template_manager.render(post_data, output_path, template_override)
    log.info(f"Image saved: {result}")
    return result
