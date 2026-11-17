"""Tests for configuration evaluation."""

import unittest

from configlang.evaluator import evaluate_tree
from configlang.parser import parse_source


class EvaluatorTests(unittest.TestCase):
    """Verify constants, numbers, and nested dictionaries."""

    def evaluate(self, source):
        """Parse and evaluate a configuration string."""
        return evaluate_tree(parse_source(source))

    def test_positive_number(self):
        """Evaluate scientific notation."""
        result = self.evaluate("@{ port = 1.5e+3; }")
        self.assertEqual(result, {"port": 1500.0})

    def test_negative_number(self):
        """Evaluate a negative number."""
        result = self.evaluate("@{ limit = -2e-1; }")
        self.assertEqual(result, {"limit": -0.2})

    def test_empty_dictionary(self):
        """Evaluate an empty dictionary."""
        self.assertEqual(self.evaluate("@{}"), {})

    def test_nested_dictionary(self):
        """Evaluate dictionaries with several nesting levels."""
        source = """
        @{
            outer = @{
                middle = @{
                    inner = 3e+0;
                };
            };
        }
        """
        expected = {
            "outer": {"middle": {"inner": 3.0}}
        }
        self.assertEqual(self.evaluate(source), expected)

    def test_constant_reference(self):
        """Replace a reference with a constant value."""
        source = "global speed = 2e+3; @{ port = ^[speed]; }"
        self.assertEqual(self.evaluate(source), {"port": 2000.0})

    def test_chained_constants(self):
        """Allow references to previously declared constants."""
        source = """
        global first = 2e+0;
        global second = ^[first];
        @{ value = ^[second]; }
        """
        self.assertEqual(self.evaluate(source), {"value": 2.0})

    def test_dictionary_constant(self):
        """Support a dictionary stored in a constant."""
        source = """
        global limits = @{ maximum = 5e+2; };
        @{ settings = ^[limits]; }
        """
        expected = {"settings": {"maximum": 500.0}}
        self.assertEqual(self.evaluate(source), expected)

    def test_declarations_not_in_output(self):
        """Exclude constant declarations from the result."""
        source = "global speed = 2e+0; @{}"
        self.assertEqual(self.evaluate(source), {})

    def test_unknown_constant(self):
        """Reject a reference to an undefined constant."""
        with self.assertRaisesRegex(ValueError, "Неизвестная"):
            self.evaluate("@{ value = ^[missing]; }")

    def test_forward_reference(self):
        """Reject references to constants declared later."""
        source = """
        global first = ^[second];
        global second = 1e+0;
        @{ value = ^[first]; }
        """
        with self.assertRaises(ValueError):
            self.evaluate(source)

    def test_duplicate_constant(self):
        """Reject repeated constant declarations."""
        source = """
        global speed = 1e+0;
        global speed = 2e+0;
        @{}
        """
        with self.assertRaisesRegex(ValueError, "уже объявлена"):
            self.evaluate(source)

    def test_duplicate_dictionary_key(self):
        """Reject repeated keys inside a dictionary."""
        source = "@{ port = 1e+0; port = 2e+0; }"
        with self.assertRaisesRegex(ValueError, "Повторяющийся"):
            self.evaluate(source)

    def test_number_overflow(self):
        """Reject a scientific number that becomes infinite."""
        with self.assertRaises(ValueError):
            self.evaluate("@{ value = 1e9999; }")

    def test_case_sensitive_names(self):
        """Distinguish uppercase and lowercase identifiers."""
        source = "@{ Speed = 1e+0; speed = 2e+0; }"
        expected = {"Speed": 1.0, "speed": 2.0}
        self.assertEqual(self.evaluate(source), expected)


if __name__ == "__main__":
    unittest.main()
