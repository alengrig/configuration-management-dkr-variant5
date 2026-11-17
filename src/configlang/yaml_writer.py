"""Save evaluated configurations in YAML format."""

from pathlib import Path

import yaml


def write_yaml(data, output):
    """Write configuration data to a UTF-8 YAML file."""
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    content = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )

    output_path.write_text(content, encoding="utf-8")
    return output_path
