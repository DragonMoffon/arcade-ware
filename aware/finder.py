from pathlib import Path
from importlib import import_module

from engine.play import Game, Transition, Fail

__all__ = (
    "load_packs",
    "get_loaded_games",
    "get_loaded_transitions",
)

def load_packs():
    pth = Path().absolute() / "packs"
    pack_modules = tuple(import_module(f"packs.{pack.name}") for pack in pth.iterdir() if pack.is_dir())
    print(pack_modules)

def get_loaded_games():
    return Game.__subclasses__()

def get_loaded_transitions():
    return Transition.__subclasses__()

def get_loaded_fails():
    return Fail.__subclasses__()