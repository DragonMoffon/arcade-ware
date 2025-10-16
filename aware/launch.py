from aware.data.loading import load_font
from aware.window import AWareWindow
from aware.views.main_menu import MainMenuView

from engine.finder import packs
# from engine.play import PlayView
from engine.resources import load_resources

def load_fonts():
    for font, ext in [
        ("AOTFShinGoProBold", "otf"),
        ("AOTFShinGoProMedium", "otf"),
        ("JosefinSans-Medium", "ttf"),
        ("JosefinSans-MediumItalic", "ttf")
    ]:
        load_font(font, ext)

def launch():
    # Prepare fonts
    load_fonts()

    # Iterate through the resources folder and load every pack found.
    load_resources()
    # load all packs into the pack manager
    packs.load_packs()
    window = AWareWindow()
    
    # At the moment just launch straight into the play view with every game and transition.
    view = MainMenuView()
    window.run(view)
