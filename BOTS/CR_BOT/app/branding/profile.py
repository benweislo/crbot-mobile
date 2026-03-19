import json
import httpx
from pathlib import Path

from app.branding.models import BrandProfile


class ProfileManager:
    def __init__(self, cache_dir: Path):
        self._cache_dir = cache_dir

    def load_cached(self) -> BrandProfile | None:
        """Load profile from local cache. Returns None if not cached."""
        brand_path = self._cache_dir / "brand.json"
        if not brand_path.exists():
            return None

        data = json.loads(brand_path.read_text(encoding="utf-8"))
        profile = BrandProfile.from_dict(data)

        logo_path = self._cache_dir / "logo.b64"
        if logo_path.exists():
            profile.logo_b64 = logo_path.read_text(encoding="utf-8").strip()

        font_reg_path = self._cache_dir / "font_regular.b64"
        if font_reg_path.exists():
            profile.font_regular_b64 = font_reg_path.read_text(encoding="utf-8").strip()

        font_bold_path = self._cache_dir / "font_bold.b64"
        if font_bold_path.exists():
            profile.font_bold_b64 = font_bold_path.read_text(encoding="utf-8").strip()

        return profile

    def download_and_cache(self, profile_url: str) -> BrandProfile:
        """Download profile from remote URL and cache locally."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        with httpx.Client(timeout=30) as client:
            resp = client.get(f"{profile_url}/brand.json")
            resp.raise_for_status()
            brand_data = resp.json()
            (self._cache_dir / "brand.json").write_text(
                json.dumps(brand_data, indent=2), encoding="utf-8"
            )

            for asset in ["logo.b64", "font_regular.b64", "font_bold.b64"]:
                try:
                    asset_resp = client.get(f"{profile_url}/{asset}")
                    asset_resp.raise_for_status()
                    (self._cache_dir / asset).write_text(
                        asset_resp.text.strip(), encoding="utf-8"
                    )
                except httpx.HTTPError:
                    pass

        return self.load_cached()
