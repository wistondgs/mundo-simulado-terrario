from pathlib import Path

def test_d2_studio_shows_all_four_scientific_boundaries():
    js=Path("terrario/lab/static/app.js").read_text()
    assert all(x in js for x in ("world_view","agent_view","observer_view","scientific_view")) or "Object.entries(s.views)" in js
    assert "ANALYST_INTERPRETATION" not in Path("terrario/lab/static/index.html").read_text()

def test_typed_and_structured_controls_update_one_patch():
    js=Path("terrario/lab/static/app.js").read_text()
    assert "state.studioPatch.difficulty" in js
    assert "state.studioPatch=JSON.parse" in js
    assert "syncStudioPatch" in js

def test_scientific_warnings_remain_visible():
    html=Path("terrario/lab/static/index.html").read_text()
    assert "SANDBOX ONLY" in html and "NOT PREREGISTERED" in html
