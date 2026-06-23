"""Tests for SEO metadata generator."""
import pytest
from unittest.mock import MagicMock
from src.uploader.seo_generator import SEOGenerator


@pytest.fixture
def cfg():
    c = MagicMock()
    c.VIDEO_LANGUAGE = "en"
    return c


@pytest.fixture
def sample_script():
    return {
        "title": "How to Learn Python Fast",
        "description": "A comprehensive guide to learning Python quickly in 2025.",
        "tags": ["python", "learn python", "coding for beginners"],
        "chapters": [{"time": "0:00", "title": "Intro"}, {"time": "2:00", "title": "Setup"}],
        "narration": "Welcome to the video!",
    }


def test_title_cleaned(cfg, sample_script):
    seo = SEOGenerator(cfg)
    meta = seo.generate(sample_script, "python tutorial")
    assert len(meta["title"]) <= 70
    assert "<" not in meta["title"]


def test_tags_under_500_chars(cfg, sample_script):
    seo = SEOGenerator(cfg)
    meta = seo.generate(sample_script, "python tutorial")
    total_chars = sum(len(t) for t in meta["tags"])
    assert total_chars <= 500


def test_description_contains_chapters(cfg, sample_script):
    seo = SEOGenerator(cfg)
    meta = seo.generate(sample_script, "python tutorial")
    assert "CHAPTERS" in meta["description"]
    assert "0:00" in meta["description"]


def test_description_max_length(cfg, sample_script):
    seo = SEOGenerator(cfg)
    meta = seo.generate(sample_script, "python tutorial")
    assert len(meta["description"]) <= 5000
