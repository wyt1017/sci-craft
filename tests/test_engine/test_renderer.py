"""Tests for engine/renderer.py - Jinja2 template rendering."""

from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from engine.renderer import Renderer, flatten_config


def test_flatten_config():
    """Test flatten_config function."""
    config = {
        "name": "Nature",
        "writing": {
            "max_sentence_words": 25,
            "tense": "present",
        },
        "nested": {
            "level1": {
                "level2": "value",
            },
        },
    }

    flat = flatten_config(config)

    assert flat["name"] == "Nature"
    assert flat["writing.max_sentence_words"] == 25
    assert flat["writing.tense"] == "present"
    assert flat["nested.level1.level2"] == "value"


def test_renderer_init():
    """Test Renderer initialization."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        renderer = Renderer(core_dir)

        assert renderer.core_dir == core_dir
        assert renderer.journals_dir == core_dir / "journals"
        assert renderer.rules_dir == core_dir / "rules"


def test_load_journal_config():
    """Test journal config loading with base config merge."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        journals_dir = core_dir / "journals"
        journals_dir.mkdir(parents=True, exist_ok=True)

        # Write base config
        base_config = {
            "name": "Base",
            "writing": {
                "max_sentence_words": 30,
            },
        }
        with open(journals_dir / "_base.yaml", "w") as f:
            yaml.dump(base_config, f)

        # Write journal config
        journal_config = {
            "name": "Nature",
            "writing": {
                "max_sentence_words": 25,
                "tense": "present",
            },
        }
        with open(journals_dir / "nature.yaml", "w") as f:
            yaml.dump(journal_config, f)

        renderer = Renderer(core_dir)
        config = renderer.load_journal_config("nature")

        # Journal config should override base
        assert config["name"] == "Nature"
        assert config["writing"]["max_sentence_words"] == 25
        assert config["writing"]["tense"] == "present"


def test_render_simple_template():
    """Test simple template rendering."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        journals_dir = core_dir / "journals"
        journals_dir.mkdir(parents=True, exist_ok=True)

        # Write journal config
        journal_config = {"name": "Nature", "max_words": 100}
        with open(journals_dir / "nature.yaml", "w") as f:
            yaml.dump(journal_config, f)

        renderer = Renderer(core_dir)

        template_content = "Journal: {{name}}, Max words: {{max_words}}"
        context = {"name": "Nature", "max_words": 100}

        result = renderer.render_template(template_content, context)
        assert result == "Journal: Nature, Max words: 100"


def test_render_conditional_template():
    """Test Jinja2 conditional rendering."""
    renderer = Renderer(Path.cwd() / "core")

    template_content = """
{% if journal_is("Nature") %}
British English
{% elif journal_is("Science") %}
American English
{% endif %}
"""

    context_nature = {"name": "Nature", "journal_is": lambda j: j == "Nature"}
    result = renderer.render_template(template_content, context_nature)
    assert "British English" in result

    context_science = {"name": "Science", "journal_is": lambda j: j == "Science"}
    result = renderer.render_template(template_content, context_science)
    assert "American English" in result


def test_render_loop_template():
    """Test Jinja2 loop rendering."""
    renderer = Renderer(Path.cwd() / "core")

    template_content = """
{% for rule in rules %}
- {{ rule }}
{% endfor %}
"""

    context = {"rules": ["Rule A", "Rule B", "Rule C"]}
    result = renderer.render_template(template_content, context)

    assert "- Rule A" in result
    assert "- Rule B" in result
    assert "- Rule C" in result
