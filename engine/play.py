from __future__ import annotations
from typing import Self
from random import shuffle

from arcade import View as ArcadeView
from arcade.clock import Clock

MAX_STRIKE_COUNT = 4
SPEED_INCREASE_GAME_COUNT = 10
SPEED_INCREASE_STEP_SIZE = 1.0

class Display:
    # TODO: seperate the game state from the game view
    def __init__(self, state: PlayState, duration: float) -> None:
        self.state: PlayState = state
        self._duration: float = duration

    @property
    def duration(self):
        return self._duration
    
    @classmethod
    def create(cls, state: PlayState) -> Self:
        raise NotImplementedError()

    def setup(self):
        pass

    def draw(self):
        pass

    def update(self, delta_time: float):
        pass

class Transition(Display):
    pass

class Game(Display):
    def __init__(self, state: PlayState, prompt: str, controls: str, duration: float, success_duration: float | None = None) -> None:
        super().__init__(state, duration)
        # The text prompt for the transition to show, and the id of the control image to show.
        self.prompt: str = prompt
        self.controls: str = controls

        # How long after the game has finished does the play view hold on.
        # This is to let the game display a success/fail animation.
        # If None the play view instead tells the trasition to show a success/failure.
        self.success_duration: float | None = success_duration

    def succeed(self):
        self.state.set_game_succeeded(True)

    def fail(self):
        self.state.set_game_succeeded(False)

    def on_time_runout(self, state: PlayState):
        self.fail()

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        pass

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        pass

# TODO
class FailScreen(Display):
    pass

class PlayState:
    
    def __init__(self, source: PlayView) -> None:
        self._source: PlayView = source

    @property
    def cursor_position(self):
        return self._source.cursor_position
    
    @property
    def screen_width(self):
        return self._source.width
    
    @property
    def screen_height(self):
        return self._source.height

    @property
    def count(self) -> int:
        # The total number of games played this session
        return self._source.count
    
    @property
    def speed(self) -> int:
        # What speed level the game is at currently
        return self._source.speed

    @property
    def strikes(self) -> int:
        return self._source.strikes

    @property
    def on_last_life(self) -> bool:
        return self._source.strikes == MAX_STRIKE_COUNT - 1
    
    @property
    def game_finished(self) -> bool:
        return self._source.active_game_succeeded is not None
    
    @property
    def game_succeeded(self) -> bool:
        return self._source.active_game_succeeded
    
    def set_game_succeeded(self, succeeded: bool):
        self._source.game_succeeded(succeeded)

    @property
    def success_duration(self) -> float | None:
        return self._source.success_duration
    
    @property
    def show_transition_success(self) -> bool:
        return not self._source.success_duration
    
    @property
    def is_speedup(self) -> bool:
        return self._source.count != 0 and self._source.count % SPEED_INCREASE_GAME_COUNT == 0
    
    @property
    def total_time(self) -> float:
        return self._source.play_clock.time
    
    @property
    def start_time(self) -> float:
        return self._source.display_time

    @property
    def display_time(self) -> float:
        return self._source.play_clock.time - self._source.display_time
    
    @property
    def next_prompt(self):
        if self._source.next_game is None:
            return ""
        return self._source.next_game.prompt

    @property
    def next_controls(self):
        if self._source.next_game is None:
            return ""
        return self._source.next_game.controls
    

