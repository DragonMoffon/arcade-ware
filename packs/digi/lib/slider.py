from collections.abc import Callable
from typing import Any
from arcade import Rect, Sound, Vec2
import arcade
from arcade.types import Color

from aware.anim import lerp, perc
from aware.utils import clamp

RT = Any

class Slider:
    def __init__(self, rect: Rect, slider_min: float = 0, slider_max: float = 100,
                 inner_color: Color = arcade.color.BLACK, outer_color: Color = arcade.color.WHITE,
                 border_thickness: int = 3, handle_color: Color = arcade.color.WHITE,
                 handle_thickness: int = 25, sound: Sound | None = None, rounding_function: Callable[[float], RT] = float) -> None:
        self._rect = rect
        self.handle_rect = self._rect.clamp_width(handle_thickness, handle_thickness)
        self.handle_rect = self.handle_rect.align_left(self._rect.left)
        self.slider_min = slider_min
        self.slider_max = slider_max
        self.inner_color = inner_color
        self.outer_color = outer_color
        self.border_thickness = border_thickness
        self.handle_color = handle_color
        self.sound = sound
        self.rounding_function = rounding_function

        self._grabbed = False

        self._registered_on_update_functions: list[Callable[[RT], None]] = []
        self._registered_on_drop_functions: list[Callable[[RT], None]] = []

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, new_rect: Rect) -> None:
        current_rect = self._rect
        handle_distance = self.handle_rect.left - current_rect.left
        self._rect = new_rect
        self.handle_rect = self.handle_rect.align_left(new_rect.left + handle_distance)

    @property
    def value(self) -> RT:
        val = lerp(self.slider_min, self.slider_max, perc(self._rect.left + self.handle_rect.width, self._rect.right, self.handle_rect.right))
        return self.rounding_function(val)

    @value.setter
    def value(self, val: RT) -> None:
        p = perc(self.slider_min, self.slider_max, val)  # type: ignore -- no idea how to solve this one
        self.handle_rect = self.handle_rect.align_right(lerp(self._rect.left + self.handle_rect.width, self._rect.right, p))

    @property
    def grabbed(self) -> bool:
        return self._grabbed

    @grabbed.setter
    def grabbed(self, val: bool) -> None:
        self._grabbed = val
        for f in self._registered_on_drop_functions:
            f(self.value)

    def register(self, f: Callable[[RT], None], on_drop: bool = False) -> None:
        if on_drop:
            if f not in self._registered_on_drop_functions:
                self._registered_on_drop_functions.append(f)
        else:
            if f not in self._registered_on_update_functions:
                self._registered_on_update_functions.append(f)

    def update(self, cursor_pos: Vec2) -> None:
        if self.grabbed or (cursor_pos in self._rect):
            self.handle_rect = self.handle_rect.align_x(clamp(self._rect.left + self.handle_rect.width / 2, cursor_pos.x, self._rect.right - self.handle_rect.width / 2))
        for f in self._registered_on_update_functions:
            f(self.value)

    def draw(self) -> None:
        arcade.draw_rect_filled(self._rect, self.inner_color)
        arcade.draw_rect_outline(self._rect, self.outer_color, self.border_thickness)
        arcade.draw_rect_filled(self.handle_rect, self.handle_color)
