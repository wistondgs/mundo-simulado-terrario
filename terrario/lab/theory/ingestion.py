"""Parsers for the project's real CSV and Markdown derived artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from terrario.lab.models import EpistemicStatus
from terrario.lab.theory.models import (
    AmbiguityRecord, CanonicalConceptCandidate, ClaimRecord, ConflictRecord,
    CoverageRecord, HyperedgeCandidateRecord, IntegrityRecord, MappingRelation,
    RawConceptRecord, RelationRecord, RelationStrength, SourceRecord,
)
from terrario.lab.theory.snapshot import artifact_version


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    tables, i = [], 0
    while i + 1 < len(lines):
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|?[\s:|-]+\|", lines[i + 1]):
            headers = [x.strip() for x in lines[i].strip().strip("|").split("|")]
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                values = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                if len(values) == len(headers): tables.append(dict(zip(headers, values)))
                i += 1
        else: i += 1
    return tables


def _text(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True)


def _status_for_attribution(value: str) -> EpistemicStatus:
    return EpistemicStatus.ANALYST_INFERENCE if "ANALYST" in value.upper() else EpistemicStatus.AUTHOR_CLAIM


def _strength(row: dict[str, str]) -> RelationStrength:
    causal = " ".join((row.get("causal_status", ""), row.get("relation_type_audited", ""))).upper()
    level = row.get("evidence_strength_level", "")
    if "EXPLICIT_CAUSAL" in causal or "CAUSAL_EXPLICIT" in causal: return RelationStrength.EXPLICIT_CAUSAL_CLAIM
    if any(x in causal for x in ("REQUIERE", "DEPENDE", "REQUIRE")): return RelationStrength.REQUIREMENT_DEPENDENCY
    if any(x in causal for x in ("FACILITA", "MODULA", "INHIBE")): return RelationStrength.FACILITATION_MODULATION
    if level and level not in {"0", "1"}: return RelationStrength.ASSOCIATION
    return RelationStrength.CONTEXTUAL_COOCCURRENCE


@dataclass(frozen=True)
class TheoryImport:
    sources: tuple[SourceRecord, ...] = ()
    claims: tuple[ClaimRecord, ...] = ()
    raw_concepts: tuple[RawConceptRecord, ...] = ()
    canonical_candidates: tuple[CanonicalConceptCandidate, ...] = ()
    relations: tuple[RelationRecord, ...] = ()
    ambiguities: tuple[AmbiguityRecord, ...] = ()
    conflicts: tuple[ConflictRecord, ...] = ()
    hyperedges: tuple[HyperedgeCandidateRecord, ...] = ()
    coverage: tuple[CoverageRecord, ...] = ()
    integrity: tuple[IntegrityRecord, ...] = ()

    def counts(self):
        return {name: len(getattr(self, name)) for name in self.__dataclass_fields__}


class TheoryIngestor:
    def __init__(self, snapshot_dir: str | Path, *, include_operational_evidence: bool = False):
        self.root = Path(snapshot_dir)
        if not (self.root / "snapshot_manifest.json").is_file(): raise ValueError("snapshot_manifest.json is required")
        self.evidence_root = self.root.parent.parent / "theory_operational_artifacts" / self.root.name
        self.include_operational_evidence = include_operational_evidence
        if include_operational_evidence:
            self._verify_operational_evidence()

    def _evidence_path(self, name: str) -> Path:
        return self.evidence_root / name

    def _verify_operational_evidence(self) -> None:
        if not self.evidence_root.exists():
            return
        manifest_path = self._evidence_path("operational_manifest.json")
        if not manifest_path.is_file():
            raise ValueError("operational evidence manifest is required")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        snapshot = json.loads((self.root / "snapshot_manifest.json").read_text(encoding="utf-8"))
        if (manifest.get("schema") != "terrario.theory.operational-evidence/v1"
                or manifest.get("base_snapshot_id") != snapshot.get("snapshot_id")
                or manifest.get("base_snapshot_manifest_sha256") != hashlib.sha256((self.root / "snapshot_manifest.json").read_bytes()).hexdigest()):
            raise ValueError("operational evidence does not match its base snapshot")
        for name, digest in manifest.get("artifacts", {}).items():
            path = self._evidence_path(name)
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError("operational evidence artifact integrity mismatch")

    def ingest(self) -> TheoryImport:
        return TheoryImport(
            sources=tuple(self._sources()), claims=tuple(self._claims()),
            raw_concepts=tuple(self._raw_concepts()), canonical_candidates=tuple(self._canonical()),
            relations=tuple(self._relations()), ambiguities=tuple(self._ambiguities()),
            conflicts=tuple(self._conflicts()), hyperedges=tuple(self._hyperedges()),
            coverage=tuple(self._coverage()), integrity=tuple(self._integrity()),
        )

    def _base(self, path: Path, row: dict, original_id: str, original_text: str, status: EpistemicStatus):
        return dict(id=original_id, original_id=original_id, original_text=original_text,
                    source_artifact=path.name, source_version=artifact_version(path.name),
                    provenance=f"{path}:record:{original_id}", epistemic_status=status, fields=row)

    def _sources(self) -> Iterable[SourceRecord]:
        path = self.root / "SOURCE_PROVENANCE_v0.3.csv"
        if path.exists():
            for row in _rows(path):
                sid = row["source_id"]; integrity = row.get("identity_verification", "UNRESOLVED")
                blocked = any(token in (integrity + row.get("integrity_notes", "")).upper() for token in ("QUARANTIN", "MISMATCH", "UNAVAILABLE"))
                yield SourceRecord(**self._base(path, row, sid, _text(row), EpistemicStatus.RAW), integrity_status=integrity, valid_evidence_source=not blocked)
        sample = self.root / "SOURCE_SAMPLE_v0.1.md"
        if sample.exists():
            for row in _table(sample):
                sid = row.get("ID", "")
                if not sid.startswith("TI-"): continue
                integrity = row.get("Estado T1", "UNRESOLVED")
                blocked = integrity in {"MISMATCH", "INCOMPLETE_HTML", "UNAVAILABLE", "LIMITED_SCAN", "QUARANTINED_DO_NOT_CITE"}
                yield SourceRecord(**self._base(sample, row, sid, _text(row), EpistemicStatus.RAW), integrity_status=integrity, valid_evidence_source=not blocked)
        primary = self._evidence_path("PRIMARY_SOURCE_PROVENANCE_v0.1.csv")
        if self.include_operational_evidence and primary.exists():
            for row in _rows(primary):
                sid = row["source_id"]
                base = self._base(primary, row, sid, _text(row), EpistemicStatus.RAW)
                base["source_artifact"] = row["source_artifact"]
                base["source_version"] = row["source_version"]
                yield SourceRecord(**base, integrity_status=row.get("identity_verification", "UNRESOLVED"), valid_evidence_source=row.get("identity_verification") == "VERIFIED_SHA256")

    def _claims(self) -> Iterable[ClaimRecord]:
        paths = [self.root / name for name in ("CLAIMS_RELATIONS_v0.1.csv", "CLAIMS_RELATIONS_PATCH_v0.3.csv")]
        if self.include_operational_evidence:
            paths.append(self._evidence_path("HYPEREDGE_ROLE_CLAIMS_v0.1.csv"))
        for path in paths:
            if not path.exists(): continue
            for row in _rows(path):
                cid = row["claim_id"]; attribution = row.get("explicit_or_inferred", "UNRESOLVED")
                yield ClaimRecord(**self._base(path, row, cid, row.get("claim_text_or_paraphrase", _text(row)), _status_for_attribution(attribution)), source_id=row.get("source_id", row.get("fuente", "UNRESOLVED")), attribution=attribution)

    def _raw_concepts(self) -> Iterable[RawConceptRecord]:
        seen = set()
        for name in ("CONCEPTS_RAW_v0.1.csv", "CONCEPT_CANONICAL_MAP_v0.2.csv", "CONCEPTS_RAW_PATCH_v0.3.csv"):
            path = self.root / name
            if not path.exists(): continue
            for row in _rows(path):
                cid = row["concept_id"]
                if cid in seen: continue
                seen.add(cid)
                yield RawConceptRecord(**self._base(path, row, cid, row.get("nombre_original", _text(row)), EpistemicStatus.RAW))

    def _canonical(self) -> Iterable[CanonicalConceptCandidate]:
        path = self.root / "CONCEPT_CANONICAL_MAP_v0.2.csv"
        if not path.exists(): return
        for index, row in enumerate(_rows(path), 1):
            relation = row.get("mapping_relation") or "UNRESOLVED"
            if relation not in MappingRelation._value2member_map_: relation = "UNRESOLVED"
            candidate = row.get("canonical_candidate_id") or f"CANON-UNRESOLVED-{index:04d}"
            rid = f"MAP-{row['concept_id']}-{candidate}"
            yield CanonicalConceptCandidate(**self._base(path, row, rid, row.get("canonical_candidate_label", _text(row)), EpistemicStatus.CANONICAL_CANDIDATE), raw_concept_id=row["concept_id"], mapping_relation=relation)

    def _relations(self) -> Iterable[RelationRecord]:
        path = self.root / "RELATIONS_AUDIT_v0.2.csv"
        if not path.exists(): return
        for row in _rows(path):
            rid = row["claim_id"]; attribution = row.get("attribution", "UNRESOLVED")
            yield RelationRecord(**self._base(path, row, rid, row.get("claim_text_or_paraphrase", _text(row)), _status_for_attribution(attribution)), source_concept=row.get("source_concept", ""), target_concept=row.get("target_concept", ""), relation_type=row.get("relation_type_audited", row.get("relation_type_original", "UNRESOLVED")), strength=_strength(row), attribution=attribution)

    def _ambiguities(self) -> Iterable[AmbiguityRecord]:
        path = self.root / "AMBIGUITIES_v0.2.md"
        if not path.exists(): return
        for index, row in enumerate(_table(path), 1):
            rid = f"AMB-{index:03d}"
            yield AmbiguityRecord(**self._base(path, row, rid, _text(row), EpistemicStatus.UNRESOLVED))

    def _conflicts(self) -> Iterable[ConflictRecord]:
        path = self.root / "CONCEPT_CONFLICTS_v0.1.md"
        if not path.exists(): return
        sections = re.split(r"(?m)^## \d+\. ", path.read_text(encoding="utf-8"))[1:]
        for index, section in enumerate(sections, 1):
            title, _, body = section.partition("\n")
            participants = tuple(re.findall(r"\*\*([^:*]+)(?:\s*\([^)]*\))?:\*\*", body))
            rid = f"CONFLICT-{index:03d}"
            yield ConflictRecord(**self._base(path, {"title": title, "body": body.strip()}, rid, section.strip(), EpistemicStatus.UNRESOLVED), participants=participants)

    def _hyperedges(self) -> Iterable[HyperedgeCandidateRecord]:
        path = self.root / "HYPEREDGE_CANDIDATES_v0.2.md"
        if not path.exists(): return
        for row in _table(path):
            rid = row.get("ID", "")
            if not rid.startswith("HYPERCAND-"): continue
            yield HyperedgeCandidateRecord(**self._base(path, row, rid, _text(row), EpistemicStatus.TESTABLE_CONJUNCTION), components=tuple(x.strip() for x in row["Componentes"].split(";") if x.strip()), predicted_outcome=row["Resultado"], attribution=row["Atribución"], conjunction_explicitness=row["Conjunción explícita"], necessity=row["Necesidad"], sufficiency=row["Suficiencia"], level=row["Nivel"], discriminating_test=row["Prueba discriminante"], confounders=tuple(x.strip() for x in row["Confusores"].split(";") if x.strip()), decision=row["Decisión"])

    def _coverage(self) -> Iterable[CoverageRecord]:
        for name in ("COVERAGE_MATRIX_v0.3.csv", "CONCEPT_COVERAGE_AUDIT_v0.3.csv"):
            path = self.root / name
            if not path.exists(): continue
            for index, row in enumerate(_rows(path), 1):
                rid = row.get("family_id") or f"COVERAGE-{index:03d}"
                status = row.get("remaining_status") or row.get("coverage_after_patch") or row.get("status_v0_3_after_patch") or "UNRESOLVED"
                yield CoverageRecord(**self._base(path, row, f"{path.stem}:{rid}", _text(row), EpistemicStatus.UNRESOLVED), concept_family=row.get("concept_family", row.get("area", rid)), coverage_status=status)

    def _integrity(self) -> Iterable[IntegrityRecord]:
        path = self.root / "CORPUS_INTEGRITY_PATCH_v0.1.md"
        if not path.exists(): return
        for row in _table(path):
            rid = row.get("ID", "")
            if not rid: continue
            status = row.get("Resolución", "UNRESOLVED")
            yield IntegrityRecord(**self._base(path, row, rid, _text(row), EpistemicStatus.RAW), integrity_status=status)
