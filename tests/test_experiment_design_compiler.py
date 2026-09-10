from dataclasses import replace
import pytest
from terrario.lab.theory.factory import ExperimentDesignCompiler, ReviewState
from tests.hypothesis_factory_helpers import family
def test_compiler_requires_reviewed_family_and_emits_generated_design():
    with pytest.raises(PermissionError): ExperimentDesignCompiler().compile(family())
    d=ExperimentDesignCompiler().compile(replace(family(),review_state=ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN)); assert d.review_state == ReviewState.GENERATED
