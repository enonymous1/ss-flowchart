"""Build graph construction utilities.

This module converts a list of build steps into the internal `BuildGraph`
representation used by renderers.
"""

from __future__ import annotations

from collections.abc import Iterable

from .models import BuildGraph, BuildStep


def build_graph(
    steps: Iterable[BuildStep], *, check_acyclic: bool = False
) -> BuildGraph:
    """Build the internal graph from a collection of build steps.

    The function converts each step into a node and each dependency into a
    directed edge. Duplicate node identifiers are rejected, and the resulting
    graph is validated for missing nodes. Cycles are allowed by default (see
    `BuildGraph.validate`); pass `check_acyclic=True` to reject them.

    Args:
        steps: An iterable of `BuildStep` instances.
        check_acyclic: If true, raise `ValueError` when the graph has a cycle.

    Returns:
        A validated `BuildGraph` instance.

    Raises:
        ValueError: If duplicate step IDs are found, or a dependency is
            unknown, or (with `check_acyclic=True`) a cycle is found.
    """
    # Materialize first: a generator would be exhausted by the node loop
    # and the edge loop would then silently produce no edges.
    steps_list = list(steps)

    nodes: dict[str, BuildStep] = {}
    edges: list[tuple[str, str]] = []

    # Build a dictionary of unique node IDs to step definitions.
    for step in steps_list:
        if step.id in nodes:
            raise ValueError(f"Duplicate step id found: {step.id}")
        nodes[step.id] = step

    # Build directed edges from each declared dependency to its dependent step.
    for step in steps_list:
        for dependency in step.depends_on:
            edges.append((dependency, step.id))

    graph = BuildGraph(nodes=nodes, edges=edges)
    graph.validate(check_acyclic=check_acyclic)
    return graph
