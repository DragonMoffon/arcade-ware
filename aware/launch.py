from aware.window import AWareWindow
from aware.finder import load_packs, get_loaded_games, get_loaded_transitions
from engine.play import PlayView
from engine.resources import load_resources

def launch():
    # Iterate through the packs folder and import every folder found.
    load_packs()
    # Iterate through the resources folder and load every pack found.
    load_resources()
    window = AWareWindow()
    
    # At the moment just launch straight into the play view with every game and transition.
    view = PlayView(tuple(get_loaded_games()), tuple(get_loaded_transitions()), ())
    window.run(view)