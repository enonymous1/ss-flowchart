"""Tests for the CLI: output resolution and friendly error handling."""

from pathlib import Path

import pytest

from build_viz import __version__
from build_viz.cli import main, parse_args, resolve_output_path
from build_viz.renderers.graphviz_renderer import GraphvizRenderer


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--version"])
    assert exc_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_resolve_output_path_prefers_cli_output_and_dir():
    path = resolve_output_path(
        cli_output="custom/diagram",
        cli_output_dir="ignored",
        metadata={"output": "meta/diagram", "output_dir": "meta"},
        output_format="png",
    )
    assert path == "custom/diagram"


def test_resolve_output_path_uses_metadata_and_strips_suffix():
    path = resolve_output_path(
        cli_output=None,
        cli_output_dir=None,
        metadata={"output": "examples/rmf_flowchart/rmf_flowchart", "output_dir": "."},
        output_format="png",
    )
    assert path == "examples/rmf_flowchart/rmf_flowchart"


def test_resolve_output_path_absolute_output_ignores_dir():
    path = resolve_output_path(
        cli_output="/tmp/diagram.png",
        cli_output_dir="out",
        metadata={},
        output_format="dot",
    )
    assert path == "/tmp/diagram"


def test_resolve_output_path_rejects_non_string_metadata():
    with pytest.raises(ValueError, match="output"):
        resolve_output_path(
            cli_output=None,
            cli_output_dir=None,
            metadata={"output": 42},
            output_format="png",
        )


def write_yaml(tmp_path: Path, text: str) -> Path:
    input_file = tmp_path / "build.yaml"
    input_file.write_text(text, encoding="utf-8")
    return input_file


def test_main_dot_mode_end_to_end(tmp_path: Path, capsys):
    """DOT mode renders the full CLI path with no Graphviz binary."""
    input_file = write_yaml(
        tmp_path,
        "title: Demo\nsteps:\n  - id: A\n  - id: B\n    depends_on: [A]\n",
    )
    code = main(
        [
            "--input",
            str(input_file),
            "--output-dir",
            str(tmp_path / "nested" / "out"),
            "--format",
            "dot",
        ]
    )

    assert code == 0
    out = capsys.readouterr()
    assert "Diagram created at:" in out.out
    assert (tmp_path / "nested" / "out" / "build_diagram.dot").exists()


def test_main_output_suffix_is_not_doubled(tmp_path: Path):
    input_file = write_yaml(tmp_path, "steps:\n  - id: A\n")
    code = main(
        [
            "--input",
            str(input_file),
            "--output",
            str(tmp_path / "diagram.png"),
            "--format",
            "dot",
        ]
    )
    assert code == 0
    assert (tmp_path / "diagram.dot").exists()
    assert not (tmp_path / "diagram.png.dot").exists()


def test_main_missing_file_returns_2_without_traceback(capsys):
    code = main(["--input", "no-such-file.yaml", "--format", "dot"])
    out = capsys.readouterr()
    assert code == 2
    assert "ss-flowchart: error:" in out.err
    assert "Traceback" not in out.err


def test_main_unknown_dependency_returns_2(tmp_path: Path, capsys):
    input_file = write_yaml(tmp_path, "steps:\n  - id: A\n    depends_on: [Missing]\n")
    code = main(["--input", str(input_file), "--format", "dot"])
    assert code == 2
    assert "Unknown dependency" in capsys.readouterr().err


def test_main_rmf_dot_ok_but_strict_acyclic_fails(tmp_path: Path, capsys):
    rmf = Path(__file__).parent.parent / "examples" / "rmf_flowchart" / "build.yaml"
    code = main(
        [
            "--input",
            str(rmf),
            "--output-dir",
            str(tmp_path),
            "--format",
            "dot",
        ]
    )
    assert code == 0
    code = main(
        [
            "--input",
            str(rmf),
            "--output-dir",
            str(tmp_path),
            "--format",
            "dot",
            "--strict-acyclic",
        ]
    )
    assert code == 2
    assert "Cycle" in capsys.readouterr().err


def test_main_renderer_error_returns_2(monkeypatch, tmp_path: Path, capsys):
    """A Graphviz failure is a clean error, not a traceback."""

    def boom(*args, **kwargs):
        raise RuntimeError("dot binary missing")

    monkeypatch.setattr(GraphvizRenderer, "render", boom)
    input_file = write_yaml(tmp_path, "steps:\n  - id: A\n")
    code = main(["--input", str(input_file), "--format", "png"])
    assert code == 2
    assert "dot binary missing" in capsys.readouterr().err
