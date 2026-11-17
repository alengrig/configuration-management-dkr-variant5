"""Command-line interface for the configuration translator."""

import argparse
import sys

from configlang.evaluator import evaluate_tree
from configlang.parser import parse_source
from configlang.yaml_writer import write_yaml


def parse_arguments(arguments=None):
    """Read the output file path from command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Translate configuration language into YAML."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output YAML file",
    )
    return parser.parse_args(arguments)


def translate(source, output):
    """Parse, evaluate, and save the configuration."""
    tree = parse_source(source)
    data = evaluate_tree(tree)
    return write_yaml(data, output)


def main(arguments=None):
    """Read standard input and save the resulting YAML."""
    config = parse_arguments(arguments)

    try:
        source = sys.stdin.read()
        result = translate(source, config.output)
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    print(f"YAML created: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
