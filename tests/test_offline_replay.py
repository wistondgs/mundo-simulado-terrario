from terrario.lab.models import RunTimeline, TimelinePoint
from terrario.lab.replay import OfflineReplay

def test_offline_replay_navigation_uses_recorded_points():
    timeline=RunTimeline("r",(TimelinePoint(0),TimelinePoint(1,action=2,causal_change=True)),"trace")
    replay=OfflineReplay(timeline).forward().backward().jump("causal-change")
    assert replay.position == 1 and replay.current.origin == "RECORDED"
