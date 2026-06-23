"""Tests for script generator module."""
import json
import pytest
from unittest.mock import MagicMock, patch
from src.script_generator.gpt_writer import ScriptWriter


@pytest.fixture
def cfg():
    c = MagicMock()
    c.OPENAI_API_KEY = "sk-test"
    c.OPENAI_MODEL = "gpt-4o"
    c.MAX_VIDEO_DURATION = 600
    c.VIDEO_LANGUAGE = "en"
    return c


@pytest.fixture
def sample_script():
    return {
        "title": "Top 10 Python Libraries in 2025",
        "narration": "Hey everyone, welcome back! Today we're covering...",
        "chapters": [{"time": "0:00", "title": "Intro"}, {"time": "1:30", "title": "Libraries"}],
        "hook": "Hey everyone, welcome back!",
        "cta": "Hit subscribe and the bell icon!",
        "description": "In this video we cover the top Python libraries...",
        "tags": ["python", "programming", "tutorial"],
        "thumbnail_text": "Top Python Libraries 2025",
        "topic": "python libraries",
    }


def test_script_has_required_keys(sample_script):
    required = ["title", "narration", "chapters", "hook", "cta", "description", "tags"]
    for key in required:
        assert key in sample_script, f"Missing key: {key}"


def test_title_max_length(sample_script):
    assert len(sample_script["title"]) <= 70


def test_tags_is_list(sample_script):
    assert isinstance(sample_script["tags"], list)
    assert len(sample_script["tags"]) > 0


@patch("src.script_generator.gpt_writer.OpenAI")
def test_generate_calls_openai(mock_openai, cfg, sample_script):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(sample_script)

    writer = ScriptWriter(cfg)
    result = writer.generate("python libraries")

    mock_client.chat.completions.create.assert_called_once()
    assert result["title"] == sample_script["title"]
