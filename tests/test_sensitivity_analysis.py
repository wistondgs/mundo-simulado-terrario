from terrario.experiment.statistics import sensitivity_label


def test_sensitivity_labels_are_descriptive():
    assert sensitivity_label(.7, [.72, .68]) == "THRESHOLD_STABLE"
