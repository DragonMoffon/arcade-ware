from __future__ import annotations

import arcade

from engine.play import PlayState, Game, Transition
from engine.resources import get_sound

class ShakeEmUp(Game):
    
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "SHAKE!", controls = "move_mouse", duration = 4.0, success_duration = None)
        self.box = arcade.SpriteSolidColor(100, 100, self.state.screen_width / 2, self.state.screen_height / 2)
        self.text = arcade.Text("0 SHAKES!", self.state.screen_width / 2, 100, anchor_x='center', anchor_y='center')
        self.dragging: bool = False
        self.sep: tuple[float, float] = (0.0, 0.0)
        self.shakes: int = 0
        self.shake_goal: int = 30
        self.motion_dir: tuple[float, float] | None = None
        self.sound = get_sound('default.growth')
        self.player = None

    @classmethod
    def create(cls, state: PlayState) -> ShakeEmUp:
        return ShakeEmUp(state)
    
    def start(self):
        self.box.position = self.state.screen_width / 2, self.state.screen_height / 2
        self.dragging = False
        self.sep = (0.0, 0.0)
        self.shakes = 0
        self.shake_goal = 30
        self.motion_dir = None
        self.player = self.sound.play(0.0) # Setting the speed does nothing?

    def finish(self):
        if self.player is not None:
            self.player.delete()
            self.player = None
    
    def draw(self):
        self.text.text = f"{self.shakes} SHAKES!"
        p = self.shakes / self.shake_goal
        c = int(255 * max(0.0, 1.0 - p))
        self.text.color = (255, c, c)
        self.text.font_size = 12 * (1 - p) + p * 36
        self.text.draw()
        arcade.draw_sprite(self.box)

    def update(self, delta_time: float):
        if self.player is not None:
            self.player.volume = min(1.0, self.shakes / self.shake_goal)

    def on_time_runout(self, state: PlayState):
        if self.shakes >= self.shake_goal:
            self.succeed()
            return
        self.fail()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if arcade.MOUSE_BUTTON_LEFT == symbol:
            self.dragging = pressed
            pos = self.state.cursor_position
            self.sep = self.box.center_x - pos[0], self.box.center_y - pos[1]

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        if self.dragging:
            self.box.position = x + self.sep[0], y + self.sep[1]
            if self.motion_dir is None:
                self.motion_dir = dx, dy
            else:
                diff = dx * self.motion_dir[0] + dy * self.motion_dir[1]
                if diff < 0.0:
                    # The motion of the mouse has switched so we have shaken once.
                    self.shakes += 1
                    self.motion_dir = dx, dy
    
class DefaultTransition(Transition):

    def __init__(self, state: PlayState) -> None:
        super().__init__(state, 3)
        self.text = arcade.Text("", self.state.screen_width/2.0, self.state.screen_height/2.0, anchor_x="center", anchor_y="center")

    @classmethod
    def create(cls, state: PlayState) -> DefaultTransition:
        return DefaultTransition(state)
    
    def draw(self):
        if self.state.show_transition_success and self.state.display_time <= 1.0:
            text = "WELLDONE" if self.state.has_game_succeeded else "YOU FAILED"
        elif self.state.is_speedup and self.state.display_time >= 2.0:
            text = "SPEEDUP!!!"
        else:
            text = "TRANSITION"
        self.text.text = f"{text}! GAME: {self.state.count}, FAILED: {self.state.strikes}"
        self.text.draw()
