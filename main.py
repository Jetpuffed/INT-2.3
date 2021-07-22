import os
import sys
from numpy.lib.shape_base import tile
import pygame
import numpy as np
from pygame.constants import RLEACCEL, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE


WINDOW = X, Y = 224, 288
TILE_SIZE = 8
TILE_X, TILE_Y = X // TILE_SIZE, Y // TILE_SIZE
DOTS = 240
BIG_DOTS = 4


tile_map = np.zeros((X // TILE_SIZE, Y // TILE_SIZE, 2), dtype = bool)

legal_tile = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
    5: [1, 6, 12, 15, 21, 26],
    6: [1, 6, 12, 15, 21, 26],
    7: [1, 6, 12, 15, 21, 26],
    8: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
    9: [1, 6, 9, 18, 21, 26],
    10: [1, 6, 9, 18, 21, 26],
    11: [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 15, 16, 17, 18, 21, 22, 23, 24, 25, 26],
    12: [6, 12, 15, 21],
    13: [6, 12, 15, 21],
    14: [6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21],
    15: [6, 9, 18, 21],
    16: [6, 9, 18, 21],
    17: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
    18: [6, 9, 18, 21],
    19: [6, 9, 18, 21],
    20: [6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21],
    21: [6, 9, 18, 21],
    22: [6, 9, 18, 21],
    23: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
    24: [1, 6, 12, 15, 21, 26],
    25: [1, 6, 12, 15, 21, 26],
    26: [1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 24, 25, 26],
    27: [3, 6, 9, 18, 21, 24],
    28: [3, 6, 9, 18, 21, 24],
    29: [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 15, 16, 17, 18, 21, 22, 23, 24, 25, 26],
    30: [1, 12, 15, 26],
    31: [1, 12, 15, 26],
    32: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
    33: None,
    34: None,
    35: None,
}

for y in range(TILE_Y):
    if legal_tile[y] is not None:
        for x in range(TILE_X):
            if x in legal_tile[y]:
                tile_map[x, y] = (True, True)


def load_image(file, colorkey=None):
    """
    TODO: Make this an elegant and descriptive docstring...
    """

    file_path = os.path.join("assets", file)

    try:
        image = pygame.image.load(file_path)
    except pygame.error as message:
        print("Unable to load image:", file)
        raise SystemExit(message)

    image = image.convert_alpha()

    if colorkey is not None:
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


def get_sprite(file, x, y, width, height):
    """
    TODO: Make this an elegant and descriptive docstring...
    """

    sprite, _ = load_image(file)

    return sprite.subsurface((x, y, width, height))


def load_sound(file):
    """
    TODO: Make this an elegant and descriptive docstring...
    """

    class NoneSound:
        def play(self):
            pass
    
    if not pygame.mixer:
        return NoneSound()
    
    file_path = os.path.join("assets", file)

    try:
        sound = pygame.mixer.Sound(file_path)
    except pygame.error as message:
        print("Unable to load sound:", file)
        raise SystemExit(message)
    
    return sound


class Pacman(pygame.sprite.Sprite):
    """
    TODO: Make this an elegant and descriptive docstring...
    """

    def __init__(self):
        self.WIDTH, self.HEIGHT = 13, 13
        self.SPRITE_X = [0, 13, 26]
        self.SPRITE_Y = [0, 13, 26, 39]

        pygame.sprite.Sprite.__init__(self)  # Calls the sprite initializer
        self.sprite_arr = [[get_sprite("pacman.bmp", x, y, self.WIDTH, self.HEIGHT) for x in self.SPRITE_X] for y in self.SPRITE_Y]

        self.curr_y, self.curr_x = 0, 1
        self.curr_tile = [14, 26]
        self.image = self.sprite_arr[self.curr_y][self.curr_x]
        
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

        self.rect = self.image.get_rect()
        self.rect.center = (self.curr_tile[0] * TILE_SIZE) + 3, (self.curr_tile[1] * TILE_SIZE) + 3

        self.speed = [1, 0]
        self.timer = 0
    

    def update(self):
        self.timer += 1
        if self.timer == 3:
            self.timer = 0
            self.curr_x -= 1
            if self.curr_x < 0:
                self.curr_x = 2

        self.image = self.sprite_arr[self.curr_y][self.curr_x]

        next_pos = self.rect.move((self.speed[0], self.speed[1]))

        if next_pos.right == X:
            next_pos.left = 1
            self.rect.left = 1
            self._update_tile()
        elif next_pos.left == 0:
            next_pos.right = X - 1
            self.rect.right = X - 1
            self._update_tile()

        center_tile = (
            (self.curr_tile[0] * TILE_SIZE) + 3,
            (self.curr_tile[1] * TILE_SIZE) + 3,
        )

        # print("Current tile: " + str(self.curr_tile))
        # print("Current position (x, y): " + str((self.curr_tile[0] * TILE_SIZE, self.curr_tile[1] * TILE_SIZE)))
        # print("Center of tile (x, y): " + str(center_tile))
        # print("Next position (x, y): " + str(next_pos.center) + "\n")

        if self._is_legal(next_pos.centerx // TILE_SIZE, next_pos.centery // TILE_SIZE):
            if (self.speed == [1, 0]) and (next_pos.centery == center_tile[1]):
                if not self._is_legal(self.curr_tile[0] + 1, self.curr_tile[1]):
                    if next_pos.centerx <= ((self.curr_tile[0] + 1) * TILE_SIZE) - 5:
                        self.rect.centerx = next_pos.centerx
                else:
                    self.rect.centerx = next_pos.centerx

            if (self.speed == [-1, 0]) and (next_pos.centery == center_tile[1]):
                if not self._is_legal(self.curr_tile[0] - 1, self.curr_tile[1]):
                    if next_pos.centerx >= ((self.curr_tile[0] - 1) * TILE_SIZE) + 11:
                        self.rect.centerx = next_pos.centerx
                else:
                    self.rect.centerx = next_pos.centerx

            if (self.speed == [0, 1]) and (next_pos.centerx == center_tile[0]):
                if not self._is_legal(self.curr_tile[0], self.curr_tile[1] + 1):
                    if next_pos.centery <= ((self.curr_tile[1] + 1) * TILE_SIZE) - 5:
                        self.rect.centery = next_pos.centery
                else:
                    self.rect.centery = next_pos.centery

            if (self.speed == [0, -1]) and (next_pos.centerx == center_tile[0]):
                if not self._is_legal(self.curr_tile[0], self.curr_tile[1] - 1):
                    if next_pos.centery >= ((self.curr_tile[1] - 1) * TILE_SIZE) + 11:
                        self.rect.centery = next_pos.centery
                else:
                    self.rect.centery = next_pos.centery

        self._update_tile()


    def _move(self, direction):
        compass = {
            "north": [[0, -1], 3],
            "south": [[0, 1], 1],
            "east": [[1, 0], 0],
            "west": [[-1, 0], 2],
        }

        if compass[direction] != self.speed:
            self.curr_y = compass[direction][1]
            self.speed = compass[direction][0]


    def _update_tile(self):
        if (self.curr_tile[0] != self.rect.centerx // TILE_SIZE):
            self.curr_tile[0] = self.rect.centerx // TILE_SIZE
        
        if (self.curr_tile[1] != self.rect.centery // TILE_SIZE):
            self.curr_tile[1] = self.rect.centery // TILE_SIZE


    def _is_legal(self, x, y):
        if np.all(tile_map[x, y]):
            return True
        else:
            return False


    def get_current_tile(self):
        return self.curr_tile


class Ghost(pygame.sprite.Sprite):
    """
    TODO: Make this an elegant and descriptive docstring...
    """

    def __init__(self, ghost_id):
        self.WIDTH, self.HEIGHT = 14, 14
        self.SPRITE_X = [0, 14]
        self.SPRITE_Y = [0, 14, 28, 42]

        self.ghost = ["BLINKY", "PINKY", "INKY", "CLYDE"][ghost_id]  # Selects respective ghost from list
        self.behavior = None  # Behaviors are: CHASE, SCATTER, and FRIGHTENED

        pygame.sprite.Sprite.__init__(self)  # Calls the sprite initializer
        self.sprite_arr = [[get_sprite("ghost.bmp", x, y, self.WIDTH, self.HEIGHT) for x in self.SPRITE_X] for y in self.SPRITE_Y]

        self.curr_y, self.curr_x = 0, 0
        self.curr_tile = [14, 14]
        self.image = self.sprite_arr[self.curr_y][self.curr_x]

        self.rect = self.image.get_rect()
        self.rect.center = (self.curr_tile[0] * TILE_SIZE) + 4, (self.curr_tile[1] * TILE_SIZE) + 4

        self.speed = [1, 0]
        self.timer = 0


    def update(self):
        self.timer += 1
        if self.timer == 8:
            self.timer = 0
            if self.curr_x == 0:
                self.curr_x = 1
            else:
                self.curr_x = 0
        
        self.image = self.sprite_arr[self.curr_y][self.curr_x]

        next_pos = self.rect.move((self.speed[0], self.speed[1]))

        if next_pos.right == X:
            next_pos.left = 1
            self.rect.left = 1
            self._update_tile()
        elif next_pos.left == 0:
            next_pos.right = X - 1
            self.rect.right = X - 1
            self._update_tile()

        center_tile = (
            (self.curr_tile[0] * TILE_SIZE) + 4,
            (self.curr_tile[1] * TILE_SIZE) + 4,
        )


    def _move(self, target=None):
        if self.ghost == "BLINKY":
            pass


    def _update_tile(self):
        if (self.curr_tile[0] != self.rect.centerx // TILE_SIZE):
            self.curr_tile[0] = self.rect.centerx // TILE_SIZE
        
        if (self.curr_tile[1] != self.rect.centery // TILE_SIZE):
            self.curr_tile[1] = self.rect.centery // TILE_SIZE


    def _is_legal(self, x, y):
        if np.all(tile_map[x, y]):
            return True
        else:
            return False


if __name__ == "__main__":
    pygame.init()  # Initializes pygame

    flags = pygame.SCALED | pygame.NOFRAME
    screen = pygame.display.set_mode(WINDOW, flags)

    board = load_image("board.bmp")

    pacman = Pacman()
    blinky = Ghost(0)
    sprites = pygame.sprite.RenderClear((pacman, blinky))

    clock = pygame.time.Clock()

    while True:  # The game's main loop
        clock.tick(60)

        screen.fill((0,0,0))
        screen.blit(*board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()

                if event.key == K_UP:
                    pacman._move("north")

                if event.key == K_DOWN:
                    pacman._move("south")

                if event.key == K_LEFT:
                    pacman._move("west")

                if event.key == K_RIGHT:
                    pacman._move("east")

        sprites.update()
        sprites.draw(screen)
        pygame.display.flip()
