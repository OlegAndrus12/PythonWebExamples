"""State — one class per state.

Each state owns its own transitions instead of one big if/elif in Character.
A State enum member tags each class, so callers compare by kind rather than
by class identity.

Run: python3 classes.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
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


class CharacterState(ABC):
    kind: State

    @abstractmethod
    def handle(self, event: Event) -> CharacterState: ...


class Idle(CharacterState):
    kind = State.IDLE

    def handle(self, event: Event) -> CharacterState:
        if event is Event.RUN:
            return Running()
        if event is Event.JUMP:
            return Jumping()
        return self


class Running(CharacterState):
    kind = State.RUNNING

    def handle(self, event: Event) -> CharacterState:
        if event is Event.STOP:
            return Idle()
        if event is Event.JUMP:
            return Jumping()
        return self


class Jumping(CharacterState):
    kind = State.JUMPING

    def handle(self, event: Event) -> CharacterState:
        if event is Event.LAND:
            return Idle()
        return self


class Character:
    def __init__(self) -> None:
        self.state: CharacterState = Idle()

    def send(self, event: Event) -> None:
        current = self.state.kind
        self.state = self.state.handle(event)
        print(
            f"on {event.name:<5} current={current.name:<8} new={self.state.kind.name}"
        )


def main() -> None:
    hero = Character()
    for event in (Event.RUN, Event.JUMP, Event.LAND, Event.STOP, Event.JUMP, Event.LAND):
        hero.send(event)


if __name__ == "__main__":
    main()
