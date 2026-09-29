"""
Style constants, CSS custom properties, and shared UI helpers for the NiceGUI frontend.

Four built-in themes are available and can be switched live via `theme_switcher()`.
Import as `from shipaw.nicegui_ui import theme` — never scatter raw class strings
through page code.
"""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import app as _ng_app
from nicegui import ui

from shipaw.models.alerts import AlertType, Alerts

# ── Theme registry ────────────────────────────────────────────────────────────

DEFAULT_THEME = 'Steel Blue'


@dataclass
class ThemeConfig:
    key: str  # appended to body class: ``body.theme-{key}``
    label: str  # display name shown in the selector
    dark: bool = False  # enable Quasar dark-mode palette


THEMES: dict[str, ThemeConfig] = {
    'Steel Blue': ThemeConfig(
        key='steel',
        label='🔵 Steel Blue',
    ),
    'Dark Slate': ThemeConfig(
        key='dark',
        label='🌑 Dark Slate',
        dark=True,
    ),
    'Ocean Teal': ThemeConfig(
        key='teal',
        label='🌊 Ocean Teal',
    ),
    'Warm Parchment': ThemeConfig(
        key='parchment',
        label='📜 Warm Parchment',
    ),
}

# ── Global CSS (injected once per page) ───────────────────────────────────────

PAGE_CSS = """
/* ── Per-theme custom properties ─────────────────────────────────────── */
body.theme-steel {
    --bg:              #9da8ab;
    --card-bg:         rgba(108,117,125,0.45);
    --card-border:     #445566;
    --card-shadow:     0 2px 12px rgba(0,0,0,0.18);
    --header-bg:       #455a64;
    --header-text:     #eceff1;
    --text-primary:    #1c2833;
    --text-muted:      #546e7a;
    --btn-primary-bg:  #1565c0;
    --btn-primary-txt: #fff;
    --btn-positive-bg: #2e7d32;
    --btn-flat-color:  #1565c0;
    --success-bg:      rgba(27,144,30,0.32);
    --fail-bg:         rgba(198,40,40,0.18);
    --alert-error-bg:  rgba(198,40,40,0.22);
    --alert-warn-bg:   rgba(255,193,7,0.42);
    --alert-info-bg:   #6495ed;
    --alert-info-txt:  #fff;
    --sep-color:       rgba(0,0,0,0.15);
}
body.theme-dark {
    --bg:              #181c24;
    --card-bg:         rgba(26,32,46,0.96);
    --card-border:     #364060;
    --card-shadow:     0 2px 18px rgba(0,0,0,0.55);
    --header-bg:       #0e1117;
    --header-text:     #b8cee0;
    --text-primary:    #d8e6f0;
    --text-muted:      #7090a8;
    --btn-primary-bg:  #2563ab;
    --btn-primary-txt: #e8f0fe;
    --btn-positive-bg: #1a7245;
    --btn-flat-color:  #5a9fd4;
    --success-bg:      rgba(22,100,48,0.48);
    --fail-bg:         rgba(155,30,30,0.38);
    --alert-error-bg:  rgba(175,30,30,0.42);
    --alert-warn-bg:   rgba(170,110,0,0.42);
    --alert-info-bg:   rgba(40,100,160,0.58);
    --alert-info-txt:  #d8e6f0;
    --sep-color:       rgba(255,255,255,0.1);
}
body.theme-teal {
    --bg:              #ddf0ee;
    --card-bg:         rgba(174,222,216,0.52);
    --card-border:     #00897b;
    --card-shadow:     0 2px 10px rgba(0,100,88,0.14);
    --header-bg:       #00796b;
    --header-text:     #e0f2f1;
    --text-primary:    #00302a;
    --text-muted:      #2e7066;
    --btn-primary-bg:  #00796b;
    --btn-primary-txt: #fff;
    --btn-positive-bg: #388e3c;
    --btn-flat-color:  #00796b;
    --success-bg:      rgba(56,142,60,0.25);
    --fail-bg:         rgba(196,50,50,0.16);
    --alert-error-bg:  rgba(196,50,50,0.22);
    --alert-warn-bg:   rgba(230,110,0,0.26);
    --alert-info-bg:   rgba(0,121,107,0.48);
    --alert-info-txt:  #fff;
    --sep-color:       rgba(0,100,90,0.22);
}
body.theme-parchment {
    --bg:              #f0e8d5;
    --card-bg:         rgba(238,226,200,0.78);
    --card-border:     #b89458;
    --card-shadow:     0 2px 10px rgba(110,80,30,0.14);
    --header-bg:       #7d5a35;
    --header-text:     #fdf5e6;
    --text-primary:    #3a280d;
    --text-muted:      #7a6040;
    --btn-primary-bg:  #8b5e3c;
    --btn-primary-txt: #fdf5e6;
    --btn-positive-bg: #5c8a3e;
    --btn-flat-color:  #8b5e3c;
    --success-bg:      rgba(92,138,62,0.26);
    --fail-bg:         rgba(175,50,50,0.16);
    --alert-error-bg:  rgba(175,50,50,0.22);
    --alert-warn-bg:   rgba(185,110,0,0.28);
    --alert-info-bg:   rgba(90,110,180,0.38);
    --alert-info-txt:  #fff;
    --sep-color:       rgba(110,80,30,0.2);
}

/* ── Shared rules (driven by CSS vars) ────────────────────────────────── */
body {
    background-color: var(--bg) !important;
    color: var(--text-primary) !important;
    font-family: Roboto, sans-serif;
    transition: background-color 0.35s ease, color 0.35s ease;
}

/* Header */
.ship-header {
    background: var(--header-bg) !important;
    color: var(--header-text) !important;
    border-bottom: 1px solid rgba(0,0,0,0.2);
}
.ship-header .q-btn { color: var(--header-text) !important; }

/* Cards */
.ship-card {
    border-radius: 1rem !important;
    border: 2px solid var(--card-border) !important;
    background: var(--card-bg) !important;
    box-shadow: var(--card-shadow) !important;
    transition: background 0.3s ease, border-color 0.3s ease;
}
.ship-card.q-card { background: var(--card-bg) !important; }

/* Buttons — override Quasar's colour-prop colouring */
.q-btn.ship-btn-primary {
    background: var(--btn-primary-bg) !important;
    color: var(--btn-primary-txt) !important;
    border-radius: .5rem;
}
.q-btn.ship-btn-primary:hover { filter: brightness(1.12); }

.q-btn.ship-btn-positive {
    background: var(--btn-positive-bg) !important;
    color: #fff !important;
    border-radius: .5rem;
}
.q-btn.ship-btn-positive:hover { filter: brightness(1.12); }

.q-btn.ship-btn-flat {
    background: transparent !important;
    color: var(--btn-flat-color) !important;
}
.q-btn.ship-btn-flat:hover { background: rgba(0,0,0,0.07) !important; }

/* Text helpers */
.ship-muted { color: var(--text-muted) !important; }
.ship-separator { border-color: var(--sep-color) !important; opacity: 1 !important; }

/* Inputs — tint label and native text */
.ship-input .q-field__label  { color: var(--text-muted) !important; }
.ship-input .q-field__native { color: var(--text-primary) !important; }

/* Results */
.result-success { background: var(--success-bg); border-radius: 1rem; }
.result-fail    { background: var(--fail-bg);    border-radius: 1rem; }

/* Inline alert labels */
.alert-ERROR        { background: var(--alert-error-bg); border-radius:.5rem; padding:.4rem .8rem; }
.alert-WARNING      { background: var(--alert-warn-bg);  border-radius:.5rem; padding:.4rem .8rem; }
.alert-NOTIFICATION { background: var(--alert-info-bg);  border-radius:.5rem; padding:.4rem .8rem; color: var(--alert-info-txt); }

/* Theme-switcher select — keep readable in header */
.ship-theme-select .q-field__native,
.ship-theme-select .q-field__label { color: var(--header-text) !important; }
.ship-theme-select .q-field__control { border-color: var(--header-text) !important; }
"""

