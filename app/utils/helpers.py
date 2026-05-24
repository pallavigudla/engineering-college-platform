"""
app/utils/helpers.py — General helper functions and Jinja2 filters
"""

import json
from flask import current_app


def register_template_filters(app):
    """Register custom Jinja2 template filters."""

    @app.template_filter("currency_inr")
    def currency_inr(value):
        """Format integer as Indian currency ₹X,XX,XXX"""
        if value is None:
            return "N/A"
        try:
            value = int(value)
            # Indian number formatting (uses lakhs/crores)
            s = str(value)
            if len(s) > 3:
                last3 = s[-3:]
                rest = s[:-3]
                groups = []
                while len(rest) > 2:
                    groups.append(rest[-2:])
                    rest = rest[:-2]
                if rest:
                    groups.append(rest)
                groups.reverse()
                return "₹" + ",".join(groups) + "," + last3
            return "₹" + s
        except (ValueError, TypeError):
            return "N/A"

    @app.template_filter("lpa_display")
    def lpa_display(value):
        """Format LPA value nicely."""
        if value is None:
            return "N/A"
        try:
            v = float(value)
            return f"₹{v:.1f} LPA"
        except (ValueError, TypeError):
            return "N/A"

    @app.template_filter("short_number")
    def short_number(value):
        """Shorten large numbers: 1200 → 1.2K, 1500000 → 1.5L"""
        if value is None:
            return "N/A"
        try:
            v = float(value)
            if v >= 100000:
                return f"{v/100000:.1f}L"
            elif v >= 1000:
                return f"{v/1000:.1f}K"
            return str(int(v))
        except (ValueError, TypeError):
            return "N/A"

    @app.template_filter("truncate_name")
    def truncate_name(value, length=40):
        """Truncate long college names."""
        if not value:
            return ""
        if len(value) <= length:
            return value
        return value[:length].rstrip() + "…"

    @app.template_filter("parse_json")
    def parse_json(value):
        """Parse a JSON string to Python object."""
        if not value:
            return []
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Fallback: try comma-separated
            return [v.strip() for v in str(value).split(",") if v.strip()]

    @app.template_filter("placement_color")
    def placement_color(value):
        """Return Bootstrap color class based on placement %."""
        if value is None:
            return "secondary"
        v = float(value)
        if v >= 90:
            return "success"
        elif v >= 75:
            return "primary"
        elif v >= 60:
            return "warning"
        return "danger"
