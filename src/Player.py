from src.public.ProjectConstants import *
from src.public.ProjectGlobals import *

from src.public.Base import Base
from .Tile import Tiles, Tile
from .Rack import Rack
from .Table import Table
from .Timer import PlayerTimer

import pygame

from typing import *
import random


class Player(Base):

    def __init__(self, name: str, rack: Rack, *args, **kwargs):
        super().__init__()
        self.name = name
        self.rack = rack

        # AI's card default UnFold
        self.ai_tiles_fold = True

        # Flag for ice broken (Only reset after next ROUND!)
        self.flag_has_broken_ice = False

        # Two tiles for draw
        self.two_tiles = []
        self.flag_draw_two_tile = False
        self.flag_return_drawn_one_tile = False
        # Self Timer
        self.time_limit = TIME_LIMIT
        self.player_timer = PlayerTimer()

        # Computer Control
        self.computer_control = True

        # Score
        self.score = 0

    def __str__(self):
        return f"Player: {self.name}"

    def __repr__(self):
        return str(self)

    def is_computer_control_on(self):
        return self.computer_control

    def set_ai_tiles_fold(self, fold: bool = False):
        self.ai_tiles_fold = fold
        self.update_rack_tile_status()

    def update_rack_tile_status(self):
        for tile in self.rack.tiles:
            tile.setFold(self.ai_tiles_fold)
            # tile.draw()

    def start_turn(self):
        print(self, "start turn!", "-" * 50)
        print(self, "rack tiles", self.rack.tiles)
        if self.is_computer_control_on():
            # Random Time Limit (When AI takes control)
            self.time_limit = random.randint(TIME_LIMIT_MIN, TIME_LIMIT_MIN + TIME_LIMIT_MAX_FOR_AI_RESOLVE)

        self.reset()
        self.rack.reset()

        # Set User's End Turn Button Available
        if self.game.is_player_user_turn():
            self.game.btn_endturn.set_click_enabled(True)
            self.game.btn_rollback.set_click_enabled(True)
            self.game.btn_draw_tile.set_click_enabled(True)

    def draw_and_return_random_tiles(self):
        # Can not play any valid tile
        # draw and return tiles
        GAME = self.game
        POOL = GAME.pool
        tiles = POOL.player__draw_2_tiles_from_pool()
        self.handle_2_drawn_tiles_from_pool(tiles)
        self.return_a_random_tile()

    def end_turn(self):
        print(self, "end turn!", "-" * 50)
        self.player_timer.stop()

        GAME = self.game
        TABLE = GAME.table
        POOL = GAME.pool
        PLAYER = GAME.current_player
        RACK = PLAYER.rack

        table_valid, lst_of_lst_tiles = TABLE.check_table_validity()
        if not table_valid:
            print(PLAYER, "Invalid table", lst_of_lst_tiles)
            PLAYER.rollback()
            print(PLAYER, "Rollback")
        else:
            print(PLAYER, "Valid table", lst_of_lst_tiles)

        # Check has broken ice
        if not PLAYER.has_broken_ice():
            # Now table is valid
            # Calculate the value added to table
            pre_number = TABLE.sum_valid_list_of_lst_tile_number(RACK.list_of_lst_table_tiles_turn_begin)
            cur_number = TABLE.sum_valid_list_of_lst_tile_number(TABLE.get_all_lst_tiles_on_table())
            number_added = cur_number - pre_number
            if number_added >= 30:
                PLAYER.break_ice()
                print(PLAYER, "has successfully broken ice", number_added)
            else:
                print(PLAYER, "Not enough number to break ice", number_added)

        # Has drawn tiles but not returned
        drawn_but_not_return = False
        # Has moved tiles from rack to table
        moved_tiles_from_rack_to_table = PLAYER.has_moved_tiles_from_rack_to_table()
        # Has broken ice
        has_broken_ice = PLAYER.has_broken_ice()

        # Drawn tiles
        if PLAYER.has_drawn_two_tile():
            # Returned
            if PLAYER.has_return_drawn_one_tile():
                pass
            # Not returned
            else:
                drawn_but_not_return = True
                # Choose a random tile to return
                PLAYER.return_a_random_tile()

            # Drawn and moved
            if moved_tiles_from_rack_to_table:
                PLAYER.rollback()
            # Drawn but not moved
            else:
                pass

        else:
            # Not broken ice
            if not has_broken_ice:
                # Moved
                if moved_tiles_from_rack_to_table:
                    PLAYER.rollback()
                    # Force to draw tiles
                    PLAYER.draw_and_return_random_tiles()
                # Not moved
                else:
                    # Force to draw tiles
                    PLAYER.draw_and_return_random_tiles()
            else:
                # Broken ice and moved
                if moved_tiles_from_rack_to_table:
                    pass
                # Not moved
                else:
                    # Force to draw tiles
                    PLAYER.draw_and_return_random_tiles()

        # Time is up
        if GAME.timer.is_time_up():
            print(PLAYER, "time is up, penalty applied!")
            tiles = POOL.penalty__draw_1_tiles()
            for tile in tiles:
                # Add tiles to rack
                RACK.add_tile(tile)

        # GAME = self.game
        # POOL = GAME.pool
        # Check Winner
        for idx, rack in enumerate(GAME.rack_list):
            # Winner Condition Check
            if rack.get_tile_count() <= 0:
                winner_idx = idx
                break
        else:
            winner_idx = -1

        if winner_idx != -1:
            print("Round Over, Winner is", winner_idx, GAME.players_list[winner_idx])
            GAME.round_winner_idx = winner_idx

            # Calculate Score
            for player in GAME.players_list:
                player.calculate_score()

            GAME.next_game_status(GameStatus.PLAYING.value)
            return

        elif POOL.get_tile_count() == 0:
            print("Round Over, Run out of tiles!")
            for player in GAME.players_list:
                player.calculate_score()

            cmp_player = GAME.players_list[:]
            cmp_player.sort(key=lambda x: x.score)
            winner = cmp_player[-1]
            winner_idx = GAME.players_list.index(winner)

            print("Round Over, Winner is", winner_idx, GAME.players_list[winner_idx])
            GAME.round_winner_idx = winner_idx
            GAME.next_game_status(GameStatus.PLAYING.value)
            return

        else:
            GAME.switch_to_next_player()
            GAME.player_round_start()

    def auto_play_algorithm_v1(self):
        GAME = self.game
        TABLE = GAME.table
        PLAYER = GAME.current_player
        RACK = PLAYER.rack

        # Auto-Play Second Edition
        tile_played = False
        valid_run = Tiles.group_by_run(RACK.tiles)[0]
        for run in valid_run[:]:
            if Tiles.is_a_run(run):
                tile_played = True
                valid_run.remove(run)
                for tile in run:
                    RACK.play_tile(tile)
                TABLE.place_tiles(run)

        valid_group = Tiles.group_by_number(RACK.tiles)[0]
        for group in valid_group[:]:
            if Tiles.is_a_group(group):
                tile_played = True
                valid_group.remove(group)
                for tile in group:
                    RACK.play_tile(tile)
                TABLE.place_tiles(group)

        # if can not play any valid tile
        if not tile_played:
            self.draw_and_return_random_tiles()

    def auto_play_algorithm(self):
        GAME = self.game

        if not GAME.current_player == self:
            return

        TABLE = GAME.table
        PLAYER = GAME.current_player
        RACK = PLAYER.rack

        pre_rack_tiles = RACK.tiles

        if PLAYER.has_broken_ice():
            used_tiles, final_table = Tiles.find_all_combinations(
                pre_rack_tiles, TABLE.get_all_lst_tiles_on_table())
        else:
            used_tiles, final_table = Tiles.find_all_combinations(
                pre_rack_tiles)
            tmp = TABLE.get_all_lst_tiles_on_table()
            tmp.extend(final_table)
            final_table = tmp

        for tile in used_tiles:
            RACK.play_tile(tile)
            TABLE.add_tile(tile)

        TABLE.relocate_tiles(final_table)

        if not used_tiles:
            PLAYER.draw_and_return_random_tiles()

    def set_two_tiles(self, tiles: list[Tile]):
        self.two_tiles = tiles

    def is_among_the_tile_drawn_from_pool(self, tile):
        return tile in self.two_tiles

    def drawn_two_tile(self, bol: bool = True):
        self.flag_draw_two_tile = bol

    def reset(self):
        self.drawn_two_tile(False)
        self.set_two_tiles([])
        self.flag_return_drawn_one_tile = False

        self.player_timer.start()

    def has_broken_ice(self):
        return self.flag_has_broken_ice

    def break_ice(self):
        self.flag_has_broken_ice = True

    def has_drawn_two_tile(self):
        return self.flag_draw_two_tile

    def return_drawn_one_tile(self):
        self.flag_return_drawn_one_tile = True

    def has_return_drawn_one_tile(self):
        return self.flag_return_drawn_one_tile

    def has_moved_tiles_from_rack_to_table(self):
        RACK = self.rack
        # TABLE = get_value("TABLE")
        # cur_tiles = TABLE.tiles
        # set_table_changed = set(cur_tiles) - set(RACK.list_of_lst_table_tiles_turn_begin)
        set_rack_changed = set(RACK.rack_tiles_turn_begin) - set(RACK.tiles)

        # # Debug
        # # if set_table_changed:
        # #     print(self, "table changed", set_table_changed)
        # if set_rack_changed:
        #     print(self, "rack changed", set_rack_changed)

        # return set_table_changed or set_rack_changed
        return set_rack_changed

    def return_a_random_tile(self):
        # Choose a random tile to return
        tile_lst = random.sample(self.two_tiles, k=min(1, len(self.two_tiles)))
        if tile_lst:
            tile = tile_lst[0]
            self.rack.play_tile(tile)
            POOL = get_value("POOL")
            POOL.add_tile(tile)
            print(self, "return a random tile:", tile)
        self.return_drawn_one_tile()

    def handle_2_drawn_tiles_from_pool(self, tiles):
        # # Debug
        # print(self, "draw two tiles:", tiles)

        for tile in tiles:
            # Bug fix: Preset fold, Tiles would not flash
            tile.setFold(self.ai_tiles_fold)
            tile.draw()
            # Add tiles to rack
            self.rack.add_tile(tile)

        if len(tiles) >= 2:
            self.set_two_tiles(tiles)
            self.drawn_two_tile()
        # Corner case, If there is 0 or 1 tile left in the pool
        # Make it there, mark it has returned the tile!
        else:
            self.return_drawn_one_tile()

    def rollback(self):
        self.rack.restore_tiles_from_turn_begin()

    def update(self, events, *args, **kwargs):
        self.update_rack_tile_status()

        GAME = self.game
        if GAME.current_player != self:
            return

        if self.is_computer_control_on():
            # AI's turn started
            if self.player_timer.seconds_elapsed() > self.time_limit:
                self.auto_play_algorithm()

                self.end_turn()

        for event in events:
            pass

    def draw(self, *args, **kwargs):
        pass

    def calculate_score(self):
        self.score = -Tiles.calculate_score(self.rack.tiles)


