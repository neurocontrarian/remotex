import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pro.license as lic


# ── helpers ───────────────────────────────────────────────────────────────────

def _write_license(tmp_dir: str, data: dict | str):
    p = Path(tmp_dir) / 'license.key'
    if isinstance(data, str):
        p.write_text(data)
    else:
        p.write_text(json.dumps(data))
    return p


def _patch_license_path(tmp_dir: str):
    """Context manager: redirect license/trial paths to tmp_dir."""
    tmp = Path(tmp_dir)
    return patch.multiple(
        'pro.license',
        _LICENSE_FILE=tmp / 'license.key',
        _TRIAL_FILE=tmp / '.trial',
        _CONFIG_DIR=tmp,
    )


def _write_trial(tmp_dir: str, started_at: str):
    p = Path(tmp_dir) / '.trial'
    p.write_text(json.dumps({'started_at': started_at, 'machine_id': 'test', 'version': 1}))
    return p


# ── is_pro_active ─────────────────────────────────────────────────────────────

def test_is_pro_active_first_run_seeds_trial():
    """Fresh install: no files → trial is seeded, is_pro_active returns True."""
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            with patch('pro.license._set_gsettings_trial_date'):
                assert lic.is_pro_active() is True
                assert (Path(tmp) / '.trial').exists()


def test_is_pro_active_no_file_expired_trial():
    """Post-trial, no license → is_pro_active returns False."""
    expired_start = (date.today() - timedelta(days=lic.TRIAL_DAYS + 1)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_trial(tmp, expired_start)
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=None):
                assert lic.is_pro_active() is False


def test_is_pro_active_lifetime():
    with tempfile.TemporaryDirectory() as tmp:
        _write_license(tmp, {'key': 'VALID-KEY', 'type': 'lifetime', 'expires': None})
        with _patch_license_path(tmp):
            assert lic.is_pro_active() is True


