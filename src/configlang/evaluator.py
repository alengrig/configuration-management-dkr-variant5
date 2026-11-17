"""Evaluate configuration values and compile-time constants."""

import math


def evaluate_number(node):
    """Convert a scientific-notation number to a float."""
    value = float(node.children[0])

    if not math.isfinite(value):
        raise ValueError("Число вне допустимого диапазона")

    return value


def evaluate_reference(node, constants):
    """Replace a constant reference with its value."""
    name = str(node.children[0])

    if name not in constants:
        raise ValueError(f"Неизвестная константа: {name}")

    return constants[name]


def evaluate_dictionary(node, constants):
    """Evaluate all entries of a possibly nested dictionary."""
    result = {}

    for entry in node.children:
        name = str(entry.children[0])

        if name in result:
            raise ValueError(f"Повторяющийся ключ: {name}")

        result[name] = evaluate_value(entry.children[1], constants)

    return result


def evaluate_value(node, constants):
    """Evaluate one value from the Lark parse tree."""
    if node.data == "number":
        return evaluate_number(node)

    if node.data == "reference":
        return evaluate_reference(node, constants)

    if node.data == "dictionary":
        return evaluate_dictionary(node, constants)

    raise ValueError(f"Неизвестная конструкция: {node.data}")


def evaluate_tree(tree):
    """Evaluate declarations and the final configuration."""
    constants = {}

    for declaration in tree.children[:-1]:
        name = str(declaration.children[0])

        if name in constants:
            raise ValueError(f"Константа уже объявлена: {name}")

        value = declaration.children[1]
        constants[name] = evaluate_value(value, constants)

    return evaluate_value(tree.children[-1], constants)
