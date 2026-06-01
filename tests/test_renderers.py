"""Tests for rendering build graphs into Graphviz output files.

These tests verify that the Graphviz renderer can accept an internal
`BuildGraph` and produce an actual image file using the configured backend.
"""

import os
from pathlib import Path

import pytest

from build_viz.core_graph import build_graph
from build_viz.models import BuildStep
from build_viz.renderers.graphviz_renderer import GraphvizRenderer


def test_graphviz_renderer_generates_file(tmp_path: Path):
    """Ensure that GraphvizRenderer produces a PNG file from a simple graph."""
    pytest.importorskip("graphviz")

    steps = [
        BuildStep(id="A", label="Step A"),
        BuildStep(id="B", label="Step B", depends_on=["A"]),
    ]
    graph = build_graph(steps)
    renderer = GraphvizRenderer()

    output = renderer.render(
        graph,
        str(tmp_path / "test_diagram"),
        output_format="png",
    )

    # The renderer should return the rendered file path and that file should exist.
    assert output.endswith(".png")
    assert Path(output).exists()
