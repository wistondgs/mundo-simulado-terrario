# Operational Hypergraph Contract

The Theory Hypergraph is a graph of scientific candidate conjunctions. The
Operational Hypergraph is separate: it defines the n-ary runtime contracts that
bind design, execution, scientific observation, raw artifacts, playback and
causal forks. It never emits an EvidenceGraph node or a causal conclusion.

| Edge | Members → output |
| --- | --- |
| OHG-01 | hypothesis + experiment + scenario/world + observer + seeds → preregistration |
| OHG-02 | preregistration + plan + intent + scenario + agent + seeds + observer → attempt |
| OHG-03 | attempt + World Truth + Agent Observation + observer + tick → scientific frame |
| OHG-04 | attempt + frames + raw trace/result → CAS blob |
| OHG-05 | attempt + sealed trace + observer → read-only playback |
| OHG-06 | attempt + snapshot + control/intervention + spec → causal fork |
| OHG-07 | fork + paired branch traces → descriptive causal diff |

The executable catalogue is `terrario.lab.hypergraph.operational`; each member
has a role, cardinality and causal/observational classification. A view may
render these as junction nodes, but must preserve their n-ary membership.
