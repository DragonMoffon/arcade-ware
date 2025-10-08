from engine.resources import load_font
from .games import DoNothingGame
from .charm import CharmGame

from engine.pack import Pack

__all__ = [
    "DoNothingGame",
    "CharmGame"
]

def setup():
    load_font("digi.8bojve")
    return Pack(
        games=(DoNothingGame, CharmGame),
        transitions=(),
        fails=()
    )
