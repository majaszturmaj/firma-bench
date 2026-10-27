#!/usr/bin/env python3
"""Ocena odpowiedzi modelu na zadania FIRMA-bench.

Wejście: plik JSONL, jeden wiersz na zadanie: {"zadanie": "W01", "odpowiedz": "<surowa odpowiedź modelu>"}.
Wyjście: tabela wyników na ekranie; z --json — szczegóły każdego zadania w pliku JSONL.

Użycie: python narzedzia/ocen.py odpowiedzi.jsonl [--json wyniki.jsonl]
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scoring import score  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("odpowiedzi", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    tasks = {}
    for f in (ROOT / "dane/zadania").rglob("*.yaml"):
        t = yaml.safe_load(f.read_text(encoding="utf-8"))
        tasks[t["id"]] = t
    manifest = {d["id"]: d for d in json.loads((ROOT / "dane/korpus/manifest.json").read_text(encoding="utf-8"))["dokumenty"]}

    rows, by_cat = [], defaultdict(list)
    for line in a.odpowiedzi.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        t = tasks.get(r["zadanie"])
        if t is None:
            print(f"pominięto nieznane zadanie: {r['zadanie']}", file=sys.stderr)
            continue
        sc = score(t, r.get("odpowiedz") or "", manifest)
        failed = [c["id"] for c in sc["sprawdzenia"] if not c["ok"]]
        rows.append({"zadanie": t["id"], "kategoria": t["kategoria"], **sc})
        by_cat[t["kategoria"]].append(sc)
        print(f"{t['id']:4} {'✔' if sc['sukces'] else '✘'} {sc['wynik']:.2f}  {'JSON' if sc['json_poprawny'] else 'brak JSON'}"
              + (f"  niezaliczone: {', '.join(failed)}" if failed else ""))
    if not rows:
        sys.exit("brak odpowiedzi do oceny")
    print("\nKategoria            zaliczone  średni wynik")
    for k, v in sorted(by_cat.items()):
        print(f"{k:20} {sum(x['sukces'] for x in v):3}/{len(v):<5} {sum(x['wynik'] for x in v) / len(v):.3f}")
    n = len(rows)
    print(f"{'RAZEM':20} {sum(x['sukces'] for x in rows):3}/{n:<5} {sum(x['wynik'] for x in rows) / n:.3f}"
          + (f"  (ocenionych zadań: {n} z {len(tasks)})" if n < len(tasks) else ""))
    if a.json:
        a.json.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")


if __name__ == "__main__":
    main()
