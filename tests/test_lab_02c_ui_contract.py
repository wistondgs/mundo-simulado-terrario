from pathlib import Path


def test_02c_views_and_components_are_visible():
    html=Path("terrario/lab/static/index.html").read_text()
    assert all(x in html for x in (
        "Lab · Capabilities","capabilityMatrix","CapabilityEvidencePanel","AgentInspector","CompatibilityReport",
        "Lab · Metrics","MetricDetail","ObserverConfigurator","Observer channel registry",
        "Lab · Experiments · Compose","ExperimentComposer","ScientificWarningPanel","TrialMatrix","ExperimentIdentityPanel",
    ))


def test_ui_preserves_scientific_language_and_no_execution_control():
    html=Path("terrario/lab/static/index.html").read_text();js=Path("terrario/lab/static/app.js").read_text()
    assert "STRUCTURAL SUPPORT ≠ SCIENTIFIC COMPETENCE" in html
    assert "CONSTRUCT ≠ OPERATIONAL PROXY ≠ IMPLEMENTATION" in html
    assert "REVIEW REQUIRED · NO EXECUTION" in html
    assert "experiment-drafts/validate" in js and "trial-matrices/build" in js
    assert "experiment-drafts/execute" not in js and "APPROVED_FOR_EXECUTION" not in js


def test_frontend_consumes_domain_api_without_reimplementing_assessment_logic():
    js=Path("terrario/lab/static/app.js").read_text()
    assert all(x in js for x in ("get(\"capabilities\")","get(\"metrics\")","get(\"observer/profiles\")","post(\"compatibility\"","post(\"observer/estimate\""))
    assert "module.includes" not in js and "capability ===" not in js


def test_trial_matrix_ui_discloses_all_multipliers_and_non_execution():
    js=Path("terrario/lab/static/app.js").read_text()
    assert all(x in js for x in ("variants:m.variants","agent_control_conditions:m.agent_control_conditions","world_seeds:m.world_seeds","agent_seeds:m.agent_seeds","repetitions:m.repetitions","total_trials:m.total_trials","execution_performed:m.execution_performed"))
