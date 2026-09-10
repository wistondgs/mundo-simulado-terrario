from pathlib import Path

def test_ui_exposes_real_graph_controls_and_scientific_boundaries():
    html=Path("terrario/lab/static/index.html").read_text()
    js=Path("terrario/lab/static/app.js").read_text()
    assert all(x in html for x in ("BLOCKED_CUDA","graphConflicts","graphHyperedges","nodeDetail","findPaths"))
    assert "ninguno seleccionado como correcto" in js and "REVIEW_REQUIRED" in js
    assert "Lab · Scientific Review" in html and "NO EXECUTION" in html
    assert "theory/scientific-review" in js and "HUMAN DECISION: NOT SET" in js