class Player_AI(Player):

    def __init__(self, name: str, rack: Rack, img,
                 x, y, w, h,
                 *args, **kwargs
                 ):
        super().__init__(name, rack, *args, **kwargs)

        self.img = pygame.image.load(img)

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)

        self.is_hovered = False

        self.font = pygame.font.SysFont('Arial', 16)

    def end_turn(self):
        super().end_turn()

        self.rack.relocate_tiles_by_number_and_color()

    def rollback(self):
        super().rollback()

    def update(self, events, *args, **kwargs):
        super().update(events, *args, **kwargs)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)
        self.image = pygame.transform.scale(self.img, (self.w, self.h))
        self.image_rect = self.image.get_rect(topleft=(self.x, self.y))
        self.screen.blit(self.image, self.image_rect)

        # Player Name
        self.text_name = self.font.render(str(self), True, BLACK)
        self.text_name_rect = self.text_name.get_rect()
        self.text_name_rect.midtop = (
            self.image_rect.x + self.image.get_width() * 0.5,
            self.image_rect.y + 85
        )
        self.screen.blit(self.text_name, self.text_name_rect)

        # Player Tiles Count
        self.text_tiles_count = self.font.render("Tiles: " + str(self.rack.get_tile_count()), True, RED)
        self.text_tiles_count_rect = self.text_tiles_count.get_rect()
        self.text_tiles_count_rect.midtop = (
            self.text_name_rect.x + self.text_name.get_width() * 0.5,
            self.text_name_rect.y + self.text_name.get_height()
        )
        self.screen.blit(self.text_tiles_count, self.text_tiles_count_rect)


@SingletonDecorator
class Player_User(Player):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ai_tiles_fold = False

        # Computer Control
        self.computer_control = False

    def update(self, events, *args, **kwargs):
        super().update(events, *args, **kwargs)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)
        # Player Tiles Count
        n = str(self.rack.get_tile_count())

    def set_computer_control(self, is_on: bool):
        self.computer_control = is_on

    def rollback(self):
        super().rollback()

    def end_turn(self):
        super().end_turn()

        if self.is_computer_control_on():
            if Tiles.group_by_number(self.rack.tiles)[0]:
                self.rack.relocate_tiles_by_group()
            elif Tiles.group_by_run(self.rack.tiles)[0]:
                self.rack.relocate_tiles_by_group()
            else:
                self.rack.relocate_tiles()
