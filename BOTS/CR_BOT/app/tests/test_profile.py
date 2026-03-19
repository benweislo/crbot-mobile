import json
import pytest
from pathlib import Path

from app.branding.models import BrandProfile
from app.branding.profile import ProfileManager


class TestBrandProfile:
    def test_from_dict(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        assert profile.company_name == "Test Corp"
        assert profile.primary_color == "#2563EB"

    def test_defaults_for_missing_fields(self):
        minimal = {"company_name": "Minimal"}
        profile = BrandProfile.from_dict(minimal)
        assert profile.primary_color == "#6e3ea8"
        assert profile.language == "fr"


class TestProfileManager:
    def test_load_from_local_cache(self, tmp_dir, sample_brand):
        cache_dir = tmp_dir / ".crbot" / "profile"
        cache_dir.mkdir(parents=True)
        (cache_dir / "brand.json").write_text(json.dumps(sample_brand))
        (cache_dir / "logo.b64").write_text("FAKELOGO")
        (cache_dir / "font_regular.b64").write_text("FAKEFONT")
        (cache_dir / "font_bold.b64").write_text("FAKEFONTBOLD")

        mgr = ProfileManager(cache_dir=cache_dir)
        profile = mgr.load_cached()
        assert profile is not None
        assert profile.company_name == "Test Corp"
        assert profile.logo_b64 == "FAKELOGO"

    def test_no_cache_returns_none(self, tmp_dir):
        mgr = ProfileManager(cache_dir=tmp_dir / "nonexistent")
        assert mgr.load_cached() is None
