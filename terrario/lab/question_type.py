"""Which *kind* of uncertainty to resolve next, which is not which precursor.

The tempting output for 1.8 is "acquire EVSENS".  That would still be an
invented choice wearing a derivation, and the alphabetical failure already
showed how convincing those look.  What the state of the graph actually
determines is something weaker and more useful: the **class** of question.

    1.8   the realised family cannot express the sealed construct
          -> FAMILY_PROBE, with three candidate dimensions, selection unresolved

    1.5   psi is present and its necessity is unadjudicated
          -> LESION_PROBE(psi), with five acquisition candidates, none ordered

Two types, because the project has two real cases.  Twenty speculative ones
would be a taxonomy nobody earned.

The order of derivation is the point.  A family that cannot express the
construct makes every question about precursors premature -- no precursor
rescues a mechanism that cannot state the thing -- so the family question comes
first whenever a contradiction of that shape exists.  Only then does an
existing-but-unadjudicated capability ask for a lesion, and only then do absent
candidates ask to be acquired.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from terrario.lab.ceiling_probe import BlockerClass, CeilingProbe

SCHEMA_VERSION = "terrario.lab.question-type/v1"


class QuestionType(StrEnum):
    FAMILY_PROBE = "FAMILY_PROBE"
    LESION_PROBE = "LESION_PROBE"
    ACQUISITION_PROBE = "ACQUISITION_PROBE"
    NONE_REQUIRED = "NONE_REQUIRED"


class Selection(StrEnum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class DerivedQuestion:
    """A class of question, its dimensions, and whether anything orders them."""

    target: str
    question_type: QuestionType
    question: str
    candidate_dimensions: tuple[str, ...]
    selection: Selection
    why: str
    schema_version: str = SCHEMA_VERSION

    def as_record(self) -> Mapping[str, Any]:
        return {"schema_version": self.schema_version, "target": self.target,
                "question_type": self.question_type.value, "question": self.question,
                "candidate_dimensions": list(self.candidate_dimensions),
                "selection": self.selection.value, "why": self.why}


def derive_question(target: str, probes: tuple[CeilingProbe, ...],
                    gap) -> DerivedQuestion:
    """From the state of the graph, not from a table of good ideas.

    `gap` is a `GapReport`.  Its `lesion_candidates` already carry the one
    thing that distinguishes a lesion from an acquisition: whether the
    capability is present.
    """
    del_target = [p for p in probes if p.target_capability == target]

    # 1 · Una familia que no puede expresar el constructo hace prematura
    #     cualquier pregunta sobre precursores: ningún precursor rescata a un
    #     mecanismo incapaz de enunciar la cosa.
    familia = next((p for p in del_target
                    if p.blocker_class is BlockerClass.FAMILY_CANNOT_EXPRESS), None)
    if familia is not None:
        dimensiones = tuple(sorted(familia.candidate_missing_precursors))
        pregunta = (familia.candidate_family_questions[0]
                    if familia.candidate_family_questions
                    else f"can any mechanism family realise the sealed construct of {target}?")
        return DerivedQuestion(
            target=target, question_type=QuestionType.FAMILY_PROBE,
            question=pregunta, candidate_dimensions=dimensiones,
            selection=Selection.UNRESOLVED if len(dimensiones) != 1 else Selection.RESOLVED,
            why=(f"{familia.probe_id}: {familia.observed_blocker[:90]}… · "
                 f"no precursor repairs a family that cannot state the construct"))

    # 2 · Una capacidad presente con necesidad sin adjudicar pide lesión, no
    #     adquisición. Preguntar si se puede adquirir algo que ya está sería
    #     la pregunta equivocada sobre el objeto correcto.
    if gap.lesion_candidates:
        candidatos = tuple(sorted(gap.lesion_candidates))
        return DerivedQuestion(
            target=target, question_type=QuestionType.LESION_PROBE,
            question=(f"is «{candidatos[0]}» functionally required for {target}, "
                      f"or scaffolding? remove it and look"),
            candidate_dimensions=candidatos,
            selection=Selection.RESOLVED if len(candidatos) == 1 else Selection.UNRESOLVED,
            why="precursor present, necessity unadjudicated")

    # 3 · Sólo entonces, adquirir. Y sin elegir cuál si nada los ordena.
    if gap.tied_candidates:
        empatados = tuple(sorted(gap.tied_candidates))
        return DerivedQuestion(
            target=target, question_type=QuestionType.ACQUISITION_PROBE,
            question=(f"which of these, acquired on its own with every other "
                      f"channel held fixed, moves {target}?"),
            candidate_dimensions=empatados,
            selection=Selection.RESOLVED if len(empatados) == 1 else Selection.UNRESOLVED,
            why=("the evidence does not order them" if len(empatados) > 1
                 else "only one candidate sits at the frontier"))

    return DerivedQuestion(
        target=target, question_type=QuestionType.NONE_REQUIRED,
        question="", candidate_dimensions=(), selection=Selection.RESOLVED,
        why="no unresolved precursor relation for this target")
