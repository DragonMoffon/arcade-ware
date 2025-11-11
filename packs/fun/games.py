from __future__ import annotations

import arcade

from engine.play import ContentFlag, PlayState, Game
from engine.resources import get_sound, get_sprite

class ShooterGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "SHOOT!", controls = "default.inputs.mouse",
                         duration = 3.0, flags = ContentFlag.NONE)
        
        self.sky = get_sprite("fun.gun.sky")
        self.wood = get_sprite("fun.gun.wood")

        self.sky.center_x, self.sky.center_y = self.window.center
        self.wood.center_x, self.wood.center_y = self.window.center
        self.wood.bottom = 0

        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.sky)
        self.sprite_list.append(self.wood)
    
    def start(self):
        ...

    def finish(self):
        ...

    def draw(self):
        self.sprite_list.draw()

    def update(self, delta_time: float):
        ...

    def on_time_runout(self):
        self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        ...

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        ...
