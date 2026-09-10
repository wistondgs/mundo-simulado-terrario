from terrario.lab.theory.factory import CausalIdentifiabilityAudit, Identification
def test_identifiability_has_four_outcomes():
    audit=CausalIdentifiabilityAudit(); assert audit.audit({}).status == Identification.INVALID
    assert audit.audit({"paired_seeds":1,"identical_environment":1}).status == Identification.DESCRIPTIVE
    assert audit.audit(dict.fromkeys(audit.KEYS, True)).status == Identification.STRONG
