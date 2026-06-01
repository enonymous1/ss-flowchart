"""Input file parsing for build visualization definitions.

This module loads a build definition from YAML or JSON, validates the
required structure, and converts it into the package's internal data models.
"""

import json
import os
from typing import List

from .models import BuildDefinition, BuildStep

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def load_build_definition(file_path: str) -> BuildDefinition:
    """Load a build definition from a YAML or JSON file.

    The function supports YAML via PyYAML and JSON via the standard library.
    It validates that a top-level `steps` list exists and returns a
    `BuildDefinition` with title, parsed steps, and any additional metadata.

    Args:
        file_path: Path to the build definition file.

    Returns:
        A BuildDefinition instance containing the parsed definition.

    Raises:
        RuntimeError: If YAML support is requested but PyYAML is not installed.
        ValueError: If the file format is unsupported or the data is malformed.
    """
    extension = os.path.splitext(file_path)[1].lower()
    with open(file_path, "r", encoding="utf-8") as handle:
        if extension in {".yml", ".yaml"}:
            if yaml is None:
                raise RuntimeError(
                    "PyYAML is required for YAML input. Install it with `pip install PyYAML`."
                )
            data = yaml.safe_load(handle)
        elif extension == ".json":
            data = json.load(handle)
        else:
            raise ValueError("Unsupported build definition format: %s" % extension)

    if not isinstance(data, dict) or "steps" not in data:
        raise ValueError("Build definition must include a top-level 'steps' key.")

    title = data.get("title", "Build Process")
    metadata = {k: v for k, v in data.items() if k not in {"steps", "title"}}
    steps = data["steps"]
    if not isinstance(steps, list):
        raise ValueError("'steps' must be a list of step definitions.")

    return BuildDefinition(
        title=title,
        steps=[BuildStep.from_dict(item) for item in steps],
        metadata=metadata,
    )


def load_build_steps(file_path: str) -> List[BuildStep]:
    """Load and return only the list of build steps from a definition file."""
    return load_build_definition(file_path).steps
