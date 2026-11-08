"""Grader tests: it must accept the reference solution (and answers just inside the tolerance), reject answers just
outside it, reject every known wrong-method value (with the right label), and reject malformed output."""
import json, os, sys
import pytest
sys.path.insert(0, os.path.dirname(__file__))
import grade

IDS = list(grade.TASKS)


def ans(task_id, v):
    return f'reasoning...\nANSWER: {json.dumps({grade.TASKS[task_id]["key"]: v})}'


@pytest.mark.parametrize("tid", IDS)
def test_reference_passes(tid):
    assert grade.grade(tid, ans(tid, grade.EXPECTED[tid]["ref"]))["ok"]


@pytest.mark.parametrize("tid", IDS)
def test_tolerance_edges(tid):
    ref, tol = grade.EXPECTED[tid]["ref"], grade.TASKS[tid]["tol"]
    step = tol["value"] * abs(ref) if tol["type"] == "rel" else tol["value"]
    for s in (+1, -1):
        assert grade.grade(tid, ans(tid, ref + s * 0.98 * step))["ok"]
        assert not grade.grade(tid, ans(tid, ref + s * 1.5 * step))["ok"]


@pytest.mark.parametrize("tid", IDS)
def test_wrong_methods_fail_and_are_labelled(tid):
    for name, w in grade.EXPECTED[tid]["wrong"].items():
        r = grade.grade(tid, ans(tid, w))
        assert not r["ok"], (tid, name)
        assert r["label"] == "wrong method: " + name, (tid, name, r)


@pytest.mark.parametrize("tid", IDS)
def test_malformed_output_fails(tid):
    key, ref = grade.TASKS[tid]["key"], grade.EXPECTED[tid]["ref"]
    bad = [
        "",                                              # empty
        f"The answer is {ref}",                          # no ANSWER line
        f'ANSWER: {{"{key}": "{ref}"}}',                 # string, not a number
        f'ANSWER: {{"wrong_key": {ref}}}',               # wrong key
        f"ANSWER: {{'{key}': {ref}}}",                   # not JSON (single quotes)
        f'ANSWER: {{"{key}": NaN}}',                     # NaN is rejected by the finite check
    ]
    for b in bad:
        assert not grade.grade(tid, b)["ok"], b


@pytest.mark.parametrize("tid", IDS)
def test_listing_every_candidate_does_not_pass(tid):
    """A response that mentions the reference value in prose but answers something else must fail."""
    ref = grade.EXPECTED[tid]["ref"]
    wrongs = list(grade.EXPECTED[tid]["wrong"].values())
    wrong = wrongs[0] if wrongs else 1.5 * ref
    text = f"candidates: {ref}, {wrong}\n" + ans(tid, wrong)
    assert not grade.grade(tid, text)["ok"]


def test_last_answer_line_wins():
    tid = IDS[0]
    ref = grade.EXPECTED[tid]["ref"]
    assert grade.grade(tid, ans(tid, 0.9) + "\n" + ans(tid, ref))["ok"]
    assert not grade.grade(tid, ans(tid, ref) + "\n" + ans(tid, 0.9))["ok"]
