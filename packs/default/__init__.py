from engine.pack import Pack

from packs.default.games import ShakeEmUp, JuggleTheBall
from .transitions import DefaultTransition
from .fails import DefaultFail

__all__ = (
    "ShakeEmUp",
    "DefaultTransition",
    "DefaultFail",
)

def setup():
    yield Pack(
        games = (ShakeEmUp, JuggleTheBall),
        transitions = (DefaultTransition,),
        fails = (DefaultFail,)
    )
