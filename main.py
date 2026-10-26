"""Thin entry point for running from a checkout.

Install the package first (`pip install -e .`), then prefer the
`ss-flowchart` console script. This file exists only for `python main.py`.
"""

from ss_flowchart.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
