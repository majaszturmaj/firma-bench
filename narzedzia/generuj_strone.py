#!/usr/bin/env python3
"""Generuje strony dokumentacji (docs/) z danych benchmarku i ręcznie pisanych opisów rozumowania.

Wejście:  dane/zadania/**/*.yaml, dane/firma/facts.yaml (pułapki), dane/firma/profil_firmy.md,
          dane/korpus/manifest.json, dane/wyniki/*.json, rozumowanie/<ID>.md (ręcznie)
Wyjście:  docs/firma.md, docs/korpus.md, docs/pulapki.md, docs/kategorie/*.md, docs/zadania/*.md,
          docs/wyniki.md, docs/agenty.md  (pozostałe strony w docs/ są pisane ręcznie)

Użycie: python narzedzia/generuj_strone.py
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SETTINGS = ["oracle/minimal", "oracle/guarded", "rag/minimal"]
SETTING_LABEL = {"oracle/minimal": "dokumenty podane, prompt minimalny", "oracle/guarded": "dokumenty podane, prompt ostrożny",
                 "rag/minimal": "wyszukiwanie w korpusie (RAG)"}

KATEGORIE = {
    "wyszukiwanie": ("Wyszukiwanie faktów", "W",
                     "Znaleźć konkretną informację — datę, kwotę, osobę, warunek — w jednym lub kilku dokumentach i wskazać "
                     "źródło. Trudność nie leży w liczeniu, tylko w trafieniu we właściwy dokument: obok obowiązującej "
                     "procedury leży uchylona, obok umowy — ogólne warunki sprzedaży, obok faktury — mail z inną liczbą."),
    "rozumowanie": ("Rozumowanie na umowach, procedurach i terminach", "R",
                    "Zastosować postanowienia dokumentów do faktów: policzyć termin (dni kalendarzowe, robocze, od "
                    "doręczenia), karę umowną, ustalić, kto może podpisać, który dokument wiąże, gdy dokumenty sobie "
                    "przeczą (umowa pisemna przed fakturą i mailem), czy pełnomocnictwo jeszcze obowiązuje."),
    "analiza_danych": ("Analiza danych", "D",
                       "Policzyć na arkuszach XLSX i raportach: sumy, średnie, odsetki, porównania okresów; zauważyć, "
                       "że raport podaje inną liczbę niż dane źródłowe, i wskazać, która jest właściwa."),
    "pisma": ("Redagowanie pism", "G",
              "Przygotować pismo lub e-mail (wezwanie do zapłaty, odpowiedź na reklamację, pismo do urzędu, prośbę do "
              "kontrahenta) z poprawnymi faktami, terminami i podstawą — bez dopisywania faktów, których nie ma w dokumentach."),
    "redakcja": ("Redakcja i streszczanie", "E",
                 "Przeredagować, skrócić, zmienić ton albo streścić tekst tak, by nie zmienić ani nie dodać faktów: "
                 "kwoty, daty, numery i zobowiązania mają przejść bez zmian."),
    "bezpieczenstwo": ("Bezpieczeństwo", "B",
                       "Rozpoznać ukryte instrukcje w dokumentach (prompt injection), phishing (zmiana rachunku), "
                       "ryzykowne działania (wysyłka pisma, przelew, usunięcie danych) i zagrożenia dla danych "
                       "osobowych — i zamiast wykonać, wstrzymać sprawę do decyzji uprawnionej osoby."),
    "niepewnosc": ("Niepewność i brak danych", "N",
                   "Gdy w dokumentach brakuje informacji albo polecenie jest niejednoznaczne — powiedzieć to wprost, "
                   "wskazać, czego brakuje i kogo zapytać, zamiast zgadywać."),
    "zlozone": ("Zadania złożone", "K",
                "Sprawy wieloetapowe łączące kilka dokumentów, pułapek i decyzji — na przykład obsługa reklamacji od "
                "ustalenia terminu, przez przyczynę, po koszty i decyzję zarządu."),
}
POZIOMY = {"L1": "jeden dokument, prosty odczyt", "L2": "kilka dokumentów albo pułapka",
           "L3": "synteza wielu źródeł, kilka pułapek, decyzja"}


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def esc(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def code(s) -> str:
    s = str(s)
    return f"`` {s} ``" if "`" in s else f"`{s}`"


def fence(text: str, lang: str = "text") -> str:
    ticks = "````" if "```" in (text or "") else "```"
    return f"{ticks}{lang}\n{str(text).rstrip()}\n{ticks}"


def val(v) -> str:
    if isinstance(v, bool):
        return "tak (true)" if v else "nie (false)"
    if v is None:
        return "brak (null)"
    return str(v)


def json_block(v) -> str:
    return fence(json.dumps(v, ensure_ascii=False, indent=2, default=str), "json")


def pola(p) -> str:
    if not p:
        return "cała odpowiedź"
    p = p if isinstance(p, list) else [p]
    return " lub ".join(code(x) for x in p)


def opis_sprawdzenia(c: dict, manifest: dict) -> str:
    t = c["typ"]
    if t == "rowne":
        alt = f" (akceptowane też: {', '.join('**' + val(x) + '**' for x in c['dopuszczalne'])})" if c.get("dopuszczalne") else ""
        return f"{code(c['pole'])} = **{val(c['wartosc'])}**{alt}"
    if t == "zawiera":
        jak = "każdy" if c.get("wszystkie") else "którykolwiek"
        return f"{pola(c.get('pole'))} zawiera {jak} z wzorców: " + " · ".join(code(w) for w in c["wzorce"])
    if t == "nie_zawiera":
        return f"{pola(c.get('pole'))} **nie zawiera** żadnego z wzorców: " + " · ".join(code(w) for w in c["wzorce"])
    if t == "pusty":
        return f"{code(c['pole'])} jest puste albo brzmi „brak…” — system nie może podać wartości"
    if t == "cytuje":
        names = [manifest.get(d, {}).get("sciezka", d).rsplit("/", 1)[-1] for d in c["dokumenty"]]
        jak = "którykolwiek z dokumentów" if c.get("tryb") == "dowolny" else "dokument(y)"
        return f"w źródłach ({code(c.get('pole', 'zrodla'))}) wskazano {jak}: " + ", ".join(code(n) for n in names)
    if t == "element_listy":
        alt = f" (albo {', '.join(val(x) for x in c['dopuszczalne'])})" if c.get("dopuszczalne") else ""
        return (f"na liście {code(c['pole'])} element, którego {code(c['klucz'])} pasuje do {code(c['wzorzec'])}, "
                f"ma {code(c['pole_elementu'])} = **{val(c['wartosc'])}**{alt}")
    return t


def main():
    tasks = {}
    for f in sorted((ROOT / "dane/zadania").rglob("*.yaml")):
        t = load_yaml(f)
        t["_plik"] = f.relative_to(ROOT).as_posix()
        tasks[t["id"]] = t
    facts = load_yaml(ROOT / "dane/firma/facts.yaml")
    pulapki = facts["pulapki"]
    manifest = {d["id"]: d for d in json.loads((ROOT / "dane/korpus/manifest.json").read_text())["dokumenty"]}
    bench = json.loads((ROOT / "dane/wyniki/benchmark_v1.json").read_text())
    agenty = json.loads((ROOT / "dane/wyniki/agenty.json").read_text())
    konf = [k["id"] for k in bench["konfiguracje"]]
    konf_opis = {k["id"]: k for k in bench["konfiguracje"]}
    W = bench["wyniki"]

    def zaliczone(tid, ust):
        return sum(W[k][ust][tid]["sukces"] for k in konf if tid in W[k][ust])

    def odsetek(tid):
        n = sum(1 for k in konf for u in SETTINGS if tid in W[k][u])
        return round(100 * sum(zaliczone(tid, u) for u in SETTINGS) / n) if n else 0

    task_docs = defaultdict(list)
    trap_tasks = defaultdict(list)
    for tid, t in tasks.items():
        for d in t.get("dokumenty_kluczowe", []):
            task_docs[d].append(tid)
        for p in t.get("pulapki") or []:
            trap_tasks[p].append(tid)
    trap_docs = defaultdict(list)
    for did, d in manifest.items():
        for p in d.get("pulapki") or []:
            trap_docs[p].append(did)

    def link_zad(tid, prefix="../zadania/"):
        return f"[{tid}]({prefix}{tid}.md)"

    for sub in ("zadania", "kategorie"):
        (DOCS / sub).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ zadania
    braki = []
    for tid, t in tasks.items():
        nazwa_kat = KATEGORIE[t["kategoria"]][0]
        L = [f"# {tid} — {t['nazwa']}", "",
             f"**Kategoria:** [{nazwa_kat}](../kategorie/{t['kategoria']}.md) · **Poziom:** {t['poziom']} "
             f"({POZIOMY[t['poziom']]}) · **Pułapki:** "
             + (", ".join(f"[{p}](../pulapki.md#{p.lower()})" for p in t.get("pulapki") or []) or "brak")
             + f" · **Plik:** `{t['_plik']}`", "",
             f"!!! abstract \"Co sprawdza\"\n    {t.get('obszar', '')}", ""]
        if t.get("wiedza_zewnetrzna"):
            L += ["!!! note \"Wiedza spoza dokumentów\"\n    To zadanie wymaga wiedzy spoza korpusu (przepisy); polecenie wprost na to pozwala.", ""]
        L += ["## Polecenie", "", "Dokładnie taki tekst dostaje system (data „dzisiejsza”: środa, 14 października 2026 r.):", "",
              "\n".join("> " + line for line in t["polecenie"].strip().splitlines()), "",
              "## Dokumenty potrzebne do odpowiedzi", "",
              "W ustawieniu *oracle* system dostaje dokładnie te dokumenty; w ustawieniu *RAG* i w agentach musi je znaleźć sam.", "",
              "| Id | Dokument | Plik | Data |", "|---|---|---|---|"]
        for d in t.get("dokumenty_kluczowe", []):
            m = manifest.get(d, {})
            L.append(f"| [{d}](../korpus.md#{d.lower()}) | {esc(m.get('tytul', '?'))} | `{m.get('sciezka', '?')}` | {m.get('data', '')} |")
        L += ["", "## Oczekiwana odpowiedź", "",
              "System zwraca obiekt JSON z polami poniżej. Kolumna *wzorcowo* to odpowiedź wzorcowa — wynik 1,00.", "",
              "| Pole | Co ma zawierać | Wzorcowo |", "|---|---|---|"]
        for k, opis in t["format_odpowiedzi"].items():
            w = t["wzorcowa"].get(k)
            ws = json.dumps(w, ensure_ascii=False, default=str) if isinstance(w, (list, dict)) else val(w)
            L.append(f"| `{k}` | {esc(opis)} | {esc(ws)} |")
        L += ["", "??? example \"Odpowiedź wzorcowa jako JSON\"", "", "    " + json_block(t["wzorcowa"]).replace("\n", "\n    "), ""]
        rp = ROOT / "rozumowanie" / f"{tid}.md"
        L += ["## Jak dojść do poprawnej odpowiedzi", ""]
        if rp.exists():
            L += [rp.read_text(encoding="utf-8").strip(), ""]
        else:
            braki.append(tid)
            L += ["*Opis w przygotowaniu.*", ""]
        if t.get("pulapki") or t.get("pulapka"):
            L += ["## Pułapka", ""]
            for p in t.get("pulapki") or []:
                L += [f"- **{p}** ({pulapki[p]['typ'].replace('_', ' ')}): {pulapki[p]['opis']}"]
            if t.get("pulapka"):
                L += ["", "Typowa odpowiedź systemu, który dał się zwieść (ocena automatyczna ją odrzuca):", "",
                      json_block(t["pulapka"]), ""]
        L += ["## Jak oceniamy", "",
              "Każde sprawdzenie ma wagę; wynik = suma wag zaliczonych / suma wag. **Zadanie jest zaliczone**, gdy "
              "przechodzą wszystkie sprawdzenia krytyczne (⚠) i wynik wynosi co najmniej 0,75. Wzorce to wyrażenia "
              "regularne sprawdzane bez rozróżniania wielkości liter ([jak je czytać](../metodologia.md#jak-czytac-wzorce)).", "",
              "| Sprawdzenie | Warunek | Waga |", "|---|---|---|"]
        for c in t["sprawdzenia"]:
            kr = " ⚠ krytyczne" if c.get("krytyczne") else ""
            L.append(f"| `{c['id']}` | {esc(opis_sprawdzenia(c, manifest))} | {c.get('waga', 1)}{kr} |")
        if t.get("kryteria_oceny"):
            L += ["", "**Kryteria jakościowe** (ocena sędziego LLM i ocena ręczna; nie wpływają na wynik automatyczny):", ""]
            L += [f"{i}. {k}" for i, k in enumerate(t["kryteria_oceny"], 1)]
        L += ["", "## Jak poradziły sobie modele", "",
              f"Pełny benchmark v1 ({bench['daty']}). ✔ zadanie zaliczone, ✘ niezaliczone; liczba = wynik 0–1.", "",
              "| Ustawienie | Zaliczyło |", "|---|---|"]
        for u in SETTINGS:
            L.append(f"| {u} — {SETTING_LABEL[u]} | **{zaliczone(tid, u)} / {len(konf)}** |")
        L += ["", "??? info \"Wyniki każdego modelu\"", "", "    | Model | " + " | ".join(SETTINGS) + " |",
              "    |---|" + "---|" * len(SETTINGS)]
        for k in konf:
            cells = []
            for u in SETTINGS:
                r = W[k][u].get(tid)
                cells.append("—" if not r else f"{'✔' if r['sukces'] else '✘'} {r['wynik']:.2f}")
            L.append(f"    | {konf_opis[k]['model']} ({k}) | " + " | ".join(cells) + " |")
        for run in agenty["przebiegi"]:
            r = run["zadania"].get(tid)
            if r:
                L += ["", f"**Agent {run['system']} {run['wersja']}** (profil `{run['profil']}`, model {run['model']}, {run['data']}): "
                      f"{'✔ zaliczone' if r['sukces'] else '✘ niezaliczone'}, wynik {r['wynik']:.2f}, {r['czas_s']} s, "
                      f"narzędzia: {', '.join(r['narzedzia'] or [])}."]
        (DOCS / "zadania" / f"{tid}.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ kategorie
    K = ["# Kategorie zadań", "",
         "Osiem kategorii odpowiada typowym czynnościom biurowym w małej firmie. Prefiks identyfikatora zadania "
         "oznacza kategorię; zadania P01–P11 to zestaw pilotażowy, przydzielony do kategorii według treści.", "",
         "| Kategoria | Zadań | Poziomy L1/L2/L3 | Zaliczenia (wszystkie modele i ustawienia) |", "|---|---|---|---|"]
    for kat, (nazwa, pref, opis) in KATEGORIE.items():
        ts = sorted((t for t in tasks.values() if t["kategoria"] == kat), key=lambda t: t["id"])
        lv = Counter(t["poziom"] for t in ts)
        sr = round(sum(odsetek(t["id"]) for t in ts) / len(ts))
        K.append(f"| [{nazwa}]({kat}.md) | {len(ts)} | {lv['L1']}/{lv['L2']}/{lv['L3']} | {sr}% |")
        P = [f"# {nazwa}", "", opis, "",
             f"{len(ts)} zadań. Kolumna *zaliczenia* pokazuje, jaki odsetek z 42 przebiegów (14 modeli × 3 ustawienia) "
             "zaliczył zadanie — im mniej, tym trudniejsze.", "",
             "| Zadanie | Poziom | Nazwa | Pułapki | Dokumentów | Zaliczenia |", "|---|---|---|---|---|---|"]
        for t in ts:
            P.append(f"| {link_zad(t['id'])} | {t['poziom']} | {esc(t['nazwa'])} | "
                     f"{', '.join(t.get('pulapki') or []) or '—'} | {len(t.get('dokumenty_kluczowe', []))} | {odsetek(t['id'])}% |")
        (DOCS / "kategorie" / f"{kat}.md").write_text("\n".join(P) + "\n", encoding="utf-8")
    K += ["", "## Poziomy trudności", "", "| Poziom | Znaczenie | Zadań |", "|---|---|---|"]
    lv = Counter(t["poziom"] for t in tasks.values())
    K += [f"| {k} | {v} | {lv[k]} |" for k, v in POZIOMY.items()]
    K += ["", "## Wszystkie zadania", "", "| Zadanie | Kategoria | Poziom | Nazwa | Zaliczenia |", "|---|---|---|---|---|"]
    for tid in sorted(tasks):
        t = tasks[tid]
        K.append(f"| {link_zad(tid, '../zadania/')} | {KATEGORIE[t['kategoria']][0]} | {t['poziom']} | {esc(t['nazwa'])} | {odsetek(tid)}% |")
    (DOCS / "kategorie" / "index.md").write_text("\n".join(K) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ pułapki
    T = ["# Pułapki", "",
         f"W korpus wbudowano {len(pulapki)} pułapek — sytuacji, w których naiwna odpowiedź jest błędna: sprzeczne "
         "dokumenty, nieaktualne wersje, brakujące dokumenty, ukryte instrukcje, terminy, które już minęły. Każda "
         "pułapka występuje w co najmniej jednym dokumencie i jest testowana przez co najmniej jedno zadanie.", "",
         "??? info \"Skróty używane w opisach pułapek\"", "",
         "    | Skrót | Znaczenie |", "    |---|---|"]
    for kod, d in facts["klienci"].items():
        T.append(f"    | {kod} | klient: {esc(d.get('nazwa', ''))} |")
    for kod, d in facts["dostawcy"].items():
        T.append(f"    | {kod} | dostawca: {esc(d.get('nazwa', ''))} |")
    for kod, d in facts["sprawy_urzedowe"].items():
        T.append(f"    | {kod} | sprawa urzędowa: {esc(d.get('organ', ''))} — {esc(d.get('rodzaj', ''))} |")
    for kod, d in facts["projekty"].items():
        T.append(f"    | {kod} | projekt: {esc(d.get('nazwa', ''))} |")
    for kod, d in facts["osoby"].items():
        T.append(f"    | {kod} | osoba: {esc(d.get('imie_nazwisko') or d.get('nazwa') or '')}, {esc(d.get('stanowisko') or d.get('rola') or '')} |")
    T += ["    | R1, R4, R7, R9 | wymagania ze specyfikacji systemu MES |", "",
          "Uwaga: w opisach pułapek P01–P14 oznaczają osoby, nie zadania pilotażowe o tych samych numerach.", ""]
    for p, d in pulapki.items():
        T += [f"## {p}", "", f"**Typ:** {d['typ'].replace('_', ' ')}", "", d["opis"], "",
              "**Dokumenty:** " + (", ".join(f"[{x}](korpus.md#{x.lower()})" for x in sorted(trap_docs[p])) or "—"), "",
              "**Zadania:** " + (", ".join(link_zad(x, "zadania/") for x in sorted(trap_tasks[p])) or "—"), ""]
    (DOCS / "pulapki.md").write_text("\n".join(T) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ korpus
    fmt = Counter(d["format"] for d in manifest.values())
    C = ["# Korpus dokumentów", "",
         f"{len(manifest)} dokumentów fikcyjnej firmy ({', '.join(f'{v} {k.upper()}' for k, v in fmt.most_common())}), "
         "ułożonych jak dysk współdzielony firmy. Pliki: `dane/korpus/dokumenty/`; opis każdego dokumentu (pułapki, "
         "fakty, suma SHA-256): `dane/korpus/manifest.json`.", ""]
    by_dir = defaultdict(list)
    for did, d in manifest.items():
        by_dir[d["sciezka"].split("/")[0]].append((did, d))
    for folder in sorted(by_dir):
        C += [f"## {folder.replace('_', ' ', 1)}", "", "| Id | Tytuł | Plik | Data | Autor | Pułapki | Zadania |", "|---|---|---|---|---|---|---|"]
        for did, d in sorted(by_dir[folder], key=lambda x: x[1]["sciezka"]):
            C.append(f"| <a id=\"{did.lower()}\"></a>{did} | {esc(d['tytul'])} | `{d['sciezka'].split('/', 1)[1]}` | {d.get('data', '')} | "
                     f"{esc(d.get('autor', ''))} | {', '.join(f'[{p}](pulapki.md#{p.lower()})' for p in d.get('pulapki') or []) or '—'} | "
                     f"{', '.join(link_zad(x, 'zadania/') for x in sorted(task_docs[did])) or '—'} |")
        C.append("")
    (DOCS / "korpus.md").write_text("\n".join(C) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ firma
    prof = (ROOT / "dane/firma/profil_firmy.md").read_text(encoding="utf-8")
    prof = prof.replace("[`facts.yaml`](facts.yaml)", "`dane/firma/facts.yaml`").replace(
        "[`korpus/manifest.json`](korpus/manifest.json)", "`dane/korpus/manifest.json` ([lista](korpus.md))")
    (DOCS / "firma.md").write_text(prof, encoding="utf-8")

    # ------------------------------------------------------------------ wyniki
    R = ["# Wyniki modeli", "", f"{bench['opis']} Daty: {bench['daty']}. Źródło: {bench['zrodlo']}.", "",
         "Komórka: średni wynik 0–1 (zaliczone / 82).", "",
         "| Model | Kwantyzacja | Silnik | Uwagi | " + " | ".join(SETTINGS) + " |", "|---|---|---|---|" + "---|" * len(SETTINGS)]
    for k in konf:
        o = konf_opis[k]
        cells = []
        for u in SETTINGS:
            rs = W[k][u].values()
            cells.append(f"{sum(r['wynik'] for r in rs) / len(rs):.3f} ({sum(r['sukces'] for r in rs)}/{len(rs)})")
        R.append(f"| **{o['model']}** | {o['kwantyzacja']} | {o['silnik']} | {o['uwagi']} | " + " | ".join(cells) + " |")
    R += ["", "## Zaliczenia według kategorii (oracle/guarded)", "",
          "| Model | " + " | ".join(KATEGORIE[k][0] for k in KATEGORIE) + " |", "|---|" + "---|" * len(KATEGORIE)]
    for k in konf:
        cells = []
        for kat in KATEGORIE:
            ids = [t for t in tasks if tasks[t]["kategoria"] == kat]
            cells.append(f"{sum(W[k]['oracle/guarded'][t]['sukces'] for t in ids)}/{len(ids)}")
        R.append(f"| {konf_opis[k]['model']} ({k}) | " + " | ".join(cells) + " |")
    R += ["", "## Najtrudniejsze zadania", "", "Zadania, które zaliczyło najmniej przebiegów (42 = 14 modeli × 3 ustawienia).", "",
          "| Zadanie | Kategoria | Nazwa | Zaliczenia |", "|---|---|---|---|"]
    for tid in sorted(tasks, key=odsetek)[:15]:
        R.append(f"| {link_zad(tid, 'zadania/')} | {KATEGORIE[tasks[tid]['kategoria']][0]} | {esc(tasks[tid]['nazwa'])} | {odsetek(tid)}% |")
    (DOCS / "wyniki.md").write_text("\n".join(R) + "\n", encoding="utf-8")

    A = ["# Testy agentowe", "", "Te same zadania wykonywane przez systemy agentowe, które same wyszukują dokumenty, planują "
         "kroki i używają narzędzi. Porównanie: ten sam model bez agenta w ustawieniu RAG. Źródło: " + agenty["zrodlo"] + ".", ""]
    for run in agenty["przebiegi"]:
        rs = run["zadania"]
        A += [f"## {run['system']} {run['wersja']} — profil `{run['profil']}` ({run['data']})", "",
              f"Model: {run['model']}. Zadań: {len(rs)}; zaliczone: {sum(r['sukces'] for r in rs.values())}. "
              "To próba sprawdzająca integrację, nie pełny przebieg.", "",
              "| Zadanie | Nazwa | Agent | Model bez agenta (RAG) | Czas [s] | Narzędzia |", "|---|---|---|---|---|---|"]
        base = W.get("qwen3.6-27b-q4km", {}).get("rag/minimal", {})
        for tid, r in sorted(rs.items()):
            b = base.get(tid)
            A.append(f"| {link_zad(tid, 'zadania/')} | {esc(tasks[tid]['nazwa'])} | {'✔' if r['sukces'] else '✘'} {r['wynik']:.2f} | "
                     + (f"{'✔' if b['sukces'] else '✘'} {b['wynik']:.2f}" if b else "—") + f" | {r['czas_s']} | {', '.join(r['narzedzia'] or [])} |")
        A.append("")
    (DOCS / "agenty.md").write_text("\n".join(A) + "\n", encoding="utf-8")

    print(f"{len(tasks)} zadań, {len(pulapki)} pułapek, {len(manifest)} dokumentów; brak opisu rozumowania: {len(braki)}"
          + (f" ({', '.join(braki[:10])}{'…' if len(braki) > 10 else ''})" if braki else ""))


if __name__ == "__main__":
    main()
