from __future__ import annotations
import random

import arcade
from arcade.types import AnchorPoint

from aware.anim import bounce
from engine.play import ContentFlag, PlayState, Game
from engine.resources import get_sound, get_sprite

from .lib import noa

LEEWAY_TIME = 1.5

class DoNothingGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "DO NOTHING!", controls = "default.inputs.nothing", duration = LEEWAY_TIME + 3, flags = ContentFlag.PHOTOSENSITIVE)
        self.sprites = [
            get_sprite("digi.donothing.3", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.2", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.1", self.window.center_x, self.window.center_y),
            get_sprite("digi.donothing.stop", self.window.center_x, self.window.center_y)
        ]

        self.party_noise = get_sound("digi.donothing.party")
        self.stop_noise = get_sound("digi.donothing.night")

        self.party_player = None
        self.stop_player = None

    @property
    def current_sprite(self) -> arcade.Sprite:
        return self.sprites[min(3, int(self.time * (3 / LEEWAY_TIME)))]
    
    @property
    def current_hue(self) -> int:
        return int(self.time * 4) % 12
    
    def start(self):
        self.party_player = self.party_noise.play(speed = self.tick_speed)
        self.stop_player = self.stop_noise.play()
        self.stop_player.pause()

    def finish(self):
        self.party_player.delete()
        self.stop_player.delete()

    def draw(self):
        if self.time < LEEWAY_TIME:
            arcade.draw_rect_filled(self.window.rect, noa.get_color(self.current_hue, 8, 8))
        arcade.draw_sprite(self.current_sprite)

    def update(self, delta_time: float):
        if self.time < LEEWAY_TIME:
            self.current_sprite.center_y = bounce(self.window.center_y, self.window.center_y + 50, 60 * (3 / LEEWAY_TIME), self.time)
            self.current_sprite.color = noa.get_color((self.current_hue + 6) % 12, 4, 8)
        else:
            self.party_player.pause()
            self.stop_player.play()

    def on_time_runout(self):
        self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if self.time > LEEWAY_TIME:
            self.fail()

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        if self.time > LEEWAY_TIME:
            self.fail()

VERY_LONG = 60 * 60
BALL_COUNT = 10
BALL_RADIUS = 20
SORT_DURATION = 7.5

RED_BALL_COLOR = noa.get_color(0, 4, 9)
RED_SIDE_COLOR = noa.get_color(0, 8, 9)
BLUE_BALL_COLOR = noa.get_color(9, 4, 9)
BLUE_SIDE_COLOR = noa.get_color(9, 8, 9)

class SortGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "SORT!", controls = "default.inputs.mouse", duration = VERY_LONG, flags = ContentFlag.COLORBLIND)
        self.red_balls = [arcade.SpriteCircle(BALL_RADIUS, RED_BALL_COLOR) for _ in range(int(BALL_COUNT / 2))]
        self.blue_balls = [arcade.SpriteCircle(BALL_RADIUS, BLUE_BALL_COLOR)  for _ in range(int(BALL_COUNT / 2))]

        self.spritelist = arcade.SpriteList()
        self.spritelist.extend(self.red_balls + self.blue_balls)

        self.red_side = self.window.rect.scale_axes((0.5, 1.0), AnchorPoint.CENTER_LEFT)
        self.blue_side = self.window.rect.scale_axes((0.5, 1.0), AnchorPoint.CENTER_RIGHT)

        self.cursor_pos = (0, 0)
        self.selected_ball: arcade.SpriteCircle | None = None

        self.scrambling_done = False
        self.scrambling_text = arcade.Text('SCRAMBLING...', self.window.center_x, self.window.center_y, anchor_x = "center", anchor_y = "center", font_size = 72, font_name = "A-OTF Shin Go Pro", bold = True)

        self.sorting_done = False
        self.finish_time = float("inf")
        self.sorting_text = arcade.Text('GOOD JOB!', self.window.center_x, self.window.center_y, anchor_x = "center", anchor_y = "center", font_size = 72, font_name = "A-OTF Shin Go Pro", bold = True)

    @property
    def all_balls(self) -> list[arcade.SpriteCircle]:
        return self.red_balls + self.blue_balls
    
    def scramble(self) -> None:
        for ball in self.all_balls:
            x = random.randrange(BALL_RADIUS, self.window.width - BALL_RADIUS)
            y = random.randrange(BALL_RADIUS, self.window.height - BALL_RADIUS - 65) + 65
            ball.position = (x, y)

    @property
    def completed(self) -> bool:
        return (all([ball.position in self.red_side for ball in self.red_balls]) and
                all([ball.position in self.blue_side for ball in self.blue_balls])) or \
                (all([ball.position in self.red_side for ball in self.blue_balls]) and
                all([ball.position in self.blue_side for ball in self.red_balls]))

    def check_scramble(self) -> bool:
        if self.completed or self.time < 1:
            return False
        for ball in self.all_balls:
            other_balls = [b for b in self.all_balls if b is not ball]
            for other_ball in other_balls:
                if ball.collides_with_sprite(other_ball):
                    return False
        return True
    
    def start(self):
        self.scrambling_done = False
        self.sorting_done = False

    def finish(self):
        ...

    def draw(self):
        arcade.draw_rect_filled(self.red_side, RED_SIDE_COLOR)
        arcade.draw_rect_filled(self.blue_side, BLUE_SIDE_COLOR)
        self.spritelist.draw()

        if not self.scrambling_done:
            self.scrambling_text.draw()

        if self.sorting_done:
            self.sorting_text.draw()

    def update(self, delta_time: float):
        if not self.scrambling_done:
            if self.check_scramble():
                self.scrambling_done = True
                # !: This accesses a private member to do this, but does it have to be private?
                self._duration = SORT_DURATION + self.time
                return
            else:
                self.scramble()
        else:
            if self.selected_ball:
                self.selected_ball.position = self.cursor_pos if (self.cursor_pos in self.red_side or self.cursor_pos in self.blue_side) else self.selected_ball.position
            if self.completed and not self.sorting_done:
                self.finish_time = self.time
                self.sorting_done = True
        if self.time > self.finish_time + 1:
            self.succeed()

    def on_time_runout(self):
        if self.sorting_done:
            self.succeed()
        else:
            self.fail()

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        self.cursor_pos = (x, y)

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if symbol == arcade.MOUSE_BUTTON_LEFT and pressed and not self.sorting_done:
            for ball in self.all_balls:
                if ball.collides_with_point(self.cursor_pos):
                    self.selected_ball = ball
        elif symbol == arcade.MOUSE_BUTTON_LEFT and not pressed:
            self.selected_ball = None

LETTERS = "abcdefghijklmnopqrstuvwxyz"
KEY_MAPPING = {getattr(arcade.key, let.upper()): let for let in LETTERS}
LEAVE_TIME = 1.0

class LetterGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "PRESS!", controls = "default.inputs.keyboard", duration = 3.0)
        self.chosen_letter = random.choice(LETTERS)
        self.sound = get_sound(f"digi.letters.{self.chosen_letter}")
        self.text = arcade.Text('?', self.window.center_x, self.window.center_y, anchor_x = "center", anchor_y = "bottom", font_size = 240, font_name = "8BITOPERATOR JVE")

        self.win_sound = get_sound("digi.sounds.snd_coin")
        self.lose_sound = get_sound("digi.sounds.snd_error")

        self.win_state: bool | None = None
        self.win_time = float("inf")

    def start(self):
        self.chosen_letter = random.choice(LETTERS)
        self.sound = get_sound(f"digi.letters.{self.chosen_letter}")
        self.text.text = self.chosen_letter.upper()
        self.text.color = arcade.color.WHITE
        self.win_state = None

        self.sound.play()

    def draw(self):
        self.text.draw()

    def on_time_runout(self):
        if self.win_state is True:
            self.succeed()
        else:
            self.fail()

    def update(self, delta_time: float):
        if self.time > self.win_time + LEAVE_TIME:
            self.on_time_runout()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if symbol in KEY_MAPPING and pressed and self.win_state is None:
            if KEY_MAPPING[symbol] == self.chosen_letter:
                self.text.color = arcade.color.GREEN
                self.win_sound.play()
                self.win_state = True
                self.win_time = self.time
            else:
                self.text.color = arcade.color.RED
                self.lose_sound.play()
                self.win_state = False
                self.win_time = self.time

