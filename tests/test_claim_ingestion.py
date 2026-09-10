from tests.theory_helpers import theory_import

def test_claims_preserve_authorship_and_original_text():
    claims=theory_import().claims
    assert len(claims)==189 and all(x.original_text and x.provenance for x in claims)
