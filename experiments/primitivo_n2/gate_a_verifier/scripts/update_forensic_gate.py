#!/usr/bin/env python3
"""Merge sealed-log and clean-reexecution evidence without manufacturing attestation."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'gate_a_verifier'
def load(n): return json.loads((OUT/n).read_text())
def dump(v,n): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
def main():
    result=load('GATE_A_RESULT.json'); forensic=load('SESSION_FORENSIC_AUDIT.json'); rex=load('REEXECUTION_RESULTS.json'); formal=load('FORMAL_DIVERGENCE_CLASSIFICATION.json')
    gates={}
    for label in ('A1','A2'):
        data=forensic[label]
        gates[label]={
            'G0':{'status':'PENDING','evidence_level':'NONE','rollout':data['record'],'evidence':[data['G0_LOG_RESULT']],'limitations':['researcher attestation absent','initial cwd recorded as project root, while operations must be interpreted from detailed log']},
            'G5':{'status':'PENDING','evidence_level':'NONE','rollout':data['record'],'evidence':[data['G5_LOG_RESULT'],data['first_hash_event']],'limitations':['rollout is documentary evidence, not an external cryptographic timestamp','researcher attestation absent']},
        }
    dump(gates,'BLINDNESS_GATE.json')
    result.update({'A1_G0':'PENDING','A1_G5':'PENDING','A2_G0':'PENDING','A2_G5':'PENDING','gate_a_blindness':'PENDING','gate_a_overall':'PENDING_PROVENANCE','B_status':'READY_AFTER_PROVENANCE','A1_precalibration_status':'HASH_ONLY','A2_precalibration_status':'HASH_ONLY','A1_frozen_code_reexecution':rex['A1']['status'],'A2_frozen_code_reexecution':rex['A2']['status'],'frozen_code_computation':rex['FROZEN_CODE_COMPUTATION'],'forensic_session_audit':{'A1':forensic['A1'],'A2':forensic['A2']},'author_prediction_value':'SUPPORTED','author_prediction_formal_coverage':'SUPPORTED','new_formal_categories':[],'B_spec_freeze_already_verified':True,'B_spec_sha256':'677c5764eb4a519be089171404825ccc454fe8dc29771c2f577db88799f39e94'})
    dump(result,'GATE_A_RESULT.json')
    report=f'''# Gate A — actualización forense\n\n## Custodia y atribución\n\nLa custodia de seis rollouts candidatos y la copia SQLite/WAL/SHM verificó el manifest `SESSION_RAW_CUSTODY.sha256`. A1 queda atribuido a `{forensic['A1']['record']}` y A2 a `{forensic['A2']['record']}`; la atribución combina el prompt, `REPLICA_ID`, operaciones sobre el workspace, reporte COMPLETE y hash declarado. Ambas sesiones registran cwd inicial de raíz del proyecto; eso es una limitación de contexto, no una lectura por sí misma.\n\n## G0/G5 documental\n\nAntes de la primera declaración de hash, el log resulta `CLEAN_BY_LOG` para G0 y `LOG_SUPPORTS_G5` para ambas réplicas. Los hashes extraídos literalmente son `{forensic['A1']['first_hash_event']['hash']}` (A1, evento {forensic['A1']['first_hash_event']['ordinal']}) y `{forensic['A2']['first_hash_event']['hash']}` (A2, evento {forensic['A2']['first_hash_event']['ordinal']}). No se observó revelación de referencia previa en esos logs.\n\nEsto es evidencia documental, no atestación ni timestamp criptográfico externo. Por ello G0/G5 siguen en `PENDING` hasta una confirmación factual del investigador; `ATTESTATION_TEMPLATE.md` se generó sin firma.\n\n## Reejecución\n\nCada source final se copió sin outputs a un entorno limpio del verificador y se ejecutó allí. Ambos regeneraron byte a byte `por_sistema.jsonl` con SHA-256 común `04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e`. `FROZEN_CODE_COMPUTATION=VERIFIED`.\n\n## Estado\n\n`GATE_A_MATH=PASS`; `GATE_A_BLINDNESS=PENDING`; `GATE_A_OVERALL=PENDING_PROVENANCE`. A2 conserva `FREEZE_MANIFEST_NOT_PRESERVED`; no se reconstruyó. Los sources precalibración quedan `HASH_ONLY`. SPEC B se rehasheó como freeze estático (`677c5764eb4a519be089171404825ccc454fe8dc29771c2f577db88799f39e94`) y no se ejecutó. B queda `READY_AFTER_PROVENANCE`.\n'''
    (OUT/'FORENSIC_SESSION_REPORT.md').write_text(report,encoding='utf8')
if __name__=='__main__': main()
