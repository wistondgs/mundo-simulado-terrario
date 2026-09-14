# Fork Ledger Contract

Migration 8 adds CAS-backed snapshots, fork identities, append-only ledger
events, and immutable branch bindings. A fork records parent identity, snapshot,
shared-history hash, intervention-spec hash, branch roles, trace artifacts and
verification event. It has no EvidenceGraph write path.
