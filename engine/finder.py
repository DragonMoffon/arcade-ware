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

def load_packs():
    local_modules = _import_packs(Path().absolute() / "packs")
    for module in local_modules:
        _load_pack(module)
    appdata_modules = _import_packs(USER_APPDATA_PATH)
    for module in appdata_modules:
        _load_pack(module)

class _PackImport(Protocol):
    def setup(self) -> Pack | Iterable[Pack] | Generator[Pack, None, None]: ...

def _import_packs(pth: Path) -> Generator[_PackImport, None, None]:
    for pack in pth.iterdir():
        # TODO: support packs that are zips
        if not pack.is_dir():
            continue
        yield _import_pack_dir(f"packs.{pack.stem}", pack) # type: ignore -- this is an implicit cast, as valid packs **do** have a setup function

def _import_pack_dir(name: str, pth: Path) -> ModuleType:
    if name in sys.modules:
        raise ImportError(f'A pack with the name {name} already exists')

    spec = spec_from_file_location(name, pth / "__init__.py")
    if spec is None:
        raise ImportError(f'The pack {name} is not a valid python module')
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module) # type: ignore -- The loader should be real at this point
    return module

def _load_pack(pack: _PackImport):
    try:
        pack_def = pack.setup()
    except Exception as e:
        print(e)
        pack_def = ()
    print(pack_def)

def get_loaded_games():
    return Game.__subclasses__()

def get_loaded_transitions():
    return Transition.__subclasses__()

def get_loaded_fails():
    return Fail.__subclasses__()