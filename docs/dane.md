# Dane i ocena własnego modelu

## Struktura repozytorium

```text
dane/
├── zadania/
│   ├── pilot/          # P01–P11 — zestaw pilotażowy
│   └── v1/             # 71 zadań zestawu głównego
├── korpus/
│   ├── dokumenty/      # 95 dokumentów — to widzą testowane systemy
│   └── manifest.json   # tylko dla oceny: id, tytuł, pułapki, fakty, SHA-256
├── firma/
│   ├── facts.yaml      # jedyne źródło prawdy: fakty, z których wygenerowano dokumenty i odpowiedzi
│   ├── dane/           # większe tabele faktów
│   └── profil_firmy.md # opis firmy
└── wyniki/             # wyniki zagregowane (per zadanie, bez odpowiedzi modeli)
narzedzia/
├── ocen.py             # ocena własnych odpowiedzi
├── scoring.py          # implementacja sprawdzeń
├── generuj_strone.py   # generator tej dokumentacji
└── eksport_wynikow.py  # eksport wyników z repozytorium eksperymentów
rozumowanie/            # opisy „jak dojść do odpowiedzi” — po jednym na zadanie
docs/                   # ta strona
```

## Format zadania

| Pole | Znaczenie |
|---|---|
| `id`, `nazwa` | identyfikator (prefiks = kategoria: W, R, D, G, E, B, N, K; P = pilot) i nazwa |
| `poziom`, `kategoria`, `obszar` | poziom L1–L3, kategoria, opis sprawdzanej umiejętności |
| `pulapki` | pułapki z `facts.yaml` (T01–T25) testowane przez zadanie |
| `dokumenty_kluczowe` | identyfikatory dokumentów potrzebnych do odpowiedzi (ustawienie oracle, recall wyszukiwania) |
| `polecenie` | polecenie użytkownika — **to dostaje system** |
| `format_odpowiedzi` | pola obiektu JSON, który system ma zwrócić — **to dostaje system** |
| `sprawdzenia` | automatyczne sprawdzenia z wagami; `krytyczne: true` decyduje o zaliczeniu |
| `kryteria_oceny` | kryteria jakościowe dla sędziego LLM i oceny ręcznej (opcjonalnie) |
| `wzorcowa` | odpowiedź wzorcowa (wynik 1,00) |
| `pulapka` | typowa błędna odpowiedź (nie przechodzi oceny) |
| `aliasy_dokumentow` | dodatkowe nazwy dokumentów akceptowane w polu `zrodla` |
| `wiedza_zewnetrzna` | `true`, gdy zadanie wymaga wiedzy spoza dokumentów (tylko R12) |

## Ocena własnego modelu

1. Dla każdego zadania zbuduj prompt z polecenia, formatu odpowiedzi i dokumentów (zob. [Metodologia](metodologia.md)) i zapisz surową odpowiedź modelu.
2. Zapisz odpowiedzi w pliku JSONL — jeden wiersz na zadanie:

    ```json
    {"zadanie": "W01", "odpowiedz": "{\"gwarancja_powloki_miesiace\": 36, …}"}
    ```

3. Uruchom ocenę (Python 3.10+, `pyyaml`):

    ```bash
    python narzedzia/ocen.py odpowiedzi.jsonl
    ```

    Skrypt wypisze wynik i zaliczenie każdego zadania, niezaliczone sprawdzenia, sumę dla kategorii i łączny wynik; z `--json wyniki.jsonl` zapisze szczegóły.

Odpowiedź może zawierać tekst wokół obiektu JSON albo blok kodu — skrypt wyodrębni obiekt. Odpowiedź bez poprawnego JSON-a dostaje wynik tylko ze sprawdzeń, które działają na całym tekście.
