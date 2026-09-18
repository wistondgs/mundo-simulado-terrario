# Brief · Documentos que el corpus necesita

> **Anexo.** El documento maestro es `ORIENTACIONES_CORPUS_COMPLETAS.md`, que cubre estado,
> defectos, contrato de claims, tipos de documento, artefactos, hashes, construcción,
> adquisición y aceptación. Esto queda como detalle de una parte.


**2026-09-18.** Para quien vaya a conseguir los ficheros. Cada entrada trae identificación exacta,
qué desbloquea, y por qué la necesito ahora y no después.

## La regla que hace válida una adquisición

Del propio corpus HEA: **una URL sola no cuenta como incorporación.** Un documento adquirido exige
fichero local, procedencia, metadatos mínimos, validación y **sha256**. Un PDF sin hash es un PDF,
no una fuente.

Para las doce primeras el **sha256 ya está declarado** en el snapshot sellado. Eso significa que la
adquisición es verificable: si el fichero que se consigue no da ese hash, **no es el documento que
el corpus dice que es**, y hay que reportarlo en vez de usarlo.

---

# Grupo A · Doce documentos que YA ESTÁN EN EL CORPUS y cuyo PDF no está aquí

Estos ya tienen `source_id`, metadatos, DOI y sha256 declarados en
`theory_snapshots/theory-f59dbb6d6ee3850c/SOURCE_PROVENANCE_v0.3.csv`. Lo único que falta es el
fichero: su `archivo_local` apunta a `/workspace/scratch/...`, una ruta de la máquina de ingesta
que aquí no existe.

**Son el trabajo más barato del proyecto**: no hay que decidir nada, ya están aprobados, y sin
ellos sus 59 conceptos son incitables para siempre.

## A.1 · Prioridad MÁXIMA — cierran «¿tiene mundo el organismo?»

Esta es la pregunta abierta más importante. El organismo percibe hoy una ventana 5×5 de números y
su «modelo del mundo» predice su propio latente. No tiene objetos, ni espacio, ni permanencia.

| id | documento | por qué |
|---|---|---|
| **X01** | Spelke, *Principles of Object Perception*, 1990 · `10.1207/s15516709cog1401_3` | Qué hace que algo sea **un objeto** y no una mancha de píxeles. Sin esto no hay criterio de qué debería representar el organismo. |
| **X02** | O'Regan & Noë, *A sensorimotor account of vision and visual consciousness*, 2001 · `10.1017/S0140525X01000115` | El mundo constituido **a través de la acción**, no por representación interna. Es la alternativa a construirle un modelo: que el mundo sea lo que su acción revela. |
| **X07** | Piloto, Weinstein, Battaglia & Botvinick, *Intuitive physics learning in a deep-learning model*, 2022 · `10.1038/s41562-022-01394-8` | Un modelo profundo que **aprende física intuitiva**. El caso más cercano a lo que Terrario intenta, ya hecho por otros. |

Cierran la familia `PERCEPTION_WORLD`, hoy `OPEN_GAP` con prioridad `HIGH`.

## A.2 · Prioridad ALTA — el linaje y el desarrollo

El bloqueo medido hoy: A4 y A5 no se distinguen dentro de una vida porque 68 pasos no bastan para
que un gradiente de política cambie nada, y el organismo muere de inanición a los 133.

| id | documento | por qué |
|---|---|---|
| **X16** | Smith & Thelen, *Development as a dynamic system*, 2003 · `10.1016/S1364-6613(03)00156-6` | El desarrollo como sistema dinámico: capacidades que emergen en escalas de tiempo largas. Es la teoría de por qué una vida no basta. |
| **X03** | Adolph & Hoch, *Motor Development: Embodied, Embedded, Enculturated*, 2019 · `10.1146/annurev-psych-010418-102836` | Cómo se adquiere la locomoción. El organismo no llega a las estaciones: 2 columnas de 34. |
| **TI-0085-PATCH** | Kirkpatrick et al., *Overcoming catastrophic forgetting*, 2017 | Qué se rompe al acumular experiencia entre episodios. Es el riesgo directo del linaje. |
| **TI-0092-PATCH** | Wang, Lehman, Clune & Stanley, *POET*, 2019 | Generar entornos cada vez más difíciles emparejados con agentes. Es la alternativa a que yo diseñe los mundos a mano — que es lo que hice y salió mal. |

