# Changelog

## 0.3.0 — 2026-10-26

Package rename, approved after 0.2.0 and before any push of it.

### Changed

- Package renamed `build_viz` → `ss_flowchart`, the direct underscore
  form of the distribution and CLI name. Import it as
  `from ss_flowchart.cli import main`. The distribution name, the
  `ss-flowchart` command, and all CLI behavior are unchanged.
- Version bumped to 0.3.0 because the import path is a breaking change
  for anyone importing `build_viz` directly.

## 0.2.0 — 2026-10-26

Modernization on top of the original history. No repo or CLI rename:
the package stays `build_viz` and the command stays `ss-flowchart`.

### Added

- MIT LICENSE, GitHub Actions CI (Python 3.10–3.12), ruff, mypy-strict,
  and pre-commit configuration.
- `--format dot`: writes DOT source without the Graphviz system binary.
- `--version` and `--strict-acyclic` flags.
- `GraphvizRenderer.to_dot()` for DOT source without rendering.
- `py.typed` marker; `BuildStep(id=...)` now defaults its label to the id.
- 38 tests (plus 1 integration test gated on the `dot` binary), covering
  parser, graph, renderer, and CLI behavior.

### Changed

- Renderer styling is neutral: the RMF title, comment, dashed `Prepare`
  edges, gray edges, and fixed 1.5×1.5 node size are gone. Per-step
  attributes from the input file still apply.
- Default layout engine is now `dot` instead of `neato`. The RMF example
  still specifies `neato` in its YAML, so its output is unchanged.
- `main()` returns an exit code (0, or 2 with a one-line stderr message)
  instead of raising `SystemExit` with a traceback-prone message.
- Output resolution is documented and explicit: `--output` is used as-is;
  otherwise file `output` metadata is joined with `--output-dir`.
- `requirements.txt` removed; `pyproject.toml` is the single source of
  truth, with pytest/ruff/mypy/types-PyYAML under the `dev` extra.
- `tests/conftest.py` and the `main.py` `sys.path` hacks removed; tests
  run against the installed package.
- Modern typing throughout (`list`/`dict` builtins, `X | None`).

### Fixed

- `build_graph` no longer silently drops edges when given a generator:
  the input is materialized before the node and edge loops.
- `topological_order` uses a deque instead of `list.pop(0)`.
- Missing output parent directories are now created by the renderer.
- A trailing output suffix (`.png`, `.svg`, `.pdf`, `.dot`) is stripped
  before the renderer appends its own, so `diagram.png` + `--format dot`
  produces `diagram.dot`, not `diagram.png.dot`.
- Validation is honest about cycles: they are allowed by default
  (the RMF example is cyclic), and only rejected with
  `--strict-acyclic` / `check_acyclic=True`.

## 0.1.0

Initial public version: YAML/JSON parser, dependency graph, Graphviz
renderer, two examples, and a basic test suite.
