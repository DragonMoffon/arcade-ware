from __future__ import annotations

import arcade

from aware.anim import ease_quadout, perc
from aware.graphics import style
from aware.graphics.gradient import Gradient
from aware.graphics.wave import Wave
from engine.play import PlayState, Transition
from engine.resources import get_sprite

SHADOW_DISTANCE = 3

class DefaultTransition(Transition):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, 3.0)
        self.gradient = Gradient(self.window.rect, ((0.0, style.MENU_LIGHT), (0.5, style.MENU_MIDDLE), (1.0, style.MENU_DARK)), vertical=True)
        self.wave_1 = Wave(arcade.LRBT(0, self.window.width, 0, 215), 110, 1300, style.SMALL_WAVE_SPEED, 0.0, style.MENU_YELLOW, Wave.TOP_FACE, 3)
        self.wave_2 = Wave(arcade.LRBT(0, self.window.width, 0, 290), 135, 2000, style.BIG_WAVE_SPEED, 0.0, style.MENU_YELLOW, Wave.TOP_FACE, 3)

        self.text = arcade.Text("", self.state.screen_width/2.0, self.state.screen_height/4.0, anchor_x="center", anchor_y="center",
                                font_size = 24, font_name = "A-OTF Shin Go Pro", bold = True)
        self.text_shadow = arcade.Text("", self.state.screen_width/2.0 + SHADOW_DISTANCE, self.state.screen_height/4.0 - SHADOW_DISTANCE, anchor_x="center", anchor_y="center",
                                       font_size = 24, font_name = "A-OTF Shin Go Pro", bold = True, color = arcade.color.BLACK.replace(a = 128))
        
        self.heart_1 = get_sprite("default.heart")
        self.heart_2 = get_sprite("default.heart")
        self.heart_3 = get_sprite("default.heart")
        self.heart_4 = get_sprite("default.heart")

        for s in [self.heart_1, self.heart_2, self.heart_3, self.heart_4]:
            s.scale = 0.75
            s.top = self.window.rect.top - 20

        self.heart_1.left = self.window.rect.left + 20
        self.heart_2.left = self.heart_1.right + 30
        self.heart_4.right = self.window.rect.right - 20
        self.heart_3.right = self.heart_4.left - 30

        self.text2 = arcade.Text("", self.state.screen_width/2.0, self.heart_1.center_y, anchor_x="center", anchor_y="center",
                                 font_size = 48, font_name = "A-OTF Shin Go Pro", bold = True)
        self.text2_shadow = arcade.Text("", self.state.screen_width/2.0 + SHADOW_DISTANCE, self.heart_1.center_y - SHADOW_DISTANCE, anchor_x="center", anchor_y="center",
                                        font_size = 48, font_name = "A-OTF Shin Go Pro", bold = True, color = arcade.color.BLACK.replace(a = 128))
    
    def update(self, delta_time: float):
        self.wave_1.time = self.wave_2.time = self.state.total_time
        alpha = int(ease_quadout(0, 128, perc(0, 1, self.time)))
        self.wave_1.color = (*self.wave_1.color[0:3], int(alpha))
        self.wave_2.color = (*self.wave_2.color[0:3], int(alpha))

        if self.state.is_speedup and self.state.display_time >= 2.0:
            text = f"SPEEDUP! ({round(self.state.tick_speed, 2)}x)"
        elif self.state.has_game_finished:
            text = "WELL DONE!" if self.state.has_game_succeeded else "YOU FAILED."
        else:
            text = ""
        self.text.text = text
        self.text2.text = f"{self.state.count}"

        self.text_shadow.text = self.text.text
        self.text2_shadow.text = self.text2.text

    def draw(self):
        self.gradient.draw()
        self.wave_1.draw()
        self.wave_2.draw()
        self.text_shadow.draw()
        self.text2_shadow.draw()
        self.text.draw()
        self.text2.draw()

        for h in [self.heart_1, self.heart_2, self.heart_3, self.heart_4][:self.state.lives_remaining]:
            arcade.draw_sprite(h)
