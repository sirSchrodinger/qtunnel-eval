"""Code-based grader. Outcome only: parse the last `ANSWER: {"key": number}` line and compare the number with the
reference within the task tolerance. If the answer misses, it is also compared with the values that common wrong
methods give (reference/expected.json) so every failure is labelled when possible."""
import json, math, os, re

HERE = os.path.dirname(__file__)
TASKS = {t["id"]: t for t in json.load(open(os.path.join(HERE, "..", "tasks", "tasks.json")))}
EXPECTED = json.load(open(os.path.join(HERE, "..", "reference", "expected.json")))

_ANS = re.compile(r"ANSWER\s*:\s*(\{[^{}]*\})")


def parse_answer(text: str, key: str):
    """Return (value, error). Last ANSWER line wins; value must be a finite real number (JSON)."""
    hits = _ANS.findall(text or "")
    if not hits:
        return None, "no ANSWER line"
    try:
        obj = json.loads(hits[-1])
    except Exception:
        return None, "ANSWER is not valid JSON"
    if key not in obj:
        return None, f"missing key {key!r}"
    v = obj[key]
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None, "value is not a finite number"
    return float(v), None


def within(x: float, ref: float, tol: dict) -> bool:
    if tol["type"] == "rel":
        return abs(x - ref) <= tol["value"] * abs(ref)
    return abs(x - ref) <= tol["value"]


def grade(task_id: str, text: str) -> dict:
    t = TASKS[task_id]
    e = EXPECTED[task_id]
    v, err = parse_answer(text, t["key"])
    if err:
        return {"ok": False, "value": None, "label": "format: " + err}
    if within(v, e["ref"], t["tol"]):
        return {"ok": True, "value": v, "label": "correct"}
    for name, w in e["wrong"].items():
        if within(v, w, t["tol"]):
            return {"ok": False, "value": v, "label": "wrong method: " + name}
    return {"ok": False, "value": v, "label": "wrong: other"}
