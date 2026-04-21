import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import i18n
from i18n import _, set_language, SUPPORTED_LANGUAGES


# ── set_language ──────────────────────────────────────────────────────────────

def test_set_language_english_clears_translations():
    set_language("en")
    assert i18n._translations == {}


def test_set_language_system_clears_translations():
    set_language("system")
    assert i18n._translations == {}


def test_set_language_empty_string_clears_translations():
    set_language("")
    assert i18n._translations == {}


def test_set_language_french_loads_dict():
    set_language("fr")
    assert len(i18n._translations) > 0


def test_set_language_unknown_code_falls_back_gracefully():
    set_language("xx")  # no such file — must not raise
    assert i18n._translations == {}


def test_set_language_updates_current_lang():
    set_language("de")
    assert i18n._current_lang == "de"


# ── _() translation function ──────────────────────────────────────────────────

def test_translate_known_key_french():
    set_language("fr")
    # "Preferences" is always in the French translation file
    translated = _("Preferences")
    assert translated != "Preferences"  # must differ from English original
    assert len(translated) > 0


def test_translate_unknown_key_returns_original():
    set_language("fr")
    result = _("this_key_does_not_exist_in_any_translation")
    assert result == "this_key_does_not_exist_in_any_translation"


def test_translate_falls_back_to_english_after_unknown_lang():
    set_language("xx")
    result = _("Preferences")
    assert result == "Preferences"  # returned as-is (no translation loaded)


def test_translate_english_returns_original():
    set_language("en")
    result = _("Preferences")
    assert result == "Preferences"


# ── SUPPORTED_LANGUAGES ───────────────────────────────────────────────────────

def test_supported_languages_contains_system():
    assert "system" in SUPPORTED_LANGUAGES


def test_supported_languages_contains_english():
    assert "en" in SUPPORTED_LANGUAGES


def test_supported_languages_all_have_display_names():
    for code, name in SUPPORTED_LANGUAGES.items():
        assert isinstance(name, str) and len(name) > 0, f"Empty display name for {code}"


# ── isolation: restore English after each test ────────────────────────────────

def teardown_module(module):
    set_language("en")
