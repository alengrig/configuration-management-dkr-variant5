"""Tests for writing YAML configuration files."""

import tempfile
import unittest
from pathlib import Path

import yaml

from configlang.yaml_writer import write_yaml


class YamlWriterTests(unittest.TestCase):
    """Verify YAML output and file handling."""

    def setUp(self):
        """Create a temporary directory for each test."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.output = Path(directory.name) / "result.yaml"

    def read_yaml(self):
        """Load the generated YAML for verification."""
        text = self.output.read_text(encoding="utf-8")
        return yaml.safe_load(text)

    def test_creates_yaml_file(self):
        """Create the requested output file."""
        result = write_yaml({"port": 1500.0}, self.output)
        self.assertEqual(result, self.output)
        self.assertTrue(self.output.is_file())

    def test_scientific_values(self):
        """Preserve evaluated numeric values in YAML."""
        data = {"positive": 1500.0, "negative": -0.2}
        write_yaml(data, self.output)
        self.assertEqual(self.read_yaml(), data)

    def test_nested_dictionaries(self):
        """Preserve nested configuration dictionaries."""
        data = {
            "server": {
                "network": {
                    "port": 8000.0,
                },
            },
        }
        write_yaml(data, self.output)
        self.assertEqual(self.read_yaml(), data)

    def test_creates_parent_directory(self):
        """Create missing directories for the output path."""
        self.output = self.output.parent / "nested" / "result.yaml"
        write_yaml({"value": 1.0}, self.output)
        self.assertTrue(self.output.is_file())

    def test_preserves_key_order(self):
        """Keep configuration keys in their original order."""
        data = {"zebra": 1.0, "alpha": 2.0}
        write_yaml(data, self.output)
        content = self.output.read_text(encoding="utf-8")
        self.assertLess(content.index("zebra"), content.index("alpha"))

    def test_empty_dictionary(self):
        """Write an empty dictionary as valid YAML."""
        write_yaml({}, self.output)
        self.assertEqual(self.read_yaml(), {})

    def test_unicode_output(self):
        """Write Unicode text using UTF-8 encoding."""
        data = {"message": "Привет"}
        write_yaml(data, self.output)
        self.assertEqual(self.read_yaml(), data)


if __name__ == "__main__":
    unittest.main()
