# D2 visual validation fixture

This is a deterministic rendering-validation fixture, not a scientific run.
Its permanent label is `INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE`; it executes
no agent and does not write EvidenceGraph.

Run the Lab with an isolated absolute data root:

```bash
.venv/bin/python -m terrario.lab.api --root . --data-root /absolute/temporary/root
```

Open `http://127.0.0.1:8765/workspace/index.html`, locate **D2 Scientific
Studio**, and select **Open D2 visual validation fixture**. The timeline is
the human-facing inspection surface; it receives its frame records from
`D2BindingProtocol` via `/api/studio/d2/visual-fixture`.

Manual check card:

1. At tick 0, confirm `INITIAL` and no observer error.
2. Seek tick 4: object `#0` is `OCCLUDED · occluded`, not deleted.
3. Seek tick 5: object `#0` is `VISIBLE · visible_again` with the same ID.
4. Seek tick 6: inspect the record to confirm object `#0` retained its ID and
   changed its property signature.
5. Seek tick 8: confirm object `#99` appears as a legitimate world object.
6. Seek tick 10: confirm `BINDING_ERROR` and the scope label
   `INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE`.
7. Seek backward to tick 3, then forward to tick 10. The previous binding
   classification must not remain at tick 3, and tick 10 must match its direct
   rendering.
8. At every tick, Agent Observation and Cognitive State must read
   `NOT_APPLICABLE`.
