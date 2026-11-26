# Comparativa: proyecto original vs proyecto corregido

Proyecto: predicción mensual de energía en las Zonas No Interconectadas (ZNI) de Colombia.
Original: `original/entrega_final.ipynb` · Nuevo: `notebooks/`

Cada sección agrega sus filas. Columnas: qué se hacía antes, qué se hace ahora y **por qué** (el argumento para la presentación).

---

## Sección 1 · Entender los datos y definir el problema
Notebook: `notebooks/01_entender_datos.ipynb`

| Tema | Antes (original) | Ahora (corregido) | Por qué importa |
|---|---|---|---|
| Objetivo del modelo | Predecir `PROMEDIO DIARIO EN HORAS` (sin justificarlo) | Pronosticar `ENERGÍA ACTIVA` (kWh) por localidad, a 1 y 3 meses | El profesor pidió un modelo de **predicción energética mensual**; antes no había ningún pronóstico |
| Variables predictoras | `ENERGÍA ACTIVA` y `POTENCIA MÁXIMA` del **mismo mes** (con `ENERGÍA ACTIVA` repetida) | Solo información **pasada** (rezagos), mes del año y datos de la localidad | horas ≈ E / (P·0,75·días): correlación 0,97. El modelo reconstruía una fórmula (fuga de información) |
| Resultado "MAE 0,70 h" | Se presentaba como buen desempeño | Explicado como un artefacto de la fuga | No mide capacidad de predecir el futuro |
| Unidad de observación | No se analizaba | Localidad × mes; 133 series, mediana de 29 meses, 93 con huecos | Determina la validación y el tipo de modelo (global vs local) |
| Partición entrenamiento/prueba | `train_test_split` aleatorio 80/20 | Validación temporal (pasado → futuro) | Aleatorio = entrenar con el futuro |
| Valores faltantes | `fillna(0)` y luego `dropna()` (sin efecto: no hay nulos) | Se distinguen **meses faltantes** (filas ausentes) de **ceros reales** | Rellenar energía con 0 inventa apagones |
| Calidad de datos | Solo `isnull` y `drop_duplicates` | 5 tipos de problemas detectados: potencia ×100/×1000 (29), horas = 0 con energía (3), energía imposible (13), energía = 0 (15), caídas > 90 % (17) | Esos errores sesgan cualquier modelo |
| Concentración | Tortas por departamento | Pareto: San Andrés 51 %, top 5 = 80 % | Evaluar por localidad, con métricas relativas (sMAPE, MASE) |
| Choques externos | No identificados | COVID-19 en 2020 (San Andrés −25 %) | Distorsiona la estacionalidad si no se trata |
| Agrupación | Por nombre de localidad | Por `id_loc` (nombres inconsistentes) | Evita separar o mezclar series |
| Fecha de demanda máxima | One-hot con miles de columnas; bloque con nombre mal escrito (`FEHCA`) que nunca se ejecutó | Se convierte a fecha; poco útil para pronóstico mensual | Ruido y sobreajuste |
| Nombres de columnas | Con tildes y espacios | `snake_case` y diccionario de datos con unidades | Menos errores, código más legible |
| Modelo de referencia | Ninguno | Ingenuo (mes anterior) e ingenuo estacional (hace 12 meses) | Un modelo solo vale si les gana |
| Contenido del repositorio | Notebook mezclado con una app web ajena (nextONE) | Proyecto separado: `datos/`, `notebooks/`, `figuras/`, `docs/` | Claridad para la entrega |

---

## Sección 2 · Limpieza de datos
Notebook: `notebooks/02_limpieza.ipynb` · Salidas: `datos/processed/energia_limpia.csv`, `bitacora_limpieza.csv`, `localidades.csv`

| Tema | Antes (original) | Ahora (corregido) | Por qué importa |
|---|---|---|---|
| Criterio de limpieza | `fillna(0)`, `dropna()`, `drop_duplicates()` (sin efecto) | Principio: corregir solo si los datos indican el valor correcto; si no, `NaN`; nunca inventar | Limpieza defendible y auditable |
| Detección de errores | Ninguna | Factor de carga FC = E / (P·h·días), comparado con el normal de cada localidad | Usa la física para detectar incoherencias sin otra fuente de datos |
| Errores de escala | No detectados | R1: 29 potencias ÷10ᵏ y 7 energías ×10ᵏ (los desvíos caen exactamente en −1, −2, −3) | Ej.: Leticia dic-2020 venía en MWh; San Andrés abr-2021 con potencia ×100 |
| Horas = 0 con energía | No detectado | R2: horas → `NaN` (3 filas) | Imposible físicamente; el valor correcto no se puede deducir |
| Registros de otra localidad | No detectado | R3a/R3b: `NaN` en 3 filas (Leticia nov-2020, Puerto Conto may-2020, Puerto Leguízamo may-2020) | Un valor ajeno contaminaría el modelo |
| Energía = 0 | Se trataba igual que "menor acceso" | R4: se conserva como evento real + banderas `sin_servicio` (18) y `servicio_parcial` (24) | Los apagones son reales en las ZNI; no son errores |
| Meses faltantes | Filas ausentes, invisibles | R6: calendario completo, 475 meses faltantes explícitos con bandera | Evita que `shift(1)` tome el mes equivocado |
| COVID-19 | Ignorado | R7: variable `covid` (mar–dic 2020) | Se mide su efecto en lugar de borrar 2020 |
| Localidades a modelar | Todas mezcladas | R8: 78 elegibles (≥24 meses, ≥100 kWh/mes) = 99,2 % de la energía | Series muy cortas no permiten entrenar ni evaluar |
| Trazabilidad | Ninguna | Bitácora con 47 cambios (fila, regla, antes, después) | El profesor puede auditar cada corrección |

