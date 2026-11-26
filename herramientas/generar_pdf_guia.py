"""Convierte docs/GUIA_SUSTENTACION.md en un HTML de estudio con colores (luego Chrome lo imprime a PDF)."""
import re, sys, html
from pathlib import Path
import markdown

ROOT = Path(sys.argv[1]); OUT = Path(sys.argv[2])
FIG = (ROOT / "figuras").resolve().as_uri()
src = (ROOT / "docs" / "GUIA_SUSTENTACION.md").read_text(encoding="utf-8")

# ---------- contenido adicional para el aprendizaje ----------
FIGURAS = {
    "4.": [("s1_mapa_presencia.png", "Mapa de presencia de datos",
            "Cada fila es una localidad y cada columna un mes. Azul = hay dato; blanco = falta. Los huecos blancos sueltos son meses sin reporte. El bloque blanco de abajo a la izquierda son localidades que <b>entraron tarde</b> al monitoreo. Conclusión: las series son cortas y con huecos, y eso descarta un modelo por localidad."),
           ("s1_pareto.png", "Concentración de la energía (Pareto)",
            "Barras: % de energía de cada localidad, ordenadas de mayor a menor. Línea roja: % acumulado. La primera barra (San Andrés) ya es el 51 %. Conclusión: hay que evaluar por localidad y con errores en %, no en kWh."),
           ("s1_horas_formula.png", "La prueba de la fuga del modelo original",
            "Eje X: energía ÷ (potencia × días), calculado sin usar las horas. Eje Y: las horas reportadas. Los puntos caen sobre la línea roja: las horas <b>se deducen</b> de la energía y la potencia. Por eso el modelo original tenía un error tan bajo: reconstruía una fórmula.")],
    "5.": [("s2_desvio_fc.png", "Desvío del factor de carga (la figura central de la limpieza)",
            "Cada barra cuenta filas según cuántas potencias de 10 se aleja su factor de carga de lo normal. La gran mayoría está en 0 (filas coherentes). Los errores forman picos <b>exactamente</b> en −1, −2 y −3 (÷10, ÷100, ÷1000). Si los errores fueran ruido, estarían repartidos; al ser potencias exactas de 10, son errores de digitación o de unidades, y el valor correcto se puede recuperar."),
           ("s2_antes_despues.png", "Antes (rojo) y después (azul) de limpiar",
            "En escala logarítmica, un error ×100 aparece como un salto de dos escalones. Después de limpiar, la serie azul queda en su nivel habitual. Donde el dato no se pudo recuperar (Leticia, noviembre de 2020), queda un <b>hueco</b>, no un valor inventado.")],
    "6.": [("s3_perfil_mensual.png", "Efecto calendario",
            "Rojo: energía del mes. Azul: energía por día. La caída de febrero (0,93) desaparece con kWh/día (1,00). No era estacionalidad: febrero tiene 28 días. Por eso el modelo trabaja en kWh/día."),
           ("s3_autocorrelacion.png", "Autocorrelación por tamaño de localidad",
            "Eje X: cuántos meses hacia atrás se compara. Eje Y: qué tanto se parece. Las grandes (azul oscuro) se parecen mucho al mes anterior (0,71). En el rezago 12 no hay pico, así que la estacionalidad es débil. Conclusión: lo más útil son los meses recientes."),
           ("s3_horas_vs_energia.png", "La energía sigue a las horas de servicio",
            "Cada punto es un mes de una localidad con servicio limitado. Eje X: cuánto cambiaron las horas de servicio. Eje Y: cuánto cambió la energía. La nube diagonal muestra que si la planta opera más horas, se entrega más energía. Esto es <b>energía servida</b> (oferta), no solo demanda."),
           ("s3_volatilidad.png", "Volatilidad según tamaño y horas de servicio",
            "Eje X: tamaño de la localidad (escala log). Eje Y: cuánto varía de un mes a otro. Color: horas de servicio al día (amarillo = 24 h). Las localidades grandes y con 24 h son estables (~5 %). Las pequeñas, con pocas horas (morado), varían más de 20 %.")],
    "7.": [("s4_origen_rodante.png", "Validación con origen rodante",
            "Cada fila es un pronóstico. Azul: los datos con los que se entrena. Rojo: el mes que se evalúa. Al pasar a la siguiente fila, el entrenamiento crece un mes. El modelo <b>nunca</b> ve el mes que pronostica."),
           ("s4_comparacion_modelos.png", "Comparación de los 6 modelos",
            "Barras más cortas = menor error. Gris: referencias simples. Azul: ETS local. Rojo: modelos globales de ML. El Random Forest global es el mejor en ambos horizontes; la ventaja es pequeña a 1 mes y más clara a 3 meses."),
           ("s4_importancia.png", "Qué variables usa el Random Forest",
            "Cuánto empeora el modelo si se desordena cada variable. <code>lag0</code> (qué tan raro fue el último mes) es la más importante: el modelo aprende cuánto creerle al último dato. <code>covid_obj</code> vale 0 porque en 2022–2023 no hay meses COVID."),
           ("s4_pronosticos_ejemplo.png", "Pronósticos frente a la realidad",
            "Negro: real. Gris: ingenuo. Rojo: Random Forest. A la derecha de la línea punteada está el periodo de prueba. En San Andrés y Leticia ambos siguen bien la serie. En Beté, las caídas bruscas (fallas) no se pueden anticipar.")],
    "8.": [("s5_escalera_fuga.png", "La escalera de la fuga",
            "Error del modelo original a medida que se le quitan los problemas. Pasa de 0,70 h (con fuga) a 0,99 h (pronóstico real), y queda <b>peor</b> que la regla trivial (0,96 h). El 0,70 solo parecía bueno frente a predecir siempre el promedio (6,60 h).")],
}

CHEQUEO = {
    "4.": ["¿Por qué cada fila no es un caso independiente y qué consecuencia tiene eso?",
           "¿Qué es una fuga de información y dónde estaba en el modelo original?",
           "¿Por qué se trabaja por localidad y no con el total de las ZNI?"],
    "5.": ["¿Qué es el factor de carga y por qué sirve para encontrar errores?",
           "¿Cuándo se corrige un dato y cuándo se deja como NaN?",
           "¿Por qué los meses con energía 0 no se borran?",
           "¿Para qué sirve el calendario completo (regla R6)?"],
    "6.": ["¿Por qué febrero parecía consumir menos?",
           "¿Qué dice la autocorrelación sobre la estacionalidad?",
           "¿Por qué decimos que en las ZNI se mide energía servida y no demanda?"],
    "7.": ["¿Qué significa entrenar con filas cuyo OBJETIVO es ≤ origen?",
           "¿Por qué el modelo aprende el cambio y no el valor?",
           "¿Por qué la mejora a 1 mes no es significativa y la de 3 meses sí?",
           "¿Qué es un modelo global y por qué le gana al ETS local?"],
    "8.": ["¿Qué tres pasos tiene el experimento de la escalera?",
           "¿Por qué un MAE de 0,70 h parecía bueno?"],
}

RESPUESTAS = {
    "4.": ["Porque los datos son 133 series de tiempo (localidad × mes). Los meses de una localidad dependen unos de otros. Consecuencia: no se puede usar partición aleatoria; hay que entrenar con el pasado y evaluar con el futuro.",
           "Usar para predecir información que no se conocería en el momento del pronóstico. El modelo original predecía las horas con la energía y la potencia del mismo mes, y con esas dos las horas se calculan casi exactamente (correlación 0,97).",
           "Porque San Andrés es el 51 % de la energía: pronosticar el total sería pronosticar San Andrés. Además, las localidades son de tamaños muy distintos y deben evaluarse con errores en %."],
    "5.": ["FC = E / (P × horas × días). Está entre 0 y 1 y ronda 0,75. Si una fila da un FC 100 veces menor de lo normal, alguna variable tiene un error de escala.",
           "Se corrige cuando el error es una potencia exacta de 10 y se sabe qué variable la tiene (R1). Si el error es real pero el valor correcto no se puede deducir, se deja como NaN (R2, R3).",
           "Porque energía, potencia y horas coinciden en 0: el sistema no operó. Es un evento real de las ZNI, no un error. Se marca con una bandera.",
           "Para que los meses faltantes existan como filas con NaN. Sin esto, shift(1) tomaría el mes equivocado cuando hay huecos."],
    "6.": ["Porque tiene 28 días. Con kWh/día la diferencia desaparece (0,93 → 1,00). Es el efecto calendario.",
           "Que es débil: no hay pico en el rezago 12. Un mes no se parece especialmente al mismo mes del año anterior.",
           "Porque en las localidades con servicio limitado la energía cambia cuando cambian las horas de operación. En los meses con horas estables, la volatilidad baja de ~30 % a ~8 %."],
    "7.": ["Que el modelo solo aprende de ejemplos cuyo valor real ya se conocía en ese momento. Así nunca ve el futuro.",
           "Porque los árboles no pueden predecir valores mayores a los que vieron, y hay tendencia creciente. Además, el cambio relativo es comparable entre localidades, lo que permite un modelo global.",
           "A 1 mes, el intervalo de confianza del bootstrap incluye el 0 [−1,9; +0,2]. A 3 meses lo excluye [−2,8; −0,1], y el RF gana en el 69 % de las localidades.",
           "Un solo modelo entrenado con todas las localidades. Con series cortas (~29 meses), aprender de todas a la vez da más información que ajustar cada serie por separado (Montero-Manso & Hyndman, 2021)."],
    "8.": ["(0) Reproducir el original: 0,70 h. (1) Partición temporal: 0,83 h. (2) Pronóstico real sin fuga: 0,99 h, frente a 0,96 h de la regla trivial.",
           "Porque se comparaba implícitamente con predecir siempre el promedio (6,60 h), y no con una referencia sensata como 'las mismas horas que este mes'."],
}

ANALOGIAS = r"""
<div class="analogias">
<h3>🧠 Los conceptos difíciles, explicados con analogías</h3>
<div class="an"><b>Fuga de información</b> — Es como hacer un examen con la hoja de respuestas al lado: la nota es altísima, pero no mide lo que sabes. El modelo original "veía" la energía y la potencia del mismo mes, que prácticamente contienen la respuesta.</div>
<div class="an"><b>Partición aleatoria vs temporal</b> — Predecir el clima de mañana entrenando con el clima de pasado mañana no es pronosticar. La partición aleatoria mezcla meses futuros en el entrenamiento; la temporal solo usa el pasado.</div>
<div class="an"><b>Origen rodante</b> — Es como el meteorólogo que cada día pronostica el siguiente con lo que sabe hasta hoy, anota si acertó y al día siguiente repite con un dato más. Evaluamos así 12 meses seguidos.</div>
<div class="an"><b>Modelo global</b> — Un médico que vio a 78 pacientes aprende más que uno que vio a uno solo durante 29 visitas. El modelo global aprende patrones comunes ("después de un mes malo viene una recuperación") de todas las localidades a la vez.</div>
<div class="an"><b>Modelo ingenuo</b> — Es la "vara mínima": si tu modelo sofisticado no le gana a "el mes que viene será igual a este", no aporta nada.</div>
<div class="an"><b>Factor de carga</b> — Si un carro tiene un tanque de 50 litros, no puede recorrer el equivalente a 500 litros en un mes. La energía de un mes no puede superar lo que permiten la potencia máxima y las horas de servicio. Si los números lo violan, alguno está mal escrito.</div>
<div class="an"><b>Bootstrap</b> — Para saber si una moneda está cargada no basta con lanzarla una vez. El bootstrap "relanza" el experimento 2.000 veces remuestreando localidades, y mira si el modelo sigue ganando en casi todos los casos.</div>
<div class="an"><b>Logaritmo</b> — Equivocarse en 1.000 kWh es nada en San Andrés y enorme en una vereda. El logaritmo convierte los errores en porcentajes, para tratar a todas las localidades por igual.</div>
</div>
"""

RUTA = r"""
<div class="ruta">
<h3>📅 Ruta de estudio sugerida (5 sesiones)</h3>
<table>
<tr><th>Sesión</th><th>Qué estudiar</th><th>Meta</th></tr>
<tr><td>1</td><td>Capítulos 1–3 (resumen, mapa, conceptos y analogías)</td><td>Explicar el proyecto en 1 minuto sin leer</td></tr>
<tr><td>2</td><td>Capítulos 4–5 + notebooks 01 y 02 abiertos</td><td>Explicar la fuga y el factor de carga con las figuras</td></tr>
<tr><td>3</td><td>Capítulo 6 + notebook 03</td><td>Explicar el efecto calendario y "energía servida"</td></tr>
<tr><td>4</td><td>Capítulos 7–8 + notebooks 04 y 05</td><td>Explicar el origen rodante, la tabla de resultados y la escalera</td></tr>
<tr><td>5</td><td>Capítulos 9–12: papers, preguntas, qué no decir, cifras</td><td>Responder las 23 preguntas en voz alta</td></tr>
</table>
</div>
"""

