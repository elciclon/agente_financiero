import os
from typing import List

def cargar_lista_cedears(nombre_archivo: str) -> List[str]:
    """
    Carga una lista de tickers desde un archivo de texto plano.
    Asume un ticker por línea.
    """
    ruta_completa = os.path.join(os.getcwd(), nombre_archivo)
    if not os.path.exists(ruta_completa):
        print(f"ERROR: No se encontró el archivo '{nombre_archivo}'")
        return []

    try:
        with open(ruta_completa, 'r', encoding='utf-8') as archivo:
            lista = [line.strip() for line in archivo if line.strip()]
        return lista
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return []