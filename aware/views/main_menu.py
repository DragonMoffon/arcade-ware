from arcade import SpriteList, View as ArcadeView, LRBT
from arcade.clock import GLOBAL_CLOCK, Clock

from aware.anim import lerp, ease_quadout, perc
from aware.data.loading import load_sprite
from aware.graphics.gradient import Gradient
from aware.graphics.wave import Wave
import aware.graphics.style as style

SMALL_WAVE_SPEED = 14.3
BIG_WAVE_SPEED = 10.0
SPEEDUP = 8.0
SPEED_TIME = 2.0
FOREVER = float("inf")

class MainMenuView(ArcadeView):

    def __init__(self) -> None:
        super().__init__()
        self.gradient = Gradient(self.window.rect, ((0.0, style.MENU_LIGHT), (0.5, style.MENU_MIDDLE), (1.0, style.MENU_DARK)), vertical=True)
        self.wave_1 = Wave(LRBT(0, self.width, 0, 215), 110, 1300, SMALL_WAVE_SPEED, 0.0, style.MENU_YELLOW, Wave.TOP_FACE, 3)
        self.wave_2 = Wave(LRBT(0, self.width, 0, 290), 135, 2000, BIG_WAVE_SPEED, 0.0, style.MENU_YELLOW, Wave.TOP_FACE, 3)

        self.spritelist = SpriteList()

        self.logo = load_sprite("logo")
        self.logo.position = (self.window.center_x, self.window.height * 0.66)
        self.play_button = load_sprite("press")
        self.play_button.position = (self.window.center_x, self.window.height * 0.33)

        self.spritelist.append(self.logo)
        self.spritelist.append(self.play_button)

        self.wave_clock = Clock()

        self.click_time = FOREVER

    def progress(self) -> None:
        self.click_time = GLOBAL_CLOCK.time

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.progress()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.progress()

    def on_update(self, delta_time) -> None:
        self.wave_clock.tick(delta_time)
        self.play_button.alpha = 255 if (int(self.wave_clock.time) % 2 == 0) else 0
        self.wave_clock.set_tick_speed(ease_quadout(SPEEDUP, 1, perc(self.click_time, self.click_time + SPEED_TIME, GLOBAL_CLOCK.time)))

    def on_draw(self) -> None:
        self.clear()
        self.gradient.draw()
        self.wave_1.time = self.wave_2.time = self.wave_clock.time
        self.wave_1.draw()
        self.wave_2.draw()
        self.spritelist.draw()
