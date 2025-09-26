from __future__ import annotations
from arcade import View

MAX_STRIKE_COUNT = 3

class Display:
    # TODO: seperate the game state from the game view
    def __init__(self, view: PlayView, duration: float) -> None:
        pass

    def setup(self, state: PlayState):
        pass

    def draw(self):
        pass

    def update(self, delta_time: float):
        pass

class Counter(Display):
    pass

class Game(Display):
    def succeed(self):
        pass

    def fail(self):
        pass

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        pass

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        pass

class PlayState:
    
    def __init__(self, source: PlayView) -> None:
        self._source: PlayView = source

    @property
    def count(self):
        # The total number of games played this session
        return self._source.count
    
    @property
    def speed(self):
        # What speed level the game is at currently
        return self._source.speed

    @property
    def strikes(self):
        return self._source.strikes

    @property
    def on_last_life(self):
        return self._source.strikes == MAX_STRIKE_COUNT - 1

class PlayView(View):
    
    def __init__(self):
        self.count = 0
        self.speed = 1
        self.strikes = 0

        self._games: tuple[Game, ...] = ()
        self._counters: tuple[Counter, ...] = ()

        self._active_display: Display | None = None
        self._active_game: Game | None = None
        self._active_counter: Counter | None = None