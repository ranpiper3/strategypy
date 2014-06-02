import pygame

import settings
import bots
from core.players import Player


class Game(object):
    def __init__(self, *args):
        self.args = args
        self.occupied_cells = []
        self.init_screen()
        self.init_bots()
        self.init_players()
        self.done = False
        self.victorious_player = None

    def set_occupied_cells(self):
        """
        Update the list of the cells currently occupied by units
        """
        # TODO: Optimize by adding add update_occupied_cells instead
        self.occupied_cells = [(unit.x, unit.y) for unit in self.units]

    def init_screen(self):
        """
        Initialize screen
        """
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.fps = settings.FPS

    def init_players(self):
        """
        Create Players and load their personal bot
        """
        # I can't initialize players with a list comprehension because
        # Player __init__ need to access Game.players attribute
        # TODO: Code smell?
        self.players = []
        for i, bot_class in enumerate(self.bots):
            player = Player(pk=i, bot_class=bot_class, game=self)
            self.players.append(player)

    def init_bots(self):
        """
        Create bot action functions by getting the name of the
        package/module from the args
        """
        for arg in self.args:
            __import__('bots.{}'.format(arg))
        self.bots = [getattr(bots, arg).Bot for arg in self.args]

    @property
    def units(self):
        """
        All the units in the Game
        """
        return [unit for player in self.players for unit in player.units]

    def event_loop(self):
        """
        Fetch for events
        """
        for event in pygame.event.get():
            self.keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT or self.keys[pygame.K_ESCAPE]:
                self.done = True

    def update(self):
        """
        Fetch all unit positions and action units
        """
        for player in self.players:
            for unit in player.units:
                unit.action()
                self.set_occupied_cells()

    def draw(self):
        """
        Main drawing function called in the infinite loop
        """
        self.screen.fill(settings.BG_COLOR)
        for unit in self.units:
            unit.render()
        self.draw_grid()

    def draw_grid(self):
        """
        Draw a grid according to the game settings
        """
        X, Y = settings.SCREEN_SIZE
        gap_x, gap_y = settings.UNIT_SIZE
        for i in xrange(0, X+1, gap_x):
            pygame.draw.line(
                self.screen,
                settings.GRID_COLOR,
                (i, 0),
                (i, Y),
                1,
            )
        for i in xrange(0, Y+1, gap_y):
            pygame.draw.line(
                self.screen,
                settings.GRID_COLOR,
                (0, i),
                (X, i),
                1,
            )

    def display_caption(self):
        """
        Show the program's FPS in the window handle
        and the winner if there is one
        """
        fps = self.clock.get_fps()
        winner_info = '- WINNER: {} ({})'.format(
            self.victorious_player.name,
            self.victorious_player.get_bot_class_module_name()) \
            if self.victorious_player else ''
        caption = "{} - FPS: {:.2f} {}".format(
            settings.CAPTION, fps, winner_info)
        pygame.display.set_caption(caption)

    def check_for_victory(self):
        """
        Determine whether the game has ended or not and
        set the victorious_player attribute accordingly.
        Condition of victory: all the units should be aligned
        either vertically or horizontaly
        """
        if self.victorious_player:
            return

        for player in self.players:
            positions = [unit.current_cell for unit in player.units]
            xs = set(x for x, y in positions)
            ys = set(y for x, y in positions)
            if len(xs) == 1 or len(ys) == 1:
                # We have a winner :)
                self.victorious_player = player
                self.update_caption_with_victorious_player()

    def update_caption_with_victorious_player(self):
        """
        Update the window caption with the victorious
        player information
        """
        assert self.victorious_player

    def main_loop(self):
        """
        The main loop of the game, can be interrupted by events
        """
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(self.fps)
            self.check_for_victory()
            self.display_caption()
