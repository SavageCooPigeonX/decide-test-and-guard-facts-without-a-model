"""Invariant outcome: at a rebase, the facts about tests and guards are read from the files with no model,
and are kept apart from any model judgment.

The facts are:

- an assert removed from the intent key's own test;
- an assert removed from another key's test by its diff;
- a ``TEST_GUARDS`` row removed;
- a guard's ``purpose_contract`` or ``falsifiable_boundary`` text changed;
- a test function with no assert.

This module decides and records only. It refuses nothing, calls no model, moves no test, renames no file,
and writes nothing.

Every function in this file serves that one outcome. There is no utility module and no second purpose.
"""
from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Mapping

SCHEMA = "deterministic_guard_evidence/v1"
ASSERT_REMOVED = "assert_removed"
GUARD_ROW_REMOVED = "guard_row_removed"
GUARD_OUTCOME_TEXT_CHANGED = "guard_outcome_text_changed"
TEST_WITHOUT_ASSERT = "test_without_assert"
KINDS = (ASSERT_REMOVED, GUARD_ROW_REMOVED, GUARD_OUTCOME_TEXT_CHANGED, TEST_WITHOUT_ASSERT)
# The two guard fields that state what a test proves and where it fails.
OUTCOME_FIELDS = ("purpose_contract", "falsifiable_boundary")
TEST_ROOT = "tests/"


def _tree(source):
    try:
        return ast.parse(str(source or ""))
    except SyntaxError:
        return None


def _asserts(tree):
    return Counter(ast.unparse(node) for node in ast.walk(tree) if isinstance(node, ast.Assert))


def _guards(tree):
    """``TEST_GUARDS`` rows by guard_id, read as a literal; the test is never imported."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TEST_GUARDS" for t in node.targets):
            try:
                rows = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                return {}
            return {str(row.get("guard_id")): row for row in rows if isinstance(row, Mapping) and row.get("guard_id")}
    return {}


def _checks_something(function):
    """True when a test function holds an assert, or calls something named for asserting or raising."""
    for node in ast.walk(function):
        if isinstance(node, ast.Assert):
            return True
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if "assert" in name.lower() or name == "raises":
                return True
    return False


def own_test_facts(path, before, after):
    """Facts about the intent key's own test, from its text before and after the work."""
    old, new = _tree(before), _tree(after)
    if new is None:
        return [{"kind": "unreadable_test", "path": path, "detail": "test_after does not parse"}]
    facts = []
    if old is not None and str(before or "").strip():
        for line, count in sorted((_asserts(old) - _asserts(new)).items()):
            facts.append({"kind": ASSERT_REMOVED, "path": path, "own_key": True, "line": line, "times": count})
        was, now = _guards(old), _guards(new)
        for guard_id in sorted(set(was) - set(now)):
            facts.append({"kind": GUARD_ROW_REMOVED, "path": path, "guard_id": guard_id})
        for guard_id in sorted(set(was) & set(now)):
            for field in OUTCOME_FIELDS:
                if was[guard_id].get(field) != now[guard_id].get(field):
                    facts.append({"kind": GUARD_OUTCOME_TEXT_CHANGED, "path": path, "guard_id": guard_id,
                                  "field": field, "before": was[guard_id].get(field), "after": now[guard_id].get(field)})
    for node in new.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test") \
                and not _checks_something(node):
            facts.append({"kind": TEST_WITHOUT_ASSERT, "path": path, "test": node.name})
    return facts


def _changed_lines(diff_text):
    removed, added = [], []
    for line in str(diff_text or "").splitlines():
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("-"):
            removed.append(line[1:].strip())
        elif line.startswith("+"):
            added.append(line[1:].strip())
    return removed, added


def other_test_facts(path, diff_text):
    """Assert lines a diff takes out of another key's test and does not put back.

    Only the diff of that file reaches the rebase, so this reads the diff: a removed line that begins with
    ``assert`` and is not among the added lines. A line that only moved is in both and is not a fact.
    """
    removed, added = _changed_lines(diff_text)
    left = Counter(line for line in removed if line.startswith("assert ")) - Counter(
        line for line in added if line.startswith("assert "))
    return [{"kind": ASSERT_REMOVED, "path": path, "own_key": False, "line": line, "times": count}
            for line, count in sorted(left.items())]


def guard_evidence(intent_key, test_before, test_after, diffs):
    """Every fact the test files show for this rebase, kept apart from any model's judgment.

    ``intent_key`` is the key's own test path. ``diffs`` maps each changed path to its diff text.
    Returns the facts, a count per kind, and ``refuses`` False: these facts are recorded only.
    """
    intent_key = str(intent_key or "").replace("\\", "/")
    facts = own_test_facts(intent_key, test_before, test_after)
    for path, text in sorted((diffs or {}).items()):
        path = str(path).replace("\\", "/")
        if path != intent_key and path.startswith(TEST_ROOT) and path.endswith(".py"):
            facts += other_test_facts(path, text)
    counts = Counter(fact["kind"] for fact in facts)
    return {"schema": SCHEMA, "model_called": False,
            "read_from": "test_before_test_after_and_test_file_diffs",
            "facts": facts, "counts": {kind: counts.get(kind, 0) for kind in KINDS},
            "refuses": False, "recorded_because": "append_record_only"}
