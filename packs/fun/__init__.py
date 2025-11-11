from engine.resources import load_font
from .games import ShooterGame

from engine.pack import Pack

__all__ = ["ShooterGame"]

def setup():
    # load_font("fun.")
    return Pack(
        games=(ShooterGame),
        transitions=(),
        fails=()
    )
