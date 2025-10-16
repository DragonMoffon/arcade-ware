from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from engine.play import Game, Transition, Fail


@dataclass(frozen=True, kw_only=True)
class Pack:
    name: str | None = None
    authors: str | tuple[str, ...] = ()
    version: str | None = None
    requirements: str | tuple[str, ...] = ()
    games: type[Game] | tuple[type[Game], ...] = ()
    transitions: type[Transition] | tuple[type[Transition], ...] = ()
    fails: type[Fail] | tuple[type[Fail], ...] = ()
    external_games: str | tuple[str, ...] = ()
    external_transitions: str | tuple[str, ...] = ()
    external_fails: str | tuple[str, ...] = ()
    requires_external: bool = False

    # -- Metadata attributes not set by the user --
    origin: Path = field(init=False)
    space_name: str = field(init=False)
    creation_time: datetime = field(init=False)

    @property
    def anonymous(self) -> bool:
        return self.name == self.space_name

