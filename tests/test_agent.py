import pytest
from unittest.mock import patch, MagicMock
from docvert.agent.refiner import LLMRefiner


@pytest.fixture
def refiner() -> LLMRefiner:
    return LLMRefiner(api_key="fake-key")


def test_refiner_initialization(refiner: LLMRefiner) -> None:
    """Test that the LLMRefiner initializes correctly with an API key."""
    assert refiner.api_key == "fake-key"
    assert refiner.model == "gpt-4o-mini"
    assert refiner.base_url is None


def test_refiner_initialization_with_base_url() -> None:
    """Test that the LLMRefiner initializes correctly with a custom base URL."""
    refiner = LLMRefiner(api_key="fake-key", base_url="http://localhost:11434/v1")
    assert refiner.api_key == "fake-key"
    assert refiner.base_url == "http://localhost:11434/v1"


@patch("docvert.agent.refiner.completion")
def test_refine_markdown_success(mock_completion: MagicMock) -> None:
    """Test that refine_markdown calls the LLM and returns the expected result."""
    # Setup mock
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "# Refined Markdown"
    mock_completion.return_value = mock_response

    refiner = LLMRefiner(api_key="test-key")

    original = "raw markdown"
    result = refiner.refine_markdown(original)

    assert result == "# Refined Markdown"
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["api_key"] == "test-key"
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


def test_refiner_missing_litellm() -> None:
    """Test that ImportError is raised if litellm is not available."""
    import sys
    import importlib
    import docvert.agent.refiner

    # Temporarily remove litellm from sys.modules to trigger ImportError
    original_litellm = sys.modules.get("litellm")
    sys.modules["litellm"] = None  # type: ignore[assignment]

    try:
        importlib.reload(docvert.agent.refiner)
        with pytest.raises(ImportError, match="The 'litellm' package is required"):
            docvert.agent.refiner.LLMRefiner(api_key="test-key")
    finally:
        # Restore original state
        if original_litellm is not None:
            sys.modules["litellm"] = original_litellm
        else:
            if "litellm" in sys.modules:
                del sys.modules["litellm"]
        importlib.reload(docvert.agent.refiner)


@patch("docvert.agent.refiner.completion")
def test_refine_markdown_exception(mock_completion: MagicMock) -> None:
    """Test that refine_markdown handles exceptions gracefully."""
    mock_completion.side_effect = Exception("API error")

    refiner = LLMRefiner(api_key="test-key")

    original = "raw markdown"
    result = refiner.refine_markdown(original)

    # Should return original text on failure
    assert result == "raw markdown"

@patch("docvert.agent.refiner.completion")
def test_refine_markdown_with_base_url(mock_completion: MagicMock) -> None:
    """Test that refine_markdown includes base_url when provided."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "# Refined Markdown"
    mock_completion.return_value = mock_response

    refiner = LLMRefiner(api_key="test-key", base_url="http://localhost")
    refiner.refine_markdown("test")
    
    mock_completion.assert_called_once()
    assert mock_completion.call_args.kwargs.get("base_url") == "http://localhost"
