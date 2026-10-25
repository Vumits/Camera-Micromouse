from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

import numpy as np


class TimerState(str, Enum):
    IDLE = "IDLE"
    ARMED = "ARMED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


@dataclass
class FramePacket:
    frame: np.ndarray
    capture_ts: float
    frame_index: int


@dataclass
class RoiBundle:
    start_line: Tuple[int, int, int, int]
    goal_area: Tuple[int, int, int, int]


@dataclass
class DetectionResult:
    markers_found: int = 0
    warped_frame: Optional[np.ndarray] = None
    rois: Optional[RoiBundle] = None
    start_crossed: bool = False
    goal_changed_ratio: float = 0.0
    mouse_in_goal: bool = False
    latency_ms: float = 0.0
    debug_messages: list[str] = field(default_factory=list)
