# 🏦 agente_financiero

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![CI](https://img.shields.io/github/actions/workflow/status/adrianfernandezfazio/agente_financiero/test.yml?branch=main&label=tests)](https://github.com/adrianfernandezfazio/agente_financiero/actions)
[![requests](https://img.shields.io/badge/requests-%3E%3D2.28-green)](https://pypi.org/project/requests/)
[![beautifulsoup4](https://img.shields.io/badge/beautifulsoup4-%3E%3D4.12-green)](https://pypi.org/project/beautifulsoup4/)

**Clone top superinvestor portfolios — filtered for the Argentine market.**

A concurrent web scraper that fetches the latest stock holdings of legendary investors from [Dataroma](https://www.dataroma.com/), then cross-references them against the universe of tickers available as **Argentine CEDEARs** (Certificados de Depósito Argentinos).

Perfect for value investors in Argentina who want to know *"Which guru picks can I actually buy today?"*.

---

## ✨ Features

| Icon | Feature | Detail |
|---|---|---|
| ⚡ | **Concurrent scraping** | All guru portfolios fetched in parallel via `ThreadPoolExecutor` |
| 🎯 | **6 superinvestors tracked** | Buffett, Burry, Ackman, Li Lu, Pabrai, Klarman |
| 🔄 | **Smart ticker conversion** | Dataroma dots (`.`) → dash (`-`) to match CEDEAR format |
| 📋 | **Sorted, deduplicated output** | Clean list of matched CEDEAR tickers |
| 🇦🇷 | **Argentine-market focused** | Filtered against a curated list of ~75 CEDEAR-eligible tickers |
| 🧪 | **CI-tested** | GitHub Actions runs `pytest` on Python 3.10 & 3.11 |

---

## ⚙️ How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Dataroma   │────▶│  guru_cloner_   │────▶│  Ticker         │
│  /m/holdings │     │  node()          │     │  Conversion     │
│  ?m=<ID>    │     │  6× concurrent   │     │  BRK.B → BRK-B  │
└─────────────┘     └──────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Sorted     │◀────│  CEDEAR Match    │◀────│  cedears.txt    │
│  Output     │     │  Set             │     │  (75 tickers)   │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

1. **Scrape** — For each guru, fetch their holdings page from `https://www.dataroma.com/m/holdings.php?m=<GURU_ID>`.
2. **Parse** — Extract ticker symbols from the HTML table (`<table id="grid">`).
3. **Convert** — Replace `.` with `-` (e.g., `BRK.B` → `BRK-B`).
4. **Filter** — Keep only tickers present in the CEDEAR universe (`cedears.txt`).
5. **Output** — Return a sorted, deduplicated list of tickers.

---

## 📦 Requirements

- Python **3.10+**
- [requests](https://pypi.org/project/requests/) `>= 2.28`
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) `>= 4.12`
- [pytest](https://pypi.org/project/pytest/) `>= 7.0` *(dev/test only)*

---

## 🚀 Installation

```bash
git clone https://github.com/adrianfernandezfazio/agente_financiero.git
cd agente_financiero
pip install -r requirements.txt
```

---

## 💻 Usage

The project is designed as a **programmatic agent** (compatible with LangGraph-style workflows).

```python
from clonador import guru_cloner_node

result = guru_cloner_node({})
print(result["tickers"])
# ['AAPL', 'BAC', 'BRK-B', 'GOOGL', 'KO', 'MSFT', ...]
```

The function accepts a `state` dict (may be empty) and returns `{"tickers": [...]}` with the matched CEDEARs.

**What you'll see in the logs:**

```
2026-07-20 12:00:00 [INFO] --- [AGENTE] Iniciando Clonador Concurrente ---
2026-07-20 12:00:00 [INFO] Revisando cartera de Warren Buffett...
2026-07-20 12:00:00 [INFO] Revisando cartera de Michael Burry...
...
2026-07-20 12:00:05 [INFO] --- [AGENTE] Identificados 12 CEDEARs en carteras de Gurús ---
2026-07-20 12:00:05 [INFO] Candidatos: ['AAPL', 'BAC', 'BRK-B', ...]
```

---

## 📊 Gurus Tracked

| Investor | Dataroma ID | URL |
|---|---|---|
| 🟢 **Warren Buffett** | `BRK` | `https://www.dataroma.com/m/holdings.php?m=BRK` |
| 🔴 **Michael Burry** | `SAM` | `https://www.dataroma.com/m/holdings.php?m=SAM` |
| 🔵 **Bill Ackman** | `PSC` | `https://www.dataroma.com/m/holdings.php?m=PSC` |
| 🟡 **Li Lu** | `HC` | `https://www.dataroma.com/m/holdings.php?m=HC` |
| 🟣 **Mohnish Pabrai** | `PI` | `https://www.dataroma.com/m/holdings.php?m=PI` |
| ⚪ **Seth Klarman** | `BAUPOST` | `https://www.dataroma.com/m/holdings.php?m=BAUPOST` |

---

## 🧪 Running Tests

```bash
pytest
```

Tests are also run automatically via GitHub Actions on every push/PR to `main`.

---

## 📁 Project Structure

```
agente_financiero/
├── clonador.py                 # Main agent — guru_cloner_node() + scraper logic
├── config.py                   # Guru mappings, file paths, HTTP settings
├── file_utils.py               # CEDEAR file loader (cargar_lista_cedears)
├── cedears.txt                 # ~75 tickers available as Argentine CEDEARs
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest config (pythonpath)
├── .gitignore
├── AGENTS.md                   # AI/developer assistant instructions
├── LICENSE                     # MIT License
├── README.md                   # You are here ✌️
└── tests/
    └── test_file_utils.py      # Unit tests for CEDEAR file loading
```

---

## 📄 License

MIT — see [LICENSE](LICENSE).

Copyright © 2026 **Adrián Fernández Fazio**

---

*Built for the Argentine value investor community.* 🇦🇷
