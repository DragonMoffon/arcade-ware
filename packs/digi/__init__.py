from .games import DoNothingGame

from engine.pack import Pack

__all__ = [
    "DoNothingGame"
]

def setup():
    return Pack(
        games=(DoNothingGame, ),
        transitions=(),
        fails=()
    )
