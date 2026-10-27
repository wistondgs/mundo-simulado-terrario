#!/bin/bash
# MUTANTE DEL MECANISMO DE REANUDACIÓN. Simula un corte de luz: SIGKILL a mitad.
# Comprueba tres cosas: no se pierde ninguna fila escrita, no se repite ninguna, y el
# total final coincide con el de una corrida sin corte. Esto convierte «es reanudable»
# de afirmación en medida.
set -u
cd /home/wis/Aplicaciones/worktrees/unidad-minima-01/experiments/unidad_minima_01
P=artifacts/pruebas
export N8_TOPE=12

echo "--- A · corrida limpia de referencia, sin corte"
rm -f $P/ref.jsonl
N8_JSONL=$P/ref.jsonl timeout 900 python3 -u unidad_minima_07_n8_limpio.py correr > $P/ref.log 2>&1
REF=$(wc -l < $P/ref.jsonl)
echo "    filas de referencia: $REF"

echo "--- B · corrida con SIGKILL a mitad"
rm -f $P/corte.jsonl
N8_JSONL=$P/corte.jsonl python3 -u unidad_minima_07_n8_limpio.py correr > $P/corte.log 2>&1 &
PID=$!
# esperar a que haya escrito algo y matar en seco, como un apagón
for i in $(seq 1 600); do
  [ -f $P/corte.jsonl ] && [ "$(wc -l < $P/corte.jsonl)" -ge 4 ] && break
  sleep 1
done
ANTES=$(wc -l < $P/corte.jsonl 2>/dev/null || echo 0)
kill -9 $PID 2>/dev/null
pkill -9 -P $PID 2>/dev/null
sleep 2
TRAS_CORTE=$(wc -l < $P/corte.jsonl 2>/dev/null || echo 0)
echo "    filas escritas antes del corte: $ANTES · sobrevivieron al SIGKILL: $TRAS_CORTE"

echo "--- C · reanudar"
N8_JSONL=$P/corte.jsonl timeout 900 python3 -u unidad_minima_07_n8_limpio.py correr >> $P/corte.log 2>&1
FIN=$(wc -l < $P/corte.jsonl)
echo "    filas tras reanudar: $FIN"

echo "--- D · veredicto"
python3 - "$P/ref.jsonl" "$P/corte.jsonl" "$TRAS_CORTE" <<'PY'
import json, sys
ref = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
cor = []
malas = 0
for l in open(sys.argv[2], encoding="utf-8"):
    if not l.strip(): continue
    try: cor.append(json.loads(l))
    except ValueError: malas += 1
sobrevivieron = int(sys.argv[3])
rref = {r["rango"] for r in ref}
rcor = [r["rango"] for r in cor]
g = {}
g["ninguna fila escrita se perdio"] = len(cor) >= sobrevivieron - malas
g["ninguna fila se repitio"] = len(rcor) == len(set(rcor))
g["el total coincide con la corrida sin corte"] = set(rcor) == rref
g["las filas son identicas campo a campo (salvo reloj)"] = all(
    {k: v for k, v in a.items() if k != "reloj_s"} == {k: v for k, v in b.items() if k != "reloj_s"}
    for a, b in zip(sorted(ref, key=lambda r: r["rango"]), sorted(cor, key=lambda r: r["rango"])))
print(f"    lineas truncadas por el corte: {malas} (se recalculan, por eso no es perdida)")
for k, v in g.items(): print(f"    [{'OK' if v else 'ROTO'}] {k}")
print(f"LA REANUDACION {'FUNCIONA' if all(g.values()) else 'ESTA ROTA'}")
sys.exit(0 if all(g.values()) else 1)
PY
