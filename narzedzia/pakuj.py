#!/usr/bin/env python3
"""Buduje pliki do pobrania FIRMA-bench.

Domyślnie zapisuje je do docs/pobierz/ (strona dokumentacji je publikuje); z --out DIR — do wskazanego katalogu
(np. dist/ dla wydania na GitHubie). Archiwa ZIP mają stałe znaczniki czasu i kolejność plików.

  firma-bench.zip              pełny pakiet: zadania, dokumenty, fakty, wyniki zagregowane, skrypt oceny, licencja
  firma-bench-dokumenty.zip    tylko 95 dokumentów firmy + spis dokumenty.csv
  zadania.jsonl                82 zadania ze wszystkimi polami (w tym odpowiedzi wzorcowe i sprawdzenia)
  zadania_dla_modelu.jsonl     82 zadania — tylko pola, które dostaje testowany system
  SHA256SUMS.txt               sumy kontrolne powyższych plików

Użycie: python narzedzia/pakuj.py [--out DIR]
"""

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_ZIP = (2026, 10, 14, 0, 0, 0)  # „dzisiaj” w świecie benchmarku — stały znacznik czasu plików w archiwach
POLA_DLA_MODELU = ["id", "nazwa", "kategoria", "poziom", "polecenie", "format_odpowiedzi", "dokumenty_kluczowe"]


def load_tasks() -> list[dict]:
    tasks = [yaml.safe_load(f.read_text(encoding="utf-8")) for f in (ROOT / "dane/zadania").rglob("*.yaml")]
    return sorted(tasks, key=lambda t: t["id"])


def jsonl(rows) -> bytes:
    return "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows).encode("utf-8")


class Zip:
    def __init__(self, path: Path, prefix: str):
        self.zf = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9)
        self.prefix = prefix

    def add_bytes(self, arcname: str, data: bytes):
        info = zipfile.ZipInfo(f"{self.prefix}/{arcname}", DATA_ZIP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        self.zf.writestr(info, data)

    def add_tree(self, src: Path, arcdir: str):
        for f in sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            self.add_bytes(f"{arcdir}/{f.relative_to(src).as_posix()}", f.read_bytes())

    def close(self):
        self.zf.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ROOT / "docs/pobierz")
    a = ap.parse_args()
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    wersja = (ROOT / "WERSJA").read_text(encoding="utf-8").strip()
    tasks = load_tasks()
    manifest = {d["id"]: d for d in json.loads((ROOT / "dane/korpus/manifest.json").read_text(encoding="utf-8"))["dokumenty"]}

    full = jsonl(tasks)
    for_model = jsonl({**{k: t[k] for k in POLA_DLA_MODELU if k in t}, "polecenie": t["polecenie"].strip(),
                       "dokumenty_kluczowe": [manifest[d]["sciezka"] for d in t.get("dokumenty_kluczowe", [])]} for t in tasks)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["id", "plik", "tytul", "typ", "format", "data", "autor"])
    for did, d in sorted(manifest.items(), key=lambda x: x[1]["sciezka"]):
        w.writerow([did, d["sciezka"], d["tytul"], d.get("typ", ""), d["format"], d.get("data", ""), d.get("autor", "")])
    spis = buf.getvalue().encode("utf-8")

    (out / "zadania.jsonl").write_bytes(full)
    (out / "zadania_dla_modelu.jsonl").write_bytes(for_model)

    z = Zip(out / "firma-bench.zip", f"firma-bench-{wersja}")
    for name in ("README.md", "LICENSE", "WERSJA"):
        z.add_bytes(name, (ROOT / name).read_bytes())
    z.add_tree(ROOT / "dane", "dane")
    z.add_tree(ROOT / "rozumowanie", "rozumowanie")
    for name in ("ocen.py", "scoring.py"):
        z.add_bytes(f"narzedzia/{name}", (ROOT / "narzedzia" / name).read_bytes())
    z.add_bytes("zadania.jsonl", full)
    z.add_bytes("zadania_dla_modelu.jsonl", for_model)
    z.add_bytes("dokumenty.csv", spis)
    z.close()

    readme_dok = (f"FIRMA-bench {wersja} — dokumenty fikcyjnej firmy FIRMA Sp. z o.o.\n\n"
                  f"{len(manifest)} dokumentów (PDF, EML, XLSX, DOCX, TXT) ułożonych jak dysk współdzielony firmy; "
                  "spis w dokumenty.csv. Wszystkie podmioty, osoby, numery i rachunki są fikcyjne.\n"
                  "Zadania, odpowiedzi wzorcowe i skrypt oceny: firma-bench.zip. Licencja: MIT (plik LICENSE).\n")
    z = Zip(out / "firma-bench-dokumenty.zip", f"firma-bench-{wersja}-dokumenty")
    z.add_bytes("CZYTAJ.txt", readme_dok.encode("utf-8"))
    z.add_bytes("LICENSE", (ROOT / "LICENSE").read_bytes())
    z.add_bytes("dokumenty.csv", spis)
    z.add_tree(ROOT / "dane/korpus/dokumenty", "dokumenty")
    z.close()

    files = ["firma-bench.zip", "firma-bench-dokumenty.zip", "zadania.jsonl", "zadania_dla_modelu.jsonl"]
    sums = "".join(f"{hashlib.sha256((out / f).read_bytes()).hexdigest()}  {f}\n" for f in files)
    (out / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    for f in files:
        print(f"{(out / f).stat().st_size / 1024:8.0f} KB  {out / f}")


if __name__ == "__main__":
    main()
