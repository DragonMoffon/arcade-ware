from collections.abc import Iterable, Generator
from types import ModuleType
from typing import Protocol
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from datetime import datetime
import sys

from platformdirs import user_data_dir

from engine.play import Game, Transition, Fail
from engine.pack import Pack

# Todo: move somewhere else?
USER_APPDATA_PATH = Path(user_data_dir("arcadeware", "DigitalDragons", ensure_exists=True))

__all__ = (
    "PackManager",
    "packs",
)


class _PackModule(Protocol):
    __name__: str
    __file__: str | None
    def setup(self) -> Pack | Iterable[Pack] | Generator[Pack, None, None]: ...


class PackManager:

    def __init__(self, local_path: Path | None = None, global_path: Path | None = None) -> None:
        self._local_path: Path = local_path or Path().absolute() / "packs"
        self._global_path: Path = global_path or USER_APPDATA_PATH

        self._pack_groups: dict[str, tuple[Pack, ...]] = {} # pack folder name -> all packs from that folder
        self._pack_mapping: dict[str, Pack] = {} # namespaced pack name

        # Namespaced mapping of games, transitions, and fails
        self._game_mapping: dict[str, type[Game]] = {}
        self._transition_mapping: dict[str, type[Transition]] = {}
        self._fail_mapping: dict[str, type[Fail]] = {}

    def load_packs(self, override: bool = False):#
        packs = self._collect_packs()

        pack_groups: dict[str, list] = {}
        pack_mappings = {}

        game_mapping = {}
        transition_mapping = {}
        fail_mapping = {}

        for pack in packs:
            origin = pack.origin.stem
            spc_name = pack.space_name

            if origin not in pack_groups:
                pack_groups[origin] = []
            pack_groups[origin].append(pack)

            pack_mappings[spc_name] = pack
            if isinstance(pack.games, type):
                game_mapping[f"{spc_name}.{pack.games.__name__}"] = pack.games
            else:
                for game in pack.games:
                    game_mapping[f"{spc_name}.{game.__name__}"] = game
            
            if isinstance(pack.transitions, type):
                transition_mapping[f"{spc_name}.{pack.transitions.__name__}"] = pack.transitions
            else:
                for transition in pack.transitions:
                    transition_mapping[f"{spc_name}.{transition.__name__}"] = transition
            
            if isinstance(pack.fails, type):
                fail_mapping[f"{spc_name}.{pack.fails.__name__}"] = pack.fails
            else:
                for fail in pack.fails:
                    fail_mapping[f"{spc_name}.{fail.__name__}"] = fail

        if override:
            self._pack_groups = {group: tuple(packs) for group, packs in pack_groups.items()}
            self._pack_mapping = pack_mappings

            self._game_mapping = game_mapping
            self._transition_mapping = transition_mapping
            self._fail_mapping = fail_mapping
        else:
            self._pack_groups.update({group: tuple(packs) for group, packs in pack_groups.items()})
            self._pack_mapping.update(pack_mappings)

            self._game_mapping.update(game_mapping)
            self._transition_mapping.update(transition_mapping)
            self._fail_mapping.update(fail_mapping)

    def _collect_packs(self, load_local: bool = True, load_global: bool = True) -> Generator[Pack, None, None]:
        if load_local:
            for module in _import_packs(self._local_path):
                yield from _setup_pack(module)
            
        if load_global:
            for module in _import_packs(self._global_path):
                yield from _setup_pack(module)

    def can_play_pack(self, pack_spc_name: str) -> bool:
        if pack_spc_name not in self._pack_mapping:
            # Pack was not found
            return False
        
        pack = self._pack_mapping[pack_spc_name]

        # If the pack doesn't require any external deps then we don't care
        if not pack.requires_external:
            return True

        # If the external tuples are empty this costs very litte so no early exit.
        # TODO: use set comparison to make this way cleaner to read?
        has_external_games = True
        for external_game in pack.external_games:
            if external_game not in self._game_mapping:
                has_external_games = False
                break
        
        has_external_transitions = True
        for external_transition in pack.external_transitions:
            if external_transition not in self._game_mapping:
                has_external_transitions = False
                break

        has_external_fails = True
        for external_fail in pack.external_fails:
            if external_fail not in self._fail_mapping:
                has_external_fails = False
                break

        return (has_external_games and has_external_transitions and has_external_fails)

    def get_pack_games(self, pack_spc_name: str, include_external: bool = True) -> tuple[type[Game], ...]:
        pack = self._pack_mapping[pack_spc_name]
        
        external = ()
        if include_external:
            external = tuple(self._game_mapping[extern] for extern in pack.external_games if extern in self._game_mapping)
            if pack.requires_external and len(external) != len(pack.external_games):
                raise ValueError(f"{pack.name} cannot be played without external games which are missing.") # TODO: list missing games?

        return (*((pack.games,) if isinstance(pack.games, type) else pack.games), *external)

    def game_loaded(self, game: str) -> bool:
        return game in self._game_mapping

    def get_game(self, game: str) -> type[Game]:
        return self._game_mapping[game]

    def get_all_games(self) -> tuple[type[Game], ...]:
        return tuple(self._game_mapping.values())
    
    def transition_loaded(self, transition: str) -> bool:
        return transition in self._transition_mapping

    def get_transition(self, transition: str) -> type[Transition]:
        return self._transition_mapping[transition]

    def get_pack_transitions(self, pack_spc_name: str, include_external: bool = True) -> tuple[type[Transition], ...]:
        pack = self._pack_mapping[pack_spc_name]
        
        external = ()
        if include_external:
            external = tuple(self._transition_mapping[extern] for extern in pack.external_transitions if extern in self._transition_mapping)
            if pack.requires_external and len(external) != len(pack.external_transitions):
                raise ValueError(f"{pack.name} cannot be played without external transitions which are missing.") # TODO: list missing transitions?

        return (*((pack.transitions,) if isinstance(pack.transitions, type) else pack.transitions), *external)

    def get_all_transitions(self) -> tuple[type[Transition], ...]:
        return tuple(self._transition_mapping.values())
    
    def fail_loaded(self, fail: str) -> bool:
        return fail in self._fail_mapping

    def get_fail(self, fail: str) -> type[Fail]:
        return self._fail_mapping[fail]
    
    def get_pack_fails(self, pack_spc_name: str, include_external: bool = True) -> tuple[type[Fail], ...]:
        pack = self._pack_mapping[pack_spc_name]
        
        external = ()
        if include_external:
            external = tuple(self._fail_mapping[extern] for extern in pack.external_fails if extern in self._fail_mapping)
            if pack.requires_external and len(external) != len(pack.external_fails):
                raise ValueError(f"{pack.name} cannot be played without external fails which are missing.") # TODO: list missing fails?

        return (*((pack.fails,) if isinstance(pack.fails, type) else pack.fails), *external)
    
    def get_all_fails(self) -> tuple[type[Fail], ...]:
        return tuple(self._fail_mapping.values())


