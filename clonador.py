import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from file_utils import cargar_lista_cedears
from config import GURUS, CEDEARS_FILE, USER_AGENT, configurar_logging

TIMEOUT_SECONDS = 10

configurar_logging()
logger = logging.getLogger("clonador")


def _scrape_guru_holdings(guru_name: str, guru_id: str, cedears_disponibles: Set[str]) -> Set[str]:
    found_tickers: Set[str] = set()
    url = f"https://www.dataroma.com/m/holdings.php?m={guru_id}"
    headers = {'User-Agent': USER_AGENT}

    logger.info(f"Revisando cartera de {guru_name}...")

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red o HTTP al acceder a {url} ({guru_name}): {e}")
        return found_tickers

    try:
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', id='grid')
        if not table:
            logger.warning(f"No se encontró la tabla de holdings para {guru_name} en {url}")
            return found_tickers

        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if not cols:
                continue

            ticker_text = cols[1].text.strip()
            ticker = ticker_text.replace('.', '-')

            if ticker in cedears_disponibles:
                found_tickers.add(ticker)

    except Exception as e:
        logger.error(f"Error inesperado al parsear la cartera de {guru_name}: {e}")

    return found_tickers


def guru_cloner_node(state) -> Dict[str, List[str]]:
    logger.info("--- [AGENTE] Iniciando Clonador Concurrente ---")

    cedears_lista = cargar_lista_cedears(CEDEARS_FILE)
    cedears_disponibles = set(cedears_lista)

    if not cedears_disponibles:
        logger.warning(f"No se cargaron CEDEARs desde '{CEDEARS_FILE}'. El resultado será vacío.")
        return {"tickers": []}

    cloned_tickers: Set[str] = set()

    with ThreadPoolExecutor(max_workers=min(len(GURUS), 10)) as executor:
        futures = {
            executor.submit(_scrape_guru_holdings, name, guru_id, cedears_disponibles): name
            for name, guru_id in GURUS.items()
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                tickers_encontrados = future.result()
                cloned_tickers.update(tickers_encontrados)
            except Exception as e:
                logger.error(f"Excepción no controlada en el hilo del gurú {name}: {e}")

    lista_final = sorted(list(cloned_tickers))
    logger.info(f"--- [AGENTE] Identificados {len(lista_final)} CEDEARs en carteras de Gurús ---")
    logger.info(f"Candidatos: {lista_final}")

    return {"tickers": lista_final}
