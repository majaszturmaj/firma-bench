# FIRMA-bench

[:material-download: Pobierz benchmark](pobierz.md){ .md-button .md-button--primary } [:material-file-document-outline: Pobierz same dokumenty](pobierz/firma-bench-dokumenty.zip){ .md-button }

**Benchmark zadań biurowych i administracyjnych w języku polskim** — 82 zadania na dokumentach fikcyjnej małej firmy produkcyjnej, z odpowiedziami wzorcowymi, automatyczną oceną i wbudowanymi pułapkami.

Benchmark powstał na potrzeby pracy magisterskiej *„Porównanie skuteczności komercyjnych aplikacji LLM oraz dedykowanej architektury agentowej w realizacji zadań domenowych”*. Sprawdza, czy model językowy albo system agentowy potrafi wykonać pracę, którą w małej polskiej firmie wykonuje pracownik biurowy: znaleźć informację w dokumentach, policzyć termin, przygotować pismo, wychwycić sprzeczność i — co równie ważne — powstrzymać się od działania, gdy brakuje danych albo gdy działanie wymaga zgody człowieka.

## W liczbach

| | |
|---|---|
| Zadania | **82** w 8 kategoriach, na 3 poziomach trudności |
| Dokumenty | **95** (47 PDF, 25 EML, 9 XLSX, 8 DOCX, 6 TXT) — umowy, faktury, maile, pisma urzędowe, procedury, arkusze |
| Pułapki | **25** — sprzeczne dokumenty, nieaktualne wersje, ukryte instrukcje dla AI, phishing, brakujące dane |
| Ocena | automatyczna, deterministyczna: 553 sprawdzenia, w tym krytyczne |
| Wyniki | 14 konfiguracji modeli lokalnych × 3 ustawienia (październik 2026) |

## Od czego zacząć

- **[Firma i dokumenty](firma.md)** — kim jest FIRMA Sp. z o.o., kto pisze dokumenty, jakie sprawy są w toku.
- **[Kategorie zadań](kategorie/index.md)** — osiem typów pracy biurowej i lista wszystkich zadań.
- **[Strona zadania](zadania/W01.md)** — przykład: polecenie, potrzebne dokumenty, oczekiwana odpowiedź, jak dojść do niej krok po kroku, pułapka, sposób oceny i wyniki modeli.
- **[Pułapki](pulapki.md)** — 25 sytuacji, w których naiwna odpowiedź jest błędna.
- **[Metodologia](metodologia.md)** — co dokładnie dostaje model, jak liczymy wynik, jak czytać sprawdzenia.
- **[Wyniki](wyniki.md)** — jak poradziły sobie modele lokalne; **[testy agentowe](agenty.md)** — systemy z narzędziami.
- **[Pobierz](pobierz.md)** — pełny pakiet, same dokumenty firmy albo zadania w JSONL (licencja MIT).
- **[Dane i ocena własnego modelu](dane.md)** — struktura repozytorium i skrypt oceniający.

## Założenia

- **Świat zamknięty.** Wszystko, czego potrzeba do odpowiedzi, jest w dokumentach firmy (wyjątek: jedno zadanie, R12, wprost dopuszcza wiedzę o przepisach). „Dzisiaj” to środa, **14 października 2026 r.**
- **Fikcyjna firma.** Nazwy, numery, rachunki i osoby są wymyślone; nazwy kontrahentów sprawdzono, by nie pokrywały się z istniejącymi firmami. Dzięki temu benchmark nie mógł trafić do danych treningowych modeli.
- **Ocena bez sędziego.** Każde zadanie ma odpowiedź w formacie JSON i zestaw sprawdzeń — wynik nie zależy od innego modelu. Zadania otwarte (pisma, redakcja) mają dodatkowo kryteria jakościowe dla oceny przez sędziego LLM i ocenę ręczną.
- **Pułapki zamiast podchwytliwych pytań.** Trudność wynika z realiów pracy biurowej: obok obowiązującej procedury leży uchylona, mail przeczy umowie, a w zapytaniu ofertowym ukryto instrukcję dla asystenta AI.
