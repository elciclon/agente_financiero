import logging

GURUS = {
    "Warren Buffett": "BRK",
    "Michael Burry": "SAM",
    "Bill Ackman": "PSC",
    "Li Lu": "HC",
    "Mohnish Pabrai": "PI",
    "Seth Klarman": "BAUPOST",
}

CEDEARS_FILE = "cedears.txt"
USER_AGENT = "Mozilla/5.0"

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


def configurar_logging() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATEFMT,
    )
