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

        self.direction, self.frame = self.WEST, self.FRAMES[2]
        self.image = self.sprite_arr[self.direction][self.frame]

        self.rect = self.image.get_rect()
        self.rect.center = self.curr_center

        self.speed, self.multiplier = [-1, 0], None
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

        self.curr_tile = self._update_tile()


    def move(self, direction):
        if direction == "north":

            if ((self.speed == [-1, 0]) or (self.speed == [1, 0])) and (self._is_legal(self.curr_tile[0], self.curr_tile[1] - 1)):  # west -> north <- east

                center = ((self.rect.centerx // TILE_SIZE) * TILE_SIZE) + self.CENTER_X
                pos = (self.rect.centerx - center)

                if pos < 0:  # pre-turn if coming from west, post-turn if coming from east
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery - 1)

                if pos > 0:  # pre-turn if coming from east, post-turn if coming from west
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery - 1)

            self.speed, self.direction = [0, -1], self.NORTH

        if direction == "west":

            if ((self.speed == [0, -1]) or (self.speed == [0, 1])) and (self._is_legal(self.curr_tile[0] - 1, self.curr_tile[1])):  # north -> west <- south
                
                center = ((self.rect.centery // TILE_SIZE) * TILE_SIZE) + self.CENTER_Y
                pos = (self.rect.centery - center)

                if pos < 0:  # pre-turn if coming from north, post-turn if coming from south
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery + 1)
                
                if pos > 0:  # pre-turn if coming from south, post-turn if coming from north
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery - 1)

            self.speed, self.direction = [-1, 0], self.WEST

        if direction == "south":

            if ((self.speed == [-1, 0]) or (self.speed == [1, 0])) and (self._is_legal(self.curr_tile[0], self.curr_tile[1] + 1)):  # west -> south <- east

                center = ((self.rect.centerx // TILE_SIZE) * TILE_SIZE) + self.CENTER_X
                pos = (self.rect.centerx - center)

                if pos < 0:  # pre-turn if coming from west, post-turn if coming from east
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery + 1)

                if pos > 0:  # pre-turn if coming from east, post-turn if coming from west
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx - 1, self.rect.centery + 1)

            self.speed, self.direction = [0, 1], self.SOUTH

        if direction == "east":

            if ((self.speed == [0, -1]) or (self.speed == [0, 1])) and (self._is_legal(self.curr_tile[0] + 1, self.curr_tile[1])):  # north -> east <- south
                
                center = ((self.rect.centery // TILE_SIZE) * TILE_SIZE) + self.CENTER_Y
                pos = (self.rect.centery - center)

                if pos < 0:  # pre-turn if coming from south, post-turn if coming from north
                    for _ in range(abs(pos)):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery + 1)
                
                if pos > 0:  # pre-turn if coming from north, post-turn if coming from south
                    for _ in range(pos):
                        self.rect.center = (self.rect.centerx + 1, self.rect.centery - 1)

            self.speed, self.direction = [1, 0], self.EAST


    def get_current_tile(self):
        return self.curr_tile


    def _get_tile_coord(self, tile):
        x, y = (tile[0] * TILE_SIZE), (tile[1] * TILE_SIZE)
        return [x, y]


    def _update_tile(self):
        return [self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE]


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

    WIDTH, HEIGHT = 14, 14
    SPRITE_X, SPRITE_Y = [0, 14], [0, 14, 28, 42]
    CENTER_X, CENTER_Y = 4, 4
    EAST, SOUTH, WEST, NORTH = 0, 1, 2, 3
    FRAMES = (0, 1)
    LEFT_TUNNEL, RIGHT_TUNNEL = [0, 17], [27, 17]
    ILLEGAL_TILES = [[12, 13], [15, 13], [12, 25], [15, 25]]
    COMPASS = {
        "north": ([0, -1], NORTH),
        "west": ([-1, 0], WEST),
        "south": ([0, 1], SOUTH),
        "east": ([1, 0], EAST),
    }

    def __init__(self, ghost_id):
        self.ghost = ["BLINKY", "PINKY", "INKY", "CLYDE"][ghost_id]  # Selects respective ghost from list
        self.is_signal = False
        self.behavior = None  # Behaviors are: CHASE, SCATTER, and FRIGHTENED
        self.scatter_count = 0

        pygame.sprite.Sprite.__init__(self)  # Calls the sprite initializer
        self.sprite_arr = [[get_sprite("ghost.bmp", x, y, self.WIDTH, self.HEIGHT) for x in self.SPRITE_X] for y in self.SPRITE_Y]

        self.curr_tile = [14, 14]
        self.curr_center = [
            (self.curr_tile[0] * TILE_SIZE) + self.CENTER_X,
            (self.curr_tile[1] * TILE_SIZE) + self.CENTER_Y,
        ]

        self._speed, self._direction = None, None
        self.speed, self.direction = self.COMPASS["east"]
        self.frame = self.FRAMES[0]
        self.image = self.sprite_arr[self.direction][self.frame]

        self.rect = self.image.get_rect()
        self.rect.center = self.curr_center

        self.is_locked = False
        self.target = None
        self.intersection = None
        
        self.clock = 0


    def update(self):
        self.clock += 1

        if self.clock == 12:
            self.clock = 0
            self.frame -= 1

            if self.frame not in self.FRAMES:
                self.frame = self.FRAMES[1]
        
        if self.is_signal:
            self.speed = np.multiply(self.speed, -1).tolist()
            # self.direction = None
            self.is_signal = False

        self.image = self.sprite_arr[self.direction][self.frame]

        self.curr_center = (
            (self.curr_tile[0] * TILE_SIZE) + self.CENTER_X,
            (self.curr_tile[1] * TILE_SIZE) + self.CENTER_Y,
        )

        self.next_tile = {
            "north": [self.curr_tile[0], self.curr_tile[1] - 1],
            "west": [self.curr_tile[0] - 1, self.curr_tile[1]],
            "south": [self.curr_tile[0], self.curr_tile[1] + 1],
            "east": [self.curr_tile[0] + 1, self.curr_tile[1]],
        }
        
        self.test_tile = {
            "north": {
                "north": [self.curr_tile[0], self.curr_tile[1] - 2],
                "west": [self.curr_tile[0] - 1, self.curr_tile[1] - 1],
                "east": [self.curr_tile[0] + 1, self.curr_tile[1] - 1],
            },
            "west": {
                "north": [self.curr_tile[0] - 1, self.curr_tile[1] - 1],
                "west": [self.curr_tile[0] - 2, self.curr_tile[1]],
                "south": [self.curr_tile[0] - 1, self.curr_tile[1] + 1],
            },
            "south": {
                "west": [self.curr_tile[0] - 1, self.curr_tile[1] + 1],
                "south": [self.curr_tile[0], self.curr_tile[1] + 2],
                "east": [self.curr_tile[0] + 1, self.curr_tile[1] + 1],
            },
            "east": {
                "north": [self.curr_tile[0] + 1, self.curr_tile[1] - 1],
                "south": [self.curr_tile[0] + 1, self.curr_tile[1] + 1],
                "east": [self.curr_tile[0] + 2, self.curr_tile[1]]
            },
        }

        next_pos = self.rect.move(*self.speed)
        min = np.inf

        if (self.rect.center == self.curr_center) and (not self.is_locked):
            if (self.speed == [0, -1]):  # north
                if self._is_legal(*self.next_tile["north"]):
                    for tile in self.test_tile["north"].items():
                        key, value = tile
                        if self._is_legal(*value):
                            origin, target = np.array(value), np.array(self.target)
                            dist = np.linalg.norm(origin - target)

                            if dist < min:
                                self._speed, self._direction = self.COMPASS[key]
                                min = dist

                    self.intersection = self.next_tile["north"]
                    self.is_locked = True
                    self.rect = next_pos

            elif (self.speed == [-1, 0]):  # west
                if self._is_legal(*self.next_tile["west"]):
                    for tile in self.test_tile["west"].items():
                        key, value = tile
                        if (self._is_legal(*value) and (value not in self.ILLEGAL_TILES)):
                            origin, target = np.array(value), np.array(self.target)
                            dist = np.linalg.norm(origin - target)

                            if dist < min:
                                self._speed, self._direction = self.COMPASS[key]
                                min = dist

                    self.intersection = self.next_tile["west"]
                    self.is_locked = True
                    self.rect = next_pos

            elif (self.speed == [0, 1]):  # south
                if self._is_legal(*self.next_tile["south"]):
                    for tile in self.test_tile["south"].items():
                        key, value = tile
                        if self._is_legal(*value):
                            origin, target = np.array(value), np.array(self.target)
                            dist = np.linalg.norm(origin - target)

                            if dist < min:
                                self._speed, self._direction = self.COMPASS[key]
                                min = dist

                    self.intersection = self.next_tile["south"]
                    self.is_locked = True
                    self.rect = next_pos

            elif (self.speed == [1, 0]):  # east
                if self._is_legal(*self.next_tile["east"]):
                    for tile in self.test_tile["east"].items():
                        key, value = tile
                        if (self._is_legal(*value) and (value not in self.ILLEGAL_TILES)):
                            origin, target = np.array(value), np.array(self.target)
                            dist = np.linalg.norm(origin - target)

                            if dist < min:
                                self._speed, self._direction = self.COMPASS[key]
                                min = dist

                    self.intersection = self.next_tile["east"]
                    self.is_locked = True
                    self.rect = next_pos

        elif (self.curr_tile == self.intersection) and self.is_locked:
            if self.rect.center != self.curr_center:
                self.rect = next_pos
            else:
                self.is_locked = False
                self.speed, self.direction = self._speed, self._direction
        
        else:
            if self._is_legal(*np.add(self.curr_tile, self.speed).tolist()):
                self.rect = next_pos

        self.curr_tile = self._update_tile()


    def scatter(self):
        if self.scatter_count != 4:
            if self.ghost == "BLINKY":
                self.target = [25, 0]
            
            elif self.ghost == "PINKY":
                self.target = [2, 0]

            elif self.ghost == "INKY":
                self.target = [27, 35]

            elif self.ghost == "CLYDE":
                self.target = [0, 35]
            
            self.behavior = "SCATTER"
            self.scatter_count += 1
            self.is_locked = False
            self.is_signal = True


    def chase(self, target):
        self.target = target
        self.behavior = "CHASE"
        self.is_locked = False
        self.is_signal = True


    def get_behavior(self):
        return self.behavior


    def _update_tile(self):
        return [self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE]


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
    frames, seconds = 0, 0

    while True:  # The game's main loop
        clock.tick(60)

        screen.fill((0,0,0))
        screen.blit(*board)

        frames += 1
        if frames == 60:
            frames = 0
            seconds += 1
        # print(seconds)

        if blinky.get_behavior() == None:
            blinky.scatter()

        if (seconds == 7) and (blinky.get_behavior() != "CHASE"):
            blinky.chase(pacman.get_current_tile())
            seconds = 0
            print("MODE CHANGE: CHASE")
        elif (seconds == 20) and (blinky.get_behavior() != "SCATTER"):
            blinky.scatter()
            seconds = 0
            print("MODE CHANGE: SCATTER")

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