LEYENDA = r"""
<div class="leyenda">
<span class="lg c-para">🎯 Para qué</span><span class="lg c-cod">💻 Qué hace el código</span>
<span class="lg c-prod">📦 Qué produce</span><span class="lg c-fig">📊 Cómo leer las figuras</span>
<span class="lg c-cif">🔢 Cifras para recordar</span><span class="lg c-def">🗣️ Cómo defenderlo</span>
<span class="lg c-chk">✅ Comprueba que entiendes</span>
</div>
"""

BLOQUES = {"Para qué": ("c-para", "🎯"), "Qué hace el código": ("c-cod", "💻"), "Qué produce": ("c-prod", "📦"),
           "Cifras para recordar": ("c-cif", "🔢"), "Cómo defenderlo": ("c-def", "🗣️")}

# ---------- preprocesado del markdown ----------
src = re.sub(r"\n## Índice\n.*?\n---\n", "\n", src, flags=re.S)          # índice propio
src = re.sub(r"(\n\*\*\d\. [^\n]+\n)- ", r"\1\n- ", src)                  # listas en la sección de papers
cuerpo = src.split("\n## 1. ", 1)[1]
cuerpo = "1. " + cuerpo
partes = ["## " + s.lstrip("\n") for s in cuerpo.split("\n## ") if s.strip()]

def figuras_html(clave):
    out = ['<div class="blk c-fig"><div class="lbl">📊 Cómo leer las figuras</div>']
    for f, t, txt in FIGURAS[clave]:
        out.append(f'<figure><img src="{FIG}/{f}"><figcaption><b>{t}.</b> {txt}</figcaption></figure>')
    out.append("</div>")
    return "\n".join(out)

def chequeo_html(clave):
    items = "".join(f"<li>{html.escape(q)}</li>" for q in CHEQUEO[clave])
    return f'<div class="blk c-chk"><div class="lbl">✅ Comprueba que entiendes</div><ol>{items}</ol><p class="nota">Respuestas en el Anexo.</p></div>'

nuevo = []
for parte in partes:
    titulo = parte.splitlines()[0][3:].strip()
    clave = titulo.split(" ", 1)[0]
    parte = re.sub(r"\n---\s*$", "", parte.rstrip())
    if "### Para qué" in parte:
        cab, *subs = re.split(r"\n### ", parte)
        bloques = [cab]
        for s in subs:
            nombre, _, resto = s.partition("\n")
            nombre = nombre.strip()
            if nombre == "Cifras para recordar" and clave in FIGURAS:
                bloques.append(figuras_html(clave))
            cls, ico = BLOQUES.get(nombre, ("c-otro", "•"))
            bloques.append(f'<div class="blk {cls}" markdown="1">\n<div class="lbl">{ico} {nombre}</div>\n\n{resto.strip()}\n\n</div>')
        bloques.append(chequeo_html(clave))
        parte = "\n\n".join(bloques)
    elif clave == "8." and clave in FIGURAS:
        parte += "\n\n" + figuras_html(clave) + "\n\n" + chequeo_html(clave)
    if clave == "3.":
        parte += "\n\n" + ANALOGIAS
    cls = {"9.": "sec-papers", "10.": "sec-preg", "11.": "sec-nodecir", "12.": "sec-cifras"}.get(clave, "")
    nuevo.append(f'<section class="cap {cls}" markdown="1">\n\n{parte}\n\n</section>')

anexo = ['<section class="cap" markdown="1">\n\n## Anexo · Respuestas de autoevaluación\n']
nombres = {"4.": "Sección 1", "5.": "Sección 2", "6.": "Sección 3", "7.": "Sección 4", "8.": "Sección 5"}
for k, rs in RESPUESTAS.items():
    anexo.append(f'<div class="blk c-chk"><div class="lbl">✅ {nombres[k]}</div><ol>' +
                 "".join(f"<li><i>{html.escape(q)}</i><br>{html.escape(r)}</li>" for q, r in zip(CHEQUEO[k], RESPUESTAS[k])) + "</ol></div>")
