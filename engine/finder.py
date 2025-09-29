from collections.abc import Iterable, Generator
from types import ModuleType
from typing import Protocol
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import sys

from platformdirs import user_data_dir

from engine.play import Game, Transition, Fail
from engine.pack import Pack

# Todo: move somewhere else?
USER_APPDATA_PATH = Path(user_data_dir("arcadeware", "DigitalDragons", ensure_exists=True))

__all__ = (
    "load_packs",
    "get_loaded_games",
    "get_loaded_transitions",
)


class _PackModule(Protocol):
    def setup(self) -> Pack | Iterable[Pack] | Generator[Pack, None, None]: ...


class PackManager:

    def __init__(self) -> None:
        self._local_path: Path = Path().absolute() / "packs"
        self._global_path: Path = USER_APPDATA_PATH

        self._pack_groups: dict[str, tuple[Pack, ...]] = {} # pack folder name -> all packs from that folder
        self._pack_mapping: dict[str, Pack] = {} # namespaced pack name

        # Name spaced mapping of games, transitions, and fails
        self._game_mapping: dict[str, type[Game]] = {}
        self._transition_mapping: dict[str, type[Transition]] = {}
        self._fails_mapping: dict[str, type[Fail]] = {}

    def load_packs(self):#
        pass
    
    def _collect_packs(self, load_local: bool = True, load_global: bool = True) -> Generator[Pack, None, None]:
        if load_local:
            for module in _import_packs(self._local_path):
                yield from _setup_pack(module)
            
        if load_global:
            for module in _import_packs(self._global_path):
                yield from _setup_pack(module)


def load_packs():
    local_modules = _import_packs(Path().absolute() / "packs")
    for module in local_modules:
        yield from _setup_pack(module)
    appdata_modules = _import_packs(USER_APPDATA_PATH)
    for module in appdata_modules:
        yield from _setup_pack(module)


def _import_packs(pth: Path) -> Generator[_PackModule, None, None]:
    if not pth.exists():
        return

    for module in pth.iterdir():
        # TODO: support packs that are zips
        if not module.is_dir():
            continue
        yield _import_pack_module(f"packs.{module.stem}", module) # type: ignore -- this is an implicit cast, as valid packs **do** have a setup function


def _setup_pack(pack_module: _PackModule) -> Iterable[Pack] | Generator[Pack, None, None]:
    try:
        pack_def = pack_module.setup()
    except Exception as e:
        # TODO: add propper logging and reporting of failed imports. (including reporting to the player) 
        print(e)
        pack_def = ()

    if pack_def is None: # Technically not possible, but I don't trust our users
        pack_def = ()

    if isinstance(pack_def, Pack):
        pack_def = (pack_def,)

    return pack_def


def get_loaded_games():
    return Game.__subclasses__()


def get_loaded_transitions():
    return Transition.__subclasses__()


def get_loaded_fails():
    return Fail.__subclasses__()


def _import_pack_module(name: str, pth: Path) -> ModuleType:
    # This function is a recipe from the python docs. It's a less safe version
    # of __import__ the method used by python to import a module.
    if name in sys.modules:
        raise ImportError(f'A pack with the name {name} already exists')

    # Grabing the __init__.py of the directory is probably unsafe.
    spec = spec_from_file_location(name, pth / "__init__.py")
    if spec is None:
        raise ImportError(f'The pack {name} is not a valid python module')
    module = module_from_spec(spec)
    
    # this is the most cursed part of all of this, and it is only done
    # so the pack's internal imports all work properly, otherwise they
    # would be banished to the half executed realm safe and sound.
    sys.modules[name] = module
    spec.loader.exec_module(module) # type: ignore -- The loader should be real at this point
    return module