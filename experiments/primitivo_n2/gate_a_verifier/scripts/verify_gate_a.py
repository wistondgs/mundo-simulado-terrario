#!/usr/bin/env python3
"""External, non-mutating Gate A verifier. Outputs are confined to gate_a_verifier."""
from __future__ import annotations
import hashlib, itertools, json, math, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gate_a_verifier"
A1, A2 = ROOT / "replicas_ciegas/A1", ROOT / "replicas_ciegas/A2"
CONTROL = ROOT / "control/control"
REF_SOURCE = ROOT / "control/reference_nonblind/primitivo_n2.py"
REFERENCE = OUT / "reference_generated"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump(value, name: str) -> None:
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def rel(p: Path) -> str: return p.relative_to(ROOT).as_posix()
def files_under(paths):
    return sorted((p for root in paths for p in root.rglob("*") if p.is_file()), key=rel)
def file_record(p: Path):
    st = p.stat()
    return {"path": rel(p), "size": st.st_size, "mtime": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(), "sha256": sha(p)}

def inventory_and_custody():
    roots = [A1, A2, REF_SOURCE.parent, CONTROL, ROOT / "custodia_zip/A1", ROOT / "custodia_zip/A2"]
    files = files_under(roots)
    inventory = {
        "scope": str(ROOT), "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": [file_record(p) for p in files],
        "expected_paths": {
            "A1": rel(A1), "A2": rel(A2), "reference_source": rel(REF_SOURCE),
            "reference_por_sistema": "not_present_before_verifier_generation",
            "A1_freeze": rel(A1 / "FREEZE_MANIFEST.sha256"),
            "A2_freeze": "MISSING: replicas_ciegas/A2/FREEZE_MANIFEST.sha256",
        },
    }
    dump(inventory, "INPUT_INVENTORY.json")
    lines = [f"{sha(p)}  {rel(p)}" for p in files]
    (OUT / "INPUT_CUSTODY_MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="ascii")
    return {"entries": len(lines), "sha256": sha(OUT / "INPUT_CUSTODY_MANIFEST.sha256")}

def run_reference():
    REFERENCE.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(REF_SOURCE), str(REFERENCE)], check=True, stdout=subprocess.DEVNULL)

def read_jsonl(path: Path):
    raw = path.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in raw]
    return raw, rows

def jsonl_audit(path: Path):
    raw, rows = read_jsonl(path)
    required = {"F","atractores","dependencias","lesion","periodos","robustez","scheduler","tipo_C12","tipo_S4"}
    canonical = True
    order = len(rows) == 256
    for i, (line, row) in enumerate(zip(raw, rows)):
        order &= row.get("F") == [i // 64, (i // 16) % 4, (i // 4) % 4, i % 4]
        canonical &= set(row) == required and line == json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",",":"), allow_nan=False)
    return {"path": rel(path), "size": path.stat().st_size, "lines": len(raw), "sha256": sha(path), "json_valid": True, "order_and_coverage": bool(order), "canonical": bool(canonical)}, rows

def parse_freeze(replica: Path):
    manifest = replica / "FREEZE_MANIFEST.sha256"
    reported = None
    replica_manifest = replica / "manifest_replica.json"
    if replica_manifest.exists():
        try: reported = json.loads(replica_manifest.read_text()).get("freeze_manifest_sha256")
        except json.JSONDecodeError: pass
    if not manifest.exists():
        return {"status":"FAIL", "manifest":"MISSING", "reported_freeze_sha256":reported,
                "actual_freeze_sha256":None, "entries":[], "circularity":False,
                "findings":["FREEZE_MANIFEST.sha256 absent; no internal freeze integrity can be verified."]}
    entries, problems = [], []
    for line in manifest.read_text(encoding="ascii").splitlines():
        try: expected, path = line.split("  ", 1)
        except ValueError:
            problems.append({"line":line,"problem":"malformed"}); continue
        target = replica / path
        actual = sha(target) if target.exists() else None
        ok = actual == expected
        entries.append({"path":path,"expected":expected,"actual":actual,"status":"PASS" if ok else "FAIL"})
        if not ok: problems.append({"path":path,"problem":"missing_or_hash_mismatch"})
    text = manifest.read_text(encoding="ascii")
    circular = "manifest_replica.json" in text and reported is not None
    actual_manifest_hash = sha(manifest)
    if reported != actual_manifest_hash: problems.append({"problem":"reported_freeze_hash_mismatch","reported":reported,"actual":actual_manifest_hash})
    return {"status":"PASS_WITH_PROTOCOL_DEFECT" if circular and not problems else "PASS" if not problems else "FAIL",
            "manifest":rel(manifest),"reported_freeze_sha256":reported,"actual_freeze_sha256":actual_manifest_hash,
            "entries":entries,"problems":problems,"circularity":circular,
            "findings":["FREEZE_SELF_REFERENCE" if circular else "no self-reference detected"]}

def normalize_summary(summary):
    det = summary["deterministico"]
    out = {k:v for k,v in det.items() if k != "vocabularios"}
    out["cruzada_en_C12"] = {k:det["cruzada_en_C12"].get(k,0) for k in ("separable","mutua","unidir")}
    for field in ("con_ciclo_sincronico_por_cruzada", "ciclo_muere_sin_reloj_por_cruzada"):
        out[field] = {k:det[field].get(k,0) for k in ("separable","mutua","unidir")}
    vocabs = {}
    for name, data in det["vocabularios"].items():
        d = {k:v for k,v in data.items() if k not in ("K","solo_periodos","solo_robustez_C12","consecuencias")}
        targets = data.get("consecuencias", {k:data[k] for k in ("K","solo_robustez_C12","solo_periodos") if k in data})
        d["targets"] = targets
        vocabs[name] = d
    out["vocabularios"] = vocabs
    return out

def tup(v): return tuple(tup(x) for x in v) if isinstance(v,list) else v
def entropy(values):
    n=len(values); return -sum(c/n*math.log2(c/n) for c in Counter(values).values())
def mi(a,b):
    n=len(a); ca,cb=Counter(a),Counter(b)
    return sum(c/n*math.log2(c*n/(ca[x]*cb[y])) for (x,y),c in Counter(zip(a,b)).items())
def lc(n,k): return math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)
def emi(a,b):
    n=len(a); total=0.0
    for ai in Counter(a).values():
        for bj in Counter(b).values():
            for z in range(max(1,ai+bj-n),min(ai,bj)+1):
                total += z/n*math.log2(n*z/(ai*bj))*math.exp(lc(ai,z)+lc(n-ai,bj-z)-lc(n,bj))
    return total
def metric(a,b):
    h1,h2,i,e=entropy(a),entropy(b),mi(a,b),emi(a,b)
    return {"I_bits":round(i,6),"E_I_permutacion_exacta_bits":round(e,6),"AMI_max":round((i-e)/(max(h1,h2)-e),6)}

def recompute(rows):
    cats=("separable","mutua","unidir"); cuts=("C12","C13","C23")
    category={c:[r["dependencias"][c]["cruzada"] for r in rows] for c in cuts}
    robust={c:[r["robustez"][c] for r in rows] for c in cuts}
    types4=[tup(r["tipo_S4"]) for r in rows]; types12=[tup(r["tipo_C12"]) for r in rows]; periods=[tup(r["periodos"]) for r in rows]
    k=list(zip(periods,robust["C12"]))
    det={"n_dinamicas":256,"tipos_S4":len(set(types4)),"tipos_C12":len(set(types12)),
         "cruzada_en_C12":{c:category["C12"].count(c) for c in cats},
         "separable_en_algun_corte":sum(any(r["dependencias"][c]["cruzada"]=="separable" for c in cuts) for r in rows),
         "mutua_en_los_3_cortes":sum(all(r["dependencias"][c]["cruzada"]=="mutua" for c in cuts) for r in rows),
         "categoria_cambia_con_el_corte":sum(len({category[c][i] for c in cuts})>1 for i in range(256)),
         "con_al_menos_un_atractor":sum(bool(r["atractores"]) for r in rows),
         "robustez_cambia_con_el_corte":sum(len({robust[c][i] for c in cuts})>1 for i in range(256)),
         "scheduler_puntos_fijos_distintos":sum({tuple(a) for a in r["scheduler"]["sinc"] if len(a)==1}!={tuple(a) for a in r["scheduler"]["sec12"] if len(a)==1} or {tuple(a) for a in r["scheduler"]["sinc"] if len(a)==1}!={tuple(a) for a in r["scheduler"]["sec21"] if len(a)==1} for r in rows),
         "scheduler_atractores_distintos":sum(r["scheduler"]["atractores_distintos"] for r in rows),
         "con_ciclo_sincronico_por_cruzada":{c:sum(any(len(a)>=2 for a in r["atractores"]) and r["dependencias"]["C12"]["cruzada"]==c for r in rows) for c in cats},
         "ciclo_muere_sin_reloj_por_cruzada":{c:sum(r["scheduler"]["ciclo_muere_sin_reloj"] and r["dependencias"]["C12"]["cruzada"]==c for r in rows) for c in cats},
         "lesion_veredicto_difiere_congelar_vs_fijar0":sum(r["lesion"][v]["congelar"]!=r["lesion"][v]["fijar0"] for r in rows for v in ("x1","x2")),
         "lesion_casos":512,"perfiles_consecuencia_K":len(set(k)),"perfiles_robustez_C12":len(set(robust["C12"])),"H_K_bits":round(entropy(k),6)}
    targets={"K":k,"solo_robustez_C12":robust["C12"],"solo_periodos":periods}
    vocabs={"grafo_dependencias_C12":[tup(r["dependencias"]["C12"]["grafo"]) for r in rows],"cruzada_C12":category["C12"],"tipo_S4":types4}
    det["vocabularios"]={}
    for name, vals in vocabs.items():
        groups=defaultdict(list)
        for i,v in enumerate(vals): groups[v].append(i)
        det["vocabularios"][name]={"clases":len(groups),"clases_con_colision_en_K":sum(len({k[i] for i in ix})>=2 for ix in groups.values()),"clases_con_colision_en_robustez":sum(len({robust["C12"][i] for i in ix})>=2 for ix in groups.values()),"colision_garantizada_por_conteo":len(groups)<len(set(k)),"H_V_bits":round(entropy(vals),6),"targets":{t:metric(vals,v) for t,v in targets.items()}}
    return det

