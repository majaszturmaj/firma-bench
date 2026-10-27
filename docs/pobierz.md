# Pobierz

Benchmark i dokumenty firmy są dostępne na **licencji MIT** — można je pobrać, używać, zmieniać i rozpowszechniać, także komercyjnie, pod warunkiem zachowania informacji o licencji i autorce.

## Pliki

| Plik | Co zawiera | Dla kogo |
|---|---|---|
| **[firma-bench.zip](pobierz/firma-bench.zip)** | **pełny pakiet:** 82 zadania (YAML i JSONL), 95 dokumentów, spis dokumentów, fakty firmy (`facts.yaml`), opisy rozumowania, wyniki zagregowane, skrypt oceny, licencja | chcesz uruchomić benchmark i ocenić swój model |
| **[firma-bench-dokumenty.zip](pobierz/firma-bench-dokumenty.zip)** | **tylko dokumenty firmy:** 95 plików (PDF, EML, XLSX, DOCX, TXT) w folderach jak na dysku firmowym + `dokumenty.csv` | potrzebujesz realistycznego zbioru polskich dokumentów biurowych, np. do testów wyszukiwania |
| **[zadania.jsonl](pobierz/zadania.jsonl)** | 82 zadania ze wszystkimi polami — także odpowiedzi wzorcowe, pułapki i sprawdzenia | analizujesz zadania lub budujesz własną ocenę |
| **[zadania_dla_modelu.jsonl](pobierz/zadania_dla_modelu.jsonl)** | 82 zadania — **tylko to, co dostaje testowany system:** polecenie, format odpowiedzi, dokumenty kluczowe | uruchamiasz model i nie chcesz, żeby odpowiedzi wzorcowe trafiły do promptu |
| **[SHA256SUMS.txt](pobierz/SHA256SUMS.txt)** | sumy kontrolne powyższych plików | sprawdzasz, czy plik pobrał się bez zmian |

Wersja zbioru: **1.0** (82 zadania, 95 dokumentów, 25 pułapek). Wszystkie wydania z tymi samymi plikami są też w zakładce [Releases](https://github.com/majaszturmaj/firma-bench/releases) repozytorium.

## Inne sposoby

=== "git"

    ```bash
    git clone https://github.com/majaszturmaj/firma-bench.git
    ```

=== "archiwum repozytorium"

    [Pobierz całe repozytorium jako ZIP](https://github.com/majaszturmaj/firma-bench/archive/refs/heads/main.zip) — razem z kodem tej strony.

## Szybki start

```bash
unzip firma-bench.zip && cd firma-bench-1.0
pip install pyyaml
# 1. dla każdego wiersza zadania_dla_modelu.jsonl zbuduj prompt i zapisz odpowiedź modelu
# 2. oceń odpowiedzi:
python narzedzia/ocen.py odpowiedzi.jsonl
```

Wiersz `zadania_dla_modelu.jsonl`:

```json
{"id": "W01", "nazwa": "Gwarancja na powłokę osłon OK-12 (Liftovia)", "kategoria": "wyszukiwanie", "poziom": "L1",
 "polecenie": "Do kiedy obowiązuje gwarancja na powłokę lakierniczą osłon OK-12 …",
 "format_odpowiedzi": {"gwarancja_powloki_miesiace": "liczba miesięcy", "…": "…"},
 "dokumenty_kluczowe": ["03_Umowy/Klienci/Liftovia/Umowa_dostawy_UD-2024-11_Liftovia.pdf", "04_Sprzedaz/WZ/2026/WZ_2026_0912.pdf"]}
```

Plik z odpowiedziami do oceny — jeden wiersz na zadanie, odpowiedź modelu bez zmian:

```json
{"zadanie": "W01", "odpowiedz": "{\"gwarancja_powloki_miesiace\": 36, \"gwarancja_powloki_do\": \"2029-09-08\", …}"}
```

Jak zbudować prompt (dokumenty, prompt systemowy, data „dzisiejsza”) — [Metodologia](metodologia.md); format zadania i skrypt oceny — [Dane](dane.md).

## Sprawdzenie pobranych plików

```bash
sha256sum -c SHA256SUMS.txt
```

## Jak cytować

> Szturmaj, M. (2026). *FIRMA-bench: benchmark zadań biurowych i administracyjnych w języku polskim* (wersja 1.0). https://github.com/majaszturmaj/firma-bench

Wszystkie podmioty, osoby, numery i rachunki w zbiorze są fikcyjne.
