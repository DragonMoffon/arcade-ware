from __future__ import annotations

import arcade

from engine.play import PlayState, Game, Transition


class ShakeEmUp(Game):
    
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "SHAKE!", controls = "move_mouse", duration = 10.0, success_duration = None)

    @classmethod
    def create(cls, state: PlayState) -> ShakeEmUp:
        return ShakeEmUp(state)
    
class DefaultTransition(Transition):

    def __init__(self, state: PlayState) -> None:
        super().__init__(state, 10.0)

    @classmethod
    def create(cls, state: PlayState) -> DefaultTransition:
        return DefaultTransition(state)
    
    def draw(self):
        if self.state.show_transition_success and self.state.display_time <= 2.0:
            text = "WELLDONE" if self.state.game_succeeded else "YOU FAILED"
        elif self.state.is_speedup and self.state.display_time >= 8:
            text = "SPEEDUP!!!"
        else:
            text = "TRANSITION"
        arcade.draw_text(f"{text}! GAME: {self.state.count}, FAILED: {self.state.strikes}", self.state.screen_width/2.0, self.state.screen_height/2.0, anchor_x="center", anchor_y="center")
