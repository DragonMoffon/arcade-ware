from arcade import Text, draw_text

from aware.graphics import style
from aware.graphics.gradient import Gradient
from engine.play import Fail, PlayState

class DefaultFail(Fail):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state)
        self.gradient = Gradient(self.window.rect, ((0.0, style.FAIL_LIGHT), (0.5, style.FAIL_MIDDLE), (1.0, style.FAIL_DARK)), vertical=True)  # noqa: F821
        self.text = Text("GAME OVER", self.window.center_x, self.window.center_y, anchor_x="center", anchor_y="center",
                                      font_size = 72, font_name = "A-OTF Shin Go Pro", bold = True)
        self.text2 = Text("PRESS ANY KEY TO RESTART", self.window.center_x, self.text.bottom - 15, anchor_x="center", anchor_y="top",
                                                      font_size = 32, font_name = "A-OTF Shin Go Pro", bold = True)

    def draw(self):
        self.gradient.draw()
        self.text.draw()
        self.text2.draw()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if pressed:
            self.restart()
