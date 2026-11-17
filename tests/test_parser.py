"""Tests for configuration language syntax."""

import unittest

from configlang.parser import parse_source


class ParserTests(unittest.TestCase):
    """Verify parsing with the Lark grammar."""

    def test_positive_scientific_number(self):
        """Accept a positive number with an exponent."""
        tree = parse_source("@{ port = +1.5e+3; }")
        self.assertEqual(tree.data, "start")

    def test_negative_scientific_number(self):
        """Accept a negative number with an exponent."""
        tree = parse_source("@{ limit = -2e-1; }")
        self.assertEqual(tree.data, "start")

    def test_nested_dictionaries(self):
        """Accept dictionaries inside other dictionaries."""
        source = "@{ outer = @{ inner = 1e+0; }; }"
        tree = parse_source(source)
        self.assertEqual(tree.pretty().count("dictionary"), 2)

    def test_multiline_comment(self):
        """Ignore a comment spanning several lines."""
        source = "#| first line\nsecond line |#\n@{ port = 1e+0; }"
        tree = parse_source(source)
        self.assertEqual(tree.data, "start")

    def test_constant_declaration(self):
        """Accept a global constant declaration."""
        source = "global speed = 2e+0; @{ port = ^[speed]; }"
        tree = parse_source(source)
        self.assertEqual(tree.data, "start")

    def test_empty_dictionary(self):
        """Accept a dictionary without entries."""
        tree = parse_source("@{}")
        self.assertEqual(tree.data, "start")

    def test_number_without_exponent(self):
        """Reject a number without scientific notation."""
        with self.assertRaises(ValueError):
            parse_source("@{ port = 1500; }")

    def test_invalid_identifier(self):
        """Reject names containing underscores."""
        with self.assertRaises(ValueError):
            parse_source("@{ bad_name = 1e+0; }")

    def test_missing_semicolon(self):
        """Reject a dictionary entry without a semicolon."""
        with self.assertRaises(ValueError):
            parse_source("@{ port = 1e+0 }")

    def test_unexpected_text(self):
        """Reject additional text after the configuration."""
        with self.assertRaises(ValueError):
            parse_source("@{} unexpected")

    def test_error_contains_location(self):
        """Include the line and column in syntax errors."""
        with self.assertRaisesRegex(ValueError, "строка 1"):
            parse_source("@{ port = 1500; }")


if __name__ == "__main__":
    unittest.main()
