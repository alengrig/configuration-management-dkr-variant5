"""Tests for the command-line interface and launcher."""

import subprocess
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import yaml

from configlang.main import main, parse_arguments, translate


class CliTests(unittest.TestCase):
    """Verify command-line behavior and exit statuses."""

    def setUp(self):
        """Create a temporary output path."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name) / "result.yaml"

    def run_main(self, source, output=None):
        """Run main with controlled input and captured output."""
        destination = output if output is not None else self.output

        with patch("sys.stdin", StringIO(source)):
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                with patch("sys.stderr", new_callable=StringIO) as stderr:
                    status = main(["--output", str(destination)])

        return status, stdout.getvalue(), stderr.getvalue()

    def run_script(self, source):
        """Run the actual shell launcher."""
        root = Path(__file__).resolve().parents[1]

        return subprocess.run(
            [str(root / "run.sh"), "--output", str(self.output)],
            input=source,
            text=True,
            capture_output=True,
            cwd=root,
            check=False,
        )

    def test_output_argument(self):
        """Accept the output file argument."""
        options = parse_arguments(["--output", "result.yaml"])
        self.assertEqual(options.output, "result.yaml")

    def test_missing_output_argument(self):
        """Require an output file argument."""
        with patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit) as error:
                parse_arguments([])

        self.assertEqual(error.exception.code, 2)

    def test_translate_creates_yaml(self):
        """Translate a configuration into valid YAML."""
        source = "@{ port = 1.5e+3; }"
        translate(source, self.output)
        data = yaml.safe_load(self.output.read_text(encoding="utf-8"))
        self.assertEqual(data, {"port": 1500.0})

    def test_main_reads_standard_input(self):
        """Read configuration text from standard input."""
        source = "global speed = 8e+3; @{ port = ^[speed]; }"
        status, stdout, stderr = self.run_main(source)

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("YAML created:", stdout)
        self.assertTrue(self.output.is_file())

    def test_main_reports_syntax_error(self):
        """Report invalid input and return a failure status."""
        status, _, stderr = self.run_main("@{ port = 1500; }")

        self.assertEqual(status, 1)
        self.assertIn("Синтаксическая ошибка", stderr)
        self.assertFalse(self.output.exists())

    def test_main_reports_unknown_constant(self):
        """Report an undefined constant."""
        status, _, stderr = self.run_main("@{ port = ^[missing]; }")

        self.assertEqual(status, 1)
        self.assertIn("Неизвестная константа", stderr)

    def test_main_reports_write_error(self):
        """Report a failure to write the output file."""
        status, _, stderr = self.run_main(
            "@{}",
            output=self.output.parent,
        )

        self.assertEqual(status, 1)
        self.assertIn("Ошибка:", stderr)

    def test_run_script_success(self):
        """Convert standard input using the shell launcher."""
        result = self.run_script("@{ port = 2e+3; }")

        self.assertEqual(result.returncode, 0, result.stderr)
        data = yaml.safe_load(self.output.read_text(encoding="utf-8"))
        self.assertEqual(data, {"port": 2000.0})

    def test_run_script_failure(self):
        """Return an error for invalid input through run.sh."""
        result = self.run_script("@{ port = 100; }")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Ошибка:", result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