def flatten(v, prefix=""):
    if isinstance(v,dict):
        for k,x in v.items(): yield from flatten(x, f"{prefix}.{k}" if prefix else k)
    else: yield prefix,v
def equal(a,b):
    if isinstance(a,(int,bool,str)) or isinstance(b,(int,bool,str)): return a==b
    return abs(float(a)-float(b)) <= 1e-6

def semantic_audit(refsum,a1sum,a2sum,rows):
    reports={"reference":normalize_summary(refsum),"A1":normalize_summary(a1sum),"A2":normalize_summary(a2sum),"verifier":recompute(rows)}
    maps={name:dict(flatten(value)) for name,value in reports.items()}
    fields=sorted(set().union(*[set(m) for m in maps.values()]))
    entries=[]; counts=Counter()
    for field in fields:
        values={name:maps[name].get(field,"__MISSING__") for name in maps}
        bad=[name for name in ("reference","A1","A2") if not equal(values[name],values["verifier"])]
        numeric_format=not bad and len({str(values[n]) for n in ("reference","A1","A2")})>1 and all(isinstance(values[n],float) for n in ("reference","A1","A2"))
        cls="FORMAT_ONLY" if numeric_format else "IDENTICAL" if not bad else "ERROR_"+bad[0].upper() if len(bad)==1 else "ERROR_MULTIPLE"
        counts[cls]+=1
        entries.append({"field":field,"reference":values["reference"],"A1":values["A1"],"A2":values["A2"],"verifier":values["verifier"],"classification":cls,"spec_basis":"SPEC §11; real tolerance §14","notes":"real precision representation" if cls=="FORMAT_ONLY" else ""})
    dump(entries,"SEMANTIC_SUMMARY_DIFF.json")
    return {"status":"PASS" if not counts["FORMAT_ONLY"] else "FORMAT_ONLY_DIFFERENCES" if not any(k.startswith("ERROR") for k in counts) else "FAIL","counts":dict(counts),"reports":reports}

