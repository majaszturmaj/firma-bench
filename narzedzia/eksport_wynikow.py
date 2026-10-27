#!/usr/bin/env python3
"""Eksport wyników z repozytorium eksperymentów (Mag_Testy) do dane/wyniki/*.json.

Zapisuje wyłącznie wyniki zagregowane per zadanie (wynik, sukces, poprawność JSON) — bez odpowiedzi modeli,
promptów, ścieżek ani nazw hostów. Pełne odpowiedzi zostają w repozytorium eksperymentów.

Użycie: python narzedzia/eksport_wynikow.py --mag-testy /ścieżka/do/Mag_Testy
"""

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Opisy 14 konfiguracji pełnego benchmarku v1 (kolejność = kolejność w tabelach strony).
KONFIGURACJE = [
    ("gemma-4-31b-qat-q4-think8k", "Gemma 4 31B", "GGUF QAT Q4_0", "llama.cpp", "rozumowanie włączone, limit odpowiedzi 8000 tokenów"),
    ("qwen3.6-27b-q4km", "Qwen3.6-27B", "GGUF Q4_K_M", "llama.cpp", "rozumowanie wyłączone"),
    ("gemma-4-31b-qat-q4-nt", "Gemma 4 31B", "GGUF QAT Q4_0", "llama.cpp", "rozumowanie wyłączone"),
    ("qwen3.8-27b-q4km", "Qwen3.8-27B", "GGUF Q4_K_M", "llama.cpp", "rozumowanie wyłączone"),
    ("gemma-4-12b-fp8-tpl", "Gemma 4 12B", "FP8", "vLLM", "szablon czatu dołączony ręcznie"),
    ("gemma-4-12b-qat-q4-nt", "Gemma 4 12B", "GGUF QAT Q4_0", "llama.cpp", "rozumowanie wyłączone"),
    ("qwen3.5-9b-q8", "Qwen3.5-9B", "GGUF Q8_0", "llama.cpp", "rozumowanie wyłączone"),
    ("qwen3-14b-awq", "Qwen3-14B", "AWQ int4", "vLLM", "rozumowanie wyłączone"),
    ("qwen3-coder-30b-a3b-awq", "Qwen3-Coder-30B-A3B", "AWQ int4", "vLLM", "model do kodu (MoE, 3B aktywnych)"),
    ("qwen3-8b-bf16", "Qwen3-8B", "BF16", "vLLM", "rozumowanie wyłączone"),
    ("deepseek-r1-0528-qwen3-8b-tok", "DeepSeek-R1-0528-Qwen3-8B", "BF16", "vLLM", "rozumowanie, limit 8000; poprawiony tokenizer"),
    ("deepseek-r1-distill-14b-awq-tpl", "DeepSeek-R1-Distill-Qwen-14B", "AWQ int4", "vLLM", "rozumowanie, limit 8000; szablon czatu dołączony ręcznie"),
    ("gemma-3-27b-awq-kv8", "Gemma 3 27B", "AWQ int4", "vLLM", "pamięć podręczna KV w FP8"),
    ("bielik-11b-v3-fp8", "Bielik-11B v3.0 Instruct", "FP8", "vLLM", "polski model SpeakLeash"),
]


def jsonl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mag-testy", type=Path, required=True)
    a = ap.parse_args()
    bench = a.mag_testy / "benchmark"
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=a.mag_testy, capture_output=True, text=True).stdout.strip()

    wyniki = {}
    for d in sorted((bench / "wyniki_v1/2026-10-15_pelny").iterdir()):
        f = d / "wyniki_scalone.jsonl"
        if not f.exists():
            continue
        rows = jsonl(f)
        m, ust = rows[0]["model"], f"{rows[0]['tryb']}/{rows[0]['prompt']}"
        wyniki.setdefault(m, {})[ust] = {r["zadanie"]: {"wynik": r["wynik"], "sukces": r["sukces"], "json": r["json_poprawny"]}
                                         for r in rows}
    out = {"opis": "Pełny benchmark v1: 82 zadania, 14 konfiguracji modeli lokalnych, 3 ustawienia; RTX 4090; temperatura 0, seed 42.",
           "daty": "15–16.10.2026 (zadanie R12 — powtórzenie 16.10.2026)",
           "zrodlo": f"Mag_Testy commit {commit}, benchmark/wyniki_v1/2026-10-15_pelny (wyniki_scalone.jsonl)",
           "konfiguracje": [{"id": k, "model": m, "kwantyzacja": q, "silnik": s, "uwagi": u} for k, m, q, s, u in KONFIGURACJE],
           "wyniki": wyniki}
    (ROOT / "dane/wyniki/benchmark_v1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    agent = []
    for run in sorted((bench / "wyniki_hapilot").glob("*/run")):
        info = json.loads((run / "run.json").read_text())
        scored = {x["zadanie"]: x for x in jsonl(run.parent / "wyniki.jsonl")}
        res = {r["task_id"]: r for r in jsonl(run / "results.jsonl")}
        agent.append({"przebieg": run.parent.name, "system": "Hapilot", "wersja": info["hapilot"]["describe"],
                      "profil": info["config"]["profile"], "model": info["models"][0]["name"], "data": info["started"][:10],
                      "zadania": {t: {"wynik": s["wynik"], "sukces": s["sukces"], "czas_s": res[t].get("duration_s"),
                                      "narzedzia": res[t].get("plan_tools")} for t, s in scored.items()}})
    (ROOT / "dane/wyniki/agenty.json").write_text(json.dumps({"zrodlo": f"Mag_Testy commit {commit}, benchmark/wyniki_hapilot",
                                                               "przebiegi": agent}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"benchmark_v1: {len(wyniki)} konfiguracji; agenty: {len(agent)} przebiegów")


if __name__ == "__main__":
    main()
