from .ProjectGlobals import *


class Base:
    def __init__(self, *args, **kwargs):
        self.screen = get_value("SCREEN")
        self.game = get_value("GAME")
        self.font = get_value("FONT")

