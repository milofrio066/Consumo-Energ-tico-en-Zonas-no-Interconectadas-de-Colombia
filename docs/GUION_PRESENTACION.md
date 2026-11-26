# Guion de presentación · Pronóstico mensual de energía en las ZNI de Colombia

Duración sugerida: 12–15 minutos · 10 diapositivas. Cada diapositiva indica la figura, el mensaje principal (lo que el público debe recordar) y qué decir.

---

### 1. Título y problema
**Mensaje:** en las ZNI la energía se genera localmente (casi siempre con diésel) y planificar el combustible requiere saber cuánta energía se va a necesitar.
**Decir:** "Trabajamos con la telemetría del Centro Nacional de Monitoreo del IPSE: 133 localidades, enero de 2020 a junio de 2023. La pregunta es: ¿podemos pronosticar la energía de cada localidad a 1 y 3 meses?"

### 2. Antecedentes (literatura)
**Mensaje:** existen estudios con estos datos, pero hacen clustering y caracterización, no pronóstico.
**Decir:**
- Colmenares-Quintero et al. (2022, *Energies*) y (2021, *Cogent Engineering*): caracterizan el servicio en las ZNI.
- Revista EIA (2016): pronóstico mensual con series de tiempo, pero para el sistema interconectado nacional (SIN), no para las ZNI.
- Montero-Manso & Hyndman (2021): un modelo global supera a modelos por serie cuando hay muchas series cortas.
- "No encontramos un pronóstico mensual con los datos del CNM: ese es el aporte."

### 3. Punto de partida: qué estaba mal en la versión original
**Figura:** `figuras/s5_escalera_fuga.png`
**Mensaje:** el modelo original (MAE 0,70 h) no pronosticaba: reconstruía una fórmula.
**Decir:** "Las horas de servicio se pueden calcular casi exactamente a partir de la energía y la potencia del mismo mes. Cuando lo convertimos en un pronóstico real, el modelo no supera a decir 'las mismas horas que este mes'."

### 4. Los datos: 133 series cortas
**Figura:** `figuras/s1_mapa_presencia.png` (o `s1_pareto.png`)
**Mensaje:** son series cortas (mediana de 29 meses), con huecos, y muy concentradas: San Andrés es el 51 % de la energía.
**Decir:** "Por eso trabajamos por localidad, con métricas en porcentaje y con un modelo global."

### 5. Limpieza basada en la física
**Figura:** `figuras/s2_desvio_fc.png`
**Mensaje:** el factor de carga revela errores de digitación exactos de ×10, ×100 y ×1000.
**Decir:** "No corregimos a ojo: si el error es una potencia exacta de 10, sabemos el valor correcto. Si no, el dato queda como faltante. Hay 47 cambios documentados en una bitácora."

### 6. Qué aprendimos de las series
**Figuras:** `figuras/s3_perfil_mensual.png` y `figuras/s3_horas_vs_energia.png`
**Mensaje 1:** la "caída de febrero" es solo que febrero tiene menos días. La estacionalidad es débil.
**Mensaje 2 (el más importante):** en las ZNI se mide **energía servida**, no demanda. Con horas de servicio estables, la volatilidad de las veredas baja de ~30 % a ~8 %.

### 7. Cómo evaluamos
**Figura:** `figuras/s4_origen_rodante.png`
**Mensaje:** origen rodante: se entrena solo con el pasado y se reentrena cada mes, durante 12 meses de prueba.
**Decir:** "Cada error es el que habríamos tenido usando el modelo en la vida real."

### 8. Resultados
**Figura:** `figuras/s4_comparacion_modelos.png`
**Mensaje:** el Random Forest global es el mejor (11,0 % a 1 mes, 13,6 % a 3 meses). La mejora es significativa a 3 meses, no a 1 mes.
**Decir:** "A un mes, 'igual que el mes pasado' es muy difícil de superar. A tres meses, el modelo aprovecha la recuperación después de los choques y las horas de servicio."

### 9. Dónde funciona y dónde no
**Figura:** `figuras/s4_pronosticos_ejemplo.png`
**Mensaje:** grandes con 24 h: ~5–7 % de error. Veredas con servicio limitado: 13–20 %, porque un apagón no se puede anticipar con estos datos.

### 10. Conclusiones y trabajo futuro
- Primer pronóstico mensual con datos del CNM, con validación temporal y comparación contra referencias.
- El límite de precisión lo pone la **operación del servicio**, no el modelo.
- **Trabajo futuro:** incorporar datos de combustible y mantenimiento, actualizar con meses posteriores a junio de 2023 desde datos.gov.co y pronosticar la probabilidad de falla de servicio.

---

## Preguntas probables y cómo responderlas

**"¿Por qué no usaron SARIMA / LSTM?"**
La estacionalidad es débil (no hay pico en el rezago 12) y hay ~29 meses por serie. Un SARIMA por localidad tiene muy poca información, y el ETS local, que es más simple, ya no le ganó ni al ingenuo. Una LSTM necesita muchos más datos.

**"Su modelo no le gana al ingenuo a 1 mes, ¿entonces no sirve?"**
A 1 mes la diferencia (−0,8 puntos) no es estadísticamente significativa. A 3 meses sí lo es (IC95 % de −2,8 a −0,1 puntos) y el modelo gana en el 69 % de las localidades. Además, reportar esto honestamente es parte del rigor: muchos trabajos no comparan con el ingenuo.

**"¿Por qué excluyeron 55 localidades?"**
Tienen menos de 24 meses de datos (entraron tarde al monitoreo) y en conjunto representan solo el 0,8 % de la energía. Con menos de 2 años no hay meses suficientes para entrenar y evaluar.

**"¿Cómo saben que la limpieza no inventó datos?"**
Solo se corrigió cuando el error era una potencia exacta de 10 (gráfica del desvío del factor de carga). Todo lo demás quedó como faltante. Cada cambio está en `datos/processed/bitacora_limpieza.csv`, con su valor antes y después.

**"¿Por qué el logaritmo y kWh/día?"**
kWh/día elimina el efecto de los días del mes (febrero). El logaritmo vuelve los errores relativos, para que San Andrés no domine el entrenamiento, y garantiza pronósticos positivos.
