"""Tests for rendering build graphs.

DOT-source tests run without the Graphviz system binaries. The one test
that renders a real PNG is marked integration and skipped when `dot` is
not on PATH, so the suite stays green on a fresh checkout.
"""

import shutil
from pathlib import Path

import pytest

from ss_flowchart.core_graph import build_graph
from ss_flowchart.models import BuildStep
from ss_flowchart.renderers.graphviz_renderer import GraphvizRenderer


def simple_graph():
    steps = [
        BuildStep(id="A", label="Step A", attributes={"fillcolor": "#ADD8E6"}),
        BuildStep(id="B", label="Step B", depends_on=["A"]),
    ]
    return build_graph(steps)


def test_to_dot_is_neutral_and_contains_nodes_and_edge():
    """No example-specific title, comment, or edge styling leaks in."""
    source = GraphvizRenderer().to_dot(simple_graph())

    assert "Step A" in source
    assert "Step B" in source
    assert "->" in source
    assert "#ADD8E6" in source
    assert "Risk Management" not in source
    assert "RMF" not in source
    assert "dashed" not in source


def test_to_dot_title_is_optional():
    renderer = GraphvizRenderer()
    assert "My Title" in renderer.to_dot(simple_graph(), title="My Title")
    assert "My Title" not in renderer.to_dot(simple_graph())


def test_dot_format_writes_file_without_binary(tmp_path: Path):
    """`--format dot` works on a machine with no `dot` binary installed."""
    renderer = GraphvizRenderer()
    output = renderer.render(
        simple_graph(), str(tmp_path / "nested" / "diagram"), output_format="dot"
    )

    assert output.endswith("diagram.dot")
    assert Path(output).exists()
    assert "Step A" in Path(output).read_text(encoding="utf-8")


def test_render_strips_a_matching_suffix(tmp_path: Path):
    renderer = GraphvizRenderer()
    output = renderer.render(
        simple_graph(), str(tmp_path / "diagram.dot"), output_format="dot"
    )
    assert output == str(tmp_path / "diagram.dot")
    assert not output.endswith(".dot.dot")


def test_empty_engine_raises():
    with pytest.raises(ValueError, match="engine"):
        GraphvizRenderer(engine="")


@pytest.mark.integration
@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz binary not installed")
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
