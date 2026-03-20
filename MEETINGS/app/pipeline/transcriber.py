import time
from pathlib import Path
import requests

GLADIA_UPLOAD_URL = "https://api.gladia.io/v2/upload"
GLADIA_TRANSCRIPTION_URL = "https://api.gladia.io/v2/transcription"


class GladiaTranscriber:
    def __init__(self, api_key: str, language: str = "fr", timeout: int = 600):
        self._api_key = api_key
        self._language = language
        self._timeout = timeout

    def transcribe(self, audio_path: Path) -> dict:
        headers = {"x-gladia-key": self._api_key}

        with open(audio_path, "rb") as f:
            files = {"audio": (audio_path.name, f, "audio/mpeg")}
            resp = requests.post(GLADIA_UPLOAD_URL, headers=headers, files=files, timeout=self._timeout)

        if resp.status_code != 200:
            raise RuntimeError(f"Upload failed: {resp.status_code} - {resp.text}")

        audio_url = resp.json()["audio_url"]
        payload = {"audio_url": audio_url, "diarization": True, "language": self._language}
        resp = requests.post(GLADIA_TRANSCRIPTION_URL, headers=headers, json=payload, timeout=60)

        if resp.status_code != 201:
            raise RuntimeError(f"Transcription start failed: {resp.status_code} - {resp.text}")

        result_url = resp.json()["result_url"]
        start_time = time.time()
        while True:
            if time.time() - start_time > self._timeout:
                raise RuntimeError(f"Transcription timed out after {self._timeout}s")
            poll = requests.get(result_url, headers=headers, timeout=30)
            data = poll.json()
            status = data.get("status")
            if status == "done":
                break
            elif status == "error":
                raise RuntimeError("Gladia transcription processing failed")
            time.sleep(5)

        utterances = data.get("result", {}).get("transcription", {}).get("utterances", [])
        segments = []
        full_text_parts = []
        for u in utterances:
            speaker = f"Speaker {u.get('speaker', '?')}"
            text = u.get("text", "").strip()
            formatted = f"[{speaker}] {text}"
            segments.append({"start": u.get("start", 0.0), "end": u.get("end", 0.0), "text": formatted})
            full_text_parts.append(formatted)

        duration = segments[-1]["end"] if segments else 0.0
        return {"full_text": " ".join(full_text_parts), "segments": segments, "duration": duration}