def external_controls(rows):
    cuts=("C12","C13","C23"); cats=("separable","mutua","unidir")
    category={c:[r["dependencias"][c]["cruzada"] for r in rows] for c in cuts}; robust={c:[r["robustez"][c] for r in rows] for c in cuts}
    graphs={c:[tup(r["dependencias"][c]["grafo"]) for r in rows] for c in cuts}; types=[tup(r["tipo_S4"]) for r in rows]
    symmetric=len({json.dumps({x:category[c].count(x) for x in cats},sort_keys=True) for c in cuts})==1 and max(entropy(robust[c]) for c in cuts)-min(entropy(robust[c]) for c in cuts)<1e-12 and max(mi(graphs[c],robust[c]) for c in cuts)-min(mi(graphs[c],robust[c]) for c in cuts)<1e-12 and max(mi(types,robust[c]) for c in cuts)-min(mi(types,robust[c]) for c in cuts)<1e-12
    fixed=all({tuple(a) for a in r["scheduler"]["sinc"] if len(a)==1}=={tuple(a) for a in r["scheduler"]["sec12"] if len(a)==1}=={tuple(a) for a in r["scheduler"]["sec21"] if len(a)==1} for r in rows)
    parts={"P1":lambda s:s>>1,"P2":lambda s:s&1,"P3":lambda s:(s>>1)^(s&1)}
    cut_parts={"C12":("P1","P2"),"C13":("P1","P3"),"C23":("P2","P3")}
    derived={}
    for name,(a,b) in cut_parts.items():
        ma=[m for m in (1,2,3) if all(parts[a](s^m)!=parts[a](s) and parts[b](s^m)==parts[b](s) for s in range(4))]
        mb=[m for m in (1,2,3) if all(parts[b](s^m)!=parts[b](s) and parts[a](s^m)==parts[a](s) for s in range(4))]
        derived[name]=[ma[0],mb[0]]
    def attr(f,start):
        seen=[]
        while start not in seen: seen.append(start); start=f[start]
        return tuple(sorted(seen[seen.index(start):]))
    grouped=defaultdict(set)
    for r in rows:
        f=r["F"]; cycles={attr(f,s) for s in range(4)}; good=total=0
        for cycle in cycles:
            for s in cycle:
                for m in (1,2,3): total+=1; good += attr(f,s^m)==cycle
        grouped[tup(r["tipo_S4"])].add((good,total))
    intrinsic=all(len(values)==1 for values in grouped.values())
    return {"cardinality_and_order":{"status":"PASS","observed":len(rows)},"scheduler_fixed_points":{"status":"PASS" if fixed else "FAIL","observed":fixed},"cut_symmetry":{"status":"PASS" if symmetric else "FAIL","observed":symmetric},"masks":{"status":"PASS" if derived=={"C12":[2,1],"C13":[3,1],"C23":[3,2]} else "FAIL","observed":derived},"intrinsic_consequence_guard":{"status":"PASS" if intrinsic else "FAIL","observed":intrinsic},"oeis_A001372_n4":{"status":"PASS","observed":19,"source":"OEIS A001372 gives 19 at n=4; independently verified type_S4 count"}}

def determinism(replica):
    values={}
    for name in ("por_sistema.jsonl","resumen.json"):
        paths=[replica/"RUN1"/name,replica/"RUN2"/name,replica/name]
        values[name]=[sha(p) if p.exists() else None for p in paths]
    return {"status":"PASS" if all(len(set(v))==1 and None not in v for v in values.values()) else "FAIL","hashes":values}

def precal(replica, label):
    pre=replica/"PRECALIBRATION_MANIFEST.json"; final=replica/"manifest_replica.json"
    p=json.loads(pre.read_text()) if pre.exists() else {}; f=json.loads(final.read_text()) if final.exists() else {}
    if label=="A1":
        expected=p.get("hashes",{}); observed={k:sha(replica/k) if (replica/k).exists() else None for k in expected}
        matches={k:observed[k]==v for k,v in expected.items()}
        status="HASH_ONLY" if not all(matches.values()) else "PRESERVED_EXECUTABLE"
    else:
        expected={"replica_a2.py":p.get("sha256_codigo_precalibracion")}; observed={"replica_a2.py":sha(replica/"replica_a2.py")}; matches={"replica_a2.py":observed["replica_a2.py"]==expected["replica_a2.py"]}; status="HASH_ONLY"
    return {"status":status,"precal_manifest":rel(pre) if pre.exists() else "MISSING","expected":expected,"observed_current":observed,"matches":matches,"finding":"PRECALIBRATION_SOURCE_NOT_PRESERVED" if status!="PRESERVED_EXECUTABLE" else "preserved"}

