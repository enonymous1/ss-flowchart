# Examples

This directory contains sample flowchart definitions and related output files.

Each example is stored in its own subdirectory, which keeps example content isolated and easy to grow.

## Current examples

- `rmf_flowchart/`
  - `build.yaml`: input definition for the Risk Management Framework flowchart
  - `rmf_flowchart.png`: committed example output
  - Cyclic by design (Monitor feeds back into Categorize), rendered with
    the `neato` engine. Do not pass `--strict-acyclic` for this one.
- `ss-flowchart-process/`
  - `build.yaml`: input definition for a generic flowchart creation process
  - `flowchart_creation.png`: committed example output
  - A linear DAG, rendered with the `dot` engine.

## How to use an example

```bash
ss-flowchart --input examples/rmf_flowchart/build.yaml --format png
ss-flowchart --input examples/ss-flowchart-process/build.yaml --output flowchart --format dot
```

Output rule reminder: an explicit `--output` is used as-is. Without it,
the YAML file's `output` metadata is used (joined with `--output-dir` if
given), so the first command above regenerates the committed RMF PNG in
place, while the second writes `flowchart.dot` next to where you run it.

## Adding a new example

Create a new folder under `examples/`, add a `build.yaml` file, and use descriptive names:

```bash
examples/
  your_new_flow/
    build.yaml
```

Then render it with:

```bash
ss-flowchart --input examples/your_new_flow/build.yaml --output your_new_flow --format png
```

Generated diagrams outside the two committed example PNGs are gitignored.
