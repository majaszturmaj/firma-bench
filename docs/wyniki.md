# Wyniki modeli

Pełny benchmark v1: 82 zadania, 14 konfiguracji modeli lokalnych, 3 ustawienia; RTX 4090; temperatura 0, seed 42. Daty: 15–16.10.2026 (zadanie R12 — powtórzenie 16.10.2026). Źródło: Mag_Testy commit 2741765, benchmark/wyniki_v1/2026-10-15_pelny (wyniki_scalone.jsonl).

Komórka: średni wynik 0–1 (zaliczone / 82).

| Model | Kwantyzacja | Silnik | Uwagi | oracle/minimal | oracle/guarded | rag/minimal |
|---|---|---|---|---|---|---|
| **Gemma 4 31B** | GGUF QAT Q4_0 | llama.cpp | rozumowanie włączone, limit odpowiedzi 8000 tokenów | 0.935 (74/82) | 0.948 (78/82) | 0.762 (52/82) |
| **Qwen3.6-27B** | GGUF Q4_K_M | llama.cpp | rozumowanie wyłączone | 0.910 (70/82) | 0.918 (73/82) | 0.759 (47/82) |
| **Gemma 4 31B** | GGUF QAT Q4_0 | llama.cpp | rozumowanie wyłączone | 0.911 (70/82) | 0.917 (72/82) | 0.753 (47/82) |
| **Qwen3.8-27B** | GGUF Q4_K_M | llama.cpp | rozumowanie wyłączone | 0.904 (67/82) | 0.921 (71/82) | 0.758 (49/82) |
| **Gemma 4 12B** | FP8 | vLLM | szablon czatu dołączony ręcznie | 0.831 (55/82) | 0.841 (59/82) | 0.692 (37/82) |
| **Gemma 4 12B** | GGUF QAT Q4_0 | llama.cpp | rozumowanie wyłączone | 0.815 (52/82) | 0.846 (57/82) | 0.698 (37/82) |
| **Qwen3.5-9B** | GGUF Q8_0 | llama.cpp | rozumowanie wyłączone | 0.803 (54/82) | 0.835 (55/82) | 0.678 (39/82) |
| **Qwen3-14B** | AWQ int4 | vLLM | rozumowanie wyłączone | 0.687 (39/82) | 0.745 (48/82) | 0.617 (31/82) |
| **Qwen3-Coder-30B-A3B** | AWQ int4 | vLLM | model do kodu (MoE, 3B aktywnych) | 0.702 (41/82) | 0.739 (45/82) | 0.629 (30/82) |
| **Qwen3-8B** | BF16 | vLLM | rozumowanie wyłączone | 0.695 (37/82) | 0.720 (43/82) | 0.625 (31/82) |
| **DeepSeek-R1-0528-Qwen3-8B** | BF16 | vLLM | rozumowanie, limit 8000; poprawiony tokenizer | 0.684 (41/82) | 0.695 (42/82) | 0.584 (33/82) |
| **DeepSeek-R1-Distill-Qwen-14B** | AWQ int4 | vLLM | rozumowanie, limit 8000; szablon czatu dołączony ręcznie | 0.672 (35/82) | 0.701 (39/82) | 0.581 (27/82) |
| **Gemma 3 27B** | AWQ int4 | vLLM | pamięć podręczna KV w FP8 | 0.664 (37/82) | 0.703 (39/82) | 0.558 (26/82) |
| **Bielik-11B v3.0 Instruct** | FP8 | vLLM | polski model SpeakLeash | 0.675 (37/82) | 0.691 (36/82) | 0.618 (30/82) |

## Zaliczenia według kategorii (oracle/guarded)

