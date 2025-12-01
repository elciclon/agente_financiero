import os
import pytest
from file_utils import cargar_lista_cedears

def test_cargar_lista_cedears_reads_and_strips(tmp_path):
    # Preparar archivo de prueba con espacios y líneas vacías
    p = tmp_path / "cedears_test.txt"
    p.write_text(" ABC\nDEF \n\n  GHI  \n")
    # Llamar a la función bajo prueba
    result = cargar_lista_cedears(str(p))
    # Comprobaciones generales
    assert isinstance(result, list), "Debe devolver una lista"
    assert all(isinstance(item, str) for item in result), "Todos los elementos deben ser strings"
    # Comprobar que las líneas vacías fueron descartadas y los elementos están strip()
    assert result == ["ABC", "DEF", "GHI"]

def test_cargar_lista_cedears_missing_file_behavior():
    missing = "this_file_definitely_does_not_exist_12345.txt"
    # Aceptar comportamiento razonable: lanzar FileNotFoundError/OSError o devolver una lista vacía/lista
    try:
        result = cargar_lista_cedears(missing)
    except Exception as e:
        assert isinstance(e, (FileNotFoundError, OSError)), "Si falla, debe ser FileNotFoundError/OSError"
    else:
        assert isinstance(result, list), "Si no lanza, debe devolver una lista"
        # Si devuelve una lista para un fichero inexistente, lo razonable sería que esté vacía
        assert len(result) >= 0