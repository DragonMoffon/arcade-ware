from __future__ import annotations
from enum import Flag, auto
from typing import Self
from random import shuffle, choice

from arcade import Vec2, Text, Sprite, View as ArcadeView, draw_sprite
import arcade
from arcade.clock import Clock

from engine.resources import get_texture

from aware.bar import TimeBar

MAX_STRIKE_COUNT = 4
SPEED_INCREASE_GAME_COUNT = 5
SPEED_INCREASE_STEP_SIZE = 0.1
COUNTDOWN_TIME = 3
PROMPT_START = 1.0
PROMPT_END = 0.5
CONTROL_START = 1.0
CONTROL_END = 0.5
STALL_TIME = 60

class ContentFlag(Flag):
    NONE = 0
    PHOTOSENSITIVE = auto()
    EXTREME_MOTION = auto()
    COLORBLIND = auto()
    REQUIRES_AUDIO = auto()
    REQUIRES_TYPING = auto()
    JUMPSCARE = auto()

class Display:
    # TODO: seperate the game state from the game view
    def __init__(self, state: PlayState, duration: float) -> None:
        self.state: PlayState = state
        self._duration: float = duration

        # Store the window for fun and profit
        self.window = arcade.get_window()

    @property
    def time(self) -> float:
        """The time this display has been shown for."""
        return self.state.display_time
    
    @property
    def remaining_time(self) -> float:
        """The time until this display ends (may be infinite)."""
        return self.state.remaining_time
    
    @property
    def tick_speed(self) -> float:
        """The current tick speed as a multiplier."""
        return self.state.tick_speed

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        pass

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        pass

    @property
    def duration(self):
        return self._duration
    
    @classmethod
    def create(cls, state: PlayState) -> Self:
        raise NotImplementedError()

    def start(self):
        pass

    def finish(self):
        pass

    def draw(self):
        pass

    def update(self, delta_time: float):
        pass

class Transition(Display):
    @classmethod
    def create(cls, state: PlayState) -> Self:
        return cls(state)  # type: ignore -- signature thing

class Game(Display):
    def __init__(self, state: PlayState, prompt: str, controls: str, duration: float, flags: ContentFlag = ContentFlag.NONE, boss: bool = False) -> None:
        super().__init__(state, duration)
        # The text prompt for the transition to show, and the id of the control image to show.
        self.prompt: str = prompt
        self.controls: str = controls
        self.flags = flags
        self.boss = boss

    @classmethod
    def create(cls, state: PlayState) -> Self:
        return cls(state) # type: ignore -- This is going to be mad at us because Game subclasses have a different constructor

    def succeed(self):
        self.state.set_game_succeeded(True)

    def fail(self):
        self.state.set_game_succeeded(False)

    def on_time_runout(self):
        self.fail()

    def has_content_flag(self, flag: ContentFlag) -> bool:
        return bool(self.flags | flag)

# TODO
class Fail(Display):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, float('inf'))

    @classmethod
    def create(cls, state: PlayState) -> Self:
        return cls(state)

    def restart(self):
        self.state.reset_play()

    def quit(self):
        self.state.quit_play()

