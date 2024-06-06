from src.public.ProjectGlobals import *
from src.public.ProjectConstants import *

from .Game import Game

import pygame

import logging
import sys



def start_game():
    # Init global variables
    global_init()

    # Init Pygame
    pygame.init()
    pygame.display.set_caption(GAME_CAPTION)

    # Screen
    SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    set_value("SCREEN", SCREEN)

    # Init Font
    pygame.font.init()
    FONT = pygame.font.SysFont('Arial', 20)
    set_value("FONT", FONT)

    # Game Instance
    GAME = Game()
    GAME.after_init()

    # FPS Control
    clock = pygame.time.Clock()
    # Main loop flag
    GameRunning = True
    while GameRunning:

        """Events Begin"""
        # Deal all the events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                GameRunning = False

        GAME.update_events(events)
        """Events End"""

        # Clear the screen
        SCREEN.fill(WHITE)

        """Draw Begin"""
        # Draw all game elements
        GAME.draw_elements()

        """Draw End"""

        # Update display
        # pygame.display.update()
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Exit Pygame
    pygame.quit()
    sys.exit()
