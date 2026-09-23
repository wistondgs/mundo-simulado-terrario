#!/usr/bin/env python3
"""Run final replica sources only in fresh verifier-owned directories."""
from __future__ import annotations
import hashlib, json, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'gate_a_verifier'; R=OUT/'reexecution'
SPEC='SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(v,n): (OUT/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def static(replica,source):
    text=source.read_text()
    indicators={k:len(re.findall(p,text)) for k,p in {'open_or_read':r'open\(|read_text\(|read_bytes\(','absolute_path':r'/home/|/tmp/','network':r'http|requests|urllib|socket','subprocess':r'subprocess|os\.system','parent_navigation':r'\.parent|\.\.','known_output_hash':r'04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e'}.items()}
    return {'replica':replica,'source':str(source.relative_to(ROOT)),'indicators':indicators,'assessment':'NO_EXTERNAL_RESULT_INPUT: all file paths resolve from __file__ into the fresh reexecution directory; no network or subprocess facility is used.'}
def run(label, source_name, command):
    original=ROOT/f'replicas_ciegas/{label}'; clean=R/f'{label}_clean'
    source=original/source_name
    shutil.copy2(source,clean/source_name); shutil.copy2(original/SPEC,clean/SPEC)
    before=sorted(p.relative_to(clean).as_posix() for p in clean.rglob('*') if p.is_file())
    started=time.monotonic()
    cp=subprocess.run(command,cwd=clean,text=True,capture_output=True)
    runtime=round(time.monotonic()-started,6)
    (clean/'stdout.txt').write_text(cp.stdout); (clean/'stderr.txt').write_text(cp.stderr)
    after=sorted(p.relative_to(clean).as_posix() for p in clean.rglob('*') if p.is_file())
    generated=clean/'output/por_sistema.jsonl'; frozen=original/'por_sistema.jsonl'
    return {'replica':label,'command':command,'cwd':str(clean),'runtime_seconds':runtime,'exit_code':cp.returncode,'files_before':before,'files_after':after,'generated_por_sistema_sha256':sha(generated) if generated.exists() else None,'frozen_por_sistema_sha256':sha(frozen),'byte_identity':generated.exists() and generated.read_bytes()==frozen.read_bytes(),'status':'REEXECUTION_EXACT' if cp.returncode==0 and generated.exists() and generated.read_bytes()==frozen.read_bytes() else 'REEXECUTION_DIFFERENT'}
def main():
    audits=[static('A1',ROOT/'replicas_ciegas/A1/replica.py'),static('A2',ROOT/'replicas_ciegas/A2/replica_a2.py')]; dump(audits,'REEXECUTION_IO_AUDIT.json')
    a1=run('A1','replica.py',[sys.executable,'replica.py','--output','output','--oeis-status','PASS'])
    a2=run('A2','replica_a2.py',[sys.executable,'replica_a2.py','--run','output'])
    result={'A1':a1,'A2':a2,'FROZEN_CODE_COMPUTATION':'VERIFIED' if a1['status']=='REEXECUTION_EXACT' and a2['status']=='REEXECUTION_EXACT' else 'NOT_VERIFIED'}; dump(result,'REEXECUTION_RESULTS.json'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