class PlayView(ArcadeView):
    
    def __init__(self, games: tuple[type[Game], ...], transitions: tuple[type[Transition], ...]):
        ArcadeView.__init__(self)
        # Store the cursor position incase either the Game or Transition want to use it.
        self._cursor_position: tuple[float, float] = (0.0, 0.0)

        self.count = 0  # number of games played
        self.speed = 0  # speedups
        self.strikes = 0  # number of games failed

        # The active display is the type indifferent version of active game and counter
        # do we need both? maybe not, but keeping them seperate gives us more control.
        self._active_display: Display | None = None
        self._active_game: Game | None = None
        self._next_game: Game | None = None
        self._active_transition: Transition | None = None
        
        # If the active game has succeeded or not. If it's none then the game isn't
        # over. Otherwise it tells us how the game is over.
        self.active_game_succeeded: bool | None = None
        
        # Time the current display got shown.
        self.display_time: float = 0.0
        # The clock that gets faster and faster.
        self.play_clock: Clock = Clock(0.0, 0, 1.0)

        # The last game's success duration. If this is None then the transition shows
        # the success/fail. However if it is > 0.0 then the game view does.
        self.success_duration: float | None = None

        # A read only view of the PlayView.
        self.state: PlayState = PlayState(self)

        # The list of possible games/counters to pick from
        self._games: tuple[Game, ...] = tuple(game.create(self.state) for game in games)
        self._transitions: tuple[Transition, ...] = tuple(transition.create(self.state) for transition in transitions)

        # Whether or not to use bags to pick which game/transition to use.
        self._pick_games_bagged: bool = False
        self._game_bag: list[Game] = list(self._games)
        self._pick_transitions_bagged: bool = False
        self._transition_bag: list[Transition] = list(self._transitions)

    @property
    def cursor_position(self):
        return self._cursor_position

    @property
    def active_display(self) -> Display | None:
        return self._active_display
    
    @property
    def active_transition(self) -> Transition | None:
        return self._active_transition
    
    @property
    def next_game(self) -> Game | None:
        return self._next_game
    
    @property
    def active_game(self) -> Game | None:
        return self._active_game

    def on_show_view(self) -> None:
        # TODO: fix this cludge. To skip the first success screen we act as though the 'previous game' shows the success/fail.
        self.success_duration = 1.0 
        self.next_displayable()

    def next_displayable(self):
        # First time we call this method is when the view is shown so we need to pick
        # the next game. Could this be done in a setup method?
        if self._next_game is None:
            self._next_game = self.pick_game()

        if self._active_transition is None or self._active_display is None:
            # show transition as either the first display, or after a game.
            transition = self.pick_transition()
            self._active_game = None # TODO: do we need a cleanup function?
            self._active_transition = self._active_display = transition
        elif self._active_game is None:
            # Show a game after a transition.
            if self.state.is_speedup:
                # This works because we:
                # iterate the count -> move to transition -> speed up -> move to game
                self.speedup_game()
            self._active_transition = None
            self._active_game = self._active_display = self._next_game
            self.success_duration = self._active_game.success_duration
            self._next_game = self.pick_game()
            # setup the next display.
        self.display_time = self.play_clock.time
        self._active_display.setup()
        
        # ! this assumes one of the two cases above occured. It shouldn't be possible
        # ! for this to not be true, but i'm leaving this note incase weirdness.
        
    def pick_transition(self) -> Transition:
        shuffle(self._transition_bag)
        transition = self._transition_bag[-1]
        if not self._pick_transitions_bagged:
            return transition
        self._transition_bag.pop()
        if not self._transition_bag:
            self._transition_bag = list(self._transitions)
        return transition

    def pick_game(self) -> Game:
        shuffle(self._game_bag)
        game = self._game_bag[-1]
        if not self._pick_games_bagged:
            return game
        self._game_bag.pop()
        if not self._game_bag:
            self._game_bag = list(self._games)
        return game

    def game_succeeded(self, succeeded: bool):
        if not self._active_game:
            return
        
        self.active_game_succeeded = succeeded

    def speedup_game(self):
        self.play_clock.set_tick_speed(1.0 + self.speed * SPEED_INCREASE_STEP_SIZE)

    def on_update(self, delta_time: float) -> bool | None:
        self.play_clock.tick(delta_time)
        if self._active_game is not None:
            self.update_game(self.play_clock.delta_time)
            return
        elif self._active_transition is not None:
            self.update_transition(self.play_clock.delta_time)
            return

    def update_game(self, delta_time: float):
        if self._active_game is None:
            raise ValueError('There is no active game to update.')

        if self.state.display_time >= self._active_game.duration:
            self._active_game.on_time_runout(self.state)

        overtime = False
        if self._active_game.success_duration:
            overtime = self.state.display_time - self._active_game.duration < self._active_game.success_duration

        if self.active_game_succeeded is not None and not overtime:
            if not self.active_game_succeeded:
                self.strikes += 1
            if self.strikes >= MAX_STRIKE_COUNT:
                # The play session is finished.
                raise ValueError('YOU FAILEDDDD!!!!!! todo a real end to the game.')
                return
            self.count += 1
            self.next_displayable()
            # the game is finsihed
            return
        
        self._active_game.update(delta_time)

    def update_transition(self, delta_time: float):
        if self._active_transition is None:
            raise ValueError('There is no active trasition to update.')
        
        if self.state.display_time >= self._active_transition.duration:
            self.next_displayable()
            return

        self._active_transition.update(delta_time)

    def on_draw(self) -> bool | None:
        self.clear()
        if self.active_display:
            self.active_display.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if self.active_game is None:
            return
        self.active_game.on_input(symbol, modifiers, True)

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        if self.active_game is None:
            return
        self.active_game.on_input(symbol, modifiers, False)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        self._cursor_position = (x, y)
        if self.active_game is None:
            return
        self.active_game.on_input(button, modifiers, True)
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        self._cursor_position = (x, y)
        if self.active_game is None:
            return
        self.active_game.on_input(button, modifiers, False)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        self._cursor_position = (x, y)
        if self.active_game is None:
            return
        self.active_game.on_cursor_motion(x, y, dx, dy)