# Scientific observability traceability

| Requirement | Implementation | Test | Status |
| --- | --- | --- | --- |
| durable terminal playback | observation service + CAS trace | memory-loss playback test | PASS |
| exact provenance | identity carried in trace/frame/cursor | memory-loss playback test | PASS |
| read-only viewer | World2D Scientific panel | source inspection | PASS |
| sandbox isolation | independent route/service/panel | existing firewall | PASS |
| SSE reconnect/resync | not implemented | — | DEFERRED |