def test_is_pro_active_yearly_not_expired():
    future = (date.today() + timedelta(days=60)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_license(tmp, {'key': 'K', 'type': 'yearly', 'expires': future})
        with _patch_license_path(tmp):
            assert lic.is_pro_active() is True


def test_is_pro_active_yearly_expired_beyond_grace():
    past = (date.today() - timedelta(days=lic._GRACE_DAYS + 1)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_license(tmp, {'key': 'K', 'type': 'yearly', 'expires': past})
        with _patch_license_path(tmp):
            assert lic.is_pro_active() is False


def test_is_pro_active_yearly_within_grace_period():
    just_expired = (date.today() - timedelta(days=1)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_license(tmp, {'key': 'K', 'type': 'yearly', 'expires': just_expired})
        with _patch_license_path(tmp):
            assert lic.is_pro_active() is True  # still within grace


# ── _is_expired ───────────────────────────────────────────────────────────────

def test_is_expired_lifetime_always_false():
    assert lic._is_expired({'type': 'lifetime', 'expires': None}) is False


def test_is_expired_yearly_future():
    future = (date.today() + timedelta(days=10)).isoformat()
    assert lic._is_expired({'type': 'yearly', 'expires': future}) is False


def test_is_expired_yearly_past_grace():
    past = (date.today() - timedelta(days=lic._GRACE_DAYS + 1)).isoformat()
    assert lic._is_expired({'type': 'yearly', 'expires': past}) is True


# ── _compute_days_until ───────────────────────────────────────────────────────

def test_compute_days_until_none():
    assert lic._compute_days_until(None) is None


def test_compute_days_until_future():
    future = (date.today() + timedelta(days=30)).isoformat()
    assert lic._compute_days_until(future) == 30


def test_compute_days_until_past():
    past = (date.today() - timedelta(days=5)).isoformat()
    assert lic._compute_days_until(past) == -5


def test_compute_days_until_invalid():
    assert lic._compute_days_until("not-a-date") is None


# ── plain-text migration ──────────────────────────────────────────────────────

def test_plain_text_key_migrated_to_json():
    with tempfile.TemporaryDirectory() as tmp:
        _write_license(tmp, 'LEGACY-PLAIN-KEY')
        with _patch_license_path(tmp):
            data = lic._read_raw()
        assert data is not None
        assert data['key'] == 'LEGACY-PLAIN-KEY'
        assert data['type'] == 'lifetime'
        # file should now be valid JSON
        content = (Path(tmp) / 'license.key').read_text()
        parsed = json.loads(content)
        assert parsed['key'] == 'LEGACY-PLAIN-KEY'


# ── validate_license_online ───────────────────────────────────────────────────

def _ls_activate_response(key: str, instance_id: str = "inst-1",
                           expires_at=None, customer_email="buyer@example.com",
                           activation_limit=3, activation_usage=1) -> dict:
    return {
        "activated": True,
        "license_key": {
            "key": key,
            "expires_at": expires_at,
            "activation_limit": activation_limit,
            "activation_usage": activation_usage,
        },
        "instance": {"id": instance_id},
        "meta": {"customer_email": customer_email},
    }


def test_validate_license_online_success_lifetime():
    key = 'TESTKEY-LIFETIME-001'
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            with patch('pro.license._post', return_value=_ls_activate_response(key)):
                ok, kind, expires = lic.validate_license_online(key)
            assert ok is True
            assert kind == 'lifetime'
            assert expires is None
            data = json.loads((Path(tmp) / 'license.key').read_text())
            assert data['key'] == key
            assert data['instance_id'] == 'inst-1'


def test_validate_license_online_success_yearly():
    future = (date.today() + timedelta(days=365)).isoformat() + "T00:00:00Z"
    key = 'TESTKEY-YEARLY-0002'
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            with patch('pro.license._post', return_value=_ls_activate_response(key, expires_at=future)):
                ok, kind, expires = lic.validate_license_online(key)
            assert ok is True
            assert kind == 'yearly'
            assert expires is not None


def test_validate_license_online_network_error():
    key = 'TESTKEY-NETWORK-003'
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            with patch('pro.license._post', side_effect=Exception("timeout")):
                ok, kind, _ = lic.validate_license_online(key)
        assert ok is False
        assert kind == 'network_error'


def test_validate_license_online_limit_reached():
    import urllib.error
    key = 'TESTKEY-LIMIT-00004'
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            err = urllib.error.HTTPError(url='', code=422, msg='', hdrs=None, fp=None)
            with patch('pro.license._post', side_effect=err):
                ok, kind, _ = lic.validate_license_online(key)
        assert ok is False
        assert kind == 'limit_reached'


def test_validate_license_online_email_mismatch():
    key = 'TESTKEY-EMAIL-00005'
    resp = _ls_activate_response(key, customer_email="real@example.com")
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            with patch('pro.license._post', return_value=resp):
                ok, kind, _ = lic.validate_license_online(key, email='wrong@example.com')
        assert ok is False
        assert kind == 'email_mismatch'


def test_validate_license_online_short_key_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            ok, _, _ = lic.validate_license_online('X')
        assert ok is False


# ── Trial logic ───────────────────────────────────────────────────────────────

def test_trial_seed_on_first_call():
    """_is_trial_active() seeds the trial and returns True on first call (no files)."""
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            with patch('pro.license._set_gsettings_trial_date') as mock_gs:
                with patch('pro.license._get_gsettings_trial_date', return_value=None):
                    result = lic._is_trial_active()
        assert result is True
        trial_file = Path(tmp) / '.trial'
        assert trial_file.exists()
        data = json.loads(trial_file.read_text())
        assert data['started_at'] == date.today().isoformat()
        mock_gs.assert_called_once_with(date.today().isoformat())


def test_trial_active_within_period():
    started = (date.today() - timedelta(days=7)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_trial(tmp, started)
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=None):
                assert lic._is_trial_active() is True


def test_trial_active_day_zero():
    with tempfile.TemporaryDirectory() as tmp:
        _write_trial(tmp, date.today().isoformat())
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=None):
                assert lic._is_trial_active() is True


def test_trial_expired():
    expired_start = (date.today() - timedelta(days=lic.TRIAL_DAYS)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_trial(tmp, expired_start)
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=None):
                assert lic._is_trial_active() is False


def test_trial_not_seeded_when_license_exists():
    """If license.key exists (even without .trial), no trial is seeded."""
    with tempfile.TemporaryDirectory() as tmp:
        _write_license(tmp, {'key': 'SOME-KEY', 'type': 'lifetime', 'expires': None})
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=None):
                result = lic._is_trial_active()
        assert result is False
        assert not (Path(tmp) / '.trial').exists()


def test_license_overrides_trial():
    """Active license takes precedence; is_pro_active returns True via license path."""
    started = (date.today() - timedelta(days=7)).isoformat()
    future = (date.today() + timedelta(days=300)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_license(tmp, {'key': 'K', 'type': 'yearly', 'expires': future})
        _write_trial(tmp, started)
        with _patch_license_path(tmp):
            assert lic.is_pro_active() is True


def test_trial_antitamper_gsettings_wins():
    """Anti-tamper: GSettings date older than .trial file → uses GSettings date."""
    # Trial file backdated to look fresh, GSettings has the real older date
    fake_start = date.today().isoformat()
    real_start = (date.today() - timedelta(days=lic.TRIAL_DAYS)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_trial(tmp, fake_start)
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=real_start):
                result = lic._is_trial_active()
    assert result is False  # real_start is expired → trial expired


def test_get_trial_info_active():
    started = (date.today() - timedelta(days=5)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_trial(tmp, started)
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=None):
                info = lic.get_trial_info()
    assert info['active'] is True
    assert info['days_remaining'] == lic.TRIAL_DAYS - 5
    assert info['started_at'] == started


def test_get_trial_info_expired():
    expired_start = (date.today() - timedelta(days=lic.TRIAL_DAYS + 2)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        _write_trial(tmp, expired_start)
        with _patch_license_path(tmp):
            with patch('pro.license._get_gsettings_trial_date', return_value=None):
                info = lic.get_trial_info()
    assert info['active'] is False
    assert info['days_remaining'] == 0
    assert info['started_at'] == expired_start


def test_get_trial_info_no_file():
    with tempfile.TemporaryDirectory() as tmp:
        with _patch_license_path(tmp):
            # Don't patch _set_gsettings_trial_date to avoid side effects;
            # but suppress the file creation by patching _start_trial
            with patch('pro.license._start_trial'):
                info = lic.get_trial_info()
    assert info['active'] is False
    assert info['days_remaining'] is None