class PlayState:
    
    def __init__(self, source: PlayView) -> None:
        self._source: PlayView = source

    @property
    def cursor_position(self):
        # Position of the mouse cursor on screen
        return self._source.cursor_position
    
    @property
    def screen_width(self):
        # Screen width (may eventually not be the whole screen if there are frames)
        return self._source.width
    
    @property
    def screen_height(self):
        # Screen height (may eventually not be the whole screen if there are frames)
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
        # How many game's have been failed
        return self._source.strikes
    
    @property
    def tick_speed(self) -> float:
        return self._source.tick_speed
    
    @property
    def has_play_finished(self) -> bool:
        return self._source.play_over
    
    @property
    def max_strikes(self) -> int:
        return MAX_STRIKE_COUNT

    @property
    def lives_remaining(self) -> int:
        return self.max_strikes - self.strikes

    @property
    def on_last_life(self) -> bool:
        # Utill bool to check for last life
        return self._source.strikes == MAX_STRIKE_COUNT - 1
    
    @property
    def has_game_finished(self) -> bool:
        # has the game currently playing or just played finish?
        return self._source.active_game_succeeded is not None
    
    @property
    def has_game_succeeded(self) -> bool | None:
        # was the game currently playing or just played won?
        return self._source.active_game_succeeded
    
    def set_game_succeeded(self, succeeded: bool):
        # Finish the current game and say wether it is done.
        self._source.game_succeeded(succeeded)

    def reset_play(self):
        self._source.restart()

    def quit_play(self):
        self._source.quit()
    
    @property
    def is_speedup(self) -> bool:
        # Is the next game a speedup?
        return self._source.count != 0 and self._source.count % SPEED_INCREASE_GAME_COUNT == 0
    
    @property
    def total_time(self) -> float:
        # Total amount of time the current session has been running
        return self._source.play_clock.time
    
    @property
    def start_time(self) -> float:
        # The time that the current display was shown
        return self._source.display_time

    @property
    def display_time(self) -> float:
        # The time elapsed since the current display was shown
        return self._source.play_clock.time - self._source.display_time
    
    @property
    def remaining_time(self) -> float:
        # The time left for the current game
        if self._source.active_display is None:
            return float('inf')
        return self._source.active_display.duration - (self._source.play_clock.time - self._source.display_time)

    @property
    def next_prompt(self):
        # What is the prompt for the next game
        if self._source.next_game is None:
            return ""
        return self._source.next_game.prompt

    @property
    def next_controls(self):
        # what are the controls for the next game
        if self._source.next_game is None:
            return ""
        return self._source.next_game.controls
    

