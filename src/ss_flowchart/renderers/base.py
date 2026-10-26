"""Base rendering abstractions for build visualization."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import BuildGraph


class BaseRenderer(ABC):
    """Abstract renderer interface for build graph visualization.

    Concrete renderer implementations should translate the internal
    `BuildGraph` representation into a specific format or backend.

    The renderer must return the path to the generated output file.
    """

    @abstractmethod
    def render(
        self,
        graph: BuildGraph,
        output_path: str,
        output_format: str = "png",
        title: str | None = None,
    ) -> str:
        """Render a build graph to a file.

        Args:
            graph: The internal build dependency graph to render.
            output_path: The file path prefix for the rendered output.
            output_format: The format to produce, such as "png", "svg",
                "pdf", or "dot" (DOT source, no Graphviz binary needed).
            title: Optional chart title to display in the rendered diagram.

        Returns:
            The full path to the generated output file.
        """
        raise NotImplementedError

    def to_dot(self, graph: BuildGraph, title: str | None = None) -> str:
        """Return the DOT source for a build graph, without rendering it.

        Renderers that do not build DOT source should leave this raising
        `NotImplementedError`.
        """
        raise NotImplementedError
