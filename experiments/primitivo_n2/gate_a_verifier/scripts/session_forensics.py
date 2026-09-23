#!/usr/bin/env python3
"""Read-only forensic extraction from sealed session_custody/raw copies."""
from __future__ import annotations
import hashlib, json, re, sqlite3
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'gate_a_verifier'; CUST=OUT/'session_custody'; RAW=CUST/'raw'
SHA_RE=re.compile(r'POR_SISTEMA_SHA256\s*:\s*([0-9a-f]{64})',re.I)
HASH='04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e'

def dump(v,n): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
def flatten(v):
    if isinstance(v,str): return v
    if isinstance(v,list): return '\n'.join(flatten(x) for x in v)
    if isinstance(v,dict): return '\n'.join(flatten(x) for x in v.values())
    return ''
def sealed_ok():
    for line in (CUST/'SESSION_RAW_CUSTODY.sha256').read_text().splitlines():
        expected,path=line.split('  ',1); actual=hashlib.sha256((CUST/path).read_bytes()).hexdigest()
        if expected!=actual: raise RuntimeError(f'custody mismatch: {path}')
def events(path): return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines()]
def meta(es): return es[0]['payload']
def tool_access(text):
    t=text.lower()
    if any(x in t for x in ('reference_nonblind','control/','spec_primitivo_n2_b')): return 'PARENT_OR_EXTERNAL_READ'
    if 'attachments/' in t: return 'UNKNOWN' # user-provided prompt transport; not project material
    if '../' in t or 'cd ..' in t or 'ls ..' in t or 'find ..' in t: return 'PARENT_OR_EXTERNAL_READ'
    if 'replicas_ciegas/a1' in t or 'replicas_ciegas/a2' in t: return 'WORKSPACE_INTERNAL'
    return 'UNKNOWN'
def candidate(path):
    es=events(path); m=meta(es); whole='\n'.join(flatten(e['payload']) for e in es)
    tool=[]; messages=[]; created=[]; hashes=[]; external=[]
    for e in es:
        p=e['payload']; txt=flatten(p)
        if isinstance(p,dict) and p.get('type')=='message': messages.append({'ordinal':e['ordinal'],'timestamp':e['timestamp'],'role':p.get('role'),'text':txt})
        if isinstance(p,dict) and p.get('type') in ('custom_tool_call','function_call'):
            access=tool_access(txt); tool.append({'ordinal':e['ordinal'],'timestamp':e['timestamp'],'name':p.get('name'),'access':access,'workdir_match':re.findall(r'"workdir"\s*:\s*"([^"]+)',txt),'command':txt[:500]})
            if access=='PARENT_OR_EXTERNAL_READ': external.append({'ordinal':e['ordinal'],'timestamp':e['timestamp'],'kind':'tool_access','detail':txt[:500]})
        for h in SHA_RE.findall(txt): hashes.append({'ordinal':e['ordinal'],'timestamp':e['timestamp'],'hash':h})
        for x in re.findall(r'(?:Add File:|Update File:)\s*([^\n]+)',txt):
            if 'replicas_ciegas/' in x: created.append(x.strip())
    def has(x): return x.lower() in whole.lower()
    a1=has('REPLICA_ID=A1'); a2=has('REPLICA_ID=A2')
    complete_a1=bool(re.search(r'REPLICA_ID:\s*A1[\s\S]{0,500}?STATUS:\s*COMPLETE',whole,re.I))
    complete_a2=bool(re.search(r'REPLICA_ID:\s*A2[\s\S]{0,500}?STATUS:\s*COMPLETE',whole,re.I))
    role='NOT_REPLICA'
    if a1 and complete_a1 and any('/A1/' in x or '/A1' in x for x in created): role='ATTRIBUTED'
    if a2 and complete_a2 and (m.get('agent_path')=='/root/a2_blind_replica' or any('/A2/' in x or '/A2' in x for x in created)): role='ATTRIBUTED'
    return {'rollout':path.name,'session_id':m.get('session_id') or m.get('id'),'started_at':m.get('timestamp'),'initial_cwd':m.get('cwd'),'model_provider':m.get('model_provider'),'model':m.get('model_provider'),'agent_path':m.get('agent_path'),'parent_thread_id':m.get('parent_thread_id'),'contains_A1_path':has('/replicas_ciegas/A1'),'contains_A2_path':has('/replicas_ciegas/A2'),'contains_REPLICA_ID_A1':a1,'contains_REPLICA_ID_A2':a2,'contains_master_task_A1':has('RÉPLICA CIEGA A1') or has('REPLICA CIEGA A1'),'contains_master_task_A2':has('RÉPLICA CIEGA A2') or has('REPLICA CIEGA A2'),'contains_COMPLETE_A1':complete_a1,'contains_COMPLETE_A2':complete_a2,'declared_por_sistema_sha256':hashes[0]['hash'] if hashes else None,'hash_events':hashes,'created_files':created,'candidate_role':role,'tool_access_counts':dict(Counter(x['access'] for x in tool)),'external_access_events':external,'tool_calls':tool,'messages':messages}
