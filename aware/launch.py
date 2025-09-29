from aware.window import AWareWindow
from aware.views.main_menu import MainMenuView

from engine.finder import load_packs, get_loaded_games, get_loaded_transitions, get_loaded_fails
from engine.play import PlayView
from engine.resources import load_resources

def launch():
    # Iterate through the packs folder and import every folder found.
    # for pack in load_packs():
    #     print(pack)
    # # Iterate through the resources folder and load every pack found.
    # load_resources()
    window = AWareWindow()
    
    # At the moment just launch straight into the play view with every game and transition.
    view = MainMenuView() # PlayView(tuple(get_loaded_games()), tuple(get_loaded_transitions()), tuple(get_loaded_fails()))
    window.run(view)