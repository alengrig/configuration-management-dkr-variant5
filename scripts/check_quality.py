"""Check source-code restrictions from the assignment."""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_LINES = 1000
MAX_LINE_LENGTH = 80
MAX_FUNCTION_LINES = 40
MAX_ARGUMENTS = 7


def check_lines(path, source):
    """Check file length and Python line lengths."""
    errors = []
    lines = source.splitlines()

    if len(lines) > MAX_FILE_LINES:
        errors.append(f"{path}: файл длиннее 1000 строк")

    for number, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            errors.append(f"{path}:{number}: строка длиннее 80 символов")

    return errors


def check_function(path, node):
    """Check function length, arguments, names, and documentation."""
    errors = []
    length = node.end_lineno - node.lineno + 1
    arguments = node.args
    count = len(arguments.posonlyargs) + len(arguments.args)
    count += len(arguments.kwonlyargs)
    count += int(arguments.vararg is not None)
    count += int(arguments.kwarg is not None)

    if length > MAX_FUNCTION_LINES:
        errors.append(f"{path}:{node.lineno}: функция >40 строк")
    if count > MAX_ARGUMENTS:
        errors.append(f"{path}:{node.lineno}: аргументов >7")
    if not ast.get_docstring(node):
        errors.append(f"{path}:{node.lineno}: отсутствует docstring")
    unittest_method = (
        path.parts[0] == "tests"
        and node.name in {
            "setUp",
            "tearDown",
            "setUpClass",
            "tearDownClass",
        }
    )
    valid_name = re.fullmatch(r"_*[a-z][a-z0-9_]*", node.name)

    if not (valid_name or unittest_method):
        errors.append(f"{path}:{node.lineno}: неверное имя функции")

    return errors


def check_class(path, node):
    """Check class naming and documentation."""
    errors = []

    if not re.fullmatch(r"[A-Z][a-zA-Z0-9]*", node.name):
        errors.append(f"{path}:{node.lineno}: неверное имя класса")

    if not ast.get_docstring(node):
        errors.append(f"{path}:{node.lineno}: нет docstring класса")

    return errors


def check_comparison(path, node):
    """Detect magic numeric literals in comparisons."""
    errors = []
    operands = [node.left, *node.comparators]

    for operand in operands:
        if isinstance(operand, ast.Constant):
            number = operand.value

            if type(number) in (int, float) and number not in (0, 1):
                errors.append(
                    f"{path}:{node.lineno}: магическое число"
                )

    return errors


def check_tree(path, source):
    """Check functions, classes, and numeric comparisons."""
    errors = []

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            errors.extend(check_function(path, node))

        elif isinstance(node, ast.ClassDef):
            errors.extend(check_class(path, node))

        elif isinstance(node, ast.Compare):
            errors.extend(check_comparison(path, node))

    return errors


def main():
    """Inspect all project Python source and test files."""
    paths = []
    for folder in ("src", "tests", "scripts"):
        paths.extend((ROOT / folder).rglob("*.py"))

    errors = []

    for path in sorted(paths):
        source = path.read_text(encoding="utf-8")
        errors.extend(check_lines(path.relative_to(ROOT), source))
        errors.extend(check_tree(path.relative_to(ROOT), source))

    if errors:
        print("\n".join(errors))
        return 1

    print(f"Качество кода: OK. Проверено файлов: {len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
