"""The screening campaign must survive an interruption and must not invent findings.

Campaigns run for hours, so a cut is expected. What is at stake is not the run
in flight -- that costs minutes -- but the hours already paid for.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("screen_concepts", ROOT / "scripts/screen_concepts.py")
screen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(screen)


def _write(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def _row(condition, seed, **measures):
    return {"condition": condition, "seed": seed, "measures": measures}


def test_the_matrix_is_one_arm_per_concept_not_every_combination():
    keys = ["a", "b", "c"]
    names = [name for name, _ in screen.conditions(keys)]
    # k+1, not 2^k: main effects first, and only then the pairs worth paying for.
    assert names == ["completo", "sin:a", "sin:b", "sin:c"]
    mixes = {name: mix for name, mix in screen.conditions(keys)}
    assert mixes["completo"] == {} and mixes["sin:b"] == {"b": False}


def test_finished_runs_are_never_repeated(tmp_path):
    ledger = tmp_path / "campaign.jsonl"
    _write(ledger, [_row("completo", 1, x=1.0), _row("sin:a", 1, x=2.0)])
    done = screen.already_done(ledger)
    assert set(done) == {("completo", 1), ("sin:a", 1)}


def test_a_line_torn_in_half_by_the_cut_costs_that_run_and_no_other(tmp_path):
    # A process killed mid-write leaves a partial line. Refusing to parse the
    # whole file would throw away the hours before it.
    ledger = tmp_path / "campaign.jsonl"
    ledger.write_text(json.dumps(_row("completo", 1, x=1.0)) + "\n" +
                      json.dumps(_row("sin:a", 1, x=2.0))[:20], encoding="utf-8")
    done = screen.already_done(ledger)
    assert set(done) == {("completo", 1)}


def test_a_missing_ledger_is_a_fresh_campaign_not_an_error(tmp_path):
    assert screen.already_done(tmp_path / "nunca-existio.jsonl") == {}


def test_an_effect_smaller_than_the_seed_spread_is_not_called_a_finding():
    # Two arms whose means differ by less than the spread within one arm: the
    # difference is the seed, not the concept.
    rows = [_row("completo", 1, m=10.0), _row("completo", 2, m=20.0),
            _row("sin:a", 1, m=14.0), _row("sin:a", 2, m=17.0)]
    effect = next(e for e in screen.effects(rows, ["a"]) if e["mesh"] == "m")
    assert effect["evaluable"] is True
    assert effect["larger_than_seed_spread"] is False


def test_an_effect_larger_than_the_seed_spread_is_reported_with_both_arms():
    rows = [_row("completo", 1, m=10.0), _row("completo", 2, m=10.0),
            _row("sin:a", 1, m=2.0), _row("sin:a", 2, m=2.0)]
    effect = next(e for e in screen.effects(rows, ["a"]) if e["mesh"] == "m")
    assert effect["effect"] == 8.0 and effect["larger_than_seed_spread"] is True
    # Both arms travel with the difference: a lone delta hides whether the
    # concept added something or the ablated arm collapsed.
    assert effect["with"] == 10.0 and effect["without"] == 2.0


def test_a_mesh_missing_from_one_arm_is_not_evaluable_rather_than_zero():
    rows = [_row("completo", 1, m=10.0), _row("sin:a", 1, m=None)]
    effect = next(e for e in screen.effects(rows, ["a"]) if e["mesh"] == "m")
    assert effect["evaluable"] is False and effect["reason"] == "NOT_EVALUABLE_IN_ONE_ARM"
