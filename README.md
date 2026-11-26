# Pronóstico mensual de energía en las Zonas No Interconectadas (ZNI) de Colombia

Pronóstico de la energía activa (kWh) de cada localidad de las ZNI a 1 y 3 meses, con datos de telemetría del Centro Nacional de Monitoreo (CNM) del IPSE (enero de 2020 a junio de 2023, 133 localidades).

## Resultado principal
Con validación temporal de origen rodante (julio de 2022 a junio de 2023), un **Random Forest global** (un solo modelo para todas las localidades) obtiene un sMAPE de **11,0 % a 1 mes** y de **13,6 % a 3 meses**. Supera a las referencias simples, aunque la mejora solo es estadísticamente significativa a 3 meses. El error es de ~5–7 % en las localidades grandes con servicio de 24 h y de 13–20 % en las veredas con servicio limitado.

## Estructura
```
datos/raw/            datos originales (energia.csv, ENERGIA.tif)
datos/interim/        datos renombrados (Sección 1)
datos/processed/      panel limpio, bitácora de limpieza, predicciones y métricas
notebooks/            01 → 05, ejecutar en orden
figuras/              todas las gráficas (prefijo = sección)
docs/COMPARATIVA.md   proyecto original vs corregido, sección por sección
docs/GUION_PRESENTACION.md
original/             notebook original, sin modificar
```

## Secciones
| Notebook | Contenido |
|---|---|
| `01_entender_datos` | Diccionario de datos, cobertura, problemas de calidad, definición del problema |
| `02_limpieza` | 8 reglas de limpieza basadas en el factor de carga y bitácora de cambios |
| `03_exploracion_series` | Efecto calendario, estacionalidad, tendencia, volatilidad, oferta vs demanda, COVID |
| `04_modelos` | 3 referencias + ETS local + Random Forest y Gradient Boosting globales; origen rodante; bootstrap |
| `05_comparativa_final` | Reproducción del modelo original y demostración de la fuga de información |

## Reproducir
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\jupyter.exe lab
```
En Linux o macOS:
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/jupyter lab
```
Para ejecutar los cinco notebooks sin abrir Jupyter:
```bash
cd notebooks && for n in 0*.ipynb; do ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace "$n"; done
```
Ejecuta los notebooks en orden (01 → 05): cada uno lee lo que guardó el anterior.

## Referencias principales
- Colmenares-Quintero, R. F. et al. (2022). *Data Analysis of Electricity Service in Colombia's Non-Interconnected Zones through Different Clustering Techniques*. Energies, 15(20), 7644.
- Colmenares-Quintero, R. F. et al. (2021). *Analysis of the energy service in non-interconnected zones of Colombia using business intelligence*. Cogent Engineering.
- Gil-Vera, V. D. (2016). *Pronóstico de la demanda mensual de electricidad con series de tiempo*. Revista EIA, 13(26). DOI 10.24050/reia.v13i26.749.
- Castaño, E. (2010). *El "efecto calendario" y la especificación de un modelo de series de tiempo para la demanda de electricidad*. Lecturas de Economía. DOI 10.17533/udea.le.n35a5115.
- Colmenares-Quintero, R. F. et al. (2026). *Decision tree-based prediction of economic activities in Colombia's Non-Interconnected Zones*. Energy Sources, Part B.
- Bustos et al. (2025). *Evaluating Sampling Strategies for Characterizing Energy Demand in Regions of Colombia Without AMI Infrastructure*. Applied Sciences, 15(17), 9588.
- Montero-Manso, P. & Hyndman, R. J. (2021). *Principles and algorithms for forecasting groups of time series: Locality and globality*. International Journal of Forecasting.
