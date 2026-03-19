import httpx


class SummarizeClient:
    def __init__(self, proxy_url: str, license_key: str):
        self._proxy_url = proxy_url.rstrip("/")
        self._license_key = license_key

    def summarize(self, transcript: str, context: str = "", language: str = "fr") -> str:
        """Send transcript to proxy for summarization. Returns CR text."""
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{self._proxy_url}/summarize",
                json={
                    "license_key": self._license_key,
                    "transcript": transcript,
                    "context": context,
                    "language": language,
                },
            )
            resp.raise_for_status()
            return resp.json()["summary"]
