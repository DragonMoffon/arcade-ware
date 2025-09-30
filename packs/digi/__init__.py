from .games import DoNothingGame
from .charm import CharmGame

from engine.pack import Pack

__all__ = [
    "DoNothingGame",
    "CharmGame"
]

def setup():
    return Pack(
        games=(DoNothingGame, CharmGame),
        transitions=(),
        fails=()
    )
