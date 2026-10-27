# FIRMA-bench

Benchmark zadań biurowych i administracyjnych w języku polskim: **82 zadania** na **95 dokumentach** fikcyjnej firmy produkcyjnej FIRMA Sp. z o.o., z odpowiedziami wzorcowymi, automatyczną oceną i **25 pułapkami** (sprzeczne dokumenty, nieaktualne wersje, ukryte instrukcje dla AI, phishing, brakujące dane).

Dokumentacja — opis firmy i dokumentów, kategorii, każdego zadania (co ma zawierać odpowiedź, jak dojść do niej krok po kroku, jaka jest pułapka, jak oceniamy) oraz wyniki modeli — jest w katalogu [`docs/`](docs/index.md) i po publikacji będzie dostępna jako strona GitHub Pages.

> **Status:** repozytorium prywatne. Zadania, odpowiedzi wzorcowe i dokumenty zostaną upublicznione po zakończeniu testów modeli komercyjnych i systemów agentowych, żeby nie mogły trafić do ich wyszukiwania ani danych treningowych przed testem.

## Zawartość

| Katalog | Co zawiera |
|---|---|
| `dane/zadania/` | 82 zadania (YAML): `pilot/` P01–P11 i `v1/` |
| `dane/korpus/` | 95 dokumentów firmy i `manifest.json` (tylko dla oceny) |
| `dane/firma/` | `facts.yaml` — fakty, z których wygenerowano dokumenty i odpowiedzi; profil firmy |
| `dane/wyniki/` | wyniki zagregowane (per zadanie, bez odpowiedzi modeli) |
| `rozumowanie/` | ręcznie pisane opisy „jak dojść do poprawnej odpowiedzi”, po jednym na zadanie |
| `narzedzia/` | ocena odpowiedzi (`ocen.py`, `scoring.py`), generator dokumentacji, eksport wyników |
| `docs/` | strona dokumentacji (MkDocs Material); strony zadań, kategorii, pułapek, korpusu i wyników są generowane |

## Ocena własnego modelu

```bash
python narzedzia/ocen.py odpowiedzi.jsonl
```

`odpowiedzi.jsonl` — jeden wiersz na zadanie: `{"zadanie": "W01", "odpowiedz": "<surowa odpowiedź modelu>"}`. Szczegóły: [docs/dane.md](docs/dane.md) i [docs/metodologia.md](docs/metodologia.md).

## Budowanie dokumentacji

```bash
python -m venv .venv && .venv/bin/pip install -r requirements-docs.txt
.venv/bin/python narzedzia/generuj_strone.py   # strony generowane z danych i rozumowanie/*.md
.venv/bin/mkdocs serve                          # podgląd na http://127.0.0.1:8000
```

Wyniki modeli eksportuje `narzedzia/eksport_wynikow.py` z repozytorium eksperymentów (Mag_Testy). Publikację strony włącza zmienna repozytorium `PUBLIKUJ_STRONE=tak` (workflow `.github/workflows/strona.yml`); do tego czasu workflow tylko buduje stronę i sprawdza, że odpowiedzi wzorcowe przechodzą ocenę.

## Pochodzenie

Benchmark powstał w ramach pracy magisterskiej *„Porównanie skuteczności komercyjnych aplikacji LLM oraz dedykowanej architektury agentowej w realizacji zadań domenowych”* (Maja Szturmaj, 2026). Dane skopiowano z repozytorium eksperymentów Mag_Testy (commit `2741765`).

Wszystkie podmioty, osoby, numery i rachunki są fikcyjne; numery NIP/REGON mają celowo błędne sumy kontrolne, a rachunki prefiks `PL00 9990`.
