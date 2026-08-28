"""Descarga muestral del dataset 'Resultados unicos Saber 11' (datos.gov.co, kgxf-xxbe).

Muestreo sistematico sobre el periodo 20224 (calendario A, 2022) ordenando por
estu_consecutivo y tomando bloques equiespaciados. Se guarda el CSV crudo, SIN
ninguna limpieza, para que el cuaderno documente el proceso completo.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

DATASET_ID = "kgxf-xxbe"
BASE = f"https://www.datos.gov.co/resource/{DATASET_ID}.json?"
PERIODO = "20224"
TOTAL_PERIODO = 1_065_888
N_BLOQUES = 6
TAM_BLOQUE = 40_000
SALIDA = Path(__file__).parent / "data" / "saber11_20224_muestra_cruda.csv"

COLUMNAS = [
    "periodo", "estu_consecutivo",
    "cole_area_ubicacion", "cole_bilingue", "cole_calendario", "cole_caracter",
    "cole_depto_ubicacion", "cole_mcpio_ubicacion", "cole_genero", "cole_jornada",
    "cole_naturaleza", "cole_sede_principal",
    "estu_genero", "estu_fechanacimiento", "estu_nacionalidad", "estu_pais_reside",
    "estu_depto_reside", "estu_privado_libertad", "estu_estadoinvestigacion",
    "estu_estudiante", "estu_tipodocumento",
    "fami_cuartoshogar", "fami_educacionmadre", "fami_educacionpadre",
    "fami_estratovivienda", "fami_personashogar", "fami_tieneautomovil",
    "fami_tienecomputador", "fami_tieneinternet", "fami_tienelavadora",
    "desemp_ingles", "punt_ingles", "punt_matematicas", "punt_sociales_ciudadanas",
    "punt_c_naturales", "punt_lectura_critica", "punt_global",
]


def descargar_pagina(offset: int, limite: int, reintentos: int = 4) -> list[dict]:
    consulta = (
        "$select=" + ",".join(COLUMNAS) +
        f"&$where=periodo='{PERIODO}'"
        "&$order=estu_consecutivo"
        f"&$limit={limite}&$offset={offset}"
    )
    url = BASE + urllib.parse.quote(consulta, safe="=&$'(),*")
    ultimo_error = None
    for intento in range(reintentos):
        try:
            with urllib.request.urlopen(url, timeout=600) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:            # red inestable / throttling del portal
            ultimo_error = exc
            print(f"    reintento {intento + 1} en offset {offset}: {exc}")
            time.sleep(10 * (intento + 1))
    raise RuntimeError(f"No se pudo descargar el offset {offset}") from ultimo_error


def main() -> None:
    paso = TOTAL_PERIODO // N_BLOQUES
    registros: list[dict] = []
    for i in range(N_BLOQUES):
        offset = i * paso
        inicio = time.time()
        pagina = descargar_pagina(offset, TAM_BLOQUE)
        registros.extend(pagina)
        print(f"  bloque {i + 1}/{N_BLOQUES} offset={offset:>8} "
              f"filas={len(pagina):>6} acumulado={len(registros):>7} "
              f"({time.time() - inicio:.1f}s)")

    df = pd.DataFrame(registros)[COLUMNAS]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False, encoding="utf-8")
    print(f"\nGuardado: {SALIDA}  ->  {df.shape[0]} filas x {df.shape[1]} columnas")


if __name__ == "__main__":
    main()
