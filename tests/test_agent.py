import pytest
from unittest.mock import patch, MagicMock
from docvert.agent.refiner import LLMRefiner


@pytest.fixture
def refiner() -> LLMRefiner:
    return LLMRefiner(api_key="fake-key")


def test_refiner_initialization(refiner: LLMRefiner) -> None:
    """Test that the LLMRefiner initializes correctly with an API key."""
    assert refiner.client.api_key == "fake-key"
    assert refiner.model == "gpt-4o-mini"


@patch("docvert.agent.refiner.OpenAI")
def test_refine_markdown_success(mock_openai_class: MagicMock) -> None:
    """Test that refine_markdown calls the LLM and returns the expected result."""
    # Setup mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "# Refined Markdown"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    refiner = LLMRefiner(api_key="test-key")
    # Manually inject the mocked client since we mocked the class
    refiner.client = mock_client

    original = "raw markdown"
    result = refiner.refine_markdown(original)

    assert result == "# Refined Markdown"
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert "raw markdown" in call_kwargs["messages"][1]["content"]


@pytest.mark.live
def test_refine_markdown_live() -> None:
    """Live test that requires OPENAI_API_KEY environment variable."""
    import os

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    refiner = LLMRefiner(api_key=api_key)
    original = "1. heading\n\nsome txt"
    result = refiner.refine_markdown(original)

    assert result is not None
    assert len(result) > 0


def test_refiner_missing_openai() -> None:
    """Test that ImportError is raised if openai is not available."""
    import sys
    import importlib
    import docvert.agent.refiner

    # Temporarily remove openai from sys.modules to trigger ImportError
    original_openai = sys.modules.get("openai")
    sys.modules["openai"] = None  # type: ignore[assignment]

    try:
        importlib.reload(docvert.agent.refiner)
        with pytest.raises(ImportError, match="The 'openai' package is required"):
            docvert.agent.refiner.LLMRefiner(api_key="test-key")
    finally:
        # Restore original state
        if original_openai is not None:
            sys.modules["openai"] = original_openai
        else:
            del sys.modules["openai"]
        importlib.reload(docvert.agent.refiner)


@patch("docvert.agent.refiner.OpenAI")
def test_refine_markdown_exception(mock_openai_class: MagicMock) -> None:
    """Test that refine_markdown handles exceptions gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API error")
    mock_openai_class.return_value = mock_client

    refiner = LLMRefiner(api_key="test-key")
    refiner.client = mock_client

    original = "raw markdown"
    result = refiner.refine_markdown(original)

    # Should return original text on failure
    assert result == "raw markdown"
