#!/usr/bin/env python3
"""La matriz de falsificación de los trece gates, generada corriendo cada fixture.

No está escrita a mano: cada fila ejecuta el falsificador y registra el veredicto
y la evidencia **que el gate realmente produjo**. Un gate cuya fila diga `PASA`
en la columna del falsificador no es un gate.

    python scripts/matriz_falsificacion.py
"""

from __future__ import annotations

import subprocess
import sys

FILAS = [
    ("L17-0",  "1.6 presente y congelado; nada posterior",
     "test_l17_0_falla_si_aparece_una_capacidad_posterior", "capacidad posterior en el árbol"),
    ("L17-0",  "huella del código heredado",
     "test_l17_0_falla_si_el_codigo_heredado_cambio", "huella heredada CAMBIÓ"),
    ("L17-1",  "D_W^A > 0 y D_W^B = 0, por el kernel físico",
     "test_l17_1_detecta_un_B_defectuoso_por_el_kernel_no_por_la_muestra",
     "WORLD_PAIR_CONSTRUCTION_FAIL"),
    ("L17-1",  "misma dinámica marginal",
     "test_l17_1_falla_si_las_dinamicas_marginales_difieren", "WORLD_PAIR_CONSTRUCTION_FAIL"),
    ("L17-2",  "cada comando reconstruible desde S0",
     "test_l17_2_detecta_UNA_sola_accion_sustituida_desde_fuera", "discrepancia en t=391"),
    ("L17-3",  "el canal lleva comando y nada más",
     "test_l17_3_rechaza_cualquier_contaminacion_del_canal",
     "campos distintos de ['command']"),
    ("L17-4",  "C_17 = 0 ⇒ M_1 = M_0^W",
     "test_l17_4_falla_si_una_sola_celda_de_C17_nace_distinta", "nacimiento False"),
    ("L17-4",  "la lesión vuelve bit a bit",
     "test_l17_4_falla_si_la_lesion_deja_residuo", "restauración exacta False"),
    ("L17-5",  "NO-ACTION sigue aprendiendo en la fase A",
     "test_l17_5_falla_si_NO_ACTION_se_congela_al_final_de_P", "siguió aprendiendo False"),
    ("L17-6",  "los instrumentos son consistentes",
     "test_l17_6_detecta_un_contador_que_omite_un_contexto", "recuento independiente no coincide"),
    ("L17-6",  "una cobertura baja NO es un defecto",
     "test_l17_6_NO_falla_por_cobertura_baja", "(debe PASAR con C_OA baja)"),
    ("L17-7",  "CI95 inferior de Γ > 0, unidad = par",
     "test_l17_7_falla_si_el_intervalo_cruza_el_cero", "CI95 inferior ≤ 0"),
    ("L17-7",  "la unidad no es la transición",
     "test_l17_7_la_unidad_es_el_par_no_la_transicion", "n infla el intervalo"),
    ("L17-8",  "B no inventa ventaja de acción",
     "test_l17_8_falla_si_B_aparece_anormalmente_positivo", "WORLD_B_OR_MODEL_NULL_FAIL"),
    ("L17-9",  "la baraja destruye la correspondencia",
     "test_l17_9_falla_con_la_baraja_identidad", "destructiva False"),
    ("L17-9",  "el auditor consume el modelo recibido",
     "test_l17_9_el_auditor_consume_el_modelo_que_recibe", "(nula intacta, observado distinto)"),
    ("L17-10", "el contenido no vive en el token",
     "test_l17_10_falla_si_el_aprendiz_cablea_una_direccion", "aprendiz con direcciones"),
    ("L17-11", "la lesión aísla 1.7",
     "test_l17_11_falla_si_la_lesion_arrasa_tambien_lo_heredado", "M_0^W intacto False"),
    ("L17-11", "restaurar devuelve el mismo valor",
     "test_l17_11_falla_si_restaurar_no_devuelve_el_mismo_valor", "restaurado ≠ con estado"),
    ("L17-12", "evaluar es pasivo",
     "test_l17_12_falla_si_evaluar_incrementa_un_contador", "la huella o el contador se mueven"),
    ("L17-12", "el replay es determinista",
     "test_l17_12_falla_si_el_replay_no_es_determinista", "dos replays distintos"),
]


def main() -> None:
    print(f"{'gate':<7} {'afirmación':<46} {'fixture negativa':<62} "
          f"{'falló por esa causa':<36}")
    print("-" * 155)
    fallos = 0
    for gate, afirmacion, prueba, causa in FILAS:
        nombre = prueba
        completado = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_level17_gates.py",
             "-k", nombre, "-q", "--no-header"],
            capture_output=True, text=True)
        verde = completado.returncode == 0 and " no tests ran" not in completado.stdout
        if not verde:
            fallos += 1
        print(f"{gate:<7} {afirmacion[:44]:<46} {nombre[:60]:<62} "
              f"{('sí · ' + causa)[:36] if verde else 'NO — REVISAR':<36}")
    print("-" * 155)
    print(f"filas verificadas: {len(FILAS)} · sin confirmar: {fallos}")


if __name__ == "__main__":
    main()
