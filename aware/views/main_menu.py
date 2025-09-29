from arcade import View as ArcadeView, LRBT

from aware.graphics.gradient import Gradient
from aware.graphics.wave import Wave
import aware.graphics.style as style

class MainMenuView(ArcadeView):

    def __init__(self) -> None:
        super().__init__()
        self.gradient = Gradient(self.window.rect, ((0.0, style.MENU_LIGHT), (0.5, style.MENU_MIDDLE), (1.0, style.MENU_DARK)), vertical=True)
        self.wave_1 = Wave(LRBT(0, self.width, 0, 215), 110, 1300, 14.3, 0.0, style.MENU_YELLOW, Wave.TOP_FACE, 3)
        self.wave_2 = Wave(LRBT(0, self.width, 0, 290), 135, 2000, 10.0, 0.0, style.MENU_YELLOW, Wave.TOP_FACE, 3)

    def on_draw(self) -> bool | None:
        self.clear()
        self.gradient.draw()
        self.wave_1.time = self.wave_2.time = self.window.time
        self.wave_1.draw()
        self.wave_2.draw()
