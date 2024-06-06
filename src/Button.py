import random

from src.public.ProjectGlobals import *
from src.public.ProjectConstants import *
from src.public.Base import Base

from .Tile import Tiles, Tile

import pygame

from typing import *


class Button(Base):

    def __init__(self, x, y, w, h, text="",
                 color: Optional[Tuple[int]] = WHITE,
                 background: Optional[Tuple[int]] = None,
                 hover_color: Optional[Tuple[int]] = (200, 200, 200),
                 *args, **kwargs
                 ):
        super().__init__()

        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(text)
        self.color = color
        self.background = background
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_pressed = False
        self.click_enabled = True

    def update(self, events, *args, **kwargs):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.click_enabled:
                if self.is_hovered:
                    self.is_pressed = True
                    self.clicked()
            elif event.type == pygame.MOUSEBUTTONUP and self.click_enabled:
                if self.is_hovered:
                    self.is_pressed = False
                    self.released()

    def draw(self, new_text: str = None, color: Optional[Tuple[int]] = WHITE, background: Optional[Tuple[int]] = None,
             *args, **kwargs):
        if color is None:
            color = self.color
        if background is None:
            background = self.background
        # Draw the button
        if self.is_hovered:
            pygame.draw.rect(self.screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(self.screen, self.color, self.rect)

        # Render and draw the text
        if new_text is not None:
            self.text = str(new_text)
        text_surface = self.font.render(self.text, True, color, background)
        # text_surface = pygame.transform.scale(text_surface, (self.rect.width, self.rect.height))
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def clicked(self, *args, **kwargs):
        pass

    def released(self, *args, **kwargs):
        pass

    def set_click_enabled(self, bol: bool):
        self.click_enabled = bol


class Button_Start(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        if not self.is_hovered:
            img_start_button = pygame.image.load(Path(BUTTONS_DIR, "start_button.png"))

        else:
            img_start_button = pygame.image.load(Path(BUTTONS_DIR, "start_button_mousedown.png"))

        img_start_button = pygame.transform.scale(img_start_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_start_button, img_start_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        # Switch to next status
        self.game.next_game_status(GameStatus.MAIN_MENU.value)


class Player_Num(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        GAME = get_value("GAME")
        if GAME.players_count == 2:
            img_playernum_button = pygame.image.load(Path(IMG_DIR, "player_num_2.png"))
        elif GAME.players_count == 3:
            img_playernum_button = pygame.image.load(Path(IMG_DIR, "player_num_3.png"))
        else:
            img_playernum_button = pygame.image.load(Path(IMG_DIR, "player_num_4.png"))
        img_playernum_button = pygame.transform.scale(img_playernum_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_playernum_button, img_playernum_button.get_rect(topleft=(self.rect.x, self.rect.y)))


class Button_PlusPlayer(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        # if self.is_hovered:
        #     pygame.draw.rect(self.screen, (200,200,200), self.rect)
        # else:
        #     pygame.draw.rect(self.screen, (100,100,100), self.rect)
        if self.is_hovered:
            img_plusplayer_button = pygame.image.load(Path(BUTTONS_DIR, "plusplayer_button_hover.png"))
            if self.is_pressed:
                img_plusplayer_button = pygame.image.load(Path(BUTTONS_DIR, "plusplayer_button_mousedown.png"))
        else:
            img_plusplayer_button = pygame.image.load(Path(BUTTONS_DIR, "plusplayer_button.png"))

        img_plusplayer_button = pygame.transform.scale(img_plusplayer_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_plusplayer_button, img_plusplayer_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        cnt = self.game.players_count + 1
        self.game.players_count = min(4, cnt)
        # TODO set click enabled


class Button_MinusPlayer(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        if self.is_hovered:
            img_minusplayer_button = pygame.image.load(Path(BUTTONS_DIR, "minusplayer_button_hover.png"))
            if self.is_pressed:
                img_minusplayer_button = pygame.image.load(Path(BUTTONS_DIR, "minusplayer_button_mousedown.png"))
        else:
            img_minusplayer_button = pygame.image.load(Path(BUTTONS_DIR, "minusplayer_button.png"))

        img_minusplayer_button = pygame.transform.scale(img_minusplayer_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_minusplayer_button, img_minusplayer_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        cnt = self.game.players_count - 1
        self.game.players_count = max(2, cnt)


class Button_Confirm(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        if not self.is_hovered:
            img_confirm_button = pygame.image.load(Path(BUTTONS_DIR, "confirm_button.png"))

        else:
            img_confirm_button = pygame.image.load(Path(BUTTONS_DIR, "confirm_button_mousedown.png"))

        img_confirm_button = pygame.transform.scale(img_confirm_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_confirm_button, img_confirm_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        cnt = self.game.players_count
        self.game.set_players_count(cnt)

        # Each player picks a tile; the player with the highest number goes first.
        random_tile_numbers = self.game.random_tile_numbers
        idx = random_tile_numbers.index(max(random_tile_numbers))
        # Determine which player to play first
        self.game.set_player_idx(idx)
        # Switch to next status
        self.game.next_game_status(GameStatus.GAME_SETTINGS.value)
        # Deal tiles to all players
        for rack in self.game.rack_list:
            tiles = self.game.pool.deal__draw_14_tiles()
            for tile in tiles:
                rack.add_tile(tile)

        # Round start
        self.game.player_round_start()


# class Button_PickTile(Button):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def clicked(self, *args, **kwargs):
#         # Each player picks a tile; the player with the highest number goes first.
#         GAME = self.game
#         random_tile_numbers = GAME.random_tile_numbers
#         idx = random_tile_numbers.index(max(random_tile_numbers))
#         # Determine which player to play first
#         self.game.set_player_idx(idx)
#         # self.game.set_player_idx(-1)
#         # Next status
#         self.game.next_game_status(GameStatus.PICK_TILE.value)
#         # Deal tiles to all players
#         for rack in self.game.rack_list:
#             tiles = self.game.pool.deal__draw_14_tiles()
#             for tile in tiles:
#                 rack.add_tile(tile)
#
#         # Round start
#         self.game.player_round_start()


class Button_Test(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.switch_on = False

    def clicked(self, *args, **kwargs):
        # Set Player Computer Control
        GAME = self.game
        PLAYERS = GAME.players_list

        # If on, switch to off
        if self.switch_on:
            for player in PLAYERS:
                if player != GAME.players_list[-1]:
                    player.set_ai_tiles_fold(False)
            self.switch_on = False
        else:
            for player in PLAYERS:
                if player != GAME.players_list[-1]:
                    player.set_ai_tiles_fold(True)
            self.switch_on = True


class Button_Draw(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        if self.click_enabled:
            if self.is_hovered:
                img_draw_button = pygame.image.load(Path(BUTTONS_DIR, "draw_button_hover.png"))
                if self.is_pressed:
                    img_draw_button = pygame.image.load(Path(BUTTONS_DIR, "draw_button_mousedown.png"))
            else:
                img_draw_button = pygame.image.load(Path(BUTTONS_DIR, "draw_button.png"))
        else:
            img_draw_button = pygame.image.load(Path(BUTTONS_DIR, "draw_button_disable.png"))

        img_draw_button = pygame.transform.scale(img_draw_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_draw_button, img_draw_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        GAME = self.game

        if not GAME.is_player_user_turn():
            print("Not your turn, you can not press the button!")
            return

        POOL = GAME.pool
        PLAYER = GAME.current_player
        if PLAYER.has_drawn_two_tile():
            print("Already drawn!")
            return

        # If already moved tiles from rack to the table,
        # restore to the initial status after drawn pressed
        if PLAYER.has_moved_tiles_from_rack_to_table():
            print("Already move tiles from rack to the table, roll back before drawn")
            PLAYER.rollback()
        else:
            print("no need to roll back")

        tiles = POOL.player__draw_2_tiles_from_pool()
        PLAYER.handle_2_drawn_tiles_from_pool(tiles)

        # Set clicked event unavailable，set it available after player's run start
        self.set_click_enabled(False)


class Button_RollBack(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clicked(self, *args, **kwargs):
        GAME = self.game

        if not GAME.is_player_user_turn():
            print("Not your turn, you can not press the button!")
            return

        PLAYER = GAME.current_player
        PLAYER.rollback()

    def draw(self, *args, **kwargs):
        if self.click_enabled:
            if self.is_hovered:
                img_rollback_button = pygame.image.load(Path(BUTTONS_DIR, "rollback_button_hover.png"))
                if self.is_pressed:
                    img_rollback_button = pygame.image.load(Path(BUTTONS_DIR, "rollback_mousedown.png"))
            else:
                img_rollback_button = pygame.image.load(Path(BUTTONS_DIR, "rollback_button.png"))
        else:
            img_rollback_button = pygame.image.load(Path(BUTTONS_DIR, "rollback_disable.png"))

        img_rollback_button = pygame.transform.scale(img_rollback_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_rollback_button, img_rollback_button.get_rect(topleft=(self.rect.x, self.rect.y)))


class Button_EndTurn(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        if self.click_enabled:
            if self.is_hovered:
                img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "endturn_button_hover.png"))
                # if self.is_pressed:
                #    img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "endturn_button_mousedown.png"))
            else:
                img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "endturn_button.png"))
        else:
            img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "endturn_button_disable.png"))

        img_endturn_button = pygame.transform.scale(img_endturn_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_endturn_button, img_endturn_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        GAME = get_value("GAME")

        if not GAME.is_player_user_turn():
            print("Not your turn, you can not press the button!")
            return

        PLAYER = GAME.current_player
        PLAYER.end_turn()

        # Set clicked event unavailable，set it available after player's run start
        self.set_click_enabled(False)

        self.game.btn_rollback.set_click_enabled(False)
        self.game.btn_draw_tile.set_click_enabled(False)


class Button_ComputerControl(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.switch_on = False

    def clicked(self, *args, **kwargs):
        # Set Player Computer Control
        PLAYER_USER = get_value("PLAYER_USER")
        # If on, switch to off
        if self.switch_on:
            PLAYER_USER.set_computer_control(False)
            self.switch_on = False
        else:
            PLAYER_USER.set_computer_control(True)
            self.switch_on = True

        # If pressed, reset the timer_limit to random! Skip the waiting time until next turn.
        PLAYER_USER.time_limit = random.randint(TIME_LIMIT_MIN, TIME_LIMIT_MIN + TIME_LIMIT_MAX_FOR_AI_RESOLVE)

    def draw(self, *args, **kwargs):
        if self.switch_on:
            img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "computercontrol_button_on.png"))
        else:
            img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "computercontrol_button_off.png"))

        img_endturn_button = pygame.transform.scale(img_endturn_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_endturn_button, img_endturn_button.get_rect(topleft=(self.rect.x, self.rect.y)))


class Button_GetGroup(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        if self.is_hovered:
            img_getgroup_button = pygame.image.load(Path(BUTTONS_DIR, "sortgroup_button_hover.png"))
            if self.is_pressed:
                img_getgroup_button = pygame.image.load(Path(BUTTONS_DIR, "sortgroup_button_mousedown.png"))
        else:
            img_getgroup_button = pygame.image.load(Path(BUTTONS_DIR, "sortgroup_button.png"))
        img_getgroup_button = pygame.transform.scale(img_getgroup_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_getgroup_button, img_getgroup_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        RACK_USER = get_value("RACK_USER")
        # RACK_USER.relocate_tiles_by_group()
        RACK_USER.relocate_tiles_by_group_AI()


class Button_GetRun(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, *args, **kwargs):
        if self.is_hovered:
            img_getrun_button = pygame.image.load(Path(BUTTONS_DIR, "sortrun_button_hover.png"))
            if self.is_pressed:
                img_getrun_button = pygame.image.load(Path(BUTTONS_DIR, "sortrun_button_mousedown.png"))
        else:
            img_getrun_button = pygame.image.load(Path(BUTTONS_DIR, "sortrun_button.png"))
        img_getrun_button = pygame.transform.scale(img_getrun_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_getrun_button, img_getrun_button.get_rect(topleft=(self.rect.x, self.rect.y)))

    def clicked(self, *args, **kwargs):
        RACK_USER = get_value("RACK_USER")
        # RACK_USER.relocate_tiles_by_run()
        RACK_USER.relocate_tiles_by_run_AI()


class Message_Box(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.img_messagebox_button = pygame.image.load(Path(IMG_DIR, "message_box.png"))
        self.img_messagebox_button = pygame.transform.scale(self.img_messagebox_button, (self.rect.w, self.rect.h))

    def draw(self, *args, **kwargs):
        self.screen.blit(
            self.img_messagebox_button, self.img_messagebox_button.get_rect(topleft=(self.rect.x, self.rect.y)))


class Button_Fold(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.switch_on = True

    def clicked(self, *args, **kwargs):
        # Set Player Computer Control
        GAME = self.game
        PLAYERS = GAME.players_list

        # If on, switch to off
        if self.switch_on:
            for player in PLAYERS:
                if player != GAME.players_list[-1]:
                    player.set_ai_tiles_fold(False)
            self.switch_on = False
        else:
            for player in PLAYERS:
                if player != GAME.players_list[-1]:
                    player.set_ai_tiles_fold(True)
            self.switch_on = True

    def draw(self, *args, **kwargs):
        if self.switch_on:
            img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "show_ai_tiles_off.png"))
        else:
            img_endturn_button = pygame.image.load(Path(BUTTONS_DIR, "show_ai_tiles_on.png"))

        img_endturn_button = pygame.transform.scale(img_endturn_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_endturn_button, img_endturn_button.get_rect(topleft=(self.rect.x, self.rect.y)))
