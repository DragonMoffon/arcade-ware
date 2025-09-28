from __future__ import annotations

import arcade

from engine.play import PlayState, Game

class TemplateGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "PROMPT", controls = "default.inputs.nothing", duration = 4.0, success_duration = None)
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
