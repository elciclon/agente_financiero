# Agent Instructions

## Commands & Verification
- **Install dependencies**: `pip install -r requirements.txt`
- **Run tests**: `python3 -m pytest` or `pytest` (requires `pytest` dependency installed)

## Architecture & Execution Flow
- **Purpose**: A web scraper agent that clones top investor holdings ("Superinversores") from Dataroma and filters them to those available as Argentine CEDEARs.
- **Scraper entry point**: `guru_cloner_node(state)` in `clonador.py`.
- **Target Source**: Scrapes `https://www.dataroma.com/m/holdings.php?m=<GURU_ID>`.
- **Ticker Conversion**: Dataroma uses dots (e.g., `BRK.B`), but Argentine CEDEARs and standard lookups use dashes (`BRK-B`). `clonador.py` converts `.` to `-` before matching.
- **CEDEAR Universe**: Defined in `cedears.txt` (plain text, one ticker per line). Loaded via `cargar_lista_cedears` from `file_utils.py`.
- **Configuration**: Guru mappings, CEDEAR file path, user-agent, and timeout live in `config.py`.
- **Concurrency**: Guru scraping runs concurrently via `ThreadPoolExecutor` (up to 10 workers) for speed.

## Quirks & Constraints
- **Logging**: Uses Python `logging` module configured at INFO level with console output.
- **Scraper user-agent**: Uses `Mozilla/5.0` to avoid request blocking. Defined in `config.py`.
- **Dataroma ID mappings**: Defined in `config.py` dict `GURUS` (e.g., Warren Buffett -> `BRK`, Michael Burry -> `SAM`, Bill Ackman -> `PSC`).
- **HTTP timeout**: 10 seconds per request, configured in `config.py`.
