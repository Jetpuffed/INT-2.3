import os
import sys
import pygame
import numpy as np
from pygame.constants import RLEACCEL, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE


WINDOW = X, Y = 224, 288
TILE_SIZE = 8


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
        self.image = self.sprite_arr[self.curr_y][self.curr_x]
        
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

        self.rect = self.image.get_rect()
        self.rect.topleft = 106, 205

        self.speed = [1, 0]
        self.timer = 0
    

    def update(self):
        self.timer += 1
        if self.timer == 2:
            self.timer = 0
            self.curr_x -= 1
            if self.curr_x < 0:
                self.curr_x = 2

        self.image = self.sprite_arr[self.curr_y][self.curr_x]
        self.rect = self.rect.move((self.speed[0], self.speed[1]))


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


class Ghost(pygame.sprite.Sprite):
    """
    TODO: Make this an elegant and descriptive docstring...
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # Calls the sprite initializer
        self.image, self.rect = load_image("ghost.bmp")
    

    def update(self):
        pass


# bound_arr = np.zeros((X, Y, 3), dtype = np.uint8)  # Numpy slicing syntax is denoted by [matrices, rows, columns]

# for y in range(Y // 8):  # Iterates like a raster scanning pattern
#     if pixel_map[y] is not None:
#         for x in range(X):
#             if x in pixel_map[y]:
#                 flip_x = abs(x - 27)
#                 pixel_arr[(x * 8):(x * 8) + 7, (y * 8):(y * 8) + 7, :] = FG_COLOR
#                 pixel_arr[(flip_x * 8):(flip_x * 8) + 7, (y * 8):(y * 8) + 7, :] = FG_COLOR


if __name__ == "__main__":
    pygame.init()  # Initializes pygame

    flags = pygame.SCALED | pygame.NOFRAME
    screen = pygame.display.set_mode(WINDOW, flags)

    board = load_image("board.bmp")

    pacman = Pacman()
    sprites = pygame.sprite.RenderClear((pacman))

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
