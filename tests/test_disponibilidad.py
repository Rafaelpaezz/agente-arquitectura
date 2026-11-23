import math

import pytest

from app.tools.disponibilidad import ErrorTopologia, calcular_disponibilidad, nueves


def disp(expr):
    return calcular_disponibilidad(expr)["disponibilidad"]


def test_serie_multiplica():
    assert disp("serie(0.99, 0.99)") == pytest.approx(0.9801)


def test_paralelo_complemento():
    assert disp("paralelo(0.99, 0.99)") == pytest.approx(0.9999)


def test_porcentajes_y_sin_porcentaje():
    assert disp("serie(99.9%, 99.9)") == pytest.approx(0.999 * 0.999)


def test_sin_espacios():
    assert disp("serie(0.99,0.99)") == pytest.approx(0.9801)


def test_anidado_con_nombres_y_spof():
    r = calcular_disponibilidad("serie(lb=0.9999, paralelo(app1=0.999, app2=0.999), db=0.9995)")
    esperado = 0.9999 * (1 - 0.001**2) * 0.9995
    assert r["disponibilidad"] == pytest.approx(esperado)
    assert r["puntos_unicos_de_falla"] == ["lb", "db"]
    assert "db" in r["eslabon_mas_debil"]


def test_kden_2_de_3():
    a = 0.9
    esperado = 3 * a**2 * (1 - a) + a**3
    assert disp("kden(2, 3, 0.9)") == pytest.approx(esperado)


def test_replicas_equivale_a_paralelo():
    assert disp("replicas(3, 0.95)") == pytest.approx(disp("paralelo(0.95, 0.95, 0.95)"))


def test_kden_k_igual_n_es_serie():
    assert disp("kden(3, 3, 0.9)") == pytest.approx(0.9**3)


def test_un_componente():
    r = calcular_disponibilidad("0.999")
    assert r["disponibilidad"] == pytest.approx(0.999)
    assert r["avisos"]


def test_disponibilidad_perfecta_sin_infinito():
    r = calcular_disponibilidad("paralelo(1, 0.9)")
    assert r["disponibilidad"] == 1.0
    assert r["nueves"] is None
    assert math.isinf(nueves(1.0))


@pytest.mark.parametrize("expr", [
    "", "serie()", "serie(0.9", "serie(0.9))", "serie(1.5%x)", "serie(-0.9)",
    "serie(250)", "kden(4, 3, 0.9)", "kden(0, 3, 0.9)", "kden(2, 3, serie(0.9))",
    "replicas(1000, 0.9)", "foo(0.9)", "serie(0.9; 0.8)", "__import__('os')",
])
def test_entradas_invalidas(expr):
    with pytest.raises(ErrorTopologia):
        calcular_disponibilidad(expr)


def test_profundidad_maxima():
    expr = "serie(" * 12 + "0.9" + ")" * 12
    with pytest.raises(ErrorTopologia):
        calcular_disponibilidad(expr)


def test_no_es_texto():
    with pytest.raises(ErrorTopologia):
        calcular_disponibilidad(0.9)  # type: ignore[arg-type]


def test_caida_anual_tres_nueves():
    r = calcular_disponibilidad("0.999")
    assert r["caida_anual"] == "8.77 h"          # SDP: 8h 45min 57s
    assert r["caida_mensual"] == "43.8 min"       # SDP: 43m 49.7s
