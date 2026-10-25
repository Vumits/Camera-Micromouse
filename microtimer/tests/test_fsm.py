from core.fsm import TimerFSM
from core.models import TimerState


def test_fsm_flow():
    fsm = TimerFSM(debounce_ms=0, min_run_ms=0)
    fsm.arm()
    assert fsm.snapshot.state == TimerState.ARMED
    fsm.on_start_trigger()
    assert fsm.snapshot.state == TimerState.RUNNING
    fsm.on_finish_trigger()
    assert fsm.snapshot.state == TimerState.FINISHED
    assert fsm.snapshot.elapsed_s >= 0.0
