import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import build_prompt, generate_hashtags, validate_inputs


def test_validate_inputs_requires_topic():
    valid, message = validate_inputs("", ["Instagram"], "Professional", "short", True, "")
    assert valid is False
    assert "Please enter a topic" in message


def test_validate_inputs_requires_platform():
    valid, message = validate_inputs("AI App", [], "Professional", "short", True, "")
    assert valid is False
    assert "Please select at least one platform" in message


def test_build_prompt_includes_custom_instruction():
    prompt = build_prompt("AI App", ["Instagram"], "Professional", "medium", True, "Use a call to action")
    assert "AI App" in prompt
    assert "Use a call to action" in prompt


def test_generate_hashtags_contains_topic_and_platform_tags():
    tags = generate_hashtags("AI Productivity App", ["Instagram", "LinkedIn"])
    assert "#AiProductivityApp" in tags
    assert "#instagram" in tags
    assert "#linkedin" in tags
