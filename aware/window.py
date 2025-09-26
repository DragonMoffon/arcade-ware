from arcade import Window as ArcadeWindow

class AWareWindow(ArcadeWindow):

    def __init__(self, width: int = 1280, height: int = 720, title: str | None = "Arcade ") -> None:
        super().__init__(width, height, title)