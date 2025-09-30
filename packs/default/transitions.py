from __future__ import annotations

import arcade

from aware.graphics import style
from aware.graphics.gradient import Gradient
from engine.play import PlayState, Transition
    
class DefaultTransition(Transition):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, 3)
        self.gradient = Gradient(self.window.rect, ((0.0, style.MENU_LIGHT), (0.5, style.MENU_MIDDLE), (1.0, style.MENU_DARK)), vertical=True)
        self.text = arcade.Text("", self.state.screen_width/2.0, self.state.screen_height/2.0, anchor_x="center", anchor_y="center", font_size = 24, font_name = "A-OTF Shin Go Pro", bold = True)
    
    def draw(self):
        self.gradient.draw()
        if self.state.display_time <= 1.0 and self.state.has_game_finished:
            text = "WELL DONE!" if self.state.has_game_succeeded else "YOU FAILED."
        elif self.state.is_speedup and self.state.display_time >= 2.0:
            text = f"SPEEDUP!!! ({self.state.tick_speed:.2f}x)"
        else:
            text = "TRANSITION..."
        self.text.text = f"{text} GAME: {self.state.count}, FAILED: {self.state.strikes}"
        self.text.draw()
