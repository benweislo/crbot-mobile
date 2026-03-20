import subprocess


class ClaudeSummarizer:
    def __init__(self, system_prompt: str, timeout: int = 600):
        self._system_prompt = system_prompt
        self._timeout = timeout

    def summarize(self, transcript: str) -> str:
        cmd = [
            "claude", "-p",
            "--system-prompt", self._system_prompt,
            "Voici la transcription complète de la réunion :",
        ]
        try:
            result = subprocess.run(
                cmd, input=transcript, capture_output=True, text=True, timeout=self._timeout,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Claude summarization timeout after {self._timeout}s")

        if result.returncode != 0:
            raise RuntimeError(f"Claude failed (exit {result.returncode}): {result.stderr}")
        return result.stdout.strip()