| Model | Wyszukiwanie faktów | Rozumowanie na umowach, procedurach i terminach | Analiza danych | Redagowanie pism | Redakcja i streszczanie | Bezpieczeństwo | Niepewność i brak danych | Zadania złożone |
|---|---|---|---|---|---|---|---|---|
| Gemma 4 31B (gemma-4-31b-qat-q4-think8k) | 12/12 | 17/18 | 11/11 | 10/12 | 6/7 | 9/9 | 7/7 | 6/6 |
| Qwen3.6-27B (qwen3.6-27b-q4km) | 12/12 | 14/18 | 9/11 | 12/12 | 6/7 | 9/9 | 7/7 | 4/6 |
| Gemma 4 31B (gemma-4-31b-qat-q4-nt) | 12/12 | 15/18 | 10/11 | 10/12 | 6/7 | 9/9 | 7/7 | 3/6 |
| Qwen3.8-27B (qwen3.8-27b-q4km) | 11/12 | 14/18 | 8/11 | 10/12 | 6/7 | 9/9 | 7/7 | 6/6 |
| Gemma 4 12B (gemma-4-12b-fp8-tpl) | 12/12 | 11/18 | 7/11 | 8/12 | 5/7 | 8/9 | 7/7 | 1/6 |
| Gemma 4 12B (gemma-4-12b-qat-q4-nt) | 12/12 | 12/18 | 6/11 | 8/12 | 4/7 | 6/9 | 7/7 | 2/6 |
| Qwen3.5-9B (qwen3.5-9b-q8) | 12/12 | 11/18 | 5/11 | 8/12 | 4/7 | 6/9 | 6/7 | 3/6 |
| Qwen3-14B (qwen3-14b-awq) | 12/12 | 8/18 | 4/11 | 7/12 | 4/7 | 6/9 | 6/7 | 1/6 |
| Qwen3-Coder-30B-A3B (qwen3-coder-30b-a3b-awq) | 12/12 | 9/18 | 2/11 | 6/12 | 4/7 | 4/9 | 5/7 | 3/6 |
| Qwen3-8B (qwen3-8b-bf16) | 11/12 | 9/18 | 4/11 | 6/12 | 2/7 | 4/9 | 6/7 | 1/6 |
| DeepSeek-R1-0528-Qwen3-8B (deepseek-r1-0528-qwen3-8b-tok) | 11/12 | 11/18 | 5/11 | 5/12 | 3/7 | 2/9 | 5/7 | 0/6 |
| DeepSeek-R1-Distill-Qwen-14B (deepseek-r1-distill-14b-awq-tpl) | 11/12 | 8/18 | 5/11 | 3/12 | 3/7 | 2/9 | 6/7 | 1/6 |
| Gemma 3 27B (gemma-3-27b-awq-kv8) | 12/12 | 6/18 | 2/11 | 6/12 | 3/7 | 3/9 | 6/7 | 1/6 |
| Bielik-11B v3.0 Instruct (bielik-11b-v3-fp8) | 10/12 | 6/18 | 2/11 | 6/12 | 4/7 | 2/9 | 5/7 | 1/6 |

## Najtrudniejsze zadania

Zadania, które zaliczyło najmniej przebiegów (42 = 14 modeli × 3 ustawienia).

| Zadanie | Kategoria | Nazwa | Zaliczenia |
|---|---|---|---|
| [R12](zadania/R12.md) | Rozumowanie na umowach, procedurach i terminach | Rekompensata za koszty odzyskiwania należności (Montarex) | 0% |
| [D05](zadania/D05.md) | Analiza danych | Statystyka zamkniętych reklamacji 2026 | 5% |
| [K04](zadania/K04.md) | Zadania złożone | Notatka przed negocjacjami z AGRANDO | 5% |
| [R14](zadania/R14.md) | Rozumowanie na umowach, procedurach i terminach | Termin potwierdzenia zamówienia AGRANDO przy święcie | 5% |
| [D10](zadania/D10.md) | Analiza danych | Reklamacje rozpatrzone po terminie umownym | 7% |
| [K01](zadania/K01.md) | Zadania złożone | Wszystkie terminy do 23.10.2026 z weryfikacją | 10% |
| [P03](zadania/P03.md) | Rozumowanie na umowach, procedurach i terminach | Wypowiedzenie umowy z Gazomir | 12% |
| [G08](zadania/G08.md) | Redagowanie pism | Notatka dla zarządu o spadku marży w III kwartale | 12% |
| [G07](zadania/G07.md) | Redagowanie pism | Stanowisko do Flowmetic w sprawie przesunięcia wdrożenia | 14% |
| [R05](zadania/R05.md) | Rozumowanie na umowach, procedurach i terminach | Liftovia — termin usunięcia wad, kary i koszty demontażu | 17% |
| [P05](zadania/P05.md) | Analiza danych | Liczba zleceń we wrześniu | 19% |
| [K03](zadania/K03.md) | Zadania złożone | Raport ryzyk projektu MES dla prezesa | 19% |
| [D04](zadania/D04.md) | Analiza danych | Opóźnione dostawy blach i należne kary od Stalvero | 21% |
| [E01](zadania/E01.md) | Redakcja i streszczanie | Zadania z notatki zarządu z 12.10 i błędne ustalenia | 21% |
| [G04](zadania/G04.md) | Redagowanie pism | Nota obciążeniowa dla Stalvero | 21% |
