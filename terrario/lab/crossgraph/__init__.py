"""Federated scientific cross-graph.

Connects independent scientific domains (ReferenceGraph, TheoryGraph,
Hypergraph, Hypothesis, World/Scenario, Experiment, Preregistration,
EvidenceGraph) without fusing them. CrossGraph owns only cross-domain
identities, links, provenance, federation snapshots, traversal indexes,
projections, and audit history. The package initializer intentionally stays
dependency-free so persistence codecs may import domain contracts without
loading the service.
"""
