from .games import DigiGame

from engine.pack import Pack

__all__ = [
    "DigiGame"
]

def setup():
    return Pack(
        games=(DigiGame, ),
        transitions=(),
        fails=()
    )