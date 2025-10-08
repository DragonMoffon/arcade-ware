from __future__ import annotations

from random import random
from math import copysign

import arcade

from engine.play import PlayState, Game
from engine.resources import get_sound

class ShakeEmUp(Game):
    
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "SHAKE!", controls = "default.inputs.mouse_move", duration = 4.0)
        self.box = arcade.SpriteSolidColor(100, 100, self.state.screen_width / 2, self.state.screen_height / 2)
        self.text = arcade.Text("0 SHAKES!", self.state.screen_width / 2, 100, anchor_x='center', anchor_y='center', font_size = 26, font_name = "A-OTF Shin Go Pro")
        self.dragging: bool = False
        self.sep: tuple[float, float] = (0.0, 0.0)
        self.shakes: int = 0
        self.shake_goal: int = 30
        self.motion_dir: tuple[float, float] | None = None
        self.sound = get_sound('default.growth')
        self.player = None
    
    def start(self):
        self.box.position = self.state.screen_width / 2, self.state.screen_height / 2
        self.dragging = False
        self.sep = (0.0, 0.0)
        self.shakes = 0
        self.shake_goal = 30
        self.motion_dir = None
        self.player = self.sound.play(0.0, speed=self.state.tick_speed)
        self.text.text = "0 SHAKES!"
        self.text.color = arcade.color.WHITE

    def finish(self):
        if self.player is not None:
            self.player.delete()
            self.player = None
    
    def draw(self):
        self.text.draw()
        arcade.draw_sprite(self.box)

    def update(self, delta_time: float):
        if self.player is not None:
            self.player.volume = min(1.0, self.shakes / self.shake_goal)

    def on_time_runout(self):
        if self.shakes >= self.shake_goal:
            self.succeed()
            return
        self.fail()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if arcade.MOUSE_BUTTON_LEFT == symbol:
            if self.box.collides_with_point(self.state.cursor_position) and pressed:
                self.dragging = True
            elif not pressed:
                self.dragging = False
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
                    self.text.text = f"{self.shakes} SHAKES!"
                    p = self.shakes / self.shake_goal
                    c = int(255 * max(0.0, 1.0 - p))
                    self.text.color = (255, c, c) if self.shakes < self.shake_goal else (0, 255, 0)
                    # self.text.font_size = 12 * (1 - p) + p * 36


class JuggleTheBall(Game):
    REQUIRED_CLICKS = 5
    
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, "JUGGLE!", "default.inputs.mouse", 5.0)
        self.balls: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self._last_active_ball: arcade.Sprite | None = None
        self._closest_ball: arcade.Sprite | None = None
        self.balls.extend((arcade.SpriteCircle(25, (255, 255, 255, 255), center_x=self.state.screen_width/2, center_y=self.state.screen_height/2) for _ in range(3)))
        self.clicks = 0

        self.clicks_remaining_text = arcade.Text(f"{self.REQUIRED_CLICKS}", self.window.center_x, self.window.center_y, color = arcade.color.WHITE.replace(a = 64), font_size = 100, align = "center", anchor_x = "center", anchor_y = "center", font_name = "Josefin Sans")

    def start(self):
        if self._last_active_ball is not None:
            self._last_active_ball.color = (255, 255, 255)
        if self._closest_ball is not None:
            self._closest_ball.color = (255, 255, 255)
        self._last_active_ball = self._closest_ball = None

        for ball in self.balls:
            ball.position = self.state.screen_width * random(), 0.5 * self.state.screen_height
            ball.change_x = copysign(200, self.state.screen_width/2 - ball.center_x)
            # Will always be positive but that's fine
            ball.change_y = 360
        self.clicks = 0
        self.clicks_remaining_text.text = str(self.REQUIRED_CLICKS)

    def on_time_runout(self):
        self.succeed()

    def update(self, delta_time: float):
        for ball in self.balls:
            pos = ball.position
            ball.change_y = ball.change_y - 400 * delta_time
            ball.position = pos[0] + ball.change_x * delta_time, pos[1] + ball.change_y * delta_time
            if ball.center_x <= 25:
                ball.center_x = 25
                ball.change_x = copysign(ball.change_x, 1.0)
            elif ball.center_x >= self.state.screen_width - 25:
                ball.center_x = self.state.screen_width - 25
                ball.change_x = copysign(ball.change_x, -1.0)

            if ball.center_y < 25:
                self.fail()
                return
            
        if self.clicks >= self.REQUIRED_CLICKS:
            self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if symbol == arcade.MOUSE_BUTTON_LEFT and pressed:
            if self._closest_ball is None:
                return
            self._closest_ball.change_y = 360
            self._closest_ball.change_x = copysign(self._closest_ball.change_x, self.state.screen_width/2 - self._closest_ball.center_x)
            self._closest_ball.color = (125, 125, 125)
            self.clicks += 1
            self.clicks_remaining_text.text = str(self.REQUIRED_CLICKS - self.clicks)

            if self._last_active_ball is not None:
                self._last_active_ball.color = (255, 255, 255)
            self._last_active_ball = self._closest_ball
            self._closest_ball = None

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        closest_ball = self.get_closest_ball_to_pos((x, y))
        if self._closest_ball is not None:
            self._closest_ball.color = (255, 255, 255)
        self._closest_ball = closest_ball

        if closest_ball is not None:
            closest_ball.color = (255, 230, 210)

    def get_closest_ball_to_pos(self, point: tuple[float, float], range: float = 50, exclude_last: bool = True):
        closest_ball = None
        dist = float('inf')
        for ball in self.balls:
            if ball is self._last_active_ball and exclude_last:
                continue
            diff = (ball.center_x - point[0])**2 + (ball.center_y - point[1])**2
            if diff < dist:
                closest_ball = ball
                dist = diff
        if closest_ball is None:
            return
        if dist < range**2:
            return closest_ball
        

    def draw(self):
        self.clicks_remaining_text.draw()
        self.balls.draw()
