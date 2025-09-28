from __future__ import annotations

import arcade

from engine.play import PlayState, Transition
    
class DefaultTransition(Transition):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, 3)
        self.text = arcade.Text("", self.state.screen_width/2.0, self.state.screen_height/2.0, anchor_x="center", anchor_y="center")
    
    def draw(self):
        if self.state.display_time <= 1.0 and self.state.has_game_finished:
            text = "WELLDONE" if self.state.has_game_succeeded else "YOU FAILED"
        elif self.state.is_speedup and self.state.display_time >= 2.0:
            text = "SPEEDUP!!!"
        else:
            text = "TRANSITION"
        self.text.text = f"{text}! GAME: {self.state.count}, FAILED: {self.state.strikes}"
        self.text.draw()
