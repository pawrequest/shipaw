"""
Style constants and shared UI helpers for the NiceGUI frontend.

Import this module (as `from shipaw.nicegui_ui import theme`) rather than
scattering raw class/prop strings throughout page code.
"""

from __future__ import annotations

from nicegui import ui

from shipaw.models.alerts import AlertType, Alerts

# ── Global CSS ────────────────────────────────────────────────────────────────

PAGE_CSS = """
body { background-color: #9da8ab !important; font-family: Roboto, sans-serif; }
.ship-card {
    border-radius: 1rem !important;
    border: 2px solid #333 !important;
    background: rgba(108,117,125,0.42) !important;
}
.result-success { background: rgba(19,117,27,0.5); border-radius: 1rem; }
.result-fail    { background: rgba(255,0,0,0.23);  border-radius: 1rem; }
.alert-ERROR        { background: rgba(255,0,0,0.23);    border-radius:.5rem; padding:.4rem .8rem; }
.alert-WARNING      { background: rgba(255,193,7,0.48);  border-radius:.5rem; padding:.4rem .8rem; }
.alert-NOTIFICATION { background: cornflowerblue;        border-radius:.5rem; padding:.4rem .8rem; color:#fff; }
"""

# ── Reusable class / prop strings ─────────────────────────────────────────────

CARD = 'w-full q-pa-md ship-card'  # full-width section card
CARD_SM = 'col-auto q-pa-sm ship-card'  # compact info card in summary row
ROW = 'w-full q-gutter-md'  # standard horizontal row
CENTER_ROW = 'w-full justify-center q-gutter-md q-mt-sm'

INPUT_PROPS = 'outlined dense'
BTN_PRIMARY = 'color=blue-8'
BTN_POSITIVE = 'color=positive'
BTN_FLAT = 'flat color=blue-8'


# ── Helpers ───────────────────────────────────────────────────────────────────


def apply_page_styles() -> None:
    """Inject the global CSS into the current page."""
    ui.add_css(PAGE_CSS)


def show_alerts(alerts: Alerts) -> None:
    """Display each alert as a NiceGUI toast notification."""
    for alert in alerts.alert:
        if alert.type == AlertType.ERROR:
            ui.notify(alert.message, type='negative', timeout=0)
        elif alert.type == AlertType.WARNING:
            ui.notify(alert.message, type='warning', timeout=6000)
        else:
            ui.notify(alert.message, type='info', timeout=4000)


def render_alerts_inline(alerts: Alerts) -> None:
    """Render alert messages as coloured inline labels (for results page)."""
    for alert in alerts.alert:
        ui.label(alert.message).classes(f'alert-{alert.type.value} w-full q-mt-xs')
