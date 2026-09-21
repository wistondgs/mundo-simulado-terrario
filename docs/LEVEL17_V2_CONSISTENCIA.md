# 1.7 · V2 · revisión documental de consistencia

**Fecha:** 2026-09-20 · sin experimentos nuevos · **no es el cierre**

---

## 1 · La tabla archivada reproduce el agregado

```
pares archivados                 16
Γ == D_C^A − D_C^B en las 16     True   máx |dif| 0.0e+00
media recomputada del archivo    +0.280587    reportada +0.280587
CI95 inferior recomputado        +0.262909    reportado +0.262909
sha256 de resultados/v2_confirmatorio_16_pares.json   0956e104fbfd8577
```

## 2 · El ledger · una precisión sobre la forma

**No hay «16 ledgers».** Hay **uno**, con 28 entradas:

```
12 entradas de alcance campaña    L17-0…L17-7, L17-9…L17-12
16 entradas por vida              L17-8, una por cada par
─────────────────────────────
28 entradas · 13 nombres distintos · faltan: ninguno
```

Es una diferencia de diseño, no de contabilidad: doce gates son afirmaciones sobre
la campaña —linaje, par de mundos, procedencia, pureza del canal, invariantes,
paridad, exposición, endpoint, necesidad, opacidad, localización, pasividad— y
**sólo `L17-8` es por vida**, porque su nula es la de esa vida B y de ninguna otra.

```
L17-8: 16 entradas · nulas [32] · cada una de su propia semilla   True
todas las entradas PASS                                           True
```

## 3 · Hashes y árbol

```
árbol                                 0 cambios
oráculo ac12cc3 vs HEAD               IDÉNTICO
LEVEL17_ORACULO_PREREGISTRADO.md      022921cc6bfeadb8
LEVEL17_PROTOCOLO_V2.md               b4febc87c1007a6b
campaign.py                           b247e76171f099c3
gates.py                              bf1b11de769d2f9f
```

## 4 · Ingeniería entre abrir `170000011` y cerrar la campaña: **ninguna**

La campaña corrió en `HEAD = 1ca4b38`. El único commit posterior es `4b6b325`, y
toca exclusivamente:

```
resultados/v2_confirmatorio_16_pares.json
resultados/v2_ledger_gates.json
```

Datos. Ni una línea de código, gate, fixture, umbral ni documento de protocolo.

## 5 · `170000024` y `170000026` · exposición incompleta **válida**

```
170000024   C_OA 0.938   N mín 0   →  Γ +0.2959   D_K^act +0.2899
170000026   C_OA 0.976   N mín 0   →  Γ +0.2535   D_K^act +0.2276
```

Ambas tienen al menos un contexto informativo que S0 no visitó ni una vez, y ambas
quedan dentro del rango de las otras catorce. **Ninguna fue excluida ni tratada
aparte**, y `L17-6` no falló por ellas — que es exactamente para lo que se
construyó así: cobertura baja es un resultado, no un defecto de instrumento.

La lectura precisa **no** es «la exposición estaba completa». Es:

> La adquisición sobrevivió con huecos locales de exposición.

## 6 · Sobre la coincidencia V1/V2

`V1 = +0.2794` (inválida) y `V2 = +0.2806`. **V1 sigue inválida y no se suma** al
tamaño de muestra ni al argumento confirmatorio. Lo único legítimo que se afirma:

> la reparación prospectiva no produjo una señal cualitativamente distinta.
