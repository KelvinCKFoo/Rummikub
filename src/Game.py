from .Pool import *
from .Table import *
from .Rack import *
from .Button import *
from .Text import *
from .Player import *
from .ScoreBoard import ScoreBoard

from .Timer import *


@SingletonDecorator
class Game(Base):

    def __init__(self, *args, **kwargs):
        super().__init__()
        # Game status (State Enum)
        self.status = GameStatus.MAIN_MENU.value
        # Show score board after there is a winner of each round
        self.round_idx = 0
        # Your name
        self.your_name = "You"
        # Players count
        self.__players_count = 2

        # Main Menu
        self.img_main_menu = pygame.image.load(Path(IMG_DIR, "main_menu.png"))
        self.img_main_menu = pygame.transform.scale(self.img_main_menu, (SCREEN_W, SCREEN_H))

    def after_init(self):
        set_value("GAME", self)
        # Tiles
        self.__tiles = Tiles()
        # Pool
        self.__pool = Pool()
        # Table
        self.__table = Table()

        """Main Menu"""
        # StartGame button
        self.btn_start = Button_Start(
            BTN_START_X, BTN_START_Y, BTN_START_W, BTN_START_H, "START", WHITE
        )

        """Game Settings"""
        self.btn_minus_player = Button_MinusPlayer(
            BTN_MINUS_X, BTN_MINUS_Y, BTN_MINUS_W, BTN_MINUS_H, "-", GREEN
        )
        self.btn_plus_player = Button_PlusPlayer(
            BTN_PLUS_X, BTN_PLUS_Y, BTN_PLUS_W, BTN_PLUS_H, "+", RED
        )
        self.btn_confirm = Button_Confirm(
            BTN_CONFIRM_X, BTN_CONFIRM_Y, BTN_CONFIRM_W, BTN_CONFIRM_H, "Confirm", BLACK
        )
        self.player_num = Player_Num(
            PLAYER_NUM_X, PLAYER_NUM_Y, PLAYER_NUM_W, PLAYER_NUM_H, "PlayerNum", BLACK
        )

        # """Pick Tile"""
        # # PickTile button
        # self.btn_picktile = Button_PickTile(
        #     SCREEN_W * 0.5 - 100, SCREEN_H * 0.5, 200, 100, "pick tile", WHITE
        # )

        """Playing"""
        # Computer Control
        self.btn_com_con = Button_ComputerControl(
            BTN_COMPUTERCONTROL_X, BTN_COMPUTERCONTROL_Y, BTN_COMPUTERCONTROL_W, BTN_COMPUTERCONTROL_H, "ComCon", BLUE
        )
        # End Turn
        self.btn_endturn = Button_EndTurn(
            BTN_ENDTURN_X, BTN_ENDTURN_Y, BTN_ENDTURN_W, BTN_ENDTURN_H, "End Turn", GREY
        )

        # Rollback button
        self.btn_rollback = Button_RollBack(
            BTN_ROLLBACK_X, BTN_ROLLBACK_Y, BTN_ROLLBACK_W, BTN_ROLLBACK_H, "RB", RED
        )
        # Draw button
        self.btn_draw_tile = Button_Draw(
            BTN_DRAW_X, BTN_DRAW_Y, BTN_DRAW_W, BTN_DRAW_H, "Draw", GREEN
        )

        # Fold button
        self.btn_fold = Button_Fold(
            BTN_FOLD_X, BTN_FOLD_Y, BTN_FOLD_W, BTN_FOLD_H, "Fold", GREEN
        )

        # Set unavailable
        self.btn_endturn.set_click_enabled(False)
        self.btn_rollback.set_click_enabled(False)
        self.btn_draw_tile.set_click_enabled(False)

        # GetRun
        self.btn_get_run = Button_GetRun(
            BTN_GETRUN_X, BTN_GETRUN_Y, BTN_GETRUN_W, BTN_GETRUN_H, "Run", RED
        )
        # GetGroup
        self.btn_get_group = Button_GetGroup(
            BTN_GETGROUP_X, BTN_GETGROUP_Y, BTN_GETGROUP_W, BTN_GETGROUP_H, "Group", BLUE
        )
        # Test
        self.btn_test = Button_Test(100 * 0, 0, 80, 50, "test", RED)

        # button_list playing
        self.__btn_list_while_playing: list[Button] = [
            # Debug
            # self.btn_test,

            self.btn_com_con,

            self.btn_endturn,
            self.btn_rollback,
            self.btn_draw_tile,

            self.btn_get_group,
            self.btn_get_run,

            self.btn_fold,
        ]

        # Countdown Timer
        self.__timer = CountdownTimer(
            COUNTDOWN_TIMER_X, COUNTDOWN_TIMER_Y, COUNTDOWN_TIMER_W, COUNTDOWN_TIMER_H
        )

        # Message Box
        self.__message_box = Message_Box(
            MESSAGE_BOX_X, MESSAGE_BOX_Y, MESSAGE_BOX_W, MESSAGE_BOX_H, "MessageBox", BLACK
        )

        # """Score Board"""
        self.score_board = ScoreBoard(
            SB_X, SB_Y, SB_W, SB_H
        )

        # Set global variables
        set_value("TILES", self.__tiles)
        set_value("POOL", self.__pool)
        set_value("TABLE", self.__table)
        set_value("TIMER", self.__timer)

    def set_players_count(self, number_of_players: int):
        # Input validation
        if not isinstance(number_of_players, int) or not (2 <= number_of_players <= 4):
            number_of_players = 2
        self.__players_count = number_of_players

        # Player Info
        self.text_player_info = Text_PlayerInfo(
            MESSAGE_BOX_X + SCREEN_W * 0.01, MESSAGE_BOX_Y + SCREEN_W * 0.05, ""
        )

        # text_list
        self.__txt_list_while_playing: list[Text] = [
            self.text_player_info,
        ]

        # Player_AI and its rack
        self.__rack_list: list[Rack] = []
        self.__players_list: list[Player] = []

        for i in range(1, self.__players_count):
            rack_ai = Rack_AI()
            self.__rack_list.append(rack_ai)
            player_ai = Player_AI(
                "AI No.%d" % i, rack_ai, Path(IMG_DIR, "player_%d.png" % i),
                PLAYER_X[i - 1], PLAYER_Y[i - 1], PLAYER_W, PLAYER_H, RED,
            )

            self.__players_list.append(player_ai)
            rack_ai.set_player(player_ai, i - 1)
            rack_ai.make_grids()

        # Player_User and its rack
        self.__rack_user = Rack_User()
        self.__rack_list.append(self.__rack_user)
        self.__player_user = Player_User(self.your_name, self.__rack_user)
        self.__players_list.append(self.__player_user)
        # Current player index
        # The order of the players is determined based on the tile picked after started
        self.__player_idx = 0 % self.__players_count

        # Pick Tile
        self.random_tile_numbers = random.sample(TILE_NUMBER_RANGE, k=number_of_players)

        set_value("PLAYER_USER", self.__player_user)
        set_value("RACK_USER", self.__rack_user)

    def next_game_status(self, cur_status: int = None):
        if cur_status is None:
            cur_status = self.status

        self.status = cur_status + 1

    @property
    def players_count(self) -> int:
        return self.__players_count

    @players_count.setter
    def players_count(self, cnt):
        self.__players_count = cnt

    @property
    def tiles(self) -> Tiles:
        return self.__tiles

    @property
    def pool(self) -> Pool:
        return self.__pool

    @property
    def table(self) -> Table:
        return self.__table

    @property
    def buttons_playing(self):
        return self.__btn_list_while_playing

    @property
    def texts_playing(self):
        return self.__txt_list_while_playing

    @property
    def timer(self):
        return self.__timer

    @property
    def current_player(self) -> Player:
        self.__curr_player = self.__players_list[self.player_idx]
        return self.__curr_player

    @property
    def players_list(self):
        return self.__players_list

    @property
    def player_idx(self):
        return self.__player_idx % self.__players_count

    @property
    def rack_list(self):
        return self.__rack_list

    @property
    def player_user(self):
        return self.__player_user

    @property
    def rack_user(self):
        return self.__rack_user

    def set_player_idx(self, idx):
        self.__player_idx = idx % self.players_count
        self.__curr_player = self.__players_list[self.player_idx]

    def switch_to_next_player(self) -> Player:
        self.__player_idx = (self.player_idx + 1) % self.players_count
        self.__curr_player = self.__players_list[self.player_idx]
        return self.current_player

    def player_round_start(self):
        # Save current tiles
        player = self.current_player
        player.start_turn()

        # Reset Timer or Forward to next game status
        self.timer.reset()

    def is_player_user_turn(self):
        return self.current_player == self.player_user

    def update_events(self, events):
        if self.status == GameStatus.MAIN_MENU.value:
            self.btn_start.update(events)

        elif self.status == GameStatus.GAME_SETTINGS.value:
            self.btn_minus_player.update(events)
            self.btn_plus_player.update(events)
            self.btn_confirm.update(events)

        # elif self.status == GameStatus.PICK_TILE.value:
        #     self.btn_picktile.update(events)

        elif self.status == GameStatus.PLAYING.value:
            for button in self.buttons_playing:
                button.update(events)

            for tile in self.tiles.tiles:
                tile.update(events)

            for player in self.players_list:
                player.update(events)

            for rack in self.rack_list:
                rack.update(events)

            self.timer.update()

        elif self.status == GameStatus.SCORE_BOARD.value:
            self.score_board.update(events)

    def draw_main_menu(self):
        self.screen.blit(self.img_main_menu, self.img_main_menu.get_rect(topleft=(0, 0)))

        self.btn_start.draw(color=BLACK)

    def draw_game_settings(self):
        img = pygame.image.load(Path(IMG_DIR, "game_settings.png"))
        image = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        self.screen.blit(image, image.get_rect(topleft=(0, 0)))

        self.btn_minus_player.draw()
        self.btn_plus_player.draw()
        self.btn_confirm.draw()
        self.player_num.draw()

    # def draw_pick_tile(self):
    #     img = pygame.image.load(Path(IMG_DIR, "blank.png"))
    #     image = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
    #     self.screen.blit(image, image.get_rect(topleft=(0, 0)))
    #
    #     self.btn_picktile.draw(color=BLACK)

    def draw_playing(self):
        img = pygame.image.load(Path(IMG_DIR, "main_background.png"))
        image = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        self.screen.blit(image, image.get_rect(topleft=(0, 0)))

        self.draw_message_box()
        self.draw_texts()
        self.draw_pool()
        self.draw_buttons()
        self.draw_table()
        self.draw_racks()
        self.draw_tiles()
        self.draw_timer()
        self.draw_players()

    def draw_score_board(self):
        self.score_board.draw()

    def draw_texts(self):
        for text in self.texts_playing:
            text.draw(self.current_player.name)

    def draw_buttons(self):
        for button in self.buttons_playing:
            button.draw()

    def draw_table(self):
        self.table.draw()

    def draw_pool(self):
        self.pool.draw()

    def draw_racks(self):
        for rack in self.rack_list:
            rack.draw()

    def draw_tiles(self):
        for tile in self.tiles.tiles:
            tile.draw()

    def draw_timer(self):
        self.__timer.draw()

    def draw_message_box(self):
        self.__message_box.draw()

    def draw_players(self):
        for player in self.players_list:
            player.draw()

    def draw_elements(self):
        if self.status == GameStatus.MAIN_MENU.value:
            self.draw_main_menu()

        elif self.status == GameStatus.GAME_SETTINGS.value:
            self.draw_game_settings()

        # elif self.status == GameStatus.PICK_TILE.value:
        #     self.draw_pick_tile()

        elif self.status == GameStatus.PLAYING.value:
            self.draw_playing()

        elif self.status == GameStatus.SCORE_BOARD.value:
            self.draw_score_board()
