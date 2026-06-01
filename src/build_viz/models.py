"""Core data models for build visualization.

This module defines the internal structures used by the parser, graph builder,
and renderers. It includes a lightweight `BuildStep` model, a wrapper for
complete input definitions, and the internal `BuildGraph` representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class BuildStep:
    """Represents a single step in a build or process flow.

    Attributes:
        id: Unique step identifier.
        label: Display label shown on the node.
        depends_on: List of step ids this step depends on.
        attributes: Additional rendering attributes or metadata.
    """

    id: str
    label: str
    depends_on: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "BuildStep":
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
        depends_on = raw.get("depends_on", raw.get("dependencies", [])) or []
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        if not isinstance(depends_on, list):
            raise ValueError("'depends_on' must be a string or list of strings.")

        attributes = {
            key: value
            for key, value in raw.items()
            if key not in {"id", "name", "label", "depends_on", "dependencies"}
        }
        return cls(id=step_id, label=label, depends_on=depends_on, attributes=attributes)


@dataclass
class BuildDefinition:
    """Represents a complete build definition loaded from an input file.

    Attributes:
        title: Chart title extracted from the input definition.
        steps: Parsed build steps.
        metadata: Any additional top-level metadata.
    """

    title: str = "Build Process"
    steps: List[BuildStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildGraph:
    """Internal dependency graph representation used for rendering.

    Attributes:
        nodes: Mapping of step id to `BuildStep`.
        edges: Directed edges represented as tuples `(source, target)`.
    """

    nodes: Dict[str, BuildStep]
    edges: List[Tuple[str, str]]

    def validate(self) -> None:
        """Validate that all graph edges reference known nodes."""
        for source, target in self.edges:
            if source not in self.nodes:
                raise ValueError(f"Unknown dependency '{source}' for step '{target}'.")
            if target not in self.nodes:
                raise ValueError(f"Unknown target node '{target}' in edge ({source}, {target}).")

    def topological_order(self) -> List[BuildStep]:
        """Return a topologically sorted list of steps.

        Raises:
            ValueError: If the graph contains a cycle.
        """
        in_degree = {node_id: 0 for node_id in self.nodes}
        adjacency = {node_id: [] for node_id in self.nodes}
        for source, target in self.edges:
            adjacency[source].append(target)
            in_degree[target] += 1

        ordered: List[BuildStep] = []
        zero_in = [node_id for node_id, degree in in_degree.items() if degree == 0]

        while zero_in:
            current = zero_in.pop(0)
            ordered.append(self.nodes[current])
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    zero_in.append(neighbor)

        if len(ordered) != len(self.nodes):
            raise ValueError("Cycle detected in build step dependencies.")

        return ordered
