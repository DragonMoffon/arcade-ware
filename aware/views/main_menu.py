from arcade import View as ArcadeView

from aware.graphics.gradient import Gradient
import aware.graphics.style as style

class MainMenuView(ArcadeView):

    def __init__(self) -> None:
        super().__init__()
        self.gradient = Gradient(self.window.rect, ((0.0, style.MENU_LIGHT), (0.5, style.MENU_MIDDLE), (1.0, style.MENU_DARK)), vertical=True)

    def on_draw(self) -> bool | None:
        self.clear()
        self.gradient.draw()