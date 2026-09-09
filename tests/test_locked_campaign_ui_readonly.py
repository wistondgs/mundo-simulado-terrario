import pytest
from terrario.lab.sandbox import SandboxSession

def test_locked_campaign_ui_readonly():
    session=SandboxSession("campaign",locked_campaign=True)
    with pytest.raises(PermissionError): session.play()
    with pytest.raises(PermissionError): session.edit_config(seed=9)