Cierran `DEVELOPMENT` y tocan `LEARNING`, ambas `OPEN_GAP` prioridad `HIGH`.

## A.3 · Prioridad MEDIA

| id | documento | familia |
|---|---|---|
| **X06** | Oudeyer, Kaplan & Hafner, *Intrinsic Motivation Systems*, 2007 · `10.1109/TEVC.2006.890271` | `MOTIVATION_VALUE`. Conceptualmente cubierto por Pathak (TI-0090) y HEA-005, pero el corpus advierte que **progreso de aprendizaje ≠ error de predicción bruto**, y esa distinción solo se puede zanjar con el original. |
| **X08** | Squire, Genzel, Wixted & Morris, *Memory Consolidation*, 2015 · `10.1101/cshperspect.a021766` | `MEMORY`. Hoy `EPMEM-A1` y `LTMEM-A1` no tienen procedencia, y su memoria satura al clamp. |
| **X09, X11, X12, X13, X14** | Laland; Mesoudi & Thornton; Derex et al.; Galesic et al. | `TRANSMISSION_CULTURE`, `COLLECTIVE_DISTRIBUTED`. No bloquean nada ahora mismo. |

---

# Grupo B · Lo que ningún corpus cubre y el proyecto necesita

Aquí no hay `source_id` previo: hay que decidir el documento, no solo conseguirlo. Doy el hueco y
una sugerencia, pero la elección es humana.

**B.1 · Ultraestabilidad implementada, no descrita.** Ashby la define (`HEA-014 §7/26`: segundo
lazo intermitente y lento que cambia parámetros al salirse las variables esenciales) y Di Paolo &
Iizuka la operacionalizan parcialmente. Falta una fuente que la implemente y la **mida** en un
agente artificial. Sin ella, el segundo lazo de A5 se diseñaría por mi cuenta — el pecado de hoy.

**B.2 · Cómo se mide la agencia.** `HEA-009` (Particle Lenia, respuesta a perturbación) está en
extracción ahora mismo y puede bastar. Si no basta, hace falta una fuente metodológica sobre
medición de agencia bajo perturbación, porque la decisión humana de hoy fija que el endpoint
primario mida **regulación de variables esenciales bajo perturbación**, y ese instrumento no puede
salir de mi criterio.

**B.3 · Emociones funcionales.** Sofroniew et al., Anthropic 2026, *Emotion Concepts and their
Function in a Large Language Model*, `arXiv:2604.07729`. Mencionado en conversación y **no está en
ningún corpus de esta máquina**. Si va a fundamentar una familia de conceptos experienciales, hay
que ingerirlo con sha256 como cualquier otro. Advertencia que ya di: sus emociones funcionales son
**heredadas del preentrenamiento sobre texto humano**, y A4 no lee — de ahí se trasplanta el
método, no el mecanismo.

---

# Lo que hay que devolver por cada documento

```
source_id          el que ya tiene, o uno nuevo si es del grupo B
fichero local      ruta en esta máquina
sha256             calculado
COINCIDE_CON_CORPUS  sí / no / no aplica     ← si es NO, reportar y NO usar
url y fecha de recuperación
tipo de acceso     (legal: repositorio de autor, open access, PMC…)
```

Si un documento no se consigue por licencia o por estar caído, **decirlo** y dejarlo marcado
`NO_ADQUIRIDO` con el motivo. Un hueco declarado es corpus; un hueco tapado no lo es.

# Orden que yo seguiría

```
1.  X01, X02, X07          el mundo. Es la pregunta abierta más importante.
2.  X16, X03               el desarrollo y el linaje. Es el bloqueo medido.
3.  TI-0085, TI-0092       lo que se rompe al acumular, y cómo generar mundos.
4.  X06, X08               motivación y memoria. Desbloquean procedencia de 3 capacidades.
5.  grupo B                requieren decisión humana antes de adquirir.
6.  X09, X11, X12, X13, X14   no bloquean nada hoy.
```
