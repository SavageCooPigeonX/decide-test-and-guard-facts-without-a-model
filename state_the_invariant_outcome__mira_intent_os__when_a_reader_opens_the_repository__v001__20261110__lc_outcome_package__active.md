# decide_test_and_guard_facts_without_a_model

One repository. One invariant outcome.

> At a rebase, the facts about tests and guards are read from the files with no model, and are kept apart
> from any model judgment.

The intent key is the leading slug of the test file:

```
decide_test_and_guard_facts_without_a_model
```

It lives in `intent_keys/decide_test_and_guard_facts_without_a_model__mira_intent_os__when_a_rebase_reads_test_files__v001__20261110__lc_outcome_package__active.py`.

## What the outcome decides

Given the test file before the work, the test file after the work, and the diff of any other test file, the
implementation lists these facts with no model:

- an assert removed from the intent key's own test;
- an assert removed from another key's test by its diff;
- a `TEST_GUARDS` row removed;
- a guard's `purpose_contract` or `falsifiable_boundary` text changed;
- a test function with no assert.

The facts are recorded only. They refuse nothing, call no model, move no test, rename no file, and write
nothing.

## Falsifiable boundary

The outcome fails if:

- a deleted assertion in the key's own test or in another key's test is not listed;
- a removed guard row or changed guard outcome text is not listed;
- a test with no assert is not listed;
- a moved assert or a pure addition lists a fact;
- the same texts give a different answer;
- the facts claim to refuse anything or to call a model.

## File-purpose map

Every file serves the one outcome above. There is no shared utility module and no second purpose.

| File | Its single purpose |
|---|---|
| `read_test_and_guard_facts__…__active.py` | Reads the facts from the files. The only implementation. |
| `intent_keys/decide_test_and_guard_facts_without_a_model__…__active.py` | The intent key. Proves the outcome and its boundary. |
| `state_the_invariant_outcome__…__active.md` | States the invariant outcome, the boundary, and the file-purpose map. |

## Run it

The intent key is the only test file. Pass it directly, because the intent-key filename carries the full
purpose grammar rather than pytest's default `test_` prefix:

```bash
python -m pytest intent_keys/decide_test_and_guard_facts_without_a_model__mira_intent_os__when_a_rebase_reads_test_files__v001__20261110__lc_outcome_package__active.py
```

## Why the names are long

The file grammar is `<purpose>__<domain>__when_<trigger>__v<version>__<date>__lc_<surface>__<state>`. The
leading `<purpose>` token is the slug of the invariant outcome. The rest of the name states the domain, the
trigger, the version, the date, the surface, and the lifecycle state. The intent key and the implementation
share the same purpose token because they serve the same one outcome.

888 · christ is king
