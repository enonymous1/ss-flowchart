"""Core data models for build visualization.

This module defines the internal structures used by the parser, graph builder,
and renderers. It includes a lightweight `BuildStep` model, a wrapper for
complete input definitions, and the internal `BuildGraph` representation.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BuildStep:
    """Represents a single step in a build or process flow.

    Attributes:
        id: Unique step identifier.
        label: Display label shown on the node. Defaults to `id`.
        depends_on: List of step ids this step depends on.
        attributes: Additional rendering attributes or metadata.
    """

    id: str
    label: str = ""
    depends_on: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("Each step must include a non-empty string 'id'.")
        if not isinstance(self.label, str):
            raise ValueError("'label' must be a string.")
        if not self.label:
            self.label = self.id
        if not isinstance(self.depends_on, list) or not all(
            isinstance(dep, str) for dep in self.depends_on
        ):
            raise ValueError("'depends_on' must be a list of strings.")
        if not isinstance(self.attributes, dict):
            raise ValueError("'attributes' must be a mapping.")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> BuildStep:
        """Create a BuildStep from a dictionary loaded from YAML/JSON.

        Args:
            raw: Raw mapping from the input definition.

        Returns:
            A validated BuildStep instance.

        Raises:
            ValueError: If required fields are missing or malformed.
        """
        if not isinstance(raw, dict):
            raise ValueError("Each step definition must be a mapping.")

        step_id = raw.get("id") or raw.get("name")
        if not step_id or not isinstance(step_id, str):
            raise ValueError("Each step must include a string 'id'.")

        label = raw.get("label", step_id)
        if not isinstance(label, str):
            raise ValueError("'label' must be a string.")
        depends_on = raw.get("depends_on", raw.get("dependencies", [])) or []
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        if not isinstance(depends_on, list) or not all(
            isinstance(dep, str) for dep in depends_on
        ):
            raise ValueError("'depends_on' must be a string or list of strings.")

        attributes = {
            key: value
            for key, value in raw.items()
            if key not in {"id", "name", "label", "depends_on", "dependencies"}
        }
        return cls(
            id=step_id, label=label, depends_on=depends_on, attributes=attributes
        )


@dataclass
class BuildDefinition:
    """Represents a complete build definition loaded from an input file.

    Attributes:
        title: Chart title extracted from the input definition.
        steps: Parsed build steps.
        metadata: Any additional top-level metadata.
    """

    title: str = "Build Process"
    steps: list[BuildStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildGraph:
    """Internal dependency graph representation used for rendering.

    Attributes:
        nodes: Mapping of step id to `BuildStep`.
        edges: Directed edges represented as tuples `(source, target)`.
    """

    nodes: dict[str, BuildStep]
    edges: list[tuple[str, str]]

    def validate(self, *, check_acyclic: bool = False) -> None:
        """Validate that all graph edges reference known nodes.

        Cycles are allowed by default: process diagrams such as the RMF
        example deliberately loop back (Monitor feeds into Categorize).
        Pass `check_acyclic=True` when the graph must be a DAG, for example
        a build pipeline, and a cycle will raise `ValueError`.
        """
        for source, target in self.edges:
            if source not in self.nodes:
                raise ValueError(f"Unknown dependency '{source}' for step '{target}'.")
            if target not in self.nodes:
                raise ValueError(
                    f"Unknown target node '{target}' in edge ({source}, {target})."
                )
        if check_acyclic:
            self.topological_order()

    def topological_order(self) -> list[BuildStep]:
        """Return a topologically sorted list of steps.

        Raises:
            ValueError: If the graph contains a cycle.
        """
        in_degree = {node_id: 0 for node_id in self.nodes}
        adjacency: dict[str, list[str]] = {node_id: [] for node_id in self.nodes}
        for source, target in self.edges:
            adjacency[source].append(target)
            in_degree[target] += 1

        ordered: list[BuildStep] = []
        zero_in = deque(node_id for node_id, degree in in_degree.items() if degree == 0)

        while zero_in:
            current = zero_in.popleft()
            ordered.append(self.nodes[current])
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    zero_in.append(neighbor)

        if len(ordered) != len(self.nodes):
            raise ValueError("Cycle detected in build step dependencies.")

        return ordered