REQUIRED_WHACKS = 10
WHACKS_PER_SECOND = 1.5
GRID_ROWS = 5
GRID_COLUMNS = 7
SPOT_SIZE = 25

class WhackAMoleGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "WHACK!", controls = "default.inputs.mouse", duration = REQUIRED_WHACKS / WHACKS_PER_SECOND)

        self.sprites = [arcade.SpriteCircle(SPOT_SIZE, arcade.color.RED) for _ in range(GRID_ROWS * GRID_COLUMNS)]
        self.spritelist = arcade.SpriteList()
        self.spritelist.extend(self.sprites)

        self.bounds = self.window.rect.scale(0.8).align_top(self.window.height)
        self.bounds = self.bounds.resize(self.bounds.width - SPOT_SIZE * 2, self.bounds.height - SPOT_SIZE * 2)

        self.grid_layout()
        self.game_won = False
        self.won_text = arcade.Text('GOOD JOB!', self.window.center_x, self.window.center_y, anchor_x = "center", anchor_y = "center", font_size = 72, font_name = "A-OTF Shin Go Pro", bold = True)

        self.cursor_pos = (0, 0)

    def grid_layout(self):
        for c in range(GRID_COLUMNS):
            for r in range(GRID_ROWS):
                idx = (c * GRID_ROWS) + r
                sprite = self.sprites[idx]
                x = c * (self.bounds.width * (1 / (GRID_COLUMNS - 1))) + self.bounds.left
                y = r * (self.bounds.height * (1 / (GRID_ROWS - 1))) + self.bounds.bottom
                pos = (x, y)
                sprite.position = pos

    @property
    def success(self) -> bool:
        return all([s.color == arcade.color.RED for s in self.sprites])

    def starting_state(self):
        idxs = random.choices(range(GRID_COLUMNS * GRID_ROWS), k = REQUIRED_WHACKS)
        for i in idxs:
            self.sprites[i].color = arcade.color.GREEN

    def start(self):
        self.starting_state()
        self.game_won = False

    def draw(self):
        self.spritelist.draw()
        if self.game_won:
            self.won_text.draw()

    def on_time_runout(self):
        if self.game_won:
            self.succeed()
        else:
            self.fail()

    def update(self, delta_time: float):
        if self.success:
            self.game_won = True

        if self.game_won:
            for s in self.sprites:
                s.color = arcade.color.GREEN if int(self.time * 4) % 2 else arcade.color.RED

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if symbol == arcade.MOUSE_BUTTON_LEFT and pressed:
            for s in self.sprites:
                if s.collides_with_point(self.cursor_pos):
                    s.color = arcade.color.RED
                    break

    def on_cursor_motion(self, x: float, y: float, dx: float, dy: float):
        self.cursor_pos = (x, y)

CSB_TO_AW = (720 / 1080)
NEEDED_HITS = 20
PENCIL_CENTIMETERS = 10.0
PENCIL_START = 1359 * CSB_TO_AW
PENCIL_LENGTH = 716 * CSB_TO_AW

class PencilSharpeningGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "SHARPEN!", controls = "digi.inputs.qe", duration = 5.0)

        self.bg = get_sprite("digi.pencil.stage_back")
        self.stage_right_1 = get_sprite("digi.pencil.stage_right_1")
        self.stage_right_2 = get_sprite("digi.pencil.stage_right_2")
        self.pencil = get_sprite("digi.pencil.pencil")

        self.red_x = get_sprite("digi.pencil.red_x")
        self.red_x.scale = 0.5
        self.key_e = get_sprite("digi.pencil.key_e")
        self.key_e.scale = 0.5
        self.key_q = get_sprite("digi.pencil.key_q")
        self.key_q.scale = 0.5

        self.fail_sound = get_sound("digi.pencil.fail")

         # !: Remove this, these are 1080-compat CSB assets
        for s in [self.bg, self.stage_right_1, self.stage_right_2, self.pencil, self.red_x, self.key_e, self.key_q]:
            s.scale = (s.scale[0] * CSB_TO_AW, s.scale[1] * CSB_TO_AW)

        self.bg.position = self.window.center
        self.pencil.position = self.window.center
        self.pencil.right = PENCIL_START
        self.stage_right_1.position = self.window.center
        self.stage_right_1.right = self.window.rect.right
        self.stage_right_2.position = self.window.center
        self.stage_right_2.right = self.window.rect.right
        self.red_x.position = (self.stage_right_1.left, self.window.center_y)

        self.key_q.position = (self.window.width * 0.4, self.window.height * 0.25)
        self.key_e.position = (self.window.width * 0.6, self.window.height * 0.25)

        self.key_e.alpha = 64
        self.stage_right_2.alpha = 0
        self.red_x.alpha = 0

        self.spritelist = arcade.SpriteList()
        self.spritelist.extend([self.bg, self.pencil, self.stage_right_1, self.stage_right_2, self.key_e, self.key_q, self.red_x])

        self.hit_e_next = False
        self.hits = 0

        self.cm_text = arcade.Text('10.0cm', self.window.width - 10, self.window.height - 10, anchor_x = "right", anchor_y = "top", align = "right", font_size = 48, font_name = "A-OTF Shin Go Pro", bold = True)

    @property
    def failed(self) -> bool:
        return self.hits > NEEDED_HITS

    def start(self):
        self.hit_e_next = False
        self.hits = 0

        self.key_q.alpha = 255
        self.key_e.alpha = 64
        self.stage_right_1.alpha = 255
        self.stage_right_2.alpha = 0
        self.red_x.alpha = 0

        self.cm_text.text = f"{PENCIL_CENTIMETERS * (1 - self.hits / NEEDED_HITS):.1f}cm"
        self.cm_text.color = arcade.color.WHITE

    def draw(self):
        self.spritelist.draw()
        self.cm_text.draw()

    def on_time_runout(self):
        if self.hits < NEEDED_HITS or self.failed:
            self.fail()
        else:
            self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        if (self.hit_e_next and symbol == arcade.key.E and pressed and self.hits <= NEEDED_HITS) \
            or (not self.hit_e_next and symbol == arcade.key.Q and pressed and self.hits <= NEEDED_HITS):
            self.hit_e_next = not self.hit_e_next
            self.hits += 1
            self.cm_text.text = f"{PENCIL_CENTIMETERS * (1 - self.hits / NEEDED_HITS):.1f}cm"
            self.pencil.right = PENCIL_START + (PENCIL_LENGTH * (self.hits / 20))

            if symbol == arcade.key.E:
                self.key_q.alpha = 255
                self.key_e.alpha = 64
                self.stage_right_1.alpha = 255
                self.stage_right_2.alpha = 0
            elif symbol == arcade.key.Q:
                self.key_q.alpha = 64
                self.key_e.alpha = 255
                self.stage_right_1.alpha = 0
                self.stage_right_2.alpha = 255

            if self.hits == NEEDED_HITS:
                self.cm_text.color = arcade.color.GREEN
            if self.hits > NEEDED_HITS:
                self.red_x.alpha = 255
                self.fail_sound.play(volume = 0.5)
                self.cm_text.color = arcade.color.RED
