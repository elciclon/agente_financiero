import logging
import os
import sys
from typing import Dict, List, Optional, Tuple

import duckdb
import requests
import yfinance as yf
from dotenv import load_dotenv

from config import configurar_logging

load_dotenv()
configurar_logging()

logger = logging.getLogger("calculador_ccl")

DB_PATH = "ccl_data.duckdb"
TABLA = "ccl_historico"
RATIO_ADR = 10
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")
ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"
TIMEOUT_SECONDS = 10

MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN", "")
MOTHERDUCK_DB = os.getenv("MOTHERDUCK_DB", "agente_financiero")


def conectar() -> duckdb.DuckDBPyConnection:
    if MOTHERDUCK_TOKEN:
        logger.info(f"Conectando a base cloud en MotherDuck: '{MOTHERDUCK_DB}'...")
        config = {"motherduck_token": MOTHERDUCK_TOKEN} if MOTHERDUCK_TOKEN else {}
        try:
            return duckdb.connect(f"md:{MOTHERDUCK_DB}", config=config)
        except Exception as e:
            logger.error(f"Falló la conexión a MotherDuck: {e}. Usando base local como contingencia.")
            return duckdb.connect(DB_PATH)
    logger.info(f"Sin MOTHERDUCK_TOKEN: usando base local '{DB_PATH}'.")
    return duckdb.connect(DB_PATH)


def inicializar_db(conexion: duckdb.DuckDBPyConnection) -> None:
    conexion.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLA} (
            fecha DATE PRIMARY KEY,
            ccl DOUBLE
        )
    """)


def obtener_ultima_fecha(conexion: duckdb.DuckDBPyConnection) -> Optional[str]:
    fila = conexion.execute(f"SELECT MAX(fecha) FROM {TABLA}").fetchone()
    if fila is None or fila[0] is None:
        return None
    return fila[0].isoformat()


def obtener_historial_yfinance(ticker: str, desde: Optional[str] = None) -> Dict[str, float]:
    logger.info(f"Obteniendo historial de {ticker} vía yfinance (desde {desde or 'inicio'})...")
    kwargs = {"period": "max"}
    if desde:
        kwargs = {"start": desde}
    datos = yf.Ticker(ticker).history(**kwargs)
    if datos.empty:
        raise ValueError(f"yfinance no devolvió datos para {ticker}")
    cierres = datos["Close"].dropna()
    return {fecha.date().isoformat(): float(precio) for fecha, precio in cierres.items()}


def obtener_historial_alphavantage(ticker: str, desde: Optional[str] = None) -> Dict[str, float]:
    if not ALPHAVANTAGE_API_KEY:
        raise ValueError("Falta ALPHAVANTAGE_API_KEY en el entorno (.env) para el respaldo")
    parametros = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "full",
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    logger.info(f"Obteniendo historial de {ticker} vía AlphaVantage...")
    respuesta = requests.get(ALPHAVANTAGE_URL, params=parametros, timeout=TIMEOUT_SECONDS)
    respuesta.raise_for_status()
    datos = respuesta.json()
    serie = datos.get("Time Series (Daily)")
    if not serie:
        raise ValueError(f"AlphaVantage no devolvió series para {ticker}: {datos}")
    cierres = {fecha: float(valores["4. close"]) for fecha, valores in serie.items()}
    if desde:
        cierres = {fecha: precio for fecha, precio in cierres.items() if fecha >= desde}
    return cierres


def obtener_historial(ticker: str, desde: Optional[str] = None) -> Dict[str, float]:
    try:
        return obtener_historial_yfinance(ticker, desde)
    except Exception as e:
        logger.warning(f"yfinance falló para {ticker}: {e}. Probando respaldo con AlphaVantage...")
        return obtener_historial_alphavantage(ticker, desde)


def calcular_ccl_por_fecha(
    historial_local: Dict[str, float],
    historial_adr: Dict[str, float],
) -> List[Tuple[str, float]]:
    registros = []
    for fecha in sorted(set(historial_local) & set(historial_adr)):
        precio_local = historial_local[fecha]
        precio_adr = historial_adr[fecha]
        if precio_adr == 0:
            continue
        ccl = (precio_local * RATIO_ADR) / precio_adr
        registros.append((fecha, round(ccl, 4)))
    return registros


def almacenar_ccl(conexion: duckdb.DuckDBPyConnection, registros: List[Tuple[str, float]]) -> None:
    conexion.executemany(
        f"""
        INSERT OR IGNORE INTO {TABLA} (fecha, ccl)
        VALUES (?, ?)
        """,
        registros,
    )
    conexion.commit()
    logger.info(f"Registros almacenados en '{TABLA}': {len(registros)}")


def main() -> None:
    conexion = None
    try:
        conexion = conectar()
        inicializar_db(conexion)
        fecha_desde = obtener_ultima_fecha(conexion)
        if fecha_desde:
            logger.info(f"Última fecha en base: {fecha_desde}. Actualizando solo días nuevos.")
        historial_local = obtener_historial("GGAL.BA", fecha_desde)
        historial_adr = obtener_historial("GGAL", fecha_desde)
        registros = calcular_ccl_por_fecha(historial_local, historial_adr)
        if not registros:
            logger.error("No se pudo calcular CCL: no hay registros de cotización disponibles.")
            sys.exit(1)
        almacenar_ccl(conexion, registros)
    except Exception as e:
        logger.error(f"Error de conexión o comunicación con la base de datos: {e}")
        sys.exit(1)
    finally:
        if conexion:
            conexion.close()


if __name__ == "__main__":
    main()