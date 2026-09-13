"""Durable, versioned scientific reference graph.

Represents which documents exist, what they say, which protocols they use,
which limitations they report, and where each claim comes from. This package is
strictly separate from the TheoryGraph and the EvidenceGraph: a reference is
never evidence, a citation is never support, and a source claim is never one of
our own claims. The package initializer intentionally stays dependency-free so
persistence codecs may import domain contracts without loading the service.
"""