# ── Token constants (used by page code) ───────────────────────────────────────

# Layout
CARD = 'w-full q-pa-md ship-card'
CARD_SM = 'col-auto q-pa-sm ship-card'
ROW = 'w-full q-gutter-md'
CENTER_ROW = 'w-full justify-center q-gutter-md q-mt-sm'
HEADER = 'ship-header row items-center q-py-sm q-px-md w-full'

# Typography helpers
SUBTITLE = 'text-subtitle2 text-weight-bold q-mb-xs'
SUBTITLE_LG = 'text-subtitle1 q-px-xl q-py-sm'

# Inputs
INPUT_PROPS = 'outlined dense'
INPUT_CLASS = 'ship-input'

# Buttons  ← these are CSS CLASS strings, use with .classes() not .props()
BTN_PRIMARY = 'ship-btn-primary'
BTN_POSITIVE = 'ship-btn-positive'
BTN_FLAT = 'ship-btn-flat'

# Expansions / section containers
EXPANSION = 'w-full q-mt-sm ship-card'


# ── Internal helpers ──────────────────────────────────────────────────────────


def _active_theme_name() -> str:
    try:
        return _ng_app.storage.general.get('shipaw_theme', DEFAULT_THEME)
    except Exception:
        return DEFAULT_THEME


def _apply_theme_js(name: str) -> None:
    cfg = THEMES.get(name, THEMES[DEFAULT_THEME])
    ui.run_javascript(
        f"document.body.className = 'theme-{cfg.key}';Quasar.Dark.set({'true' if cfg.dark else 'false'});"
    )


# ── Public API ────────────────────────────────────────────────────────────────


def apply_page_styles() -> None:
    """Inject CSS and activate the stored/default theme. Call once per page."""
    ui.add_css(PAGE_CSS)
    name = _active_theme_name()
    _apply_theme_js(name)


def theme_switcher() -> None:
    """
    Render a compact theme-selector dropdown, intended for the app header.
    Switching theme updates CSS custom properties instantly (no page reload).
    """
    options = {k: v.label for k, v in THEMES.items()}
    current = _active_theme_name()

    def _on_change(e) -> None:
        name: str = e.value
        _ng_app.storage.general['shipaw_theme'] = name
        _apply_theme_js(name)

    (
        ui.select(options, value=current, on_change=_on_change)
        .props('dense outlined dark')
        .classes('ship-theme-select q-ml-md')
        .style('min-width: 165px;')
        .tooltip('Switch colour theme')
    )


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
    """Render alert messages as coloured inline labels (results page)."""
    for alert in alerts.alert:
        ui.label(alert.message).classes(f'alert-{alert.type.value} w-full q-mt-xs')
