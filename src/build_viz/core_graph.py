"""Build graph construction utilities.

This module converts a list of build steps into the internal `BuildGraph`
representation used by renderers.
"""

from typing import Iterable, List, Tuple

from .models import BuildGraph, BuildStep


def build_graph(steps: Iterable[BuildStep]) -> BuildGraph:
    """Build the internal graph from a collection of build steps.

    The function converts each step into a node and each dependency into a
    directed edge. Duplicate node identifiers are rejected, and the resulting
    graph is validated for missing nodes and cycles.

    Args:
        steps: An iterable of `BuildStep` instances.

    Returns:
        A validated `BuildGraph` instance.

    Raises:
        ValueError: If duplicate step IDs are found.
    """
    nodes = {}
    edges: List[Tuple[str, str]] = []

    # Build a dictionary of unique node IDs to step definitions.
    for step in steps:
        if step.id in nodes:
            raise ValueError(f"Duplicate step id found: {step.id}")
        nodes[step.id] = step

    # Build directed edges from each declared dependency to its dependent step.
    for step in steps:
        for dependency in step.depends_on:
            edges.append((dependency, step.id))

    graph = BuildGraph(nodes=nodes, edges=edges)
    graph.validate()
    return graph
