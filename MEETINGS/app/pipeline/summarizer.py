import os
import shutil
import subprocess


def _find_claude() -> str:
    """Find claude CLI — check common paths on Windows."""
    # Try shutil.which first (works if PATH is set)
    found = shutil.which("claude")
    if found:
        return found
    # Common npm global install locations on Windows
    for candidate in [
        os.path.expandvars(r"%APPDATA%\npm\claude.cmd"),
        os.path.expandvars(r"%APPDATA%\npm\claude"),
        r"C:\Users\User\AppData\Roaming\npm\claude.cmd",
    ]:
        if os.path.exists(candidate):
            return candidate
    return "claude"  # fallback


class ClaudeSummarizer:
    def __init__(self, system_prompt: str, timeout: int = 600):
        self._system_prompt = system_prompt
        self._timeout = timeout

    def summarize(self, transcript: str) -> str:
        claude_path = _find_claude()
        cmd = [
            claude_path, "-p",
            "--system-prompt", self._system_prompt,
            "Voici la transcription complète de la réunion :",
        ]
        try:
            result = subprocess.run(
                cmd, input=transcript, capture_output=True, text=True, timeout=self._timeout,
                shell=(claude_path.endswith(".cmd")),
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Claude summarization timeout after {self._timeout}s")

        if result.returncode != 0:
            raise RuntimeError(f"Claude failed (exit {result.returncode}): {result.stderr}")
        return result.stdout.strip()
