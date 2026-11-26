# Guía de sustentación
## Pronóstico mensual de energía en las Zonas No Interconectadas (ZNI) de Colombia

**Cómo usar esta guía.** Léela con el notebook de cada sección abierto al lado. Cada parte tiene cinco bloques:
- **Para qué:** el objetivo de la sección.
- **Qué hace el código:** los bloques importantes, explicados.
- **Qué produce:** archivos y figuras.
- **Cifras para recordar.**
- **Cómo defenderlo:** qué decir si te preguntan.

Al final están la comparación con los papers, un banco de preguntas y una hoja de cifras.

---

## Índice
1. [El proyecto en un minuto](#1-el-proyecto-en-un-minuto)
2. [Mapa del proyecto](#2-mapa-del-proyecto)
3. [Conceptos que debes dominar](#3-conceptos-que-debes-dominar)
4. [Sección 1 · Entender los datos](#4-sección-1--entender-los-datos-y-definir-el-problema)
5. [Sección 2 · Limpieza](#5-sección-2--limpieza-de-datos)
6. [Sección 3 · Exploración de series](#6-sección-3--análisis-exploratorio-de-series-de-tiempo)
7. [Sección 4 · Modelos](#7-sección-4--modelos-y-validación-temporal)
8. [Sección 5 · Comparativa final](#8-sección-5--comparativa-final)
9. [Comparación con los papers](#9-comparación-con-los-papers)
10. [Banco de preguntas de sustentación](#10-banco-de-preguntas-de-sustentación)
11. [Qué no decir](#11-qué-no-decir)
12. [Hoja de cifras](#12-hoja-de-cifras)

---

## 1. El proyecto en un minuto

> "Las ZNI generan su propia energía, casi siempre con diésel, y planificar el combustible exige saber cuánta energía se va a necesitar. Con la telemetría del Centro Nacional de Monitoreo del IPSE (133 localidades, enero de 2020 a junio de 2023) construimos un pronóstico mensual de energía activa por localidad, a 1 y 3 meses.
>
> La versión original del proyecto tenía una fuga de información: predecía las horas de servicio usando la energía y la potencia del mismo mes, con las que las horas se calculan casi con una fórmula. La corregimos desde cero: definimos bien el problema, limpiamos los datos con reglas físicas documentadas, analizamos las series y comparamos seis modelos con validación temporal.
>
> Un Random Forest global obtiene 11,0 % de error a 1 mes y 13,6 % a 3 meses. La mejora sobre las referencias simples es estadísticamente significativa a 3 meses. El hallazgo principal es que en las ZNI se mide energía servida, no demanda: el límite de precisión lo pone la operación del servicio, no el modelo."

---

## 2. Mapa del proyecto

```
datos/raw/energia.csv                 ← datos originales (3.294 filas)
   │
   ▼  01_entender_datos.ipynb         renombra columnas, diagnostica, define el problema
datos/interim/s1_renombrado.csv
   │
   ▼  02_limpieza.ipynb               8 reglas + bitácora + calendario completo
datos/processed/energia_limpia.csv    (3.769 filas, con banderas)
datos/processed/bitacora_limpieza.csv (47 cambios)
   │
   ▼  03_exploracion_series.ipynb     calendario, estacionalidad, tendencia, volatilidad
datos/processed/energia_eda.csv       (solo las 78 localidades elegibles + variables nuevas)
   │
   ▼  04_modelos.ipynb                6 modelos, origen rodante, métricas, bootstrap
datos/processed/predicciones_s4.csv, metricas_s4.csv
   │
   ▼  05_comparativa_final.ipynb      reproduce el modelo original y demuestra la fuga
```

**Idea clave:** cada notebook **lee lo que guardó el anterior**. Por eso se ejecutan en orden. El notebook original está intacto en `original/` para poder compararlo.

---

## 3. Conceptos que debes dominar

| Concepto | Explicación sencilla | Dónde aparece |
|---|---|---|
| **ZNI** | Zonas del país sin conexión al Sistema Interconectado Nacional (SIN); generan su propia energía, sobre todo con diésel | Todo el proyecto |
| **Energía activa (kWh)** | Energía útil entregada en el mes. **Es lo que pronosticamos** | Objetivo |
| **Potencia máxima (kW)** | El pico de demanda del mes | Limpieza, variables |
| **Factor de carga (FC)** | FC = E / (P_max × horas × días). Qué tan cerca del pico opera el sistema en promedio. Siempre está entre 0 y 1; en las ZNI ronda 0,75 | Secciones 1 y 2 |
| **Panel de datos** | Muchas entidades (localidades) observadas en el tiempo. No son filas independientes | Sección 1 |
| **Fuga de información (*data leakage*)** | Usar para predecir información que en la vida real no estaría disponible en ese momento. Da errores artificialmente bajos | Secciones 1 y 5 |
| **Validación temporal / origen rodante** | Entrenar solo con el pasado, evaluar el mes siguiente, avanzar un mes y repetir | Sección 4 |
| **Horizonte (h)** | Cuántos meses hacia adelante se pronostica (h = 1 o h = 3) | Sección 4 |
| **Rezago (*lag*)** | El valor de una variable en meses anteriores (lag 1 = mes pasado) | Secciones 3 y 4 |
| **Autocorrelación** | Qué tanto se parece una serie a sí misma desplazada L meses | Sección 3 |
| **Estacionalidad** | Patrón que se repite cada año (por ejemplo, diciembre siempre alto) | Sección 3 |
| **Efecto calendario** | Los meses tienen distinto número de días; febrero "consume menos" solo por tener 28 | Sección 3 |
| **Modelo ingenuo** | "El próximo mes = el último mes". La referencia mínima que todo modelo debe superar | Sección 4 |
| **Ingenuo estacional** | "El próximo mes = el mismo mes del año anterior" | Sección 4 |
| **ETS (Holt amortiguado)** | Modelo clásico de series de tiempo: estima nivel y tendencia y "frena" la tendencia hacia el futuro. Se ajusta uno por localidad | Sección 4 |
| **Modelo global vs local** | Global: **un** modelo entrenado con todas las localidades. Local: un modelo por localidad | Sección 4 |
| **Random Forest** | Promedio de cientos de árboles de decisión entrenados con muestras distintas. Robusto y estable | Sección 4 |
| **Gradient Boosting** | Árboles en secuencia, donde cada uno corrige el error del anterior (familia de LightGBM/XGBoost) | Sección 4 |
| **sMAPE** | Error porcentual simétrico: 2·\|pronóstico − real\| / (\|pronóstico\| + \|real\|). Comparable entre localidades de distinto tamaño | Sección 4 |
| **MAE** | Error absoluto medio, en las unidades originales (MWh). Lo domina San Andrés | Sección 4 |
| **MASE** | MAE dividido por el error histórico del ingenuo. < 1 = mejor que el ingenuo histórico | Sección 4 |
| **Bootstrap** | Remuestrear los datos muchas veces para ver cuánto varía un resultado por azar. Da intervalos de confianza | Sección 4 |
| **Importancia por permutación** | Desordenar una variable y medir cuánto empeora el modelo. Si empeora mucho, la variable importa | Sección 4 |

---

## 4. Sección 1 · Entender los datos y definir el problema
**Notebook:** `notebooks/01_entender_datos.ipynb`

### Para qué
Antes de limpiar o modelar hay que responder cuatro preguntas: qué significa cada columna, qué es una fila, cuánta historia hay y qué vamos a predecir. Esta sección **solo observa y documenta**; no cambia ningún dato.

### Qué hace el código

**1.1 · Carga y renombrado**
```python
RENOMBRE = {"ENERGÍA ACTIVA": "e_activa", "POTENCIA MÁXIMA": "pot_max", ...}
df = raw.rename(columns=RENOMBRE)
df["fecha"] = pd.to_datetime(dict(year=df.anio, month=df.mes, day=1))
```
- Cambia los nombres con tildes y espacios por nombres cortos. En el original, un error de tipeo (`'FEHCA DEMANDA MÁXIMA'`) hizo que un bloque **nunca se ejecutara** sin que nadie lo notara.
- Crea una columna `fecha` (día 1 de cada mes) para trabajar como serie de tiempo.

**1.2 · ¿Qué es una fila?**
```python
df.duplicated(["id_loc", "fecha"]).sum()   # → 0
```
- Comprueba que la pareja (localidad, mes) no se repite. Conclusión: **cada fila es una localidad en un mes** → 133 series de tiempo.

**1.3 · Cobertura**
```python
g = df.groupby("id_loc").agg(n_meses=("fecha", "nunique"), inicio=("fecha", "min"), fin=("fecha", "max"))
g["span"] = ...           # meses entre el primer y el último reporte
g["huecos"] = g.span - g.n_meses
```
- Cuenta cuántos meses tiene cada localidad y cuántos faltan en medio.
- El **mapa de presencia** (`imshow` de una tabla localidad × mes con 1/0) muestra los huecos visualmente.

**1.4 · Concentración (Pareto):** suma la energía por localidad y la ordena. San Andrés = 51 %.

**1.5 · Series de ejemplo:** grafica 6 localidades. `asfreq("MS")` deja visibles los meses faltantes como cortes en la línea.

**1.6 · Problemas de calidad:** crea "banderas" (condiciones verdadero/falso) y cuenta cuántas filas cumplen cada una:
```python
flags = {"energía = 0": d.e_activa == 0,
         "horas = 0 pero energía > 0": (d.horas_dia == 0) & (d.e_activa > 0),
         "pot_max > 50× su mediana": d.pot_max > 50 * med_pot, ...}
```

**1.7 · La relación horas ↔ energía/potencia:** calcula `E / (P × días)` y lo compara con las horas reportadas → correlación 0,97. **Esta es la prueba de la fuga del modelo original.**

**1.8 · Definición del problema:** tabla con la decisión: objetivo = `e_activa`, horizonte de 1 y 3 meses, solo información pasada, validación temporal.

### Qué produce
`datos/interim/s1_renombrado.csv`, `s1_resumen_localidades.csv` y 5 figuras (`s1_*.png`).

### Cifras para recordar
133 localidades · 18 departamentos · 42 meses (ene-2020 a jun-2023) · mediana de 29 meses por localidad · 93 localidades con huecos · solo 7 completas · San Andrés 51 %, top 5 = 80 % · correlación horas vs E/(P·días) = 0,97 · factor de carga típico 0,75.

### Cómo defenderlo
- "Una fila no es un caso independiente, es un punto de una serie de tiempo. Por eso no se puede usar partición aleatoria."
- "Cambiamos el objetivo porque el profesor pidió un pronóstico energético mensual, y porque las horas del mismo mes no se pueden predecir sin fuga."
- "Las horas no se descartan: entran como variable, pero **rezagadas** (del mes anterior)."

---

## 5. Sección 2 · Limpieza de datos
**Notebook:** `notebooks/02_limpieza.ipynb`

### Para qué
Decidir qué hacer con cada problema detectado, con **reglas escritas** y **sin inventar datos**.

> Principio: corregir solo cuando los propios datos dicen cuál es el valor correcto; si no, marcar como faltante (`NaN`).

### Qué hace el código

**La bitácora (`registrar`)**
```python
def registrar(mascara, regla, columna, nuevos_valores):
    # por cada fila afectada guarda: localidad, fecha, regla, columna, valor antes, valor después
    ...
    df.loc[idx, columna] = nuevos
```
Toda corrección pasa por esta función. Así cada cambio queda auditable en `bitacora_limpieza.csv`.

**La herramienta clave (`calcular_referencias`)**
```python
d["fc"] = d.e_activa / (d.pot_max * d.horas_dia * dias)        # factor de carga de cada fila
normal = d.fc.between(0.3, 1.0)                                # filas "sanas"
d["ref_fc"] = mediana del FC de la localidad (solo filas sanas)
d["desvio_fc"] = np.log10(d.fc / d.ref_fc)                     # cuántas potencias de 10 se aleja
d["desvio_p"]  = np.log10(d.pot_max / d.ref_pot_max)           # ¿la potencia es la de siempre?
d["desvio_e"]  = np.log10(d.e_activa / d.ref_e_activa)         # ¿la energía es la de siempre?
```
- Un `desvio_fc` de −2 significa que la fila tiene un FC **100 veces menor** de lo normal.
- El histograma de `desvio_fc` muestra los errores agrupados **exactamente** en −1, −2 y −3. Es la figura central de la limpieza (`s2_desvio_fc.png`).

**R1 · Errores de escala**
```python
k = (-df.desvio_fc).round()                                    # 1, 2 o 3
es_escala = k.isin([1, 2, 3]) & ((df.desvio_fc + k).abs() < 0.25)
culpa_p = es_escala & ((df.desvio_p - k).abs() < 0.4)          # la potencia es la que está inflada
culpa_e = es_escala & ~culpa_p & ((df.desvio_e + k).abs() < 0.4)  # la energía es la que está reducida
registrar(culpa_p, ..., "pot_max", df.pot_max / 10 ** k)
registrar(culpa_e, ..., "e_activa", df.e_activa * 10 ** k)
```
- Primero identifica **que** hay un error de escala (FC) y luego **cuál variable** lo tiene, comparando con la historia de la localidad.

**R2 · Horas = 0 con energía > 0** → horas a `NaN` (es imposible, pero el valor correcto no se puede deducir).

**R3 · Registros inconsistentes**
- R3a: energía **y** potencia más de 10× lejos de lo normal, en la misma dirección → la fila parece de **otra localidad** → `NaN`.
- R3b: energía reactiva > 3× la activa (lo normal es 0,37×) → la activa no es creíble → `NaN`.

**R4 · Meses sin servicio:** si energía, potencia y horas son 0 a la vez, el sistema **no operó**. Es real → se conserva con las banderas `sin_servicio` y `servicio_parcial`.

**R5 · Nombre canónico:** un nombre único por `id_loc`.

**R6 · Calendario completo**
```python
meses = pd.date_range(s.fecha.min(), s.fecha.max(), freq="MS")   # todos los meses de cada localidad
panel = malla.merge(df, on=["id_loc", "fecha"], how="left")      # los meses ausentes quedan con NaN
```
- **Por qué importa:** sin esto, `shift(1)` ("el mes anterior") tomaría en silencio un mes equivocado cuando hay huecos.

**R7 · `covid`** = 1 entre marzo y diciembre de 2020.

**R8 · `elegible`** = al menos 24 meses válidos y mediana ≥ 100 kWh/mes.

**Verificación:** repite los chequeos de la Sección 1 sobre los datos limpios y grafica las series antes y después (`s2_antes_despues.png`).

### Qué produce
`energia_limpia.csv` (panel con banderas), `bitacora_limpieza.csv` (47 cambios) y `localidades.csv` (elegibilidad).

### Cifras para recordar
29 potencias corregidas (÷10ᵏ) · 7 energías corregidas (×10ᵏ) · 3 horas → NaN · 3 registros inválidos → NaN · 18 meses sin servicio, 24 con servicio parcial · 475 meses faltantes explícitos · **78 localidades elegibles = 99,2 % de la energía**.

### Cómo defenderlo
- "No corregimos a ojo. El factor de carga es una restricción física, y los errores caen en potencias exactas de 10; eso indica el valor correcto."
- "Ejemplo: Leticia, diciembre de 2020, reportó 3.738 kWh cuando su nivel es 3,7 millones. Venía en MWh. La energía reactiva lo confirma: era 317 veces la activa."
- "Los apagones no se borran: son información real sobre las ZNI."
- "Un chequeo automático también falla: Macedonia sale marcada porque su mediana de potencia es 0. Por eso revisamos cada caso."

---

## 6. Sección 3 · Análisis exploratorio de series de tiempo
**Notebook:** `notebooks/03_exploracion_series.ipynb`

### Para qué
Entender **cómo se mueve** la energía en el tiempo (nivel, tendencia, estacionalidad, choques) para decidir qué variables y qué modelos usar.

### Qué hace el código

**3.1 · Efecto calendario**
```python
p["e_dia"] = p.e_activa / p.dias                       # energía por día
p["idx_dia"] = p.e_dia / promedio_de_la_localidad      # índice: 1 = normal
perfil = mediana del índice por mes del año
```
- Divide por el promedio de cada localidad para poder mezclar San Andrés con una vereda.
- Resultado: febrero pasa de 0,93 a 1,00 → **no era estacionalidad, era el número de días**.

**3.2 · Autocorrelación**
```python
p["dm"] = log(e_dia) - promedio de la localidad          # solo las variaciones
corr(dm, dm desplazado L meses)  para L = 1..12, por grupo de tamaño
```
- Rezago 1 alto (0,71 en las grandes) → persistencia. Sin pico en el rezago 12 → estacionalidad débil.

**3.3 · Tendencia:** crecimiento interanual = log(mes) − log(mismo mes del año anterior). Mediana entre localidades: +7 % (2021), +3 % (2022), +3 % (2023).

**3.4 · Volatilidad y reversión**
```python
p["d1"] = diferencia del log mes a mes (≈ % de cambio)
volatilidad = desviación estándar de d1 por localidad
corr(d1, d1 del mes siguiente) = −0,30                  # los choques se revierten
```

**3.5 · Oferta vs demanda:** separa las localidades con servicio limitado (< 23 h) de las de 24 h y mide la volatilidad en todos los meses frente a los meses en que las horas no cambiaron.

**3.6 · COVID:** compara abril–diciembre de 2020 con los mismos meses de 2021.

### Qué produce
`energia_eda.csv` (con `e_dia`, `tamano`, etc.) y 6 figuras (`s3_*.png`).

### Cifras para recordar
Febrero: 0,93 → 1,00 con kWh/día · autocorrelación rezago 1: grandes 0,71, pequeñas 0,37 · crecimiento ~3 %/año · volatilidad: grandes 6,6 %, pequeñas 22 %, medianas 24 % · reversión −0,30 · servicio limitado: volatilidad 30 % → 8 % con horas estables · COVID: típica −7 %, San Andrés −32 %.

### Cómo defenderlo
- "Usamos kWh/día porque el modelo no debe aprender algo que ya sabemos con certeza: cuántos días tiene el mes." Esto coincide con Castaño (2010), que documenta el efecto calendario en la demanda eléctrica colombiana.
- "La estacionalidad es débil; por eso el ingenuo estacional fue el peor modelo."
- **El hallazgo más importante:** "en las ZNI se mide energía servida. En las veredas, la mayor parte de la variación viene de cuántas horas operó la planta, no de cuánto quiso consumir la gente."
- "No atribuimos todo a la pandemia: en algunas localidades la caída de 2020 se mezcla con fallas de suministro, y con estos datos no se puede separar."

---

## 7. Sección 4 · Modelos y validación temporal
**Notebook:** `notebooks/04_modelos.ipynb`

### Para qué
Responder: **¿un modelo de machine learning pronostica mejor que las reglas simples?**

### Qué hace el código

**Objetivo**
```python
p["y"] = np.log((p.e_activa / p.dias).where(p.e_activa > 5))
```
- Logaritmo de kWh/día. El log vuelve los errores **relativos** (San Andrés no domina) y garantiza pronósticos positivos.
- Los meses sin servicio quedan como `NaN`: un apagón no es pronosticable con estos datos.

**`construir_tabla(p, h)` · las variables**
```python
nivel = promedio(y_origen, y_origen-1, y_origen-2)       # nivel reciente
"lag0": y_origen - nivel, "lag1": ..., "lag2": ...       # rezagos relativos al nivel
"lag_est": y(hace 12 meses del objetivo) - nivel
"horas0", "horas1", "dhoras0", "horas_med", "parcial0", "n_obs3", "mes_obj", "covid_obj"
"y_obj": y desplazado h meses hacia adelante             # lo que queremos predecir
"pred_ingenuo", "pred_estacional", "pred_promedio3"     # las 3 referencias
```
- Una fila = (localidad, mes de origen). Todas las variables usan **solo información del origen o antes**.
- El modelo aprende `y_obj − nivel`, es decir, el **cambio** respecto al nivel reciente. Así puede seguir la tendencia aunque los árboles no extrapolen, y localidades de tamaños muy distintos se vuelven comparables (modelo global).

**`evaluar(p, h)` · el origen rodante**
```python
for T in PRUEBA:                                         # 12 meses: jul-2022 … jun-2023
    origen = T - h meses
    entreno = filas cuyo OBJETIVO es ≤ origen            # solo datos que ya existían
    prueba  = filas cuyo objetivo es T
    rf = RandomForestRegressor(300 árboles, min_samples_leaf=5).fit(X, y_obj - nivel)
    gb = HistGradientBoostingRegressor(...).fit(...)
    pred = nivel + modelo.predict(...)                   # se vuelve al nivel
    pred_ets = ExponentialSmoothing(serie hasta el origen, tendencia amortiguada)
```
- Reentrena **cada mes** (24 entrenamientos en total: 12 meses × 2 horizontes).
- Filtrar por **objetivo ≤ origen**, y no por origen, es lo que evita la fuga: el modelo nunca ve un valor real posterior al momento del pronóstico.

**`metricas(res)`:** vuelve a kWh/mes con `exp(y) × días` y calcula sMAPE (promedio y mediana), MAE y MASE.

**`comparar(res)` · bootstrap**
```python
dif por localidad = sMAPE(RF) - sMAPE(referencia)
2.000 veces: remuestrear localidades con reemplazo → promedio de dif
IC95 % = percentiles 2,5 y 97,5
```
- Se remuestrea **por localidad** porque los errores de una misma localidad están correlacionados.

**Importancia por permutación** sobre el modelo del último origen.

### Qué produce
`predicciones_s4.csv`, `metricas_s4.csv` y 4 figuras (`s4_*.png`).

### Cifras para recordar
| sMAPE promedio | 1 mes | 3 meses |
|---|---|---|
| Ingenuo | 12,0 % | 15,5 % |
| Ingenuo estacional | 17,6 % | 17,8 % |
| Promedio 3 meses | 12,1 % | 15,3 % |
| ETS local | 12,3 % | 15,9 % |
| **Random Forest global** | **11,0 %** | **13,6 %** |
| Gradient Boosting global | 12,0 % | 14,6 % |

- RF vs ingenuo, 1 mes: −0,8 puntos, IC95 % [−1,9; +0,2] → **no significativo**; gana en el 55 % de las localidades.
- RF vs ingenuo, 3 meses: −1,5 puntos, IC95 % [−2,8; −0,1] → **significativo**; gana en el 69 %.
- Mediana del sMAPE del RF: 5,8 % (1 mes) y 7,4 % (3 meses).
- Por tamaño (RF, 1 mes): pequeñas 13,2 %, medianas 15,5 %, grandes 5,2 %.
- Variables más importantes: `lag0`, `lag_est`, `nivel`, luego las de horas.

### Cómo defenderlo
- "Comparamos contra tres referencias porque un modelo que no les gana no aporta nada."
- "A un mes, la diferencia con el ingenuo no es estadísticamente significativa, y lo reportamos así. A tres meses sí lo es."
- "El modelo global le gana al ETS local, como predice Montero-Manso & Hyndman (2021) para muchas series cortas."
- "No optimizamos hiperparámetros mirando el periodo de prueba: eso sería otra forma de fuga."

---

## 8. Sección 5 · Comparativa final
**Notebook:** `notebooks/05_comparativa_final.ipynb`

### Para qué
**Demostrar con un experimento** (no solo afirmar) que el resultado original venía de la fuga.

### Qué hace el código
1. **Paso 0:** copia el código original (RF con `[ENERGÍA ACTIVA, POTENCIA MÁXIMA, ENERGÍA ACTIVA]` → horas, partición aleatoria). Primero muestra que **ese código falla** en scikit-learn 1.9 por la columna duplicada; luego lo reproduce con `.values` → MAE 0,70 h.
2. **Paso 1:** mismas variables, partición temporal → 0,83 h.
3. **Paso 2:** pronóstico real de las horas del mes siguiente con información disponible → RF 0,99 h vs ingenuo 0,96 h.
4. Tabla resumen antes/después y contraste con la viabilidad estimada al inicio.

### Cifras para recordar
0,70 → 0,83 → 0,99 h (RF) frente a 0,96 h (ingenuo) · predecir siempre el promedio = 6,60 h.

### Cómo defenderlo
- "El 0,70 parecía excelente porque se comparaba, sin decirlo, con predecir el promedio (6,6 h). Contra una referencia sensata, el modelo original no aporta nada."
- "Esto no es una crítica personal: es el error más común en series de tiempo, y por eso la validación temporal y las referencias ingenuas son obligatorias."

---

## 9. Comparación con los papers

### Tabla resumen

| | **Nuestro trabajo** | Colmenares-Quintero et al. 2022 (*Energies*) | Colmenares-Quintero et al. 2021 (*Cogent Eng.*) | Colmenares-Quintero et al. 2026 (*Energy Sources B*) | Gil-Vera 2016 (*Revista EIA*) | Montero-Manso & Hyndman 2021 (*IJF*) | Bustos et al. 2025 (*Applied Sciences*) |
|---|---|---|---|---|---|---|---|
| **Zona** | ZNI | ZNI | ZNI | ZNI | SIN (interconectado) | General (metodológico) | Regiones sin AMI |
| **Datos** | Telemetría CNM-IPSE, 2020–2023, mensual | Datos del gobierno sobre servicio en ZNI, 2019–2020 | Datos abiertos del gobierno, 2018–2019 | Datos de ZNI (mayormente categóricos) | Demanda SIN de XM, 2008–2014, mensual | Miles de series de competencias (M1, M3, M4…) | Consumo mensual de >500.000 usuarios, 2020–2024 |
| **Objetivo** | **Pronosticar** energía a 1 y 3 meses | Agrupar localidades por calidad del servicio | Caracterizar el servicio con inteligencia de negocios | Predecir **actividades económicas** | Pronosticar demanda mensual | Cómo pronosticar grupos de series | Diseñar muestras representativas |
| **Método** | Referencias, ETS, RF y GB globales | K-means, K-medoids, DIANA, mapas de calor | Inteligencia de negocios / análisis descriptivo | Árboles de decisión | Modelos aditivos con tendencia lineal, cuadrática y cúbica | Teoría + experimentos local vs global | Entropía de Shannon, divergencia KL |
| **¿Pronóstico temporal?** | **Sí** | No | No | No (clasificación) | Sí | Sí | No |

### Cada paper: qué tomamos y en qué nos diferenciamos

**1. Colmenares-Quintero et al. (2022).** *Data Analysis of Electricity Service in Colombia's Non-Interconnected Zones through Different Clustering Techniques.* Energies 15(20), 7644.
- **Qué hacen:** aplican K-means, K-medoids y DIANA a datos del servicio eléctrico en las ZNI (2019–2020). Identifican grupos de localidades con deficiencias de servicio, mayor consumo o pocas horas diarias, como candidatas a proyectos de energías renovables.
- **En qué nos parecemos:** mismas variables (energía, potencia, horas de servicio) y mismo territorio. Es tu **antecedente principal**.
- **En qué nos diferenciamos:** ellos **describen y agrupan** (análisis transversal). Nosotros **pronosticamos** (análisis temporal). Ellos trabajan con 2019–2020; nosotros con 2020–2023.
- **Cómo lo conectas:** "Ellos encontraron que las horas diarias de servicio distinguen a las localidades. Nosotros mostramos que esas mismas horas explican la mayor parte de la variación mensual de energía (Sección 3.5). Nuestro resultado complementa el suyo en la dimensión temporal."

**2. Colmenares-Quintero et al. (2021).** *Analysis of the energy service in non-interconnected zones of Colombia using business intelligence.* Cogent Engineering.
- **Qué hacen:** evalúan la prestación del servicio en las ZNI entre 2018 y 2019 con datos abiertos y una metodología de inteligencia de negocios.
- **Relación:** contexto descriptivo del problema; justifica la importancia de las ZNI. No modela ni pronostica.

**3. Colmenares-Quintero et al. (2026).** *Decision tree-based prediction of economic activities in Colombia's Non-Interconnected Zones.* Energy Sources, Part B 21(1).
- **Qué hacen:** usan árboles de decisión para predecir actividades económicas en las ZNI, con datos mayormente categóricos.
- **Relación:** muestra que el mismo grupo de investigación avanzó de lo descriptivo a lo **predictivo**, con modelos basados en árboles, como nuestro Random Forest. Pero predicen otra variable (actividad económica) y sin dimensión temporal.
- **Ojo:** no tuvimos acceso al texto completo. No afirmes detalles de sus resultados.

**4. Gil-Vera, V. D. (2016).** *Pronóstico de la demanda mensual de electricidad con series de tiempo.* Revista EIA 13(26). DOI 10.24050/reia.v13i26.749.
- **Qué hace:** pronostica la demanda **mensual** del SIN con datos de XM (2008–2014) usando modelos aditivos con tendencias lineal, cuadrática y cúbica.
- **En qué nos parecemos:** pronóstico mensual de electricidad en Colombia con series de tiempo. Es la **referencia metodológica colombiana** más cercana.
- **En qué nos diferenciamos:** él modela **una** serie agregada (todo el SIN), larga (7 años) y estable. Nosotros tenemos **133 series** cortas (mediana de 29 meses), con huecos y con choques de oferta. Por eso un modelo clásico por serie (como nuestro ETS) no funciona tan bien aquí, y el modelo global sí.

**5. Montero-Manso, P. & Hyndman, R. J. (2021).** *Principles and algorithms for forecasting groups of time series: Locality and globality.* International Journal of Forecasting 37(4), 1632–1653.
- **Qué hacen:** comparan, en teoría y con experimentos sobre miles de series, los modelos **locales** (uno por serie) con los **globales** (uno para todas). Concluyen que los globales pueden ser tan buenos o mejores, sobre todo cuando las series son cortas.
- **Relación:** es el **fundamento teórico** de nuestra decisión central. Nuestro resultado lo confirma: el RF global (11,0 %) supera al ETS local (12,3 %).

**6. Bustos et al. (2025).** *Evaluating Sampling Strategies for Characterizing Energy Demand in Regions of Colombia Without AMI Infrastructure.* Applied Sciences 15(17), 9588.
- **Qué hacen:** en regiones de Colombia sin medición inteligente (AMI), con solo registros mensuales de consumo, diseñan muestras representativas de usuarios.
- **Relación:** respalda que en zonas con infraestructura limitada **la resolución mensual es la realista**, y que trabajar con ella es un problema reconocido en la literatura reciente.

**7. Castaño, E. (2010).** *El "efecto calendario" y la especificación de un modelo de series de tiempo para la demanda de electricidad.* Lecturas de Economía (Universidad de Antioquia). DOI 10.17533/udea.le.n35a5115.
- **Relación:** documenta que el número de días (y su composición) afecta la demanda eléctrica mensual en Colombia. **Respalda nuestra decisión de usar kWh/día** (Sección 3.1).

### La frase para cerrar este punto
> "Los trabajos previos sobre las ZNI son descriptivos (clustering, inteligencia de negocios) o predicen otras variables. Los trabajos de pronóstico mensual en Colombia se hicieron sobre el sistema interconectado, con una sola serie larga. Hasta donde revisamos, este es el primer pronóstico mensual por localidad con la telemetría del CNM, y lo resolvimos con el enfoque de modelo global que recomienda la literatura para muchas series cortas."

> ⚠️ Di siempre **"hasta donde revisamos"**: nunca afirmes que no existe ningún trabajo igual.

---

## 10. Banco de preguntas de sustentación

**Sobre el problema y los datos**

1. **¿De dónde salen los datos?**
   De la telemetría del Centro Nacional de Monitoreo (CNM) del IPSE: energía activa y reactiva, potencia máxima y horas de servicio por localidad y mes, de 2020 a 2023.

2. **¿Por qué cambiaron el objetivo de horas a energía?**
   Porque se pidió un pronóstico energético mensual, y porque las horas del mismo mes se deducen de la energía y la potencia (correlación 0,97). Predecirlas así no es pronosticar.

3. **¿Por qué solo 78 de las 133 localidades?**
   Las otras 55 tienen menos de 24 meses de datos (entraron tarde al monitoreo). Con eso no hay meses suficientes para entrenar y evaluar. Las 78 concentran el 99,2 % de la energía.

4. **¿Qué pasa con las localidades excluidas en la práctica?**
   Para ellas se puede usar el ingenuo o el promedio de 3 meses. A medida que acumulen historia, entran al modelo global.

**Sobre la limpieza**

5. **¿Cómo saben que la limpieza no inventó datos?**
   Solo se corrigieron errores cuyo factor es una potencia exacta de 10, visibles en el histograma del factor de carga. Lo demás quedó como `NaN`. Hay 47 cambios en la bitácora, con su valor antes y después.

6. **¿Por qué no rellenaron los meses faltantes?**
   Porque rellenar es inventar. Random Forest y Gradient Boosting en scikit-learn manejan `NaN` directamente. Solo el ETS necesitó interpolar, y únicamente para ajustarse.

7. **¿Por qué no borraron los meses con energía 0?**
   Porque energía, potencia y horas coinciden en que el sistema no operó: es un apagón real. Se marcan, pero no se pronostican (es una limitación declarada).

**Sobre el análisis**

8. **¿Por qué kWh/día y no kWh/mes?**
   Febrero aparecía 7 % más bajo solo por tener 28 días. Con kWh/día la diferencia desaparece. Es el efecto calendario (Castaño, 2010).

9. **¿Por qué logaritmo?**
   Hace los errores relativos (5 % es 5 % en San Andrés y en una vereda), evita pronósticos negativos y convierte crecimientos porcentuales en sumas.

10. **¿Hay estacionalidad?**
    Débil: ±3–5 %, sin pico en el rezago 12. Por eso el ingenuo estacional fue el peor modelo.

**Sobre los modelos**

11. **¿Por qué no SARIMA ni redes neuronales (LSTM)?**
    La estacionalidad es débil y hay ~29 meses por serie: muy poco para un SARIMA por localidad. El ETS, que es más simple, no le ganó ni al ingenuo. Una LSTM necesita muchos más datos. Elegimos un modelo global siguiendo a Montero-Manso & Hyndman (2021).

12. **¿Qué es un modelo global y por qué funciona?**
    Un solo modelo entrenado con todas las localidades. Como aprende el **cambio** relativo al nivel reciente (en log), el patrón "después de un mes malo viene una recuperación" se puede aprender de todas a la vez, en lugar de con 29 meses de una sola.

13. **¿Por qué el modelo predice el cambio y no el valor?**
    Los árboles no pueden predecir valores mayores a los que vieron al entrenar. Con una tendencia de +3 %/año, predecir el valor directo los dejaría "atascados". Predecir el cambio respecto al nivel reciente lo resuelve.

14. **¿Qué es el origen rodante?**
    Para cada uno de los 12 meses de prueba: entrenar con los datos disponibles hasta el mes anterior, pronosticar, guardar el error y avanzar. Simula el uso real del modelo.

15. **¿Por qué sMAPE y no solo MAE?**
    El MAE en kWh lo domina San Andrés (51 % de la energía). El sMAPE es un porcentaje y permite comparar localidades de cualquier tamaño.

16. **Su modelo no le gana al ingenuo a 1 mes. ¿Para qué sirve?**
    A 1 mes la mejora (−0,8 puntos) no es significativa, y lo reportamos así. A 3 meses sí lo es (IC95 % de −2,8 a −0,1) y gana en el 69 % de las localidades. Para planificar combustible, el horizonte de 3 meses es justamente el más útil.

17. **¿Qué es el bootstrap y por qué por localidad?**
    Remuestrear 2.000 veces las localidades con reemplazo y recalcular la diferencia de error. Si el intervalo del 95 % no incluye 0, la mejora no es azar. Se hace por localidad porque los errores de una misma localidad están correlacionados.

18. **¿Por qué el Gradient Boosting, más sofisticado, fue peor?**
    Con ~2.000 filas de entrenamiento, el promedio de muchos árboles independientes (Random Forest) es más estable. Más complejidad no garantiza mejor resultado con pocos datos.

19. **¿Qué variables usa más el modelo?**
    `lag0` (cuánto se alejó el último mes del nivel reciente), `lag_est` (mismo mes del año anterior) y `nivel`; después, las horas de servicio. El modelo decide **cuánto creerle al último mes**.

20. **¿Por qué el error es tan distinto entre localidades?**
    Las grandes con 24 h de servicio son estables (~5 %). Las veredas con servicio limitado dependen de fallas y del combustible, que no están en los datos (13–20 %). El límite lo pone la operación, no el modelo.

**Sobre el proyecto original**

21. **¿Qué estaba mal en la versión original?**
    Fuga de información (horas del mismo mes calculables a partir de E y P), partición aleatoria en datos temporales, ninguna referencia de comparación, variable duplicada, `fillna(0)` sin efecto y un bloque con un error de tipeo que nunca se ejecutaba.

22. **¿Cómo demuestran que el 0,70 era por la fuga?**
    Lo reprodujimos exactamente y le quitamos la fuga: el error sube a 0,99 h, peor que la regla trivial "mismas horas que este mes" (0,96 h).

**Sobre el futuro**

23. **¿Cómo mejorarían el modelo?**
    Con datos de combustible y mantenimiento (para anticipar fallas), con meses posteriores a junio de 2023, con un modelo que pronostique la probabilidad de falla de servicio, y con una optimización de hiperparámetros sobre una validación separada.

---

## 11. Qué no decir

| ❌ No digas | ✅ Di |
|---|---|
| "El modelo tiene 89 % de precisión" | "El error típico es 11 % a 1 mes y 13,6 % a 3 meses, medido con validación temporal" |
| "El modelo es mucho mejor que lo simple" | "La mejora es modesta: significativa a 3 meses, no concluyente a 1 mes" |
| "No existe ningún trabajo igual" | "Hasta donde revisamos, no encontramos un pronóstico mensual con datos del CNM" |
| "La caída de 2020 fue por el COVID" | "En San Andrés fue claramente el COVID; en otras localidades se mezcla con fallas de servicio" |
| "Predecimos la demanda" | "Pronosticamos la energía servida, que en las ZNI es demanda limitada por la oferta" |
| "Eliminamos los datos malos" | "Corregimos los errores de escala demostrables; lo demás quedó como faltante, con bitácora" |
| "El modelo original estaba mal hecho" | "El modelo original tenía una fuga de información, el error más común en series de tiempo" |

---

## 12. Hoja de cifras

| Dato | Valor |
|---|---|
| Localidades / departamentos / meses | 133 / 18 / 42 (ene-2020 a jun-2023) |
| Meses por localidad (mediana) | 29 |
| Localidades con huecos / completas | 93 / 7 |
| San Andrés / top 5 de la energía | 51 % / 80 % |
| Correlación horas vs E/(P·días) | 0,97 |
| Factor de carga típico | 0,75 |
| Correcciones en la bitácora | 47 (29 potencias, 7 energías, 3 horas, 3 registros inválidos…) |
| Meses faltantes explícitos | 475 |
| Localidades elegibles | 78 (99,2 % de la energía) |
| Febrero con kWh/mes vs kWh/día | 0,93 vs 1,00 |
| Crecimiento anual típico | ~3 % (2022–2023) |
| Volatilidad grandes / pequeñas | 6,6 % / 22 % |
| Volatilidad con servicio limitado: todos los meses vs horas estables | 30 % / 8 % |
| COVID: típica / San Andrés | −7 % / −32 % |
| **RF sMAPE 1 mes / 3 meses** | **11,0 % / 13,6 %** |
| Ingenuo 1 mes / 3 meses | 12,0 % / 15,5 % |
| RF vs ingenuo, 3 meses (IC95 %) | −1,5 puntos [−2,8; −0,1]; gana en el 69 % de las localidades |
| Modelo original: MAE con fuga → sin fuga | 0,70 h → 0,99 h (ingenuo 0,96 h) |
