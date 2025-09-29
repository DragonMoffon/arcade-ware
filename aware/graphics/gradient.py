from collections.abc import Iterable, Generator
from array import array

from arcade import ArcadeContext, get_window, Rect
from arcade.types import RGBOrA255
import arcade.gl as gl


from aware.data.loading import load_shader

class Gradient:

    def __init__(self, rect: Rect, colors: Iterable[tuple[float, RGBOrA255]], vertical: bool = False, lazy: bool = False) -> None:
        self.context: ArcadeContext
        # TODO: properties to update these
        self._rect: Rect = rect
        self._colors: tuple[tuple[float, RGBOrA255], ...] = tuple(sorted(colors))
        self._vertical: bool = vertical

        self.index_buffer: gl.Buffer
        self.coordinate_buffer: gl.Buffer
        self.colour_buffer: gl.Buffer

        self.shader: gl.Program
        self.geometry: gl.Geometry

        self._initialised: bool = False
        self._stale: bool = False
        if not lazy:
            self.init_deferred()
    
    @property
    def colors(self) -> tuple[tuple[float, RGBOrA255], ...]:
        return self._colors

    def add_color(self, fraction: float, color: RGBOrA255):
        combined = self._colors + ((fraction, color),)
        self._colors = tuple(sorted(combined))
        self._stale = True

    def remove_color(self, idx: int = -1):
        if idx < 0:
            idx = len(self.colors) + idx

        if not (0 <= idx < len(self.colors)):
            raise IndexError
        
        self._colors = self._colors[:idx] + self._colors[idx+1:]
        self._stale = True

    def set_color(self, color: RGBOrA255, idx: int = -1):
        fraction = self._colors[idx][0]
        if idx < 0:
            idx = len(self.colors) + idx

        if not (0 <= idx < len(self.colors)):
            raise IndexError

        self._colors = self._colors[:idx] + ((fraction, color),) + self._colors[idx+1:]
        self._stale = True

    def set_fraction(self, fraction: float, idx: int = -1):
        color = self._colors[idx][1]
        if idx < 0:
            idx = len(self.colors) + idx

        if not (0 <= idx < len(self.colors)):
            raise IndexError

        self._colors = tuple(sorted(self._colors[:idx] + ((fraction, color),) + self._colors[idx+1:]))
        self._stale = True

    def update_color(self, fraction: float, color: RGBOrA255, idx: int = -1):
        if idx < 0:
            idx = len(self.colors) + idx

        if not (0 <= idx < len(self.colors)):
            raise IndexError
        
        self._colors = tuple(sorted(self._colors[:idx] + ((fraction, color),) + self._colors[idx+1:]))

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, rect: Rect) -> None:
        self._rect = rect
        self._stale = True

    @property
    def vertical(self) -> bool:
        return self._vertical
    
    @vertical.setter
    def vertical(self, vertical: bool) -> None:
        self._vertical = vertical
        self._stale = True

    def draw(self):
        if not self._initialised:
            self.init_deferred()
        elif self._stale:
            self.update_geometry()

        self.geometry.render(self.shader)

    def init_deferred(self):
        if self._initialised:
            return
        self.context = ctx = get_window().ctx



        color_estimate = len(self._colors)
        vertex_count = 2 * color_estimate
        triangle_count = vertex_count - 2
        index_count = triangle_count * 3

        self.coordinate_buffer = ctx.buffer(reserve=vertex_count*16)
        self.colour_buffer = ctx.buffer(reserve=vertex_count*4)
        self.index_buffer = ctx.buffer(reserve=index_count*4)

        self.update_geometry()

        self.shader = ctx.program(
            vertex_shader=load_shader('projection_uv_coloured_2d_vs'),
            fragment_shader=load_shader('colour_blend_rgb_fs')
        )

        self.geometry = ctx.geometry(
            (
                gl.BufferDescription(self.coordinate_buffer, '4f', ('in_coordinate',)),
                gl.BufferDescription(self.colour_buffer, '4f1', ('in_colour',))
            ),
            self.index_buffer,
            ctx.TRIANGLES
        )

        self._initialised = True
    
    def update_geometry(self):
        self._stale = False

        colors = self._get_colors_clamped()
        color_count = len(colors)
        vertex_count = 2 * color_count
        triangle_count = vertex_count - 2
        index_count = triangle_count * 3

        if self.coordinate_buffer.size != vertex_count * 16: # 4 32-bit floats
            self.coordinate_buffer.orphan(vertex_count * 16)
        l, r, b, t = self.rect.lrbt
        if self._vertical:
            postions = self._get_color_positions(colors, b, t)
            def create_coord_data() -> Generator[float, None, None]:
                for pos, frac in postions:
                    yield from (l, pos, 0.0, frac)
                    yield from (r, pos, 1.0, frac)
        else:
            postions = self._get_color_positions(colors, l, r)
            def create_coord_data() -> Generator[float, None, None]:
                for pos, frac in postions:
                    yield from (pos, t, frac, 1.0)
                    yield from (pos, b, frac, 0.0)
        self.coordinate_buffer.write(array('f', create_coord_data()))

        if self.colour_buffer.size != vertex_count * 4: # 1 4 8-bit float
            self.colour_buffer.orphan(vertex_count * 4)
        def create_color_data():
            for c in colors:
                r, g, b, *a = c[1]
                a = 255 if not a else a[0]
                yield from (r, g, b, a)
                yield from (r, g, b, a)
        self.colour_buffer.write(array('B', create_color_data()))

        if self.index_buffer.size != index_count * 4: # 1 32-bit int
            self.index_buffer.orphan(index_count * 4)
        def create_index_data():
            for i in range(color_count - 1):
                idx = i * 2
                yield from (idx, idx + 3, idx + 1, idx, idx + 2, idx + 3)
        self.index_buffer.write(array('i', create_index_data()))

    def _get_colors_clamped(self) -> tuple[tuple[float, RGBOrA255], ...]:
        # Special cases where we have a degenerate gradient
        colors = self.colors
        if len(colors) == 0:
            return ((0.0, (0, 0, 0, 255)), (1.0, (0, 0, 0, 255)))
        if len(colors) == 1:
            color = colors[0][1]
            return ((0.0, color), (1.0, color))

        if colors[0][0] < 0.0:
            outer = colors[0] # The latest color outside the gradient
            inner = colors[1] # The earliest color inside the gradient
            cutoff = 1 # The idx of the cutoff, as we don't care about all earlier colors
            if inner[0] < 0.0:
                for idx, color in enumerate(colors[2:], 2):
                    outer, inner = inner, color
                    cutoff = idx
                    if color[0] > 0.0:
                        break
            a, (r1, g1, b1, *a1) = outer
            b, (r2, g2, b2, *a2) = inner
            t = a / (b - a)
            c = (
                int(r2 * t + (1 - t) * r1),
                int(g2 * t + (1 - t) * g1),
                int(b2 * t + (1 - t) * b1),
                int((255 if not a2 else a2[0]) * t + (1 - t) * (255 if not a1 else a1[0]))
            )

            colors = ((0.0, c),) + colors[cutoff:]
        elif colors[0][0] > 0.0:
            colors = ((0.0, colors[0][1]),) + colors

        if colors[-1][0] > 1.0:
            outer = colors[-1] # the earliest color outside the gradient
            inner = colors[-2] # the latest color inside the gradient
            cutoff = -1 # the negative idx+1 of the cutoff.
            if inner[0] > 1.0:
                for idx, color in enumerate(colors[:-2:-1], 2):
                    outer, inner = inner, color
                    cutoff = -idx
                    if color[0] < 1.0:
                        break
            a, (r1, g1, b1, *a1) = outer
            b, (r2, g2, b2, *a2) = inner
            t = a / (b - a)
            c = (
                int(r2 * t + (1 - t) * r1),
                int(g2 * t + (1 - t) * g1),
                int(b2 * t + (1 - t) * b1),
                int((255 if not a2 else a2[0]) * t + (1 - t) * (255 if not a1 else a1[0]))
            )

            colors = colors[:cutoff] + ((1.0, c),)
            
        elif colors[-1][0] < 1.0:
            colors = colors + ((1.0, colors[-1][1]),)

        return colors
         
    def _get_color_positions(self, colors: tuple[tuple[float, RGBOrA255], ...], start: float, end: float) -> Generator[tuple[float, float], None, None]:
        for fraction, _ in colors:
            pos = fraction * end + (1 - fraction) * start
            yield pos, fraction
