import httpx


class LicenseClient:
    def __init__(self, proxy_url: str):
        self._proxy_url = proxy_url.rstrip("/")

    def validate(self, license_key: str) -> dict:
        """Validate license key against proxy. Returns dict with 'valid', 'client_id', 'profile_url'."""
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{self._proxy_url}/auth/validate",
                json={"license_key": license_key},
            )
            resp.raise_for_status()
            return resp.json()
