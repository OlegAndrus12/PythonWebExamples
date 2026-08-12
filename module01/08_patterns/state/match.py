"""State — an Enum plus match/case, no per-state classes.

The idiomatic-Python shortcut for state: the modes are Enum members, and the
transitions live in one function instead of being spread across classes.

Run: python3 match.py
"""

from __future__ import annotations

from enum import Enum


class State(Enum):
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"


class Event(Enum):
    RUN = "run"
    JUMP = "jump"
    LAND = "land"
    STOP = "stop"


def transition(state: State, event: Event) -> State:
    match state, event:
        case State.IDLE, Event.RUN:
            return State.RUNNING
        case State.IDLE, Event.JUMP:
            return State.JUMPING
        case State.RUNNING, Event.STOP:
            return State.IDLE
        case State.RUNNING, Event.JUMP:
            return State.JUMPING
        case State.JUMPING, Event.LAND:
            return State.IDLE
        case _:
            return state


class Character:
    def __init__(self) -> None:
        self.state = State.IDLE

    def send(self, event: Event) -> None:
        current = self.state
        self.state = transition(self.state, event)
        print(f"on {event.name:<5} current={current.name:<8} new={self.state.name}")


def main() -> None:
    hero = Character()
    for event in (Event.RUN, Event.JUMP, Event.LAND, Event.STOP, Event.JUMP, Event.LAND):
        hero.send(event)


if __name__ == "__main__":
    main()
