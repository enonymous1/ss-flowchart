"""Graphviz-based rendering implementation for build graph visualization."""

try:
    from graphviz import Digraph
except ImportError as exc:  # pragma: no cover
    Digraph = None
    graphviz_import_error = exc
else:
    graphviz_import_error = None

from ..models import BuildGraph
from .base import BaseRenderer


class GraphvizRenderer(BaseRenderer):
    """Renderer implementation that generates diagrams using Graphviz.

    This renderer translates the internal `BuildGraph` representation into
    Graphviz DOT syntax, then renders it through the Graphviz backend.
    """

    def __init__(self, engine: str = "dot"):
        """Initialize the Graphviz renderer.

        Args:
            engine: The Graphviz layout engine to use, such as "dot" or "neato".
        """
        if graphviz_import_error is not None:
            raise RuntimeError(
                "The 'graphviz' Python package is required to render diagrams. "
                "Install it with 'pip install graphviz' and ensure the Graphviz system binaries are installed."
            ) from graphviz_import_error

        self.engine = engine

    def render(
        self,
        graph: BuildGraph,
        output_path: str,
        output_format: str = "png",
        title: str = "Risk Management Framework Steps",
    ) -> str:
        """Render a build graph to a Graphviz output file.

        Args:
            graph: The internal build dependency graph.
            output_path: Path prefix for the rendered file.
            output_format: The desired output format, e.g. "png", "svg", or "pdf".
            title: The chart title to display in the rendered diagram.

        Returns:
            The path to the generated file.
        """
        dot = Digraph(comment="RMF Process", engine=self.engine)

        dot.attr(
            start="5",
            normalize="0",
            layout=self.engine,
            fontname="Arial",
            label=title,
            labelloc="t",
            fontsize="24",
        )
        dot.attr(
            "node",
            shape="rect",
            style="rounded,filled",
            width="1.5",
            height="1.5",
            fixedsize="true",
            color="#00000088",
            fontname="Helvetica,Arial,sans-serif",
        )
        dot.attr("edge", len="2", penwidth="1.5", arrowhead="open")

        for step in graph.nodes.values():
            dot.node(step.id, step.label, **step.attributes)

        for source, target in graph.edges:
            # Keep the RMF example’s Prepare edges dashed and the cycle edges gray.
            if source == "Prepare":
                dot.edge(source, target, style="dashed", color="black")
            else:
                dot.edge(source, target, color="gray")

        output_file = dot.render(filename=output_path, format=output_format, cleanup=True)
        return output_file
