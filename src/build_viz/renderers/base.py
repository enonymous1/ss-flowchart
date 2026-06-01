"""Base rendering abstractions for build visualization."""

from abc import ABC, abstractmethod

from ..models import BuildGraph


class BaseRenderer(ABC):
    """Abstract renderer interface for build graph visualization.

    Concrete renderer implementations should translate the internal
    `BuildGraph` representation into a specific format or backend.

    The renderer must return the path to the generated output file.
    """

    @abstractmethod
    def render(self, graph: BuildGraph, output_path: str, output_format: str = "png") -> str:
        """Render a build graph to a file.

        Args:
            graph: The internal build dependency graph to render.
            output_path: The file path prefix for the rendered output.
            output_format: The format to produce, such as "png", "svg", or "pdf".

        Returns:
            The full path to the generated output file.
        """
        raise NotImplementedError
