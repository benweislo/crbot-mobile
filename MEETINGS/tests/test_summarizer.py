from unittest.mock import patch, MagicMock
from app.pipeline.summarizer import ClaudeSummarizer


def test_summarize_calls_claude_with_correct_args():
    summarizer = ClaudeSummarizer(system_prompt="Test prompt")
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "COMPTE RENDU DE RÉUNION\nTest summary"
    mock_result.stderr = ""

    with patch("app.pipeline.summarizer.subprocess.run", return_value=mock_result) as mock_run:
        result = summarizer.summarize("transcript text here")

    cmd = mock_run.call_args[0][0]
    assert "claude" in cmd[0]
    assert "-p" in cmd
    assert "--system-prompt" in cmd
    assert result == "COMPTE RENDU DE RÉUNION\nTest summary"


def test_summarize_passes_transcript_as_stdin():
    summarizer = ClaudeSummarizer(system_prompt="Test")
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Summary"
    mock_result.stderr = ""

    with patch("app.pipeline.summarizer.subprocess.run", return_value=mock_result) as mock_run:
        summarizer.summarize("My transcript content")

    kwargs = mock_run.call_args[1]
    assert kwargs["input"] == "My transcript content"


def test_summarize_raises_on_failure():
    summarizer = ClaudeSummarizer(system_prompt="Test")
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: claude not found"

    with patch("app.pipeline.summarizer.subprocess.run", return_value=mock_result):
        try:
            summarizer.summarize("text")
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "claude" in str(e).lower() or "Error" in str(e)


def test_summarize_raises_on_timeout():
    summarizer = ClaudeSummarizer(system_prompt="Test", timeout=1)
    import subprocess
    with patch("app.pipeline.summarizer.subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 1)):
        try:
            summarizer.summarize("text")
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "timeout" in str(e).lower()
