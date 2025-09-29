from __future__ import annotations

import arcade

from aware.anim import bounce
from engine.play import PlayState, Game
from engine.resources import get_sound, get_sprite

from .lib import noa

class DoNothingGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "DO NOTHING!", controls = "default.inputs.nothing", duration = 6.0)
        self.sprites = [
            get_sprite("digi.donothing.3", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.2", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.1", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.stop", self.window.center_x, self.window.center_y)
        ]

        self.party_noise = get_sound("digi.donothing.party")
        self.stop_noise = get_sound("digi.donothing.night")

        self.party_player = None
        self.stop_player = None

    @property
    def current_sprite(self) -> arcade.Sprite:
        return self.sprites[min(3, int(self.state.display_time))]
    
    @property
    def current_hue(self) -> int:
        return int(self.state.display_time * 4) % 12
    
    def start(self):
        self.party_player = self.party_noise.play(speed = self.state.tick_speed)
        self.stop_player = self.stop_noise.play()
        self.stop_player.pause()

    def finish(self):
        self.party_player.delete()
        self.stop_player.delete()

    def draw(self):
        if self.state.display_time < 3:
            arcade.draw_rect_filled(self.window.rect, noa.get_color(self.current_hue, 8, 8))
        arcade.draw_sprite(self.current_sprite)

    def update(self, delta_time: float):
        if self.state.display_time < 3:
            self.current_sprite.center_y = bounce(self.window.center_y, self.window.center_y + 50, 60, self.state.display_time)
            self.current_sprite.color = noa.get_color((self.current_hue + 6) % 12, 4, 8)
        else:
            self.party_player.pause()
            self.stop_player.play()

    def on_time_runout(self):
        self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if self.state.display_time > 3:
            self.fail()

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        if self.state.display_time > 3:
            self.fail()

# Game that just stalls the app
"""
class EmulateStallGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "STALL!", controls = "default.inputs.nothing", duration = 120.0)
        ...
    
    def start(self):
        ...

    def finish(self):
        ...

    def draw(self):
        ...

    def update(self, delta_time: float):
        ...

    def on_time_runout(self):
        self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        ...

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        ...
"""