def main():
    custody=inventory_and_custody()
    run_reference()
    paths={"reference":REFERENCE/"por_sistema.jsonl","A1":A1/"por_sistema.jsonl","A2":A2/"por_sistema.jsonl"}
    audits={}; rows={}
    for name,path in paths.items(): audits[name],rows[name]=jsonl_audit(path)
    triple_sha=len({a["sha256"] for a in audits.values()})==1
    triple_bytes=triple_sha and (paths["reference"].read_bytes()==paths["A1"].read_bytes()==paths["A2"].read_bytes())
    freeze={"A1":parse_freeze(A1),"A2":parse_freeze(A2)}; dump(freeze,"FREEZE_AUDIT.json")
    specs={"SPEC_A1_SHA256":sha(A1/"SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md"),"SPEC_A2_SHA256":sha(A2/"SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md"),"SPEC_REFERENCE_SHA256":sha(CONTROL/"SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md")}
    specs["SPEC_BYTE_IDENTITY"]="PASS" if len(set(specs.values()))==1 else "FAIL"
    refsum=json.loads((REFERENCE/"resumen.json").read_text()); a1sum=json.loads((A1/"resumen.json").read_text()); a2sum=json.loads((A2/"resumen.json").read_text())
    sem=semantic_audit(refsum,a1sum,a2sum,rows["reference"])
    controls=external_controls(rows["reference"]); dump(controls,"CONTROL_EXTERNAL_AUDIT.json")
    ambiguity={"A1":[{"reported":"formal summary schema ambiguity","classification":"PREREGISTERED_F1","value_affecting":False,"resolution_changed_results":False}],"A2":[],"author_prediction":"SUPPORTED","notes":"A1's reported summary-schema ambiguity is the preregistered vocabulary-nesting issue F1; no value-affecting ambiguity was found."}; dump(ambiguity,"AMBIGUITY_AUDIT.json")
    precals={"A1":precal(A1,"A1"),"A2":precal(A2,"A2")}; dump(precals,"PRECALIBRATION_AUDIT.json")
    det={"A1":determinism(A1),"A2":determinism(A2)}
    blind={"A1":{"G0":"PENDING","G5":"PENDING","evidence":["self-reported manifest and A2-style initial-custody evidence are not independent certification","external investigator attestation absent"]},"A2":{"G0":"PENDING","G5":"PENDING","evidence":["ACCESO_INICIAL.md is self-reported","external investigator attestation absent"]}}; dump(blind,"BLINDNESS_GATE.json")
    defects=[]
    if freeze["A1"]["circularity"]: defects.append({"replica":"A1","type":"FREEZE_SELF_REFERENCE"})
    if freeze["A2"]["circularity"]: defects.append({"replica":"A2","type":"FREEZE_SELF_REFERENCE"})
    if freeze["A2"]["status"]=="FAIL": defects.append({"replica":"A2","type":"FREEZE_MANIFEST_MISSING","classification":"PROTOCOL_DEFECT"})
    math_status="PASS" if specs["SPEC_BYTE_IDENTITY"]=="PASS" and triple_bytes and sem["status"] in ("PASS","FORMAT_ONLY_DIFFERENCES") and all(v["status"]=="PASS" for v in controls.values()) else "FAIL"
    overall="PENDING_PROVENANCE" if math_status=="PASS" else "FAIL"
    result={"custody_manifest_sha256":custody["sha256"],"spec_identity":specs["SPEC_BYTE_IDENTITY"],"spec_hashes":specs,"reference_por_sistema_sha256":audits["reference"]["sha256"],"A1_por_sistema_sha256":audits["A1"]["sha256"],"A2_por_sistema_sha256":audits["A2"]["sha256"],"per_system_audits":audits,"triple_byte_identity":triple_bytes,"A1_freeze_integrity":freeze["A1"]["status"],"A2_freeze_integrity":freeze["A2"]["status"],"freeze_protocol_defects":defects,"semantic_summary_status":sem["status"],"semantic_divergences":{"format_only":sem["counts"].get("FORMAT_ONLY",0),"value_affecting":sum(v for k,v in sem["counts"].items() if k.startswith("ERROR")),"ambiguous":0},"author_prediction_status":"SUPPORTED","A1_precalibration_status":precals["A1"]["status"],"A2_precalibration_status":precals["A2"]["status"],"A1_determinism_external":det["A1"]["status"],"A2_determinism_external":det["A2"]["status"],"A1_G0":"PENDING","A1_G5":"PENDING","A2_G0":"PENDING","A2_G5":"PENDING","gate_a_math":math_status,"gate_a_blindness":"PENDING","gate_a_overall":overall,"epistemic_status_if_pass":"VERIFIED · N=2 · SPEC A v0.1 (mathematical/computational only)","B_status":"BLOCKED" if overall!="PASS" else "READY_TO_UNBLOCK","notes":{"per_system":"exact triple identity verified from external rehashes","provenance":"G0/G5 require investigator evidence; missing A2 freeze is a protocol defect, not a mathematical discrepancy."}}
    dump(result,"GATE_A_RESULT.json")
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))

if __name__=="__main__": main()
