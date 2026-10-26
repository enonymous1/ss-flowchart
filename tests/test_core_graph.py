"""Tests for graph construction and validation."""

from pathlib import Path

import pytest

from build_viz.core_graph import build_graph
from build_viz.models import BuildStep
from build_viz.parser import load_build_definition


def test_duplicate_id_raises():
    with pytest.raises(ValueError, match="Duplicate"):
        build_graph([BuildStep(id="A"), BuildStep(id="A")])


def test_unknown_dependency_raises():
    with pytest.raises(ValueError, match="Unknown dependency"):
        build_graph([BuildStep(id="A", depends_on=["Missing"])])


def test_generator_input_still_produces_edges():
    """A generator must not be silently exhausted by the node loop."""
    steps = iter([BuildStep(id="A"), BuildStep(id="B", depends_on=["A"])])
    graph = build_graph(steps)
    assert graph.edges == [("A", "B")]


def test_topological_order_for_dag():
    graph = build_graph(
        [
            BuildStep(id="A"),
            BuildStep(id="B", depends_on=["A"]),
            BuildStep(id="C", depends_on=["B"]),
        ]
    )
    assert [step.id for step in graph.topological_order()] == ["A", "B", "C"]


def test_cycle_allowed_by_default_but_rejected_when_strict():
    cyclic = [BuildStep(id="A", depends_on=["B"]), BuildStep(id="B", depends_on=["A"])]
    graph = build_graph(cyclic)
    assert len(graph.edges) == 2
    with pytest.raises(ValueError, match="Cycle"):
        graph.topological_order()
    with pytest.raises(ValueError, match="Cycle"):
        build_graph(cyclic, check_acyclic=True)


def test_rmf_example_is_cyclic_by_design():
    """The shipped RMF example loops back, so it must not fail by default."""
    definition = load_build_definition(
        str(Path(__file__).parent.parent / "examples" / "rmf_flowchart" / "build.yaml")
    )
    graph = build_graph(definition.steps)
    assert len(graph.nodes) == 7
    with pytest.raises(ValueError, match="Cycle"):
        build_graph(definition.steps, check_acyclic=True)