class PlayView(ArcadeView):
    
    def __init__(self, games: tuple[type[Game], ...], transitions: tuple[type[Transition], ...], fails: tuple[type[Fail], ...],
                 filter: list[str] = []):
        ArcadeView.__init__(self)
        # Store the cursor position incase either the Game or Transition want to use it.
        self._cursor_position: tuple[float, float] = (0.0, 0.0)

        self.count = 0  # number of games played
        self.speed = 0  # speedups
        self.tick_speed = 1.0 # Actual speed scalar
        self.strikes = 0  # number of games failed

        # The play is over so let's show the FailDisplay
        self.play_over: bool = False

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

        # A read only view of the PlayView.
        self.state: PlayState = PlayState(self)

        # The list of possible games/counters to pick from
        self._games: tuple[Game, ...] = tuple(game.create(self.state) for game in games)
        self._transitions: tuple[Transition, ...] = tuple(transition.create(self.state) for transition in transitions)
        self._fails: tuple[Fail, ...] = tuple(fail.create(self.state) for fail in fails)

        if filter:
            self._games = tuple([g for g in self._games if g.__class__.__name__ in filter])

        # Whether or not to use bags to pick which game/transition to use.
        self._pick_games_bagged: bool = True
        self._game_bag: list[Game] = list(self._games)
        self._pick_transitions_bagged: bool = False
        self._transition_bag: list[Transition] = list(self._transitions)

        self.remaining_bar = TimeBar(Vec2(0, 0))
        self.remaining_bar.position = Vec2(self.width, self.remaining_bar.back_sprite.height)
        self.control_icon = Sprite(None, center_x=self.center_x, center_y=self.center_y + 30)
        self.prompt_text = Text('PROMPT!', self.center_x, self.center_y - 30, anchor_x = "center", anchor_y = "top", font_size = 48, font_name = "A-OTF Shin Go Pro", bold = True)

        self.stall_text = Text("We think the game might have stalled... press [END] to skip!", 5, 5, anchor_x = "left", anchor_y = "bottom", font_size = 11, font_name = "A-OTF Shin Go Pro")

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
        self.next_displayable()

    def next_displayable(self):
        # First time we call this method is when the view is shown so we need to pick
        # the next game. Could this be done in a setup method?
        if self._next_game is None:
            self._next_game = self.pick_game()

        if self._active_display is not None:
            self._active_display.finish()
        self._active_display

        if self.play_over:
            self._active_game = self._active_transition = None
            self._active_display = self.pick_fail()
        elif self._active_transition is None and self._active_transition is None:
            # show transition as either the first display, or after a game.
            transition = self.pick_transition()
            self._active_game = None
            self._active_transition = self._active_display = transition
            self.prompt_text.text = self._next_game.prompt
            self.control_icon.texture = get_texture(self._next_game.controls)
            self.control_icon.size = (128, 128)
        else:
            # Show a game after a transition.
            if self.state.is_speedup:
                # This works because we:
                # iterate the count -> move to transition -> speed up -> move to game
                self.speedup_game()
            self._active_transition = self.active_game_succeeded = None
            self._active_game = self._active_display = self._next_game
            self._next_game = self.pick_game()
            # setup the next display.
        self.display_time = self.play_clock.time
        self._active_display.start()
        
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
    
    def pick_fail(self) -> Fail:
        return choice(self._fails)

    def game_succeeded(self, succeeded: bool):
        if not self._active_game:
            return
        
        self.active_game_succeeded = succeeded

    def restart(self):
        # Store the cursor position incase either the Game or Transition want to use it.
        self._cursor_position: tuple[float, float] = (0.0, 0.0)

        self.count = 0  # number of games played
        self.speed = 0  # speedups
        self.tick_speed = 1.0 # Actual speed scalar
        self.strikes = 0  # number of games failed

        # The play is over so let's show the FailDisplay
        self.play_over: bool = False

        if self._active_display is not None:
            self._active_display.finish()

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

        # Whether or not to use bags to pick which game/transition to use.
        self._pick_games_bagged: bool = True
        self._game_bag: list[Game] = list(self._games)
        self._pick_transitions_bagged: bool = False
        self._transition_bag: list[Transition] = list(self._transitions)

        self.next_displayable()

    def quit(self):
        self.window.close()

    def play_failed(self):
        self.play_over = True
        self.next_displayable()

    def speedup_game(self):
        self.speed += 1
        self.tick_speed = 1.0 + self.speed * SPEED_INCREASE_STEP_SIZE
        self.play_clock.set_tick_speed(self.tick_speed)

    def on_update(self, delta_time: float) -> bool | None:
        self.play_clock.tick(delta_time)
        if self._active_game is not None:
            self.update_game(self.play_clock.delta_time)
            self.remaining_bar.percentage = min(1, self.state.remaining_time / COUNTDOWN_TIME)
            return
        elif self._active_transition is not None:
            self.update_transition(self.play_clock.delta_time)
            return

    def update_game(self, delta_time: float):
        if self._active_game is None:
            raise ValueError('There is no active game to update.')

        # TODO: this will be called every frame after the game is technically finished which we don't want.
        if self.state.display_time >= self._active_game.duration:
            self._active_game.on_time_runout()

        if self.active_game_succeeded is not None:
            if not self.active_game_succeeded:
                self.strikes += 1
            self.count += 1
            if self.strikes >= MAX_STRIKE_COUNT:
                # The play session is finished.
                self.play_failed()
                return
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
        if self._active_display:
            self._active_display.draw()
        if self._active_game and self.state.remaining_time <= COUNTDOWN_TIME:
            self.remaining_bar.draw()

        if (self._active_transition and self.state.remaining_time <= CONTROL_START) or (self._active_game and self.state.display_time <= CONTROL_END):
            draw_sprite(self.control_icon, pixelated = True)

        if (self._active_transition and self.state.remaining_time <= PROMPT_START) or (self._active_game and self.state.display_time <= PROMPT_END):
            self.prompt_text.draw()

        if self._active_display and self._active_display.state.display_time > STALL_TIME:
            self.stall_text.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if self._active_display is None:
            return
        self._active_display.on_input(symbol, modifiers, True)

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        if self._active_display is None:
            return
        self._active_display.on_input(symbol, modifiers, False)
        if self._active_display.state.display_time > STALL_TIME and symbol == arcade.key.END:
            self.next_displayable()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        self._cursor_position = (x, y)
        if self._active_display is None:
            return
        self._active_display.on_input(button, modifiers, True)
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        self._cursor_position = (x, y)
        if self._active_display is None:
            return
        self._active_display.on_input(button, modifiers, False)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        self._cursor_position = (x, y)
        if self._active_display is None:
            return
        self._active_display.on_cursor_motion(x, y, dx, dy)
