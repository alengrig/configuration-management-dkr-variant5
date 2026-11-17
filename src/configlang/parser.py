"""Parse the configuration language using Lark."""

from pathlib import Path

from lark import Lark
from lark.exceptions import UnexpectedInput

GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")

PARSER = Lark(
    GRAMMAR_PATH.read_text(encoding="utf-8"),
    parser="lalr",
    propagate_positions=True,
)


def parse_source(source):
    """Parse source text and report syntax errors."""
    try:
        return PARSER.parse(source)
    except UnexpectedInput as error:
        location = (
            f"строка {error.line}, столбец {error.column}"
        )
        context = error.get_context(source, span=30).strip()
        raise ValueError(
            f"Синтаксическая ошибка ({location}):\n{context}"
        ) from error
