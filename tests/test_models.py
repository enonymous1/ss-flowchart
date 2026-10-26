"""Tests for the core data models."""

import pytest

from build_viz.models import BuildStep


def test_label_defaults_to_id():
    step = BuildStep(id="A")
    assert step.label == "A"


def test_empty_id_raises():
    with pytest.raises(ValueError, match="id"):
        BuildStep(id="")


def test_non_string_label_raises():
    with pytest.raises(ValueError, match="label"):
        BuildStep(id="A", label=42)  # type: ignore[arg-type]


def test_non_string_dependency_raises():
    with pytest.raises(ValueError, match="depends_on"):
        BuildStep(id="A", depends_on=[1])  # type: ignore[list-item]


def test_from_dict_label_defaults_to_id():
    step = BuildStep.from_dict({"id": "Only"})
    assert step.label == "Only"
    assert step.depends_on == []
    assert step.attributes == {}


def test_from_dict_keeps_extra_fields_as_attributes():
    step = BuildStep.from_dict({"id": "A", "fillcolor": "#ADD8E6", "color": "black"})
    assert step.attributes == {"fillcolor": "#ADD8E6", "color": "black"}
