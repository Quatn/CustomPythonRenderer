import numpy as np
import testModule as tm

import pygame

pygame.init()
Resolution = (1440, 960)
Canvas = pygame.display.set_mode(Resolution)

# a = np.array([[7, 8, 9], [1, 2, 3], [4, 5, 6]])
# # # print(tm.numpyArr_ListNav(1, a))
b = np.eye(1440, 960)
b = b.astype(int)
# print(b)
pygame.pixelcopy.surface_to_array(b, Canvas)

# Canvas_Arr = np.eye(Resolution[0], Resolution[1])
# Canvas_Arr = Canvas_Arr.astype(int)
# pygame.pixelcopy.surface_to_array(Canvas_Arr, Canvas)
#
# color = 16711680
# tm.drawSquare(color, Resolution[0], (0, 0), Resolution, Canvas_Arr)
# pygame.pixelcopy.array_to_surface(Canvas, Canvas_Arr)
# pygame.display.update()

# print(tm.numpyArr_ListNav(1, 3, a))
# print(tm.drawTriangle(Resolution[1], b, [900, 300], [900, 600], [300, 450], 255))
print(tm.drawTriangle(Resolution[1], b, [300, 600], [600, 600], [900, 150], 255))
print(tm.drawTriangle(Resolution[1], b, [300, 600], [600, 600], [600, 750], 16711680))
# print(tm.drawSquare(256, Resolution[0], (300, 300), (900, 600), b))
pygame.pixelcopy.array_to_surface(Canvas, b)
pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                exit()