def _import_packs(pth: Path) -> Generator[_PackModule, None, None]:
    if not pth.exists():
        return

    for module in pth.iterdir():
        if module.name == '__pycache__':
            continue
        elif module.suffix == '.py':
            module_path = module
        elif module.suffix == '.zip':
            # TODO: support packs that are zips
            continue
        elif not module.is_dir():
            continue
        else:
            module_path = module / '__init__.py'
        yield _import_pack_module(f"packs.{module.stem}", module_path) # type: ignore -- this is an implicit cast, as valid packs **do** have a setup function


def _import_pack_module(name: str, pth: Path) -> ModuleType:
    # This function is a recipe from the python docs. It's a less safe version
    # of __import__ the method used by python to import a module.
    if name in sys.modules:
        raise ImportError(f'A pack with the name {name} already exists')

    # Grabing the __init__.py of the directory is probably unsafe.
    spec = spec_from_file_location(name, pth)
    if spec is None:
        raise ImportError(f'The pack {name} is not a valid python module')
    module = module_from_spec(spec)
    
    # this is the most cursed part of all of this, and it is only done
    # so the pack's internal imports all work properly, otherwise they
    # would be banished to the half executed realm safe and sound.
    sys.modules[name] = module
    spec.loader.exec_module(module) # type: ignore -- The loader should be real at this point

    return module


def _setup_pack(pack_module: _PackModule) -> Generator[Pack, None, None]:
    try:
        pack_def = pack_module.setup()
    except Exception as e:
        # TODO: add propper logging and reporting of failed imports. (including reporting to the player) 
        print(repr(e))
        pack_def = ()

    if pack_def is None: # Technically not possible, but I don't trust our users
        pack_def = ()

    if isinstance(pack_def, Pack):
        pack_def = (pack_def,)

    if pack_module.__file__ is None:
        print("UH OH NO PACK FILE") # TODO: better error text
        return

    # Trawl through packs and set metadata fields.
    anonymous_pack = False
    for pack in pack_def:
        source = Path(pack_module.__file__)
        origin = source if source.stem != '__init__' else source.parent
        object.__setattr__(pack, "origin", origin)

        if pack.name is None:
            if anonymous_pack:
                print(f"More than one anonymous pack were created by {origin.stem}")
                break
            object.__setattr__(pack, "name", origin.stem)
            object.__setattr__(pack, "space_name", origin.stem)
            anonymous_pack = True
        else:
            object.__setattr__(pack, "space_name", f"{origin.stem}.{pack.name}")

        object.__setattr__(pack, "creation_time", datetime.now())
        yield pack


packs = PackManager() # TODO: move somewhere smarter