from terrario.lab.sandbox import SandboxSession

def test_sandbox_controls_are_functional_and_immutable():
    original=SandboxSession("sandbox")
    changed=original.play().pause().single_step().set_speed(2)
    assert original.step == 0 and changed.step == 1 and changed.speed == 2