---

## Sección 3 · Análisis exploratorio para series de tiempo
Notebook: `notebooks/03_exploracion_series.ipynb` · Salida: `datos/processed/energia_eda.csv`

| Tema | Antes (original) | Ahora (corregido) | Por qué importa |
|---|---|---|---|
| Enfoque del análisis | Histogramas y tortas (cuánto hay) | Nivel, tendencia, estacionalidad y choques (cómo se mueve en el tiempo) | Es lo que necesita un modelo de pronóstico |
| Efecto calendario | No considerado | Febrero "−7 %" desaparece al usar kWh/día | **Objetivo = kWh/día**; el modelo no aprende algo que ya se sabe |
| Estacionalidad | No analizada | Débil (perfil ±3–5 %, sin pico en el rezago 12) | El ingenuo estacional y el SARIMA aportan poco |
| Autocorrelación | No analizada | Alta a 1–3 meses en localidades grandes (0,71), baja en pequeñas (0,37) | Los rezagos recientes son la mejor información |
| Tendencia | No analizada | +7 % (2021, rebote), +3 % anual en 2022–2023 | Modelar el cambio respecto al nivel reciente (los árboles no extrapolan) |
| Volatilidad | No analizada | Grandes ~7 % mensual; pequeñas y medianas > 20 % | Se espera menor precisión en las veredas; evaluar por grupo |
| Oferta vs demanda | No considerada | Con horas estables, la volatilidad de las veredas baja de ~30 % a ~8 % | En las ZNI se mide **energía servida**: el ruido viene sobre todo de la operación |
| Choques | No analizados | Se revierten (correlación −0,30 entre cambios consecutivos) | Referencia adicional: promedio de 3 meses |
| COVID-19 | Ignorado | Típica −7 %; San Andrés −32 %; otros casos mezclados con fallas | Variable `covid`; evaluar en 2022–2023 |

---

## Sección 4 · Modelos de pronóstico y validación temporal
Notebook: `notebooks/04_modelos.ipynb` · Salidas: `datos/processed/predicciones_s4.csv`, `metricas_s4.csv`

| Tema | Antes (original) | Ahora (corregido) | Por qué importa |
|---|---|---|---|
| Qué se predice | Horas de servicio del mismo mes | log(kWh/día) del mes siguiente (1 mes) y a 3 meses | Es un pronóstico real del futuro |
| Variables | E y P del mismo mes (fuga), `ENERGÍA ACTIVA` duplicada | 13 variables conocidas en el origen (rezagos relativos al nivel, horas rezagadas, mes, COVID) | Sin fuga; justificadas en la Sección 3 |
| Qué aprende el ML | Valor absoluto | Cambio respecto al nivel reciente | Los árboles no extrapolan; permite un modelo global |
| Meses faltantes | — | `NaN` manejado nativamente por RF/GB (sklearn 1.9) | No se inventan valores |
| Validación | `train_test_split` aleatorio | Origen rodante: 12 meses (jul-2022 a jun-2023), reentrenando cada mes | Simula el uso real |
| Comparación | Ninguna referencia | 3 referencias + ETS local + 2 modelos ML globales | Un modelo solo vale si gana a lo simple |
| Métricas | MAE, RMSE en horas | sMAPE (promedio y mediana), MAE en MWh, MASE; por tamaño | Comparables entre localidades |
| Resultado 1 mes | "MAE 0,70 h" (no comparable) | RF 11,0 % vs ingenuo 12,0 % (no significativo, IC95 % [−1,9; +0,2]) | Conclusión honesta |
| Resultado 3 meses | — | RF 13,6 % vs mejor referencia 15,3 % (significativo; gana en el 69 % de las localidades) | El ML aporta más a mayor horizonte |
| Prueba de significancia | Ninguna | Bootstrap por localidad (2.000 remuestreos) | Distingue mejora real de azar |
| Interpretación | Ninguna | Importancia por permutación: `lag0`, `lag_est`, `nivel`, horas | Se entiende qué usa el modelo |
| Local vs global | — | El global (RF) le gana al ETS local; el ETS no le gana ni al ingenuo | Confirma la literatura sobre series cortas |

---

## Sección 5 · Comparativa final
Notebook: `notebooks/05_comparativa_final.ipynb` · Guion: `docs/GUION_PRESENTACION.md`

Experimento: se reproduce el modelo original y se le quitan los problemas uno por uno (MAE en horas/día).

| Paso | MAE |
|---|---|
| 0 · Original (fuga + partición aleatoria) | 0,70 h |
| 1 · Misma fuga, partición temporal | 0,83 h |
| 2 · Pronóstico real del mes siguiente (RF, sin fuga) | 0,99 h |
| 2 · Regla ingenua: mismas horas que este mes | 0,96 h |
| Predecir siempre el promedio | 6,60 h |

**Conclusión:** sin fuga, el modelo original no supera a una regla trivial. Su "buen" MAE venía de reconstruir horas ≈ E / (P·FC·días) con datos del mismo mes. Además, el código original ya no se ejecuta en scikit-learn 1.9 (columna `ENERGÍA ACTIVA` duplicada).

| Meta | Estimado al inicio | Resultado |
|---|---|---|
| Modelo mensual bien evaluado | ~90 % | ✅ Logrado |
| Superar al ingenuo estacional | ~65–75 % | ✅ 11,0 % vs 17,6 % |
| Superar al ingenuo simple | — | ⚠️ Significativo a 3 meses, no a 1 mes |
| MAPE < 10 % en todas las localidades | ~30 % | ❌ Grandes ~5–7 %, veredas 13–20 % |
| Paper con los mismos datos y objetivo | ~10 % | ❌ No existe: es un aporte del trabajo |
