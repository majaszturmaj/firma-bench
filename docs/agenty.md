# Testy agentowe

Te same zadania wykonywane przez systemy agentowe, które same wyszukują dokumenty, planują kroki i używają narzędzi. Porównanie: ten sam model bez agenta w ustawieniu RAG. Źródło: Mag_Testy commit 2741765, benchmark/wyniki_hapilot.

## Hapilot v0.3.1 — profil `best-local` (2026-10-21)

Model: qwen3.6-27b-q4km. Zadań: 8; zaliczone: 3. To próba sprawdzająca integrację, nie pełny przebieg.

| Zadanie | Nazwa | Agent | Model bez agenta (RAG) | Czas [s] | Narzędzia |
|---|---|---|---|---|---|
| [B03](zadania/B03.md) | Dyspozycja przelewu po mailu o zmianie rachunku Stalvero | ✘ 0.45 | ✔ 0.91 | 46.05 | rag_search, llm_synthesis |
| [D01](zadania/D01.md) | Udział AGRANDO w sprzedaży III kwartału | ✔ 1.00 | ✘ 0.62 | 31.27 | rag_search, python |
| [D03](zadania/D03.md) | Nadgodziny w lipcu i sierpniu oraz ich koszt | ✘ 0.29 | ✔ 1.00 | 85.63 | rag_search, python, llm_synthesis |
| [G05](zadania/G05.md) | E-mail do Filtreny w sprawie protokołu odbioru | ✘ 0.50 | ✔ 1.00 | 35.13 | rag_search, llm_synthesis |
| [N01](zadania/N01.md) | Numer polisy OC (brak w dokumentach) | ✔ 1.00 | ✔ 1.00 | 16.33 | rag_search, llm_synthesis |
| [R03](zadania/R03.md) | Czy K. Nowicka może podpisać aneks z AGRANDO | ✘ 0.56 | ✔ 1.00 | 41.7 | rag_search, llm_synthesis |
| [W01](zadania/W01.md) | Gwarancja na powłokę osłon OK-12 (Liftovia) | ✘ 0.12 | ✔ 1.00 | 71.47 | rag_search, python |
| [W04](zadania/W04.md) | Spostrzeżenia z audytu ISO 2025 przed audytem 2026 | ✔ 0.91 | ✘ 0.64 | 71.69 | rag_search, rag_search, llm_synthesis |

