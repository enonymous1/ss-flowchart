"""Command-line interface for the build visualization package."""

import argparse
import os
from .parser import load_build_definition
from .core_graph import build_graph
from .renderers.graphviz_renderer import GraphvizRenderer


def parse_args(args=None):
    """Parse command-line arguments for the flowchart renderer.

    Args:
        args: Optional list of command-line arguments. If None, uses sys.argv.

    Returns:
        An argparse.Namespace with parsed CLI values.
    """
    parser = argparse.ArgumentParser(
        description="Render a build process definition as a Graphviz flowchart."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input build definition file (JSON or YAML).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path prefix for the generated diagram output file. Overrides metadata output if present.",
    )
    parser.add_argument(
        "--output-dir",
        "-d",
        default=None,
        help="Directory where the generated diagram file should be saved.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Override the chart title specified in the input file.",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="png",
        choices=["png", "svg", "pdf"],
        help="Output format for the generated diagram.",
    )
    parser.add_argument(
        "--engine",
        default=None,
        help="Graphviz layout engine to use (default: neato or file metadata).",
    )
    return parser.parse_args(args)


def main(argv=None):
    """Execute the CLI workflow.

    Reads the input build definition, constructs the graph, and renders it.

    Args:
        argv: Optional argument list to parse. If None, the system arguments are used.
    """
    args = parse_args(argv)
    build_definition = load_build_definition(args.input)
    graph = build_graph(build_definition.steps)

    title = args.title or build_definition.title
    output_name = args.output or build_definition.metadata.get("output", "build_diagram")
    output_dir = args.output_dir or build_definition.metadata.get("output_dir", ".")
    output_path = os.path.join(output_dir, output_name)
    engine = args.engine or build_definition.metadata.get("engine", "neato")

    # Use metadata values from the input file unless CLI overrides are provided.
    try:
        renderer = GraphvizRenderer(engine=engine)
        output_path = renderer.render(graph, output_path, output_format=args.format, title=title)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"Diagram created at: {output_path}")
