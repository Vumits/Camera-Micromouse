from __future__ import annotations

from core.fsm import TimerFSM
from core.models import DetectionResult


class AppViewModel:
    def __init__(self, timer_fsm: TimerFSM):
        self.timer_fsm = timer_fsm
        self.last_result = DetectionResult()
        self.fps = 0.0

    def update_from_process(self, result: DetectionResult, fps: float) -> None:
        self.last_result = result
        self.fps = fps

    @property
    def state_name(self) -> str:
        return self.timer_fsm.snapshot.state.value

    @property
    def elapsed_s(self) -> float:
        return self.timer_fsm.snapshot.elapsed_s
