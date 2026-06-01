"""Tests for build definition parsing.

These tests verify the parser's ability to load a YAML build definition and
map it into the package's internal data models.
"""

import os

from build_viz.parser import load_build_definition


def test_load_build_definition_from_yaml():
    """Validate that a YAML build definition loads correctly."""
    example_file = os.path.join(
        os.path.dirname(__file__), "..", "examples", "rmf_flowchart", "build.yaml"
    )

    build_definition = load_build_definition(example_file)

    # Confirm top-level metadata is parsed correctly.
    assert build_definition.title == "Risk Management Framework Steps"
    assert build_definition.metadata.get("output") == "examples/rmf_flowchart/rmf_flowchart"

    # Confirm step parsing and dependency normalization.
    assert len(build_definition.steps) == 7
    assert build_definition.steps[0].id == "Prepare"
    assert build_definition.steps[1].depends_on == ["Prepare", "Monitor"]
    assert build_definition.steps[1].label == "Categorize\nSystem"
