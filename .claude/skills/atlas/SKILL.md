---
name: atlas
description: Abrir o continuar un volumen del Atlas del proyecto — leer la implementación de un subsistema y depositarla en la cartografía. Úsala antes de mapear, cartografiar, auditar o "entender cómo funciona" cualquier parte de Terrario, Genesis o RNE. Palabras clave, atlas, cartografía, mapear, volumen, cartografiar, leer la implementación, K0 K1 K2 K3.
---

# Atlas · cómo se abre un volumen

Un volumen del Atlas es **una lectura de implementación**, no un inventario.
Contar líneas, filas y imports es el punto de partida; el entregable es el
mecanismo: qué calcula cada pieza, con qué dato, bajo qué guarda, con qué
consecuencia, y con `fichero:línea` verificado.

El índice y el estado de los ocho volúmenes están en
`docs/ATLAS_00_INDICE.md`. El programa vive en **cuatro árboles**, no en uno.

## 0 · Antes de leer código · la cartografía es caché

Éste es el paso que el Atlas 02 y el 03 se saltaron, y costó cinco hallazgos que
ya estaban en el mapa (§XLII).

```bash
python scripts/cartografia_check.py --section "IX"     # ¿sigue vigente?
```

Si la sección está **vigente por hash**, está en caché: se cita y **no se
re-deriva**. Si contradice lo que la lectura encuentra, se corrige **en su
sitio** y se marca la corrección. Nunca se deja un segundo relato en paralelo:
dos taxonomías del mismo objeto es el defecto que esta serie ya reportó dos
veces.

Las secciones que solapan se buscan por índice:

```bash
grep -n "^# " docs/CARTOGRAFIA_TERRARIO_01.md
```

## 1 · Leer

Los módulos enteros, no `grep`. Ejecutar lo que se pueda ejecutar en vez de
suponerlo — una cifra medida vale más que una inferida, y el proyecto ya perdió
tres resultados por afirmar sin correr.

## 2 · Clasificar lo hallado

| | |
|---|---|
| **K0** | establecido, verificable abriendo el fichero en la línea citada |
| **K1** | documentado, pero la implementación puede haber derivado |
| **K2** | no resuelto — **se declara, no se rellena** |
| **K3** | exige evidencia externa que el proyecto no tiene |

## 3 · Depositar y verificar

La sección va a `docs/CARTOGRAFIA_TERRARIO_01.md` como encabezado de primer
nivel. **Después de escribirla, verificar cada cita**: de 23 citas escritas en
un volumen, 4 estaban mal al escribirlas.

```bash
python scripts/cartografia_check.py          # hashes + citas fichero:línea
python scripts/cartografia_check.py --write  # SÓLO tras reescribir la prosa
```

> `--write` no puede comprobar que alguien haya releído. Regenerado tras
> cambiar código sin reescribir el texto, **el gate se pone verde sobre prosa
> vieja**. Ya pasó.

## 4 · Entregar

Un informe general en `docs/ATLAS_0N_<NOMBRE>.md`, entregado **al cerrar** el
volumen — no goteado por hallazgo — y el índice actualizado.

## Lo que este método prohíbe

* re-derivar una sección vigente en vez de citarla;
* dejar dos relatos del mismo mecanismo;
* correr `--write` para callar la alarma;
* rellenar un K2 por intuición;
* escribir una cita `fichero:línea` sin abrirla después.
