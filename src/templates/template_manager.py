"""
template_manager.py — Selects which template to render based on the day of week.

Rotation:
    Monday    → Template 01 (2×3 Grid)
    Tuesday   → Template 02 (Featured + 4 Compact)
    Wednesday → Template 03 (3 Tall Cards)
    Thursday  → Template 04 (4 Alternating)
    Friday    → Template 05 (Exam Focus)
    Saturday  → Template 01 (2×3 Grid)
    Sunday    → Template 02 (Featured + 4 Compact)
"""

import logging
from datetime import datetime

from . import template_01, template_02, template_03, template_04, template_05

log = logging.getLogger(__name__)

NAMES = {
    template_01: "Template 01 — 2×3 Grid",
    template_02: "Template 02 — Featured + 4 Compact",
    template_03: "Template 03 — 3 Tall Cards",
    template_04: "Template 04 — 4 Alternating",
    template_05: "Template 05 — Exam Focus",
}


def get_template(override: int | None = None):
    """Return the template module (always template_05)."""
    tmpl = template_05
    log.info(f"Using {NAMES.get(tmpl, 'Unknown template')}")
    return tmpl


def render(post_data: dict, output_path: str,
           template_override: int | None = None) -> str:
    """Select and render the appropriate template."""
    tmpl = get_template(template_override)
    return tmpl.render(post_data, output_path)
