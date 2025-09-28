from pathlib import Path

from arcade import Sprite, load_sound, load_texture, load_spritesheet, Sound, Texture, SpriteSheet
import arcade

__all__ = (
    "load_resources",
    "get_sound",
)

class ResourceMap:

    def __init__(self) -> None:
        self.resources: dict[str, list[str]] = {}
        self.namespace: dict[str, Path] = {}

    def __str__(self):
        return str(self.namespace)

    def flush(self):
        self.resources = {}
        self.namespace = {}

    def add(self, target: str, pth: Path):
        if target in self.namespace:
            raise KeyError(f'Conflicting resource names. Resource @ {pth} conflicts with Resource @ {self.namespace[target]} for the name {target}')
        
        name = target.split('.')[-1]
        if name not in self.resources:
            self.resources[name] = []
        self.resources[name].append(target)
        self.namespace[target] = pth
    
    def get(self, target: str) -> Path:
        if target.count('.') == 0:
            target = self.resources[target][0]
        return self.namespace[target]

    def __setitem__(self, target: str, pth: Path):
        self.add(target, pth)

    def __getitem__(self, target: str) -> Path:
        return self.get(target)

SOUND_MAP = ResourceMap()
TEXTURE_MAP = ResourceMap()
EXTENSION_MAP: dict[str, ResourceMap] = {
    "wav": SOUND_MAP,
    "mp3": SOUND_MAP,
    "ogg": SOUND_MAP,
    "png": TEXTURE_MAP,
    "jpg": TEXTURE_MAP 
}

def get_sound(target: str) -> Sound:
    pth = SOUND_MAP[target]
    return load_sound(pth)

def get_texture(target: str) -> Texture:
    pth = TEXTURE_MAP[target]
    return load_texture(pth)

def get_sprite(target: str, center_x: float = 0, center_y: float = 0, color = arcade.color.WHITE) -> Sprite:
    pth = TEXTURE_MAP[target]
    tex = load_texture(pth)
    spr = Sprite(tex, center_x = center_x, center_y = center_y)
    spr.color = color
    return spr

def get_spritesheet(target: str) -> SpriteSheet:
    pth = TEXTURE_MAP[target]
    return load_spritesheet(pth)

def load_resources() -> None:
    pth = Path().absolute() / "resources"
    depth = len(pth.parts)
    for current, _, files in pth.walk():
        for file in files:
            sep = file.split('.')
            if sep[-1] not in EXTENSION_MAP:
                continue
            mapping = EXTENSION_MAP[sep[-1]]
            parts = current.parts[depth:] + (sep[0],)
            namespace = ".".join(parts)
            mapping.add(namespace, current / file)
