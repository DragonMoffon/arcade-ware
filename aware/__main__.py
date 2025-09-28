import pyglet
pyglet.options.audio = ['directsound', 'xaudio2', "openal", "pulse", "silent"]

from aware.launch import launch

if __name__ == "__main__":
    launch()