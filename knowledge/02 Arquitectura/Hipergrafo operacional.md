---
kind: operational-hypergraph
source: terrario/lab/hypergraph/operational.py
---

# Hipergrafo operacional

[[knowledge/00 Control/Inicio|← Inicio]] · [[knowledge/02 Arquitectura/Mapa del sistema|Mapa del sistema]]

Este mapa conecta los elementos que no son una afirmación teórica: experimento,
observer, intento, frame, CAS, playback y fork. Es una relación operacional
tipada, no evidencia ni un mecanismo científico demostrado.

```mermaid
flowchart LR
  H[Hipótesis + diseño + escenario + observer] --> PR[Prerregistro]
  PR --> A[Plan + intent + agente + seeds] --> T[Trial attempt]
  T --> F[World Truth + Agent Observation + Observer View] --> SF[Scientific Frame]
  T --> R[Raw trace + result] --> CAS[CAS]
  CAS --> PB[Playback solo lectura]
  T --> S[Snapshot] --> FK[Control + intervención + Fork Ledger]
  FK --> D[Diff descriptivo]
```

Consulta [el contrato](../../docs/OPERATIONAL_HYPERGRAPH_CONTRACT.md) para
roles, cardinalidades y firewalls.
