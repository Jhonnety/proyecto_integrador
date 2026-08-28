# -*- coding: utf-8 -*-
# Aplicacion Streamlit - Prediccion de desempeno alto en las Pruebas Saber 11.
#
# Proyecto Integrador CRISP-DM.
# Fuente de datos: Datos Abiertos Colombia (datos.gov.co), recurso kgxf-xxbe.

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

RUTA_MODELO = Path(__file__).parent / "modelo_saber11.joblib"

st.set_page_config(page_title="Saber 11 — Predictor de desempeno",
                   page_icon="🎓", layout="wide")


@st.cache_resource
def cargar_modelo():
    paquete = joblib.load(RUTA_MODELO)
    return paquete["pipeline"], paquete["metadatos"]


try:
    modelo, meta = cargar_modelo()
except FileNotFoundError:
    st.error(f"No se encontro el modelo en {RUTA_MODELO}. "
             "Ejecute el cuaderno para generarlo.")
    st.stop()

ORDINALES = meta["categorias_ordinales"]
NOMINALES = meta["variables_nominales"]
PREDICTORES = meta["predictores"]
INDICADORES = meta["indicadores_ausencia"]
UMBRAL_DEF = float(meta["umbral_probabilidad_recomendado"])
COLS_FLOAT = meta.get("columnas_float", [])


def preparar_entrada(registros):
    # Normaliza tipos antes de entregar los datos al pipeline serializado.
    X = pd.DataFrame(registros).copy()
    for c in COLS_FLOAT:
        if c in X.columns:
            X[c] = pd.to_numeric(X[c], errors="coerce").astype("float64")
    return X[PREDICTORES]


def clasificar_prioridad(p):
    if p < 0.15:
        return "MUY ALTA", "Intervencion integral: refuerzo academico y apoyo material", "🔴"
    if p < 0.35:
        return "ALTA", "Programa de refuerzo focalizado", "🟠"
    if p < 0.60:
        return "MEDIA", "Seguimiento y tutoria de refuerzo ligera", "🟡"
    return "BAJA", "Sin necesidad de intervencion prioritaria", "🟢"


st.title("🎓 Predictor de desempeno alto — Pruebas Saber 11")
st.caption(
    f"Estima la probabilidad de que un estudiante alcance **{meta['umbral_puntaje']} puntos "
    "o mas** en el puntaje global, usando unicamente informacion de contexto disponible "
    "**antes** de presentar la prueba. Fuente: Datos Abiertos Colombia (datos.gov.co)."
)

pestanas = st.tabs(["Prediccion individual", "Prediccion por lotes", "Sobre el modelo"])

# ---------------------------------------------------------------- INDIVIDUAL
with pestanas[0]:
    st.subheader("Datos del estudiante")
    izq, cen, der = st.columns(3)

    with izq:
        st.markdown("**Hogar**")
        estrato = st.selectbox("Estrato de la vivienda",
                               ORDINALES["fami_estratovivienda"], index=2)
        educ_madre = st.selectbox("Educacion de la madre",
                                  ORDINALES["fami_educacionmadre"], index=4)
        educ_padre = st.selectbox("Educacion del padre",
                                  ORDINALES["fami_educacionpadre"], index=4)
        cuartos = st.selectbox("Cuartos del hogar", ORDINALES["fami_cuartoshogar"], index=2)
        personas = st.selectbox("Personas del hogar", ORDINALES["fami_personashogar"], index=1)

    with cen:
        st.markdown("**Bienes del hogar**")
        automovil = st.checkbox("Automovil", value=False)
        computador = st.checkbox("Computador", value=True)
        internet = st.checkbox("Conexion a internet", value=True)
        lavadora = st.checkbox("Lavadora", value=True)
        st.markdown("**Estudiante**")
        genero = st.radio("Genero", ["Femenino", "Masculino"], horizontal=True)
        edad = st.slider("Edad (anos)", 13.0, 30.0, 17.0, 0.5)
        extranjero = st.checkbox("Nacionalidad distinta de la colombiana", value=False)
        privado = st.checkbox("Privado de la libertad", value=False)

    with der:
        st.markdown("**Colegio**")
        naturaleza = st.radio("Naturaleza", ["OFICIAL", "NO OFICIAL"], horizontal=True)
        zona = st.radio("Zona", ["URBANO", "RURAL"], horizontal=True)
        calendario = st.selectbox("Calendario", NOMINALES["cole_calendario"])
        caracter = st.selectbox("Caracter academico", NOMINALES["cole_caracter"])
        jornada = st.selectbox("Jornada", NOMINALES["cole_jornada"])
        genero_col = st.selectbox("Genero del colegio", NOMINALES["cole_genero"])
        depto = st.selectbox("Departamento", NOMINALES["cole_depto_ubicacion"],
                             index=NOMINALES["cole_depto_ubicacion"].index("ANTIOQUIA")
                             if "ANTIOQUIA" in NOMINALES["cole_depto_ubicacion"] else 0)
        bilingue = st.checkbox("Colegio bilingue", value=False)
        sede_principal = st.checkbox("Sede principal", value=True)

    umbral = st.slider(
        "Umbral de decision (palanca de negocio: bajarlo amplia la cobertura, "
        "subirlo concentra los cupos)", 0.05, 0.95, UMBRAL_DEF, 0.01)

    if st.button("Calcular probabilidad", type="primary", use_container_width=True):
        registro = {
            "fami_estratovivienda": estrato,
            "fami_cuartoshogar": cuartos,
            "fami_personashogar": personas,
            "fami_educacionmadre": educ_madre,
            "fami_educacionpadre": educ_padre,
            "fami_tieneautomovil": int(automovil),
            "fami_tienecomputador": int(computador),
            "fami_tieneinternet": int(internet),
            "fami_tienelavadora": int(lavadora),
            "cole_bilingue": int(bilingue),
            "cole_sede_principal": int(sede_principal),
            "cole_naturaleza": int(naturaleza == "NO OFICIAL"),
            "cole_area_ubicacion": int(zona == "URBANO"),
            "estu_genero": int(genero == "Femenino"),
            "estu_privado_libertad": int(privado),
            "cole_calendario": calendario,
            "cole_caracter": caracter,
            "cole_jornada": jornada,
            "cole_genero": genero_col,
            "cole_depto_ubicacion": depto,
            "edad": float(edad),
            "indice_bienes": int(automovil) + int(computador) + int(internet) + int(lavadora),
            "es_extranjero": int(extranjero),
        }
        for ind in INDICADORES:
            registro[ind] = 0
        X = preparar_entrada([registro])
        p = float(modelo.predict_proba(X)[0, 1])
        prioridad, accion, icono = clasificar_prioridad(p)

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Probabilidad de desempeno alto", f"{p:.1%}")
        c2.metric("Prediccion", "ALTO" if p >= umbral else "NO ALTO")
        c3.metric("Prioridad de acompanamiento", f"{icono} {prioridad}")
        st.progress(min(p, 1.0))
        st.info(f"**Accion recomendada:** {accion}")
        st.caption(
            "Este resultado describe el CONTEXTO del estudiante, no su capacidad ni su "
            "esfuerzo. Su unico uso legitimo es asignar apoyo adicional; nunca debe emplearse "
            "para seleccionar, ordenar o excluir estudiantes."
        )

# -------------------------------------------------------------------- LOTES
with pestanas[1]:
    st.subheader("Priorizacion de una lista de estudiantes")
    st.markdown(
        "Cargue un archivo CSV con una fila por estudiante y las columnas del modelo. "
        "Descargue primero la plantilla para conocer el formato exacto."
    )
    plantilla = pd.DataFrame([{c: "" for c in PREDICTORES}])
    st.download_button("Descargar plantilla CSV",
                       plantilla.to_csv(index=False).encode("utf-8"),
                       "plantilla_saber11.csv", "text/csv")

    archivo = st.file_uploader("Archivo CSV", type=["csv"])
    if archivo is not None:
        try:
            lote = pd.read_csv(archivo)
            for ind in INDICADORES:
                if ind not in lote.columns:
                    lote[ind] = 0
            faltantes = [c for c in PREDICTORES if c not in lote.columns]
            if faltantes:
                st.error(f"Faltan columnas obligatorias: {faltantes}")
            else:
                probs = modelo.predict_proba(preparar_entrada(lote))[:, 1]
                salida = lote.copy()
                salida["probabilidad_desempeno_alto"] = probs.round(4)
                salida["prioridad"] = [clasificar_prioridad(p)[0] for p in probs]
                salida = salida.sort_values("probabilidad_desempeno_alto")
                st.success(f"{len(salida)} estudiantes procesados y ordenados por prioridad.")
                st.dataframe(salida.head(200), use_container_width=True)
                st.download_button("Descargar resultados",
                                   salida.to_csv(index=False).encode("utf-8"),
                                   "priorizacion_saber11.csv", "text/csv")
        except Exception as exc:
            st.error(f"No fue posible procesar el archivo: {exc}")

# ------------------------------------------------------------------- MODELO
with pestanas[2]:
    st.subheader("Documentacion del modelo")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Ficha tecnica**")
        st.json({
            "modelo": meta["nombre_modelo"],
            "version": meta["version"],
            "entrenado": meta["fecha_entrenamiento"],
            "registros de entrenamiento": meta["n_entrenamiento"],
            "fuente": meta["fuente_datos"],
            "objetivo": meta["objetivo"],
        })
        st.markdown("**Hiperparametros**")
        st.json(meta["hiperparametros"])
    with c2:
        st.markdown("**Desempeno sobre el conjunto de prueba (30 % no visto)**")
        st.dataframe(pd.DataFrame(meta["metricas_test"].items(),
                                  columns=["Metrica", "Valor"]), use_container_width=True)
        st.markdown("**Uso responsable**")
        st.warning(
            "El modelo predice a partir del contexto socioeconomico e institucional, no del "
            "merito individual. Reproduce las desigualdades presentes en el sistema educativo "
            "colombiano. Emplearlo para seleccionar o excluir estudiantes amplificaria esas "
            "desigualdades. Su unico uso legitimo es focalizar apoyo adicional."
        )
