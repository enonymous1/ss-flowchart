"""Tests for build definition parsing.

These tests verify the parser's ability to load YAML and JSON build
definitions and map them into the package's internal data models.
"""

import json
from pathlib import Path

import pytest

from build_viz.parser import load_build_definition


def example_path() -> Path:
    return Path(__file__).parent.parent / "examples" / "rmf_flowchart" / "build.yaml"


def test_load_build_definition_from_yaml():
    """Validate that a YAML build definition loads correctly."""
    build_definition = load_build_definition(str(example_path()))

    # Confirm top-level metadata is parsed correctly.
    assert build_definition.title == "Risk Management Framework Steps"
    assert (
        build_definition.metadata.get("output")
        == "examples/rmf_flowchart/rmf_flowchart"
    )

    # Confirm step parsing and dependency normalization.
    assert len(build_definition.steps) == 7
    assert build_definition.steps[0].id == "Prepare"
    assert build_definition.steps[1].depends_on == ["Prepare", "Monitor"]
    assert build_definition.steps[1].label == "Categorize\nSystem"


def test_load_build_definition_from_json(tmp_path: Path):
    """JSON input parses the same way as YAML input."""
    data = {
        "title": "Pipeline",
        "steps": [
            {"id": "Build", "label": "Build it"},
            {"id": "Test", "depends_on": "Build"},
        ],
    }
    input_file = tmp_path / "build.json"
    input_file.write_text(json.dumps(data), encoding="utf-8")

    build_definition = load_build_definition(str(input_file))

    assert build_definition.title == "Pipeline"
    assert [step.id for step in build_definition.steps] == ["Build", "Test"]
    assert build_definition.steps[1].depends_on == ["Build"]
    # Label defaults to the step id when omitted.
    assert build_definition.steps[1].label == "Test"


def test_name_alias_and_dependencies_alias(tmp_path: Path):
    """`name` works as an id alias and `dependencies` as a depends_on alias."""
    input_file = tmp_path / "build.yaml"
    input_file.write_text(
        "title: Aliases\nsteps:\n"
        "  - name: First\n"
        "  - id: Second\n    dependencies: [First]\n",
        encoding="utf-8",
    )

    build_definition = load_build_definition(str(input_file))

    assert build_definition.steps[0].id == "First"
    assert build_definition.steps[1].depends_on == ["First"]


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_build_definition("does-not-exist.yaml")


def test_missing_steps_key_raises(tmp_path: Path):
    input_file = tmp_path / "build.yaml"
    input_file.write_text("title: No steps here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="steps"):
        load_build_definition(str(input_file))


def test_empty_file_raises(tmp_path: Path):
    input_file = tmp_path / "build.yaml"
    input_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="steps"):
        load_build_definition(str(input_file))


def test_steps_must_be_a_list(tmp_path: Path):
    input_file = tmp_path / "build.yaml"
    input_file.write_text("steps: not-a-list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="steps"):
        load_build_definition(str(input_file))


def test_unsupported_extension_raises(tmp_path: Path):
    input_file = tmp_path / "build.txt"
    input_file.write_text("steps: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        load_build_definition(str(input_file))


def test_non_string_title_raises(tmp_path: Path):
    input_file = tmp_path / "build.yaml"
    input_file.write_text("title: 42\nsteps: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="title"):
        load_build_definition(str(input_file))


def test_invalid_step_fields_raise(tmp_path: Path):
    bad_inputs = [
        "steps:\n  - label: No id\n",
        "steps:\n  - id: A\n    label: 42\n",
        "steps:\n  - id: A\n    depends_on: [1]\n",
        "steps:\n  - just-a-string\n",
    ]
    for i, text in enumerate(bad_inputs):
        input_file = tmp_path / f"bad-{i}.yaml"
        input_file.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            load_build_definition(str(input_file))
