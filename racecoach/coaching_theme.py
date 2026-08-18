from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ThemeStatus = Literal[
    "emerging",
    "active",
    "improving",
    "reinforced",
    "retired",
]


@dataclass
class CoachingTheme:
    name: str
    status: ThemeStatus
    priority: int | None = None

    started: str | None = None
    last_observed: str | None = None

    occurrence_count: int = 0
    event_count: int = 0
    cumulative_opportunity_s: float = 0.0

    trend: str | None = None

    evidence: list[str] = field(default_factory=list)

    practice_objective: str | None = None
    reinforcement_cue: str | None = None
    