import json
from pathlib import Path

_translations: dict[str, str] = {}
_current_lang: str = "en"
_UI_FRAMEWORK: str = "gtk"  # set to "qt" by commandeck_qt/app.py before set_language()


def set_ui_framework(name: str) -> None:
    """Call before set_language() to prevent GTK imports in non-GTK builds."""
    global _UI_FRAMEWORK
    _UI_FRAMEWORK = name

# lang code → display name in native script (shown in Preferences picker)
SUPPORTED_LANGUAGES: dict[str, str] = {
    "system": "System default",
    "en": "English",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "it": "Italiano",
    "ja": "日本語",
    "zh": "中文（简体）",
    "ko": "한국어",
    "ru": "Русский",
    "ar": "العربية",
    "hi": "हिन्दी",
    "pt": "Português (Brasil)",
}

_RTL_LANGS = {"ar"}


def set_language(lang: str) -> None:
    """Load the translation dict for *lang*. Falls back to English silently."""
    global _translations, _current_lang
    _current_lang = lang

    if lang in ("system", "en", ""):
        _translations = {}
        _set_text_direction(False)
        return

    path = Path(__file__).parent / "translations" / f"{lang}.json"
    try:
        with open(path, encoding="utf-8") as f:
            _translations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _translations = {}

    _set_text_direction(lang in _RTL_LANGS)


def _set_text_direction(rtl: bool) -> None:
    # No-op: the Qt UI sets layout direction itself via app.setLayoutDirection().
    # (Previously wired GTK's Gtk.Widget.set_default_direction; GTK was retired.)
    return


def _(text: str) -> str:
    """Return translated string, or the original English text if not found."""
    return _translations.get(text, text)
