from typing import Literal
from array import array

from arcade import ArcadeContext, get_window, Rect
from arcade.types import RGBOrA255
import arcade.gl as gl

from aware.data.loading import load_shader


class Wave:
    TOP_FACE: Literal[0] = 0
    RIGHT_FACE: Literal[1] = 1
    BOTTOM_FACE: Literal[2] = 2
    LEFT_FACE: Literal[3] = 3

    def __init__(self, rect: Rect, depth: float, width: float, speed: float, phase: float, color: RGBOrA255, face: Literal[0, 1, 2, 3] = 0, blend: int = 0, lazy: bool = False) -> None:
        self.ctx: ArcadeContext

        self._rect: Rect = rect
        self._face: Literal[0, 1, 2, 3] = face
        self._blend: int = blend

        self.depth: float = depth
        self.width: float = width
        self.speed: float = speed
        self.phase: float = phase
        self.time: float = 0.0
        self._color: RGBOrA255 = color

        self.coordinate_buffer: gl.Buffer
        self.colour_buffer: gl.Buffer
        self.index_buffer: gl.Buffer

        self.shader: gl.Program
        self.geometry: gl.Geometry

        self._stale: bool = False
        self._initialised: bool = False
        if not lazy:
            self.init_deferred()

    @property
    def rect(self) -> Rect:
        return self._rect
    
    @rect.setter
    def rect(self, rect: Rect) -> None:
        self._rect = rect
        self._stale = True

    @property
    def face(self) -> Literal[0, 1, 2, 3]:
        return self._face
    
    @face.setter
    def face(self, face: Literal[0, 1, 2, 3]):
        self._face = face
        self._stale = True

    @property
    def color(self) -> RGBOrA255:
        return self._color
    
    @color.setter
    def color(self, color: RGBOrA255):
        self._color = color
        self._stale = True

    @property
    def blend(self) -> int:
        return self._blend
    
    @blend.setter
    def blend(self, blend: int) -> None:
        if blend == self._blend:
            return
        self._blend = blend
        self.shader['blend'] = max(0, self._blend)
        self._stale = True

    @property
    def do_blend(self) -> bool:
        return self._blend > 0

    def draw(self):
        if not self._initialised:
            self.init_deferred()
        if self._stale:
            self.update_geometry()
        self.shader['wave'] = self.depth, self.width, self.speed, self.time + self.phase
        func = self.ctx.blend_func
        with self.ctx.enabled(self.ctx.BLEND):
            self.ctx.blend_func = self.ctx.BLEND_DEFAULT
            self.geometry.render(self.shader)
        self.ctx.blend_func = func
    
    def init_deferred(self):
        if self._initialised:
            return
        
        self.ctx = ctx = get_window().ctx

        self.coordinate_buffer = ctx.buffer(reserve=64) # 16 32-bit floats
        self.colour_buffer = ctx.buffer(reserve=16) # 16 8-bit floats
        self.index_buffer = ctx.buffer(reserve=24) # 6 32-bit ints

        self.update_geometry()

        self.shader = ctx.program(
            vertex_shader=load_shader('projection_uv_coloured_2d_vs'),
            fragment_shader=load_shader('wave_fs')
        )
        self.shader['blend'] = max(0, self._blend)

        self.geometry = ctx.geometry(
            (
                gl.BufferDescription(self.coordinate_buffer, '4f', ('in_coordinate',)),
                gl.BufferDescription(self.colour_buffer, '4f1', ('in_colour',))
            ),
            self.index_buffer,
            ctx.TRIANGLES
        )

        self._stale = False
        self._initialised = True

    def update_geometry(self):
        l, r, b, t = self._rect.lrbt
        w, h = self.rect.width, self.rect.height
        bl = self._blend if self._blend > 0 else 0
        match self._face:
            case Wave.TOP_FACE:
                u0, v0, u1, v1, u2, v2, u3, v3 = 0, h, w, h, 0, -bl, w, -bl
                x0, y0, x1, y1, x2, y2, x3, y3 = l, b, r, b, l, t + bl, r, t + bl
            case Wave.RIGHT_FACE:
                u0, v0, u1, v1, u2, v2, u3, v3 = h, w, h, -bl, 0, w, 0, -bl
                x0, y0, x1, y1, x2, y2, x3, y3 = l, b, r + bl, b, l, t, r + bl, t
            case Wave.BOTTOM_FACE:
                u0, v0, u1, v1, u2, v2, u3, v3 = w, -bl, 0, -bl, w, h, 0, h
                x0, y0, x1, y1, x2, y2, x3, y3 = l, b - bl, r, b - bl, l, t, r, t
            case Wave.LEFT_FACE:
                u0, v0, u1, v1, u2, v2, u3, v3 = 0, -bl, 0, w, h, -bl, h, w
                x0, y0, x1, y1, x2, y2, x3, y3 = l - bl, b, r, b, l - bl, t, r, t
            case _:
                raise ValueError(f'Wave face is not 0, 1, 2, or 3 but {self._face}')
        
        self.coordinate_buffer.write(array('f', (
            x0, y0, u0, v0,
            x1, y1, u1, v1,
            x2, y2, u2, v2,
            x3, y3, u3, v3
        )))

        r, g, b, *a = self._color
        a = 255 if not a else a[0]
        self.colour_buffer.write(array('B', (
            r, g, b, a,
            r, g, b, a,
            r, g, b, a,
            r, g, b, a
        )))

        self.index_buffer.write(array('i', (0, 3, 1, 0, 2, 3)))

        self._stale = False