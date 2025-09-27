from typing import Self
from engine.play import Fail, PlayState

from arcade import draw_text

class DefaultFail(Fail):
    
    @classmethod
    def create(cls, state: PlayState) -> Self:
        return cls(state)
    
    def draw(self):
        draw_text(
            'YOU FAILED: click to restart',
            self.state.screen_width/2,
            self.state.screen_height/2,
            anchor_x='center',
            anchor_y='center'
        )

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if pressed:
            self.restart()
