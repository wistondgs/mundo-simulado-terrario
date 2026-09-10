from tests.theory_helpers import theory_import

def test_real_sources_are_imported_without_rewriting():
    sources=theory_import().sources
    assert len(sources)==44 and any(x.id=="TI-0004" and "Hume" in x.original_text for x in sources)
