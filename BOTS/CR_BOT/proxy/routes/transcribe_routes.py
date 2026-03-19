import asyncio
import httpx
import logging
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException

from proxy.config import GLADIA_API_KEY

router = APIRouter()
logger = logging.getLogger(__name__)

GLADIA_UPLOAD_URL = "https://api.gladia.io/v2/upload"
GLADIA_TRANSCRIPTION_URL = "https://api.gladia.io/v2/transcription"
POLL_INTERVAL = 5
MAX_POLL_ATTEMPTS = 120


async def relay_to_gladia(audio_bytes: bytes, filename: str, language: str = "fr") -> dict:
    """Upload audio to Gladia, start transcription, poll until done."""
    headers = {"x-gladia-key": GLADIA_API_KEY}

    async with httpx.AsyncClient(timeout=600) as client:
        upload_resp = await client.post(
            GLADIA_UPLOAD_URL,
            headers=headers,
            files={"audio": (filename, audio_bytes, "audio/mpeg")},
        )
        if upload_resp.status_code != 200:
            raise HTTPException(502, f"Gladia upload failed: {upload_resp.status_code}")

        audio_url = upload_resp.json().get("audio_url")

        trans_resp = await client.post(
            GLADIA_TRANSCRIPTION_URL,
            headers=headers,
            json={"audio_url": audio_url, "diarization": True, "language": language},
        )
        if trans_resp.status_code != 201:
            raise HTTPException(502, f"Gladia transcription failed: {trans_resp.status_code}")

        result_url = trans_resp.json().get("result_url")

        for _ in range(MAX_POLL_ATTEMPTS):
            poll_resp = await client.get(result_url, headers=headers)
            poll_data = poll_resp.json()
            status = poll_data.get("status")

            if status == "done":
                break
            elif status == "error":
                raise HTTPException(502, "Gladia processing error")

            await asyncio.sleep(POLL_INTERVAL)
        else:
            raise HTTPException(504, "Gladia transcription timed out")

    utterances = poll_data.get("result", {}).get("transcription", {}).get("utterances", [])
    segments = []
    full_text_parts = []

    for u in utterances:
        speaker = f"Speaker {u.get('speaker', '?')}"
        text = u.get("text", "").strip()
        segments.append({
            "start": u.get("start", 0.0),
            "end": u.get("end", 0.0),
            "speaker": speaker,
            "text": text,
        })
        full_text_parts.append(f"[{speaker}] {text}")

    duration = segments[-1]["end"] if segments else 0.0

    return {
        "segments": segments,
        "full_text": "\n".join(full_text_parts),
        "duration_seconds": duration,
    }


@router.post("/transcribe")
async def transcribe(
    request: Request,
    license_key: str = Form(...),
    audio: UploadFile = File(...),
    language: str = Form("fr"),
):
    mgr = request.app.state.license_mgr
    auth = mgr.validate(license_key)
    if not auth["valid"]:
        raise HTTPException(403, auth.get("reason", "Invalid license"))

    logger.info(f"Transcribe request from {auth['client_id']}: {audio.filename}")

    audio_bytes = await audio.read()
    result = await relay_to_gladia(audio_bytes, audio.filename or "audio.mp3", language)

    logger.info(f"Transcription complete for {auth['client_id']}: {result['duration_seconds']:.0f}s audio")
    return result
