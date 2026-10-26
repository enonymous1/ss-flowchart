"""Graphviz-based rendering implementation for build graph visualization."""

from __future__ import annotations

from pathlib import Path

from ..models import BuildGraph
from .base import BaseRenderer

graphviz_import_error: ImportError | None = None
try:
    from graphviz import Digraph
except ImportError as exc:  # pragma: no cover
    Digraph = None
    graphviz_import_error = exc


class GraphvizRenderer(BaseRenderer):
    """Renderer implementation that generates diagrams using Graphviz.

    This renderer translates the internal `BuildGraph` representation into
    Graphviz DOT syntax, then renders it through the Graphviz backend.
    Styling is deliberately neutral: per-step attributes from the input file
    (for example `fillcolor`) still apply, but no example-specific node or
    edge styling is baked in.
    """

    def __init__(self, engine: str = "dot"):
        """Initialize the Graphviz renderer.

        Args:
            engine: The Graphviz layout engine to use, such as "dot" or "neato".
        """
        if graphviz_import_error is not None:
            raise RuntimeError(
                "The 'graphviz' Python package is required to render diagrams. "
                "Install it with 'pip install graphviz' and ensure the "
                "Graphviz system binaries are installed."
            ) from graphviz_import_error
        if not isinstance(engine, str) or not engine:
            raise ValueError("Graphviz engine must be a non-empty string.")

        self.engine = engine

    def build_digraph(self, graph: BuildGraph, title: str | None = None) -> Digraph:
        """Build the Graphviz Digraph for a graph, without rendering it."""
        if Digraph is None:  # pragma: no cover - guarded in __init__
            raise RuntimeError("The 'graphviz' Python package is not installed.")
        dot = Digraph(comment="ss-flowchart", engine=self.engine)

        graph_attrs: dict[str, str] = {"fontname": "Arial"}
        if title:
            graph_attrs.update({"label": title, "labelloc": "t", "fontsize": "24"})
        dot.attr(**graph_attrs)
        dot.attr(
            "node",
            shape="rect",
            style="rounded,filled",
            width="1.5",
            height="0.75",
            fontname="Helvetica,Arial,sans-serif",
        )
        dot.attr("edge", penwidth="1.5", arrowhead="open")

        for step in graph.nodes.values():
            dot.node(step.id, step.label, **step.attributes)

        for source, target in graph.edges:
            dot.edge(source, target)

        return dot

    def to_dot(self, graph: BuildGraph, title: str | None = None) -> str:
        """Return the DOT source for a graph, without invoking `dot`."""
        return str(self.build_digraph(graph, title=title).source)

    def render(
        self,
        graph: BuildGraph,
        output_path: str,
        output_format: str = "png",
        title: str | None = None,
    ) -> str:
        """Render a build graph to a Graphviz output file.

        Args:
            graph: The internal build dependency graph.
            output_path: Path prefix for the rendered file. A trailing
                `.<format>` suffix, if present, is stripped first so
                `--output diagram.png --format png` does not produce
                `diagram.png.png`.
            output_format: The desired output format, e.g. "png", "svg",
                "pdf", or "dot" (writes DOT source, no binary needed).
            title: Optional chart title to display in the rendered diagram.

        Returns:
            The path to the generated file.
        """
        suffix = f".{output_format}"
        if output_path.endswith(suffix):
            output_path = output_path[: -len(suffix)]

        if output_format == "dot":
            dot_path = Path(f"{output_path}.dot")
            if dot_path.parent != Path("."):
                dot_path.parent.mkdir(parents=True, exist_ok=True)
            dot_path.write_text(self.to_dot(graph, title=title), encoding="utf-8")
            return str(dot_path)

        parent = Path(output_path).parent
        if str(parent) not in {"", "."}:
            parent.mkdir(parents=True, exist_ok=True)
        dot = self.build_digraph(graph, title=title)
        output_file = dot.render(
            filename=output_path, format=output_format, cleanup=True
        )
        return str(output_file)
