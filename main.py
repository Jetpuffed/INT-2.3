# Huge thanks to this document outlining Pac-Man's game mechanics and logic
# https://www.gamasutra.com/view/feature/3938/the_pacman_dossier.php

import os
import sys
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

    WIDTH, HEIGHT = 13, 13
    SPRITE_X, SPRITE_Y = [0, 13, 26], [0, 13, 26, 39]
    CENTER_X, CENTER_Y = 3, 3
    EAST, SOUTH, WEST, NORTH = 0, 1, 2, 3
    FRAMES = (0, 1, 2)
    LEFT_TUNNEL, RIGHT_TUNNEL = [0, 17], [27, 17]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # Calls the sprite initializer
        self.sprite_arr = [[get_sprite("pacman.bmp", x, y, self.WIDTH, self.HEIGHT) for x in self.SPRITE_X] for y in self.SPRITE_Y]

        self.curr_tile = [14, 26]
        self.curr_center = [
            (self.curr_tile[0] * TILE_SIZE) + self.CENTER_X,
            (self.curr_tile[1] * TILE_SIZE) + self.CENTER_Y,
        ]

        self.direction, self.frame = self.EAST, self.FRAMES[2]
        self.image = self.sprite_arr[self.direction][self.frame]

        self.rect = self.image.get_rect()
        self.rect.center = self.curr_center

        self.speed, self.multiplier = [1, 0], None
        self.is_moving = False
        
        self.clock = 0
    

    def update(self):
        self.is_moving = True if not self.speed == [0, 0] else False


        if self.is_moving:
            self.clock += 1

            if self.clock == 3:
                self.clock = 0
                self.frame -= 1

                if self.frame not in self.FRAMES:
                    self.frame = self.FRAMES[2]

        self.image = self.sprite_arr[self.direction][self.frame]

        self.curr_center = [
            (self.curr_tile[0] * TILE_SIZE) + self.CENTER_X,
            (self.curr_tile[1] * TILE_SIZE) + self.CENTER_Y,
        ]

        next_pos = self.rect.move((self.speed[0], self.speed[1]))

        if self.speed == [0, -1]:  # north
            if self._is_legal(self.curr_tile[0], self.curr_tile[1] - 1):
                self.rect.centery = next_pos.centery

            else:
                if self.curr_center[1] <= next_pos.centery:
                    self.rect.centery = next_pos.centery
                
                else:
                    self.speed = [0, 0]

        if self.speed == [-1, 0]:  # west
            if self._is_legal(self.curr_tile[0] - 1, self.curr_tile[1]):
                self.rect.centerx = next_pos.centerx

            else:
                if (self.LEFT_TUNNEL >= self.curr_tile > [(self.LEFT_TUNNEL[0] - 3), self.LEFT_TUNNEL[1]]) or (self.RIGHT_TUNNEL < self.curr_tile <= [(self.RIGHT_TUNNEL[0] + 3), self.RIGHT_TUNNEL[1]]):
                    self.rect.centerx = next_pos.centerx

                elif self.curr_tile == [(self.LEFT_TUNNEL[0] - 3), self.LEFT_TUNNEL[1]]:
                    self.rect.centerx = self._get_tile_coord((self.RIGHT_TUNNEL[0] + 3, self.RIGHT_TUNNEL[1]))[0]

                else:
                    if self.curr_center[0] <= next_pos.centerx:
                        self.rect.centerx = next_pos.centerx
                    
                    else:
                        self.speed = [0, 0]

        if self.speed == [0, 1]:  # south
            if self._is_legal(self.curr_tile[0], self.curr_tile[1] + 1):
                self.rect.centery = next_pos.centery

            else:
                if self.curr_center[1] >= next_pos.centery:
                    self.rect.centery = next_pos.centery
                
                else:
                    self.speed = [0, 0]

        if self.speed == [1, 0]:  # east
            if self._is_legal(self.curr_tile[0] + 1, self.curr_tile[1]):
                self.rect.centerx = next_pos.centerx

            else:
                if (self.RIGHT_TUNNEL <= self.curr_tile < [(self.RIGHT_TUNNEL[0] + 3), self.RIGHT_TUNNEL[1]]) or (self.LEFT_TUNNEL > self.curr_tile >= [(self.LEFT_TUNNEL[0] - 3), self.LEFT_TUNNEL[1]]):
                    self.rect.centerx = next_pos.centerx

                elif self.curr_tile == [(self.RIGHT_TUNNEL[0] + 3), self.RIGHT_TUNNEL[1]]:
                    self.rect.centerx = self._get_tile_coord((self.LEFT_TUNNEL[0] - 3, self.LEFT_TUNNEL[1]))[0]
                
                else:
                    if self.curr_center[0] >= next_pos.centerx:
                        self.rect.centerx = next_pos.centerx
                    
                    else:
                        self.speed = [0, 0]

        self._update_tile()


    def move(self, direction):
        if direction == "north":

            if ((self.speed == [-1, 0]) or (self.speed == [1, 0])) and (self._is_legal(self.curr_tile[0], self.curr_tile[1] - 1)):  # west -> north <- east

                pos = (self.rect.centerx - self.curr_center[0])

                if pos < 0:  # pre-turn if coming from west, post-turn if coming from east
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery - 1)

                if pos > 0:  # pre-turn if coming from east, post-turn if coming from west
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery - 1)

            self.speed, self.direction = [0, -1], self.NORTH

        if direction == "west":

            if ((self.speed == [0, -1]) or (self.speed == [0, 1])) and (self._is_legal(self.curr_tile[0] - 1, self.curr_tile[1])):  # north -> west <- south
                
                pos = (self.rect.centery - self.curr_center[1])

                if pos < 0:  # pre-turn if coming from north, post-turn if coming from south
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery + 1)
                
                if pos > 0:  # pre-turn if coming from south, post-turn if coming from north
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery - 1)

            self.speed, self.direction = [-1, 0], self.WEST

        if direction == "south":

            if ((self.speed == [-1, 0]) or (self.speed == [1, 0])) and (self._is_legal(self.curr_tile[0], self.curr_tile[1] + 1)):  # west -> south <- east

                pos = (self.rect.centerx - self.curr_center[0])

                if pos < 0:  # pre-turn if coming from west, post-turn if coming from east
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery + 1)

                if pos > 0:  # pre-turn if coming from east, post-turn if coming from west
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery + 1)

            self.speed, self.direction = [0, 1], self.SOUTH

        if direction == "east":

            if ((self.speed == [0, -1]) or (self.speed == [0, 1])) and (self._is_legal(self.curr_tile[0] + 1, self.curr_tile[1])):  # north -> east <- south
                
                pos = (self.rect.centery - self.curr_center[1])

                if pos < 0:  # pre-turn if coming from north, post-turn if coming from south
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery + 1)
                
                if pos > 0:
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery - 1)

            self.speed, self.direction = [1, 0], self.EAST


    def get_current_tile(self):
        return self.curr_tile


    def _get_tile_coord(self, tile):
        x, y = (tile[0] * TILE_SIZE), (tile[1] * TILE_SIZE)
        return [x, y]


    def _update_tile(self):
        if (self.curr_tile[0] != self.rect.centerx // TILE_SIZE):
            self.curr_tile[0] = self.rect.centerx // TILE_SIZE
        
        if (self.curr_tile[1] != self.rect.centery // TILE_SIZE):
            self.curr_tile[1] = self.rect.centery // TILE_SIZE


    def _is_legal(self, x, y):
        if (x < self.LEFT_TUNNEL[0]) or (x > self.RIGHT_TUNNEL[0]):
            return False
        
        else:
            if np.all(tile_map[x, y]):
                return True

            else:
                return False


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


    def _move(self, target=None):
        next_pos = self.rect.move((self.speed[0], self.speed[1]))

        center_tile = (
            (self.curr_tile[0] * TILE_SIZE) + 4,
            (self.curr_tile[1] * TILE_SIZE) + 4,
        )

        if next_pos.right == X:
            next_pos.left = 1
            self.rect.left = 1
            self._update_tile()
        elif next_pos.left == 0:
            next_pos.right = X - 1
            self.rect.right = X - 1
            self._update_tile()

        if self.ghost == "BLINKY":
            if self._is_legal(next_pos.centerx // TILE_SIZE, next_pos.centery // TILE_SIZE):

                # Ghosts select an exit based on this priority: up, left, down, or right
                if (self.speed == [0, -1]):  # up
                    up, left, right = self.curr_tile[1] - 2, self.curr_tile[0] - 1, self.curr_tile[0] + 1

                    if (up > target[1]) and (self._is_legal(self.curr_tile[0], up)):
                        self.rect.centery = next_pos.centery
                    elif (left > target[0]) and (self._is_legal(left, self.curr_tile[1] - 1)):
                        self.rect.centerx = next_pos.centerx
                        self.curr_y = 2
                        self.speed = [-1, 0]
                    elif (right < target[0]) and (self._is_legal(right, self.curr_tile[1] - 1)):
                        self.rect.centerx = next_pos.centerx
                        self.curr_y = 0
                        self.speed = [1, 0]

                if (self.speed == [-1, 0]):  # left
                    up, left, down = self.curr_tile[1] - 1, self.curr_tile[0] - 2, self.curr_tile[1] + 1

                    if (up > target[1]) and (self._is_legal(self.curr_tile[0] - 1, up)):
                        self.rect.centery = next_pos.centery
                        self.curr_y = 3
                        self.speed = [0, -1]
                    elif (left > target[0]) and (self._is_legal(left, self.curr_tile[1])):
                        self.rect.centerx = next_pos.centerx
                    elif (down < target[1]) and (self._is_legal(self.curr_tile[0] - 1, down)):
                        self.rect.centery = next_pos.centery
                        self.curr_y = 1
                        self.speed = [0, 1]

                if (self.speed == [0, 1]):  # down
                    left, down, right = self.curr_tile[0] - 1, self.curr_tile[1] + 2, self.curr_tile[0] + 1

                    if (left > target[0]) and (self._is_legal(left, self.curr_tile[1] + 1)):
                        self.rect.centerx = next_pos.centerx
                        self.curr_y = 2
                        self.speed = [-1, 0]
                    elif (down < target[1]) and (self._is_legal(self.curr_tile[0], down)):
                        self.rect.centery = next_pos.centery
                    elif (right < target[0]) and (self._is_legal(right, self.curr_tile[1] + 1)):
                        self.rect.centerx = next_pos.centerx
                        self.curr_y = 0
                        self.speed = [1, 0]

                if (self.speed == [1, 0]):  # right
                    up, down, right = self.curr_tile[1] - 1, self.curr_tile[1] + 1, self.curr_tile[0] + 2

                    if (up > target[1]) and (self._is_legal(self.curr_tile[0] + 1, up)):
                        self.rect.centery = next_pos.centery
                        self.curr_y = 3
                        self.speed = [0, -1]
                    elif (down < target[1]) and (self._is_legal(self.curr_tile[0] + 1, down)):
                        self.rect.centery = next_pos.centery
                        self.curr_y = 1
                        self.speed = [0, 1]
                    elif (right < target[0]) and (self._is_legal(right, self.curr_tile[1])):
                        self.rect.centerx = next_pos.centerx
                    
                self._update_tile()


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

        blinky._move(pacman.get_current_tile())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()

                if event.key == K_UP:
                    pacman.move("north")

                if event.key == K_DOWN:
                    pacman.move("south")

                if event.key == K_LEFT:
                    pacman.move("west")

                if event.key == K_RIGHT:
                    pacman.move("east")

        sprites.update()
        sprites.draw(screen)
        pygame.display.flip()
