import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def tmp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_brand():
    """Sample brand profile dict."""
    return {
        "company_name": "Test Corp",
        "primary_color": "#2563EB",
        "secondary_color": "#7C3AED",
        "background_color": "#0A0A0F",
        "text_color": "#E5E5E5",
        "font_family": "TestFont",
        "footer_text": "Test Corp — CR auto",
        "language": "fr",
        "context": "Test Corp est une agence digitale.",
        "cr_sections": {"summary": True, "detailed": True}
    }
