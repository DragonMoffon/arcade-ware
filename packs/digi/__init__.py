from engine.resources import load_font
from .games import ChopGame, SortGame, LetterGame, SliderGame, ComboLockGame, DoNothingGame, WhackAMoleGame, PencilSharpeningGame
from .charm import CharmGame

from engine.pack import Pack

__all__ = [
    "DoNothingGame",
    "CharmGame"
]

def setup():
    load_font("digi.8bojve")
    return Pack(
        games=(ChopGame, SortGame, LetterGame, SliderGame, ComboLockGame, DoNothingGame, WhackAMoleGame, PencilSharpeningGame, CharmGame),
        transitions=(),
        fails=()
    )