anexo.append("\n</section>")

md = markdown.Markdown(extensions=["tables", "fenced_code", "md_in_html", "toc", "sane_lists"])
cuerpo_html = md.convert("\n\n".join(nuevo + ["\n".join(anexo)]))
cuerpo_html = cuerpo_html.replace("<blockquote>\n<p>⚠️", '<blockquote class="warn">\n<p>⚠️')

toc = "".join(f'<li><a href="#{t["id"]}">{t["name"]}</a></li>' for t in md.toc_tokens)

CSS = r"""
@page { size: A4; margin: 16mm 15mm 18mm 15mm;
  @bottom-center { content: counter(page) " / " counter(pages); font: 9pt 'Segoe UI'; color: #64748b; }
  @top-right { content: "Guía de sustentación · ZNI Colombia"; font: 8pt 'Segoe UI'; color: #94a3b8; } }
@page :first { @bottom-center { content: none; } @top-right { content: none; } }
:root { --azul:#2563eb; --morado:#7c3aed; --teal:#0d9488; --verde:#16a34a; --naranja:#ea580c; --rosa:#db2777; --pizarra:#334155; }
body { font-family: 'Segoe UI', Calibri, sans-serif; font-size: 10.3pt; line-height: 1.5; color: #1e293b; }
h2 { font-size: 19pt; color: #fff; background: linear-gradient(90deg,#1e3a8a,#2563eb); padding: 10px 16px; border-radius: 10px; margin: 0 0 14px; }
.sec-papers h2 { background: linear-gradient(90deg,#065f46,#0d9488); }
.sec-preg h2 { background: linear-gradient(90deg,#9a3412,#ea580c); }
.sec-nodecir h2 { background: linear-gradient(90deg,#9f1239,#db2777); }
.sec-cifras h2 { background: linear-gradient(90deg,#14532d,#16a34a); }
h3 { color: #1e3a8a; font-size: 12.5pt; margin: 16px 0 6px; border-bottom: 2px solid #dbeafe; padding-bottom: 3px; }
section.cap { break-before: page; }
code { font-family: 'Cascadia Mono', Consolas, monospace; font-size: 8.8pt; background: #eef2ff; color: #4338ca; padding: 1px 4px; border-radius: 4px; }
pre { background: #0f172a; color: #e2e8f0; padding: 10px 12px; border-radius: 8px; font-size: 8.4pt; line-height: 1.4; white-space: pre-wrap; break-inside: avoid; border-left: 4px solid #a78bfa; }
pre code { background: none; color: inherit; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9pt; break-inside: auto; }
th { background: #1e3a8a; color: #fff; text-align: left; padding: 5px 7px; }
td { padding: 4px 7px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
tr { break-inside: avoid; }
blockquote { margin: 10px 0; padding: 8px 14px; background: #eff6ff; border-left: 5px solid var(--azul); border-radius: 0 8px 8px 0; color: #1e3a8a; }
blockquote::before { content: "💡 Idea clave"; display: block; font-weight: 700; font-size: 9pt; color: var(--azul); margin-bottom: 2px; }
blockquote.warn { background: #fff7ed; border-color: var(--naranja); color: #7c2d12; }
blockquote.warn::before { content: "Atención"; color: var(--naranja); }
.blk { border-radius: 10px; padding: 8px 14px 6px; margin: 12px 0; border: 1.5px solid; break-inside: auto; }
.blk .lbl { break-after: avoid; font-weight: 800; font-size: 10.5pt; margin-bottom: 4px; text-transform: uppercase; letter-spacing: .4px; }
.c-para { background: #eff6ff; border-color: #93c5fd; } .c-para .lbl { color: var(--azul); }
.c-cod  { background: #f5f3ff; border-color: #c4b5fd; } .c-cod .lbl { color: var(--morado); }
.c-prod { background: #f0fdfa; border-color: #5eead4; } .c-prod .lbl { color: var(--teal); }
.c-fig  { background: #f8fafc; border-color: #cbd5e1; } .c-fig .lbl { color: var(--pizarra); }
.c-cif  { background: #f0fdf4; border-color: #86efac; } .c-cif .lbl { color: var(--verde); }
.c-def  { background: #fff7ed; border-color: #fdba74; } .c-def .lbl { color: var(--naranja); }
.c-chk  { background: #fdf2f8; border-color: #f9a8d4; } .c-chk .lbl { color: var(--rosa); }
.c-chk li { margin-bottom: 6px; } .nota { font-size: 8.5pt; color: #9d174d; margin: 2px 0 4px; }
figure { margin: 10px 0 14px; break-inside: avoid; }
figure img { display: block; margin: 0 auto; max-width: 100%; max-height: 92mm; border: 1px solid #e2e8f0; border-radius: 6px; background: #fff; }
.c-para, .c-prod, .c-cif, .c-def, .c-chk, .analogias .an { break-inside: avoid; }
figcaption { font-size: 9pt; color: #334155; background: #fff; border-left: 4px solid #64748b; padding: 5px 10px; margin-top: 4px; }
.analogias { margin-top: 14px; background: #fefce8; border: 1.5px solid #fde047; border-radius: 10px; padding: 8px 14px; }
.analogias h3 { color: #854d0e; border-color: #fde68a; }
.an { margin: 6px 0; padding-left: 10px; border-left: 3px solid #facc15; }
.sec-nodecir td:first-child { color: #b91c1c; } .sec-nodecir td:last-child { color: #15803d; font-weight: 600; }
.sec-preg ol > li { margin-bottom: 8px; } .sec-preg li strong { color: #c2410c; }
.sec-papers h3 { color: #065f46; border-color: #99f6e4; }
.sec-papers table { font-size: 7.6pt; } .sec-papers th { background: #0f766e; }
.sec-cifras td:last-child { font-weight: 700; color: #166534; }
/* portada */
.portada { height: 255mm; display: flex; flex-direction: column; justify-content: center; }
.portada .eti { color: #2563eb; font-weight: 700; letter-spacing: 2px; font-size: 11pt; }
.portada h1 { font-size: 32pt; line-height: 1.1; margin: 8px 0; color: #0f172a; }
.portada .sub { font-size: 14pt; color: #475569; margin-bottom: 26px; }
.portada .barra { height: 8px; width: 120px; border-radius: 4px; background: linear-gradient(90deg,#2563eb,#7c3aed,#0d9488,#16a34a,#ea580c,#db2777); margin-bottom: 26px; }
.leyenda { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0 18px; }
.lg { padding: 4px 10px; border-radius: 14px; font-size: 9pt; font-weight: 700; border: 1.5px solid; }
.lg.c-para{color:var(--azul)} .lg.c-cod{color:var(--morado)} .lg.c-prod{color:var(--teal)} .lg.c-fig{color:var(--pizarra)}
.lg.c-cif{color:var(--verde)} .lg.c-def{color:var(--naranja)} .lg.c-chk{color:var(--rosa)}
.ruta { background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 10px; padding: 6px 14px; }
.ruta h3 { margin-top: 6px; }
.toc { break-before: page; } .toc ol { font-size: 12pt; line-height: 2; list-style: none; padding-left: 6px; } .toc a { color: #1e3a8a; text-decoration: none; }
"""

portada = f"""
<div class="portada">
<div class="eti">GUÍA DE ESTUDIO Y SUSTENTACIÓN</div>
<h1>Pronóstico mensual de energía en las Zonas No Interconectadas de Colombia</h1>
<div class="sub">Qué hace cada parte del proyecto, cómo funciona el código, cómo se compara con la literatura y cómo defenderlo</div>
<div class="barra"></div>
<p><b>Cómo está organizada.</b> Cada sección del proyecto se explica con bloques de colores. Aprende a reconocerlos: siempre significan lo mismo.</p>
{LEYENDA}
{RUTA}
</div>
<div class="toc"><h2>Contenido</h2><ol>{toc}</ol></div>
"""

OUT.write_text(f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guía de sustentación ZNI</title>
<style>{CSS}</style></head><body>{portada}{cuerpo_html}</body></html>""", encoding="utf-8")
print("html ok", OUT)
