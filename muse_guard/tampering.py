"""Adapted from Unfoolable test-tampering.ts multiset comparison.
Changed: Python AST only; no ast-grep process, host paths, or runtime dependencies.
"""
import ast
from collections import Counter


def _always_true(node):
    if isinstance(node, ast.Constant):
        return bool(node.value)
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
        a, b = node.left, node.comparators[0]
        if isinstance(a, ast.Constant) and isinstance(b, ast.Constant):
            if isinstance(node.ops[0], ast.Eq):
                return a.value == b.value
    return False


def _matches(source):
    assertions, skips, vacuous = [], [], []
    for n in ast.walk(ast.parse(source)):
        key = ast.dump(n, include_attributes=False)
        if isinstance(n, ast.Assert):
            assertions.append(key)
            if _always_true(n.test):
                vacuous.append(key)
        if isinstance(n, ast.Call):
            name = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
            if name.startswith("assert") or (isinstance(n.func, ast.Attribute) and name == "check"):
                assertions.append(key)
                if name in ("assertTrue", "assert_") and n.args and _always_true(n.args[0]):
                    vacuous.append(key)
                if name == "assertEqual" and len(n.args) >= 2 and all(isinstance(x, ast.Constant) for x in n.args[:2]) and n.args[0].value == n.args[1].value:
                    vacuous.append(key)
            if name in ("skip", "skipIf", "skipUnless", "skipTest", "xfail"):
                skips.append(key)
    return Counter(assertions), Counter(skips), Counter(vacuous)


def compare_tests(original, candidate):
    try:
        old, old_skip, old_true = _matches(original)
        new, new_skip, new_true = _matches(candidate)
    except (SyntaxError, ValueError, RecursionError):
        return ["Test source could not be parsed"]
    flags = []
    for counts, message in ((old - new, "Assertion deleted or expectation changed"),
                            (new_skip - old_skip, "New test skip"),
                            (new_true - old_true, "New always-true assertion")):
        flags.extend([message] * sum(counts.values()))
    return flags
