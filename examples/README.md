# Examples

This directory contains sample flowchart definitions and related output files.

Each example is stored in its own subdirectory, which keeps example content isolated and easy to grow.

## Current examples

- `rmf_flowchart/`
  - `build.yaml`: input definition for the Risk Management Framework flowchart
  - generated output may be written to `examples/rmf_flowchart/rmf_flowchart.png`
- `ss-flowchart-process/`
  - `build.yaml`: input definition for a generic flowchart creation process
  - generated output may be written to `examples/ss-flowchart-process/flowchart_creation.png`

## How to use an example

Run the CLI with the example definition:

```bash
python main.py --input examples/rmf_flowchart/build.yaml --format png
```

If the YAML includes `output`, `output_dir`, or `engine`, that metadata is used unless you override it with `--output`, `--output-dir`, or `--engine`.

## Adding a new example

Create a new folder under `examples/`, add a `build.yaml` file, and use descriptive names:

```bash
examples/
  your_new_flow/
    build.yaml
```

Then render it with:

```bash
python main.py --input examples/your_new_flow/build.yaml --format png
```
