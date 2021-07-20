import sys
import pygame
import numpy as np

pygame.init()

WINDOW = X, Y = 224, 288
BG_COLOR = (0, 0, 0)  # RGB value
FG_COLOR = (255, 255, 255)  # RGB value

screen = pygame.display.set_mode(WINDOW)

pixel_arr = np.zeros((X, Y, 3), dtype = np.uint8)  # Numpy slicing syntax is denoted by [matrices, rows, columns]

pixel_map = {
    0: None,
    1: None,
    2: None,
    3: [i for i in range(14)],
    4: [0, 13],
    5: [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13],
    6: [0, 2, 5, 7, 11, 13],
    7: [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13],
    8: [0],
    9: [0, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13],
    10: [0, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13],
    11: [0, 7, 8, 13],
    12: [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13],
    13: [5, 7, 8, 9, 10, 11, 13],
    14: [5, 7, 8],
    15: [5, 7, 8, 10, 11, 12],
    16: [0, 1, 2, 3, 4, 5, 7, 8, 10],
    17: [10],
    18: [0, 1, 2, 3, 4, 5, 7, 8, 10],
    19: [5, 7, 8, 10, 11, 12, 13],
    20: [5, 7, 8],
    21: [5, 7, 8, 10, 11, 12, 13],
    22: [0, 1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13],
    23: [0, 13],
    24: [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13],
    25: [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13],
    26: [0, 4, 5],
    27: [0, 1, 2, 4, 5, 7, 8, 10, 11, 12, 13],
    28: [0, 1, 2, 4, 5, 7, 8, 10, 11, 12, 13],
    29: [0, 7, 8, 13],
    30: [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13],
    31: [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13],
    32: [0],
    33: [i for i in range(14)],
    34: None,
    35: None,
}

for y in range(Y // 8):  # Iterates like a raster scanning pattern
    if pixel_map[y] is not None:
        for x in range(X):
            if x in pixel_map[y]:
                flip_x = abs(x - 27)
                pixel_arr[(x * 8):(x * 8) + 7, (y * 8):(y * 8) + 7, :] = FG_COLOR
                pixel_arr[(flip_x * 8):(flip_x * 8) + 7, (y * 8):(y * 8) + 7, :] = FG_COLOR

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    #screen.fill(BG_COLOR)
    pygame.surfarray.blit_array(screen, pixel_arr)
    pygame.display.flip()
