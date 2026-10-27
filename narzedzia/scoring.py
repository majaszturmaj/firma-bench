"""Deterministic scoring of JSON answers against task checks (sprawdzenia).

Check types (field `typ`):
  rowne        — field equals `wartosc` (numbers, dates, booleans normalised); `dopuszczalne` = extra accepted values
  zawiera      — regex(es) `wzorce` found in field(s) `pole` (any; `wszystkie: true` → all); no `pole` = whole answer
  nie_zawiera  — none of the regexes found in field(s) / whole answer (raw text incl. unparsed output)
  pusty        — field is null/empty/"brak…"
  cytuje       — `zrodla` mention the document(s) `dokumenty` (`tryb: dowolny` → any one is enough)
  element_listy — in list field `pole`, an element whose `klucz` matches `wzorzec` has `pole_elementu` == `wartosc`
                  (or one of `dopuszczalne`)
Each check has `waga` (default 1) and optionally `krytyczne: true`.
Task success (Agent Goal Accuracy) = all critical checks pass AND score ≥ PROG_SUKCESU.
"""

import json
import re
import unicodedata
from datetime import date

PROG_SUKCESU = 0.75
MONTHS = {"stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6, "lipca": 7,
          "sierpnia": 8, "września": 9, "października": 10, "listopada": 11, "grudnia": 12}


# --------------------------------------------------------------------------- parsing

def parse_answer(raw: str):
    """Extract the JSON object from a model reply (tolerates code fences and surrounding prose)."""
    if raw is None:
        return None
    text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)   # reasoning models
    text = re.sub(r"^.*</think>", "", text, flags=re.DOTALL).strip()   # template that opens <think> implicitly
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    for candidate in (text, text[text.find("{"): text.rfind("}") + 1] if "{" in text else ""):
        if not candidate:
            continue
        try:
            obj = json.loads(candidate)
            return obj if isinstance(obj, dict) else {"odpowiedz": obj}
        except json.JSONDecodeError:
            continue
    return None


def get_field(answer: dict, path: str):
    cur = answer
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s).replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


# --------------------------------------------------------------------------- normalisation

def to_bool(v):
    if isinstance(v, bool):
        return v
    s = _norm(as_text(v))
    if re.match(r"^(true|tak|yes|1|prawda)\b", s):
        return True
    if re.match(r"^(false|nie|no|0|fałsz)\b", s):
        return False
    return None


def to_number(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = _norm(as_text(v)).replace(" ", "")
    m = re.search(r"-?\d+(?:[.,]\d+)?", s)
    if not m:
        return None
    return float(m.group(0).replace(",", "."))


def to_date(v):
    s = _norm(as_text(v))
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", s)
    if m:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.search(r"(\d{1,2}) (" + "|".join(MONTHS) + r") (\d{4})", s)
    if m:
        return date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))
    return None


def is_empty(v) -> bool:
    if v in (None, "", [], {}):
        return True
    return bool(re.match(r"^(brak|nie dotyczy|null|none|nieznan|n/?a|-|—)", _norm(as_text(v))))


def equals(actual, expected) -> bool:
    if expected is None:
        return is_empty(actual)
    if isinstance(expected, bool):
        return to_bool(actual) is expected
    if isinstance(expected, (int, float)):
        n = to_number(actual)
        return n is not None and abs(n - float(expected)) < 0.005
    if isinstance(expected, date) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(expected)):
        exp = expected if isinstance(expected, date) else date.fromisoformat(str(expected))
        return to_date(actual) == exp
    return _norm(as_text(actual)) == _norm(str(expected))


# --------------------------------------------------------------------------- checks

def _fields_text(answer, raw, pole) -> str:
    if not pole:
        return _norm(as_text(answer) + " " + (raw or ""))
    fields = pole if isinstance(pole, list) else [pole]
    return _norm(" ".join(as_text(get_field(answer or {}, p)) for p in fields))


def _doc_matchers(doc_id, manifest_index, aliasy):
    names = [doc_id.lower()]
    meta = manifest_index.get(doc_id)
    if meta:
        base = meta["sciezka"].rsplit("/", 1)[-1]
        names += [base.lower(), base.rsplit(".", 1)[0].lower()]
    names += [a.lower() for a in (aliasy or {}).get(doc_id, [])]
    return names


def run_check(check: dict, answer, raw: str, manifest_index: dict, aliasy: dict) -> bool:
    typ = check["typ"]
    if typ == "rowne":
        if answer is None:
            return False
        actual = get_field(answer, check["pole"])
        expected = [check["wartosc"]] + list(check.get("dopuszczalne", []))
        return any(equals(actual, e) for e in expected)
    if typ in ("zawiera", "nie_zawiera"):
        text = _fields_text(answer, raw if typ == "nie_zawiera" and not check.get("pole") else None, check.get("pole"))
        hits = [re.search(w, text, flags=re.IGNORECASE) is not None for w in check["wzorce"]]
        if typ == "nie_zawiera":
            return not any(hits)
        return all(hits) if check.get("wszystkie") else any(hits)
    if typ == "pusty":
        return answer is not None and is_empty(get_field(answer, check["pole"]))
    if typ == "cytuje":
        sources = _norm(as_text(get_field(answer or {}, check.get("pole", "zrodla"))))
        found = [any(m in sources for m in _doc_matchers(d, manifest_index, aliasy)) for d in check["dokumenty"]]
        return any(found) if check.get("tryb") == "dowolny" else all(found)
    if typ == "element_listy":
        items = get_field(answer or {}, check["pole"])
        if not isinstance(items, list):
            return False
        for it in items:
            if isinstance(it, dict) and re.search(check["wzorzec"], as_text(it.get(check["klucz"])), re.IGNORECASE):
                expected = [check["wartosc"]] + list(check.get("dopuszczalne", []))
                return any(equals(it.get(check["pole_elementu"]), e) for e in expected)
        return False
    raise ValueError(f"nieznany typ sprawdzenia: {typ}")


def score(task: dict, raw: str, manifest_index: dict, answer=None) -> dict:
    """Score one model reply. Returns per-check results, weighted score and success flag."""
    if answer is None:
        answer = parse_answer(raw)
    results, total, got, critical_ok = [], 0.0, 0.0, True
    for chk in task["sprawdzenia"]:
        ok = run_check(chk, answer, raw or "", manifest_index, task.get("aliasy_dokumentow", {}))
        w = float(chk.get("waga", 1))
        total += w
        got += w if ok else 0.0
        if chk.get("krytyczne") and not ok:
            critical_ok = False
        results.append({"id": chk["id"], "typ": chk["typ"], "ok": ok, "waga": w, "krytyczne": bool(chk.get("krytyczne"))})
    s = got / total if total else 0.0
    return {"json_poprawny": answer is not None, "wynik": round(s, 4), "sukces": critical_ok and s >= PROG_SUKCESU,
            "krytyczne_ok": critical_ok, "sprawdzenia": results}
