from __future__ import annotations

import arcade

from engine.play import PlayState, Game
from engine.resources import get_sprite

class DoNothingGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "DO NOTHING!", controls = "default.inputs.nothing", duration = 6.0)
        self.sprites = [
            get_sprite("digi.donothing.3", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.2", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.1", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.stop", self.window.center_x, self.window.center_y)
        ]
    
    def start(self):
        ...

    def finish(self):
        ...

    def draw(self):
        arcade.draw_sprite(self.sprites[min(3, int(self.state.display_time))])

    def update(self, delta_time: float):
        ...

    def on_time_runout(self):
        self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if self.state.display_time > 3:
            self.fail()

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        if self.state.display_time > 3:
            self.fail()
