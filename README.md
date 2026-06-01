# ss-flowchart

A lightweight Python tool that converts structured build and process definitions into clean, shareable flowchart diagrams.

ss-flowchart is designed for developers and technical writers who want to create visual process documentation from YAML or JSON without manually drawing nodes and edges.

## What it does

- Reads machine-readable build/process definitions.
- Builds an internal dependency graph from steps and dependencies.
- Renders a polished flowchart with Graphviz.
- Supports metadata-driven chart titles, output locations, and Graphviz engine selection.

## Why use it

- Quickly visualize build pipelines, deployment workflows, approval processes, and other directed workflows.
- Keep process definitions in code-friendly formats like YAML/JSON.
- Generate diagrams that are easy to update and version alongside your project.

## Quick start

1. Install the package and its dependencies:

```bash
python -m pip install -U pip
python -m pip install -e .
```

2. Install the Graphviz system package:

```bash
sudo apt-get update && sudo apt-get install -y graphviz
```

3. Render an example flowchart:

```bash
python main.py --input examples/rmf_flowchart/build.yaml --format png
```

## Installation

1. Install the Python dependencies:

```bash
python -m pip install -U pip
python -m pip install -e .
```

Alternatively, install from `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

2. Install the Graphviz system package, which is required by the `graphviz` Python library:

```bash
sudo apt-get update && sudo apt-get install -y graphviz
```

## Usage

Render an example build definition:

```bash
python main.py --input examples/rmf_flowchart/build.yaml --format png
```

Or run the installed CLI:

```bash
ss-flowchart --input examples/rmf_flowchart/build.yaml --format png
```

If your YAML file specifies `output` or `output_dir`, the CLI honors that metadata unless you override it with `--output` or `--output-dir`.

Example YAML metadata fields:

```yaml
title: Risk Management Framework Steps
output: examples/rmf_flowchart
output_dir: examples
steps:
  - id: Prepare
    label: Prepare
    fillcolor: "#ADD8E6"
    color: "black"
  - id: Categorize
    label: "Categorize\nSystem"
    depends_on: [Prepare, Monitor]
    fillcolor: "#90EE90"
```

## Design

This project separates the core workflow into three layers:

1. **Parser**: reads structured build input (JSON/YAML) and converts it into `BuildStep` objects.
2. **Core graph**: builds an internal dependency graph and validates it.
3. **Renderer**: translates the graph into a Graphviz diagram.

This makes it easy to swap the rendering backend later (Mermaid, Pyvis, Diagrams) while keeping the same input/output flow.

## Example input

The example YAML file shows a simple pipeline with step labels and dependencies.
