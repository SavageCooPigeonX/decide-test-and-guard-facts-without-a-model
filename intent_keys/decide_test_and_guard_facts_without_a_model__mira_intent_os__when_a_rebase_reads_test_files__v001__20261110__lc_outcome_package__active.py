"""Intent key: decide_test_and_guard_facts_without_a_model.

Invariant outcome: at a rebase, the facts about tests and guards are read from the files with no model,
and are kept apart from any model judgment.

Falsifiable boundary: fails if a deleted assertion in the key's own test or in another key's test is not
listed, if a removed guard row or changed guard outcome text is not listed, if a test with no assert is not
listed, if a moved assert or a pure addition lists a fact, if the same texts give a different answer, or if
the facts claim to refuse anything or to call a model.

This file is the intent key. Its leading slug is the invariant outcome. The implementation it guards lives
in exactly one file, ``read_test_and_guard_facts__…``. No other file serves another outcome.
"""
import importlib
import json
import sys
from pathlib import Path

# The intent key lives one directory below the single implementation file. Put the repository root first
# so the one implementation is importable without a shared package or a second purpose.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

facts = importlib.import_module(
    'read_test_and_guard_facts__mira_intent_os__when_a_rebase_reads_test_files__v001__20261110__lc_outcome_package__active')

TEST_GUARDS = [{
    'schema': 'operator_test_guard/v1',
    'test_name': 'test_test_and_guard_facts_are_decided_without_a_model',
    'guard_id': 'GUARD.TEST.AND.GUARD.FACTS.DECIDED.WITHOUT.A.MODEL',
    'purpose_contract': 'deterministic_guard_evidence@v1',
    'behavioral_test_prompt': 'At a rebase, list from the test files alone: an assert removed from this key\'s '
                              'test or another key\'s test, a TEST_GUARDS row removed, a guard\'s purpose_contract '
                              'or falsifiable_boundary text changed, and a test function with no assert.',
    'operator_intent': 'The facts about tests and guards are read from the files with no model and kept apart '
                       'from any model judgment.',
    'protected_function_identities': ['guard_evidence', 'own_test_facts', 'other_test_facts'],
    'falsifiable_boundary': 'Fails if a deleted assertion is not listed, if a moved assert or a pure addition '
                            'lists a fact, if the same texts give a different answer, or if the facts refuse or '
                            'call a model.',
    'proving_receipt_type': 'pytest_assertion',
}]

KEY = 'tests/the_gate_is_oiled__fixture__when_it_squeaks__v001__20261110__lc_fixture__staged.py'
OTHER = 'tests/the_hinge_holds__fixture__when_the_gate_swings__v001__20261110__lc_fixture__active.py'
WORK = 'fixture_domain/oil_the_gate__fixture__when_it_squeaks__v001__20261110__lc_fixture__active.py'

BEFORE = '''TEST_GUARDS = [
    {'guard_id': 'G.OIL', 'purpose_contract': 'gate@v1', 'falsifiable_boundary': 'Fails if the gate squeaks.'},
    {'guard_id': 'G.LATCH', 'purpose_contract': 'latch@v1', 'falsifiable_boundary': 'Fails if the latch slips.'},
]


def test_the_gate_is_oiled():
    assert oil('gate') == 'quiet'
    assert oil('latch') == 'quiet'
'''

# One assert gone, one guard row gone, one boundary rewritten, and a test that checks nothing.
BENT = '''TEST_GUARDS = [
    {'guard_id': 'G.OIL', 'purpose_contract': 'gate@v1', 'falsifiable_boundary': 'Fails if the gate is missing.'},
]


def test_the_gate_is_oiled():
    assert oil('gate') == 'quiet'


def test_the_latch_runs():
    oil('latch')
'''

# The same asserts in another order, one more assert and one more guard: nothing was taken away.
ADDED = '''TEST_GUARDS = [
    {'guard_id': 'G.OIL', 'purpose_contract': 'gate@v1', 'falsifiable_boundary': 'Fails if the gate squeaks.'},
    {'guard_id': 'G.LATCH', 'purpose_contract': 'latch@v1', 'falsifiable_boundary': 'Fails if the latch slips.'},
    {'guard_id': 'G.HINGE', 'purpose_contract': 'hinge@v1', 'falsifiable_boundary': 'Fails if the hinge rusts.'},
]


def test_the_gate_is_oiled():
    assert oil('latch') == 'quiet'
    assert oil('gate') == 'quiet'
    assert oil('hinge') == 'quiet'
'''

OTHER_DIFF = '''--- a/tests/the_hinge_holds.py
+++ b/tests/the_hinge_holds.py
@@ -4,5 +4,4 @@
 def test_the_hinge_holds():
-    assert swing('hinge') == 'held'
-    assert swing('gate') == 'held'
+    assert swing('gate') == 'held'
     swing('post')
'''

WORK_DIFF = "--- a/work.py\n+++ b/work.py\n@@ -1 +1,2 @@\n def oil(part):\n+    return 'quiet'\n-    assert part\n"


def _kinds(evidence):
    return [(f['kind'], f.get('path'), f.get('line') or f.get('guard_id') or f.get('test'))
            for f in evidence['facts']]


def test_test_and_guard_facts_are_decided_without_a_model():
    bent = facts.guard_evidence(KEY, BEFORE, BENT, {KEY: 'ignored: the own test is read whole',
                                                    OTHER: OTHER_DIFF, WORK: WORK_DIFF})
    assert bent['model_called'] is False and bent['refuses'] is False
    assert bent['schema'] == 'deterministic_guard_evidence/v1'
    assert bent['read_from'] == 'test_before_test_after_and_test_file_diffs'
    assert bent['recorded_because'] == 'append_record_only'
    assert _kinds(bent) == [
        ('assert_removed', KEY, "assert oil('latch') == 'quiet'"),
        ('guard_row_removed', KEY, 'G.LATCH'),
        ('guard_outcome_text_changed', KEY, 'G.OIL'),
        ('test_without_assert', KEY, 'test_the_latch_runs'),
        ('assert_removed', OTHER, "assert swing('hinge') == 'held'"),
    ]
    changed = bent['facts'][2]
    assert (changed['field'], changed['before'], changed['after']) == (
        'falsifiable_boundary', 'Fails if the gate squeaks.', 'Fails if the gate is missing.')
    assert [f['own_key'] for f in bent['facts'] if f['kind'] == 'assert_removed'] == [True, False]
    assert bent['counts'] == {'assert_removed': 2, 'guard_row_removed': 1,
                              'guard_outcome_text_changed': 1, 'test_without_assert': 1}
    # An assert line removed from a file that is not a test is not a guard fact.
    assert not any(f.get('path') == WORK for f in bent['facts'])

    # A pure addition, a reordering and a new intent key list nothing.
    assert facts.guard_evidence(KEY, BEFORE, ADDED, {KEY: ''})['facts'] == []
    assert facts.guard_evidence(KEY, '', ADDED, {KEY: ADDED})['facts'] == []
    assert facts.guard_evidence(KEY, BEFORE, BEFORE, {})['counts'] == dict.fromkeys(facts.KINDS, 0)
    # The same texts give the same answer every time.
    assert facts.guard_evidence(KEY, BEFORE, BENT, {OTHER: OTHER_DIFF}) == facts.guard_evidence(
        KEY, BEFORE, BENT, {OTHER: OTHER_DIFF})
    # The receipt is plain data: no model object, no callable, no refusal.
    assert json.loads(json.dumps(bent)) == bent
    assert not any(isinstance(value, (bytes, set, frozenset)) for value in bent.values())
