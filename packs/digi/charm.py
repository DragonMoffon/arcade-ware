from __future__ import annotations
from dataclasses import dataclass
import random

import arcade
from arcade.types import Color

from engine.play import PlayState, Game
from engine.resources import get_sprite, get_texture

FRONT_PORCH = 1.0
BACK_PORCH = 0.5
NOTES = 8
BPM = 120
SPN = 1 / (BPM / 60)

NOTE_SIZE = 110
NOTE_GAP = 5
STRIKELINE_Y_OFFSET = 10
SECONDS_PER_SCREEN = 0.75
STRIKELINE_ALPHA = 128

BG_COLOR = Color.from_hex_string("b3fdc8")

HIT_WINDOW = 0.070  # 70ms +/-

@dataclass
class Note:
    time: float
    lane: int
    # We're not doing duration for this right now.
    hit: bool = False
    miss: bool = False

class NoteSprite:
    def __init__(self, note: Note) -> None:
        self.note = note
        self._win = arcade.get_window()
        x_pos = self._win.center_x - (NOTE_GAP * 1.5) - (NOTE_SIZE * 1.5) + (self.note.lane * NOTE_SIZE) + (NOTE_GAP * max(0, self.note.lane - 1))
        self.sprite = get_sprite(f"digi.charm.{self.note.lane + 1}", center_x = x_pos, center_y = self.get_note_y(0))
        self.sprite.size = (NOTE_SIZE, NOTE_SIZE)

    def get_note_y(self, song_time: float) -> float:
        strikeline_target = self._win.height - STRIKELINE_Y_OFFSET
        px_offset = (self.note.time - song_time) * (self._win.height / SECONDS_PER_SCREEN)
        return strikeline_target - px_offset - (NOTE_SIZE / 2)
    
    def update(self, song_time: float) -> None:
        self.sprite.center_y = self.get_note_y(song_time)
        self.sprite.alpha = 255 if not self.note.hit else 0

class CharmGame(Game):
    def __init__(self, state: PlayState) -> None:
        super().__init__(state, prompt = "HIT NOTES!", controls = "digi.inputs.dfjk", duration = FRONT_PORCH + (NOTES * SPN) + BACK_PORCH)
        self.chart: list[Note] = []
        self.note_sprites: list[NoteSprite] = []
        self.spritelist = arcade.SpriteList()

        # Strikeline
        self.strikeline_sprites: list[arcade.Sprite] = []
        self.strikeline_on_textures: list[arcade.Texture] = []
        self.strikeline_off_textures: list[arcade.Texture] = []
        self.strikeline_spritelist = arcade.SpriteList()
        strikeline_center = self.window.height - STRIKELINE_Y_OFFSET - (NOTE_SIZE / 2)
        for i in range(4):
            x = self.window.center_x - (NOTE_GAP * 1.5) - (NOTE_SIZE * 1.5) + (i * NOTE_SIZE) + (NOTE_GAP * max(0, i - 1))
            spr = get_sprite(f"digi.charm.{i+1}_strikeline", x, strikeline_center)
            spr.size = (NOTE_SIZE, NOTE_SIZE)
            spr.alpha = STRIKELINE_ALPHA
            self.strikeline_sprites.append(spr)

            self.strikeline_off_textures.append(get_texture(f"digi.charm.{i+1}_strikeline"))
            self.strikeline_on_textures.append(get_texture(f"digi.charm.{i+1}"))
        self.strikeline_spritelist.extend(self.strikeline_sprites)

    @staticmethod
    def generate_chart(notes: int, bpm: float) -> list[Note]:
        chart = []
        spn = 1 / (bpm / 60)
        for i in range(notes):
            time = spn * i
            chart.append(Note(time, random.choice((0, 1, 2, 3))))
        return chart
    
    @property
    def hits(self) -> int:
        return len([n for n in self.chart if n.hit])
    
    @property
    def misses(self) -> int:
        return len([n for n in self.chart if n.miss])

    def start(self):
        self.chart: list[Note] = self.generate_chart(NOTES, BPM)
        self.note_sprites: list[NoteSprite] = [NoteSprite(n) for n in self.chart]
        self.spritelist.extend([n.sprite for n in self.note_sprites])

    def finish(self):
        self.spritelist.clear()

    def draw(self):
        arcade.draw_rect_filled(self.window.rect, BG_COLOR)
        self.strikeline_spritelist.draw()
        self.spritelist.draw()

    def update(self, delta_time: float):
        time = self.time - FRONT_PORCH
        for ns in self.note_sprites:
            ns.update(time)

        missed_notes = [n for n in self.chart if n.time + HIT_WINDOW < time and not n.hit and not n.miss]
        for n in missed_notes:
            n.miss = True

        if self.misses > 0:
            self.fail()

    def on_time_runout(self):
        self.succeed()

    def on_input(self, symbol: int, modifier: int, pressed: bool):
        keys = [arcade.key.D, arcade.key.F, arcade.key.J, arcade.key.K]
        time = self.time - FRONT_PORCH
        if symbol in keys and pressed:
            lane = keys.index(symbol)
            available_notes = [n for n in self.chart if n.time - HIT_WINDOW < time <= n.time + HIT_WINDOW and not n.hit and not n.miss and n.lane == lane]
            for n in available_notes:
                n.hit = True

            self.strikeline_sprites[lane].texture = self.strikeline_on_textures[lane]
        elif symbol in keys and not pressed:
            lane = keys.index(symbol)
            self.strikeline_sprites[lane].texture = self.strikeline_off_textures[lane]
