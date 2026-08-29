# Predicción del desempeño alto en las Pruebas Saber 11

Proyecto Integrador — Metodología **CRISP-DM**
Maestría en Ciencia de Datos · Aprendizaje de Máquina

**Autor:** Jhon Esteban Velásquez Gómez

**Aplicación en línea:** https://proyectointegrador-uwjvxhrlyvwpueji8hmttm.streamlit.app
**Cuaderno en Google Colab:** https://drive.google.com/file/d/17KIx0GmgRSfeUUAnehJXV9F9PHaPhVFF/view?usp=sharing
**Repositorio:** https://github.com/Jhonnety/proyecto_integrador

## Descripción

Modelo de **clasificación binaria** que estima la probabilidad de que un estudiante alcance
**300 puntos o más** en el puntaje global de las Pruebas Saber 11,
utilizando **únicamente información de contexto socioeconómico e institucional** disponible
antes de la presentación del examen.

El propósito es permitir a las secretarías de educación **focalizar preventivamente** sus
programas de refuerzo, en lugar de reaccionar cuando los resultados ya se publicaron.

## Fuente de los datos

| | |
|---|---|
| Portal | **Datos Abiertos Colombia** — https://www.datos.gov.co |
| Conjunto | *Resultados únicos Saber 11* |
| Identificador | `kgxf-xxbe` |
| Entidad | ICFES |
| Periodo utilizado | 20224 |
| Registros del universo | 7.109.704 |
| Muestra de trabajo | 240.000 descargados → 119,953 tras limpieza |

## Resultados sobre el conjunto de prueba (30 % no visto)

| Métrica | Valor |
|---|---|
| Accuracy | 0.7360 |
| Precision | 0.4064 |
| Recall | 0.7018 |
| **F1 (clase positiva)** | **0.5147** |
| ROC-AUC | 0.8020 |
| PR-AUC | 0.5209 |

**Modelo final:** `Pipeline` [ imputación → codificación → escalado → Hist. Gradient Boosting ]

## Estructura del repositorio

```
.
├── notebooks/
│   └── proyecto_integrador_saber11.ipynb   Cuaderno CRISP-DM completo
├── app/
│   ├── app.py                              Aplicación Streamlit
│   ├── modelo_saber11.joblib               Pipeline serializado
│   └── requirements.txt                    Dependencias del despliegue
├── data/
│   └── saber11_20224_muestra_cruda.csv     Dataset descargado (sin limpiar)
├── modelos/
│   ├── modelo_saber11.joblib               Pipeline serializado
│   └── metadatos_modelo.json               Ficha técnica del modelo
├── reportes/
│   ├── reporte_exploratorio_saber11.html   Reporte ydata-profiling
│   ├── diccionario_datos.csv
│   ├── resultados_test.csv
│   ├── pantallazo_app_streamlit.png
│   └── hiperparametros_finales.csv
├── descarga_datos.py                       Script de descarga desde la API
├── requirements.txt
└── README.md
```

## Ejecución local

```bash
pip install -r requirements.txt
cd app && streamlit run app.py
```

## Despliegue en Streamlit Community Cloud

La aplicación está desplegada en Streamlit Community Cloud:

**https://proyectointegrador-uwjvxhrlyvwpueji8hmttm.streamlit.app**

Para replicar el despliegue: entrar en https://share.streamlit.io, iniciar sesión con la
cuenta de GitHub, pulsar **New app**, seleccionar este repositorio e indicar `app/app.py`
como *Main file path*.

## Uso responsable

El modelo predice a partir del **contexto**, no del mérito individual. Reproduce las
desigualdades estructurales presentes en el sistema educativo colombiano. Su único uso
legítimo es **asignar apoyo adicional** a estudiantes con baja probabilidad predicha.
Cualquier uso para seleccionar, ordenar o excluir estudiantes amplificaría las
desigualdades que el modelo se limita a describir.
