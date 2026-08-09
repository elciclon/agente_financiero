import datetime

import duckdb
from calculador_ccl import (
    TABLA,
    calcular_ccl_por_fecha,
    inicializar_db,
    almacenar_ccl,
    obtener_ultima_fecha,
)


def test_calcular_ccl_por_fecha_usa_fechas_solapadas():
    local = {"2025-01-02": 1000.0, "2025-01-03": 1100.0}
    adr = {"2025-01-02": 20.0, "2025-01-04": 22.0}
    resultado = calcular_ccl_por_fecha(local, adr)
    assert resultado == [("2025-01-02", round((1000.0 * 10) / 20.0, 4))]


def test_calcular_ccl_por_fecha_ignora_precio_adr_cero():
    local = {"2025-01-02": 1000.0}
    adr = {"2025-01-02": 0.0}
    assert calcular_ccl_por_fecha(local, adr) == []


def test_calcular_ccl_por_fecha_redondea_4_decimales():
    local = {"2025-01-02": 1001.0}
    adr = {"2025-01-02": 20.0}
    resultado = calcular_ccl_por_fecha(local, adr)
    assert resultado[0][1] == round((1001.0 * 10) / 20.0, 4)


def test_almacenar_ccl_no_sobrescribe_dias_existentes():
    conexion = duckdb.connect(":memory:")
    inicializar_db(conexion)
    almacenar_ccl(conexion, [("2025-01-02", 500.0)])
    almacenar_ccl(conexion, [("2025-01-02", 510.0), ("2025-01-03", 520.0)])
    filas = conexion.execute(f"SELECT fecha, ccl FROM {TABLA} ORDER BY fecha").fetchall()
    assert filas == [(datetime.date(2025, 1, 2), 500.0), (datetime.date(2025, 1, 3), 520.0)]
    conexion.close()


def test_obtener_ultima_fecha_devuelve_max():
    conexion = duckdb.connect(":memory:")
    inicializar_db(conexion)
    almacenar_ccl(conexion, [("2025-01-02", 500.0), ("2025-01-03", 520.0)])
    assert obtener_ultima_fecha(conexion) == "2025-01-03"
    conexion.close()


def test_obtener_ultima_fecha_tabla_vacia_devuelve_none():
    conexion = duckdb.connect(":memory:")
    inicializar_db(conexion)
    assert obtener_ultima_fecha(conexion) is None
    conexion.close()
