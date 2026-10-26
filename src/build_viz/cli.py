"""Command-line interface for the build visualization package."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from . import __version__
from .core_graph import build_graph
from .parser import load_build_definition
from .renderers.graphviz_renderer import GraphvizRenderer


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
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
        "--version",
        action="version",
        version=__version__,
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
        help="Path prefix for the output file. Overrides metadata output.",
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
        choices=["png", "svg", "pdf", "dot"],
        help="Output format. 'dot' writes DOT source, no binary needed.",
    )
    parser.add_argument(
        "--engine",
        default=None,
        help="Graphviz layout engine to use (default: 'dot', or file metadata).",
    )
    parser.add_argument(
        "--strict-acyclic",
        action="store_true",
        help="Reject cycles. Process loops like the RMF example are cyclic.",
    )
    return parser.parse_args(args)


def resolve_output_path(
    *,
    cli_output: str | None,
    cli_output_dir: str | None,
    metadata: dict[str, Any],
    output_format: str,
) -> str:
    """Resolve the output path prefix from CLI flags and file metadata.

    Rule: an explicit `--output` is used as-is (it is a full path prefix,
    so `--output-dir` is ignored in that case). Otherwise the file's
    `output` metadata, or `build_diagram` if there is none, is joined
    with `--output-dir`, or the file's `output_dir`, or `.`. A trailing
    output suffix (`.png`, `.svg`, `.pdf`, or `.dot`) is stripped so the
    renderer does not double-append one.
    """
    if cli_output is not None:
        if not isinstance(cli_output, str) or not cli_output:
            raise ValueError("'output' must be a non-empty string.")
        output_path = cli_output
    else:
        raw_output = metadata.get("output", "build_diagram")
        if not isinstance(raw_output, str) or not raw_output:
            raise ValueError("'output' must be a non-empty string.")
        raw_dir = cli_output_dir or metadata.get("output_dir", ".")
        if not isinstance(raw_dir, str) or not raw_dir:
            raise ValueError("'output_dir' must be a non-empty string.")
        if os.path.isabs(raw_output) or raw_dir == ".":
            output_path = raw_output
        else:
            output_path = os.path.join(raw_dir, raw_output)
    # Strip any known output suffix so the renderer does not double-append
    # one (e.g. `--output diagram.png --format dot` -> `diagram.dot`).
    for suffix in (".png", ".svg", ".pdf", ".dot"):
        if output_path.endswith(suffix):
            output_path = output_path[: -len(suffix)]
            break
    return output_path


def main(argv: list[str] | None = None) -> int:
    """Execute the CLI workflow.

    Reads the input build definition, constructs the graph, and renders it.
    Returns 0 on success and 2 on a handled error (missing file, malformed
    input, unknown dependency, missing Graphviz binary, and so on), with a
    one-line message on stderr instead of a traceback.

    Args:
        argv: Optional argument list to parse. If None, uses sys.argv.
    """
    args = parse_args(argv)
    try:
        build_definition = load_build_definition(args.input)
        graph = build_graph(build_definition.steps, check_acyclic=args.strict_acyclic)

        title = args.title or build_definition.title
        output_path = resolve_output_path(
            cli_output=args.output,
            cli_output_dir=args.output_dir,
            metadata=build_definition.metadata,
            output_format=args.format,
        )
        engine = args.engine or build_definition.metadata.get("engine", "dot")
        if not isinstance(engine, str) or not engine:
            raise ValueError("'engine' must be a non-empty string.")

        renderer = GraphvizRenderer(engine=engine)
        output_path = renderer.render(
            graph, output_path, output_format=args.format, title=title
        )
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as exc:
        print(f"ss-flowchart: error: {exc}", file=sys.stderr)
        return 2

    print(f"Diagram created at: {output_path}")
    return 0
