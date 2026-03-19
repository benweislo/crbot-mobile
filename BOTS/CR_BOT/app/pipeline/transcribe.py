import httpx
from pathlib import Path


class TranscribeClient:
    def __init__(self, proxy_url: str, license_key: str):
        self._proxy_url = proxy_url.rstrip("/")
        self._license_key = license_key

    def transcribe(self, audio_path: Path, language: str = "fr") -> dict:
        """Send audio to proxy for transcription. Returns transcript dict."""
        with httpx.Client(timeout=600) as client:
            with open(audio_path, "rb") as f:
                resp = client.post(
                    f"{self._proxy_url}/transcribe",
                    data={"license_key": self._license_key, "language": language},
                    files={"audio": (audio_path.name, f, "audio/mpeg")},
                )
            resp.raise_for_status()
            return resp.json()