def selected(matrix,label):
    hits=[m for m in matrix if m['candidate_role']=='ATTRIBUTED' and m[f'contains_REPLICA_ID_{label}']]
    if label=='A2':
        child=[m for m in hits if m.get('agent_path')=='/root/a2_blind_replica']
        if len(child)==1: return child[0]
    if label=='A1':
        own=[m for m in hits if m.get('contains_COMPLETE_A1') and any('/A1/' in x or '/A1' in x for x in m.get('created_files',[]))]
        if len(own)==1: return own[0]
    return hits[0] if len(hits)==1 else None
def ref_before(record, own):
    if not record or not record['hash_events']: return 'LOG_INSUFFICIENT','LOG_INSUFFICIENT',None
    h_event=record['hash_events'][0]['ordinal']; pre=[]
    for m in record['messages']:
        if m['ordinal']<h_event and any(x in m['text'].lower() for x in ('reference_nonblind','resultado de referencia','hash de referencia','por_sistema externo')): pre.append(m)
    forbidden=('reference_nonblind','control/','spec_primitivo_n2_b', '/a2' if own=='A1' else '/a1')
    ext=[event for event in record['external_access_events'] if event['ordinal']<h_event and any(pattern in event['detail'].lower() for pattern in forbidden)]
    if pre or ext: return 'CONTAMINATED_BY_LOG','LOG_CONTRADICTS_G5',{'messages':pre,'tools':ext}
    # Only events before the first declaration can inform the historical G0/G5
    # question; later external audit activity is not contamination of the replica.
    g0='CLEAN_BY_LOG' if not ext else 'INCOMPLETE_LOG'
    return g0,'LOG_SUPPORTS_G5',None
def formal_classification():
    diffs=json.loads((OUT/'SEMANTIC_SUMMARY_DIFF.json').read_text()); out=[]
    for d in diffs:
        if d['classification']!='FORMAT_ONLY': continue
        cat='F3' if d['field'].startswith(('ciclo_muere_sin_reloj_por_cruzada.','con_ciclo_sincronico_por_cruzada.')) and d['reference']=='__MISSING__' else 'F2'
        out.append({'field':d['field'],'classification':cat,'basis':'zero count omitted' if cat=='F3' else 'same real value under §14 precision'})
    dump(out,'FORMAL_DIVERGENCE_CLASSIFICATION.json'); return out
def main():
    sealed_ok()
    matrix=[candidate(p) for p in sorted(RAW.glob('rollout-*.jsonl'))]; dump(matrix,'SESSION_CANDIDATE_MATRIX.json')
    a1,a2=selected(matrix,'A1'),selected(matrix,'A2')
    g0a1,g5a1,e1=ref_before(a1,'A1'); g0a2,g5a2,e2=ref_before(a2,'A2')
    forensic={'custody_verified':True,'A1':{'record':a1['rollout'] if a1 else None,'attribution':'ATTRIBUTED' if a1 else 'AMBIGUOUS','initial_cwd':a1['initial_cwd'] if a1 else None,'G0_LOG_RESULT':g0a1,'G5_LOG_RESULT':g5a1,'first_hash_event':a1['hash_events'][0] if a1 and a1['hash_events'] else None,'pre_hash_reference_evidence':e1},'A2':{'record':a2['rollout'] if a2 else None,'attribution':'ATTRIBUTED' if a2 else 'AMBIGUOUS','initial_cwd':a2['initial_cwd'] if a2 else None,'G0_LOG_RESULT':g0a2,'G5_LOG_RESULT':g5a2,'first_hash_event':a2['hash_events'][0] if a2 and a2['hash_events'] else None,'pre_hash_reference_evidence':e2},'replica_family_relation':'SAME_FAMILY_SEPARATE_SESSIONS'}
    dump(forensic,'SESSION_FORENSIC_AUDIT.json')
    fs=formal_classification()
    template=f'''# Researcher provenance attestation template\n\nThis is a template, not an attestation.\n\n## A1\n\n[ ] Confirm that `{forensic["A1"]["record"]}` is the session I initiated for A1.\n\nLog evidence: initial cwd `{forensic["A1"]["initial_cwd"]}`; first declared POR_SISTEMA hash event `{forensic["A1"]["first_hash_event"]}`; G0 log result `{g0a1}`; G5 log result `{g5a1}`.\n\n## A2\n\n[ ] Confirm that `{forensic["A2"]["record"]}` is the session I initiated for A2.\n\nLog evidence: initial cwd `{forensic["A2"]["initial_cwd"]}`; first declared POR_SISTEMA hash event `{forensic["A2"]["first_hash_event"]}`; G0 log result `{g0a2}`; G5 log result `{g5a2}`.\n\nThe logs are documentary evidence, not external cryptographic timestamps. The researcher must separately attest what material was made available and when reference results were revealed.\n'''
    (OUT/'ATTESTATION_TEMPLATE.md').write_text(template,encoding='utf8')
    print(json.dumps({'A1':forensic['A1'],'A2':forensic['A2'],'formal_differences':len(fs)},indent=2))
if __name__=='__main__': main()
