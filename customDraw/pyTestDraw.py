import numpy as np
import customDraw as cda

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

# print(cda.draw2DTriangles(Resolution[1], b, [ ((300, 600), (600, 600), (900, 150), 255) , ((300, 900), (600, 900), (900, 150), 255 + 1000) ]))
# print(cda.draw3DTriangles(Resolution[1], b, [ ((-300, 200, 800), (600, 500, 300), (0, 0, 320), 255) ], 100, 1500))

while True:
    print(cda.draw3DTriangles(Resolution[1], b, 
                              [((225, 200, 521), (225, 200, 921), (225, -200, 921), 255), ((-200, 275, 921), (350, 250, 921), (350, 250, 521), 255), ((225, -200, 921), (225, -200, 521), (225, 200, 521), 255), ((350, 250, 521), (-200, 275, 521), (-200, 275, 921), 255), ((350, 250, 521), (450, 300, 521), (-200, 450, 521), 255), ((-200, 450, 521), (-200, 275, 521), (350, 250, 521), 255), ((450, 300, 521), (350, 250, 521), (650, 200, 521), 255), ((225, 200, 521), (650, 200, 521), (450, 300, 521), 255), ((225, -200, 521), (650, -200, 521), (650, 200, 521), 255), ((650, 200, 521), (225, 200, 521), (225, -200, 521), 255), ((200, 200, 521), (-200, 200, 521), (-200, -200, 521), 255), ((-200, -200, 521), (200, -200, 521), (200, 200, 521), 255), ((200, 200, 71), (-200, 200, 71), (-200, -200, 71), 255), ((-200, -200, 71), (200, -200, 71), (200, 200, 71), 255)]
                              , 100, 1500))
    pygame.pixelcopy.array_to_surface(Canvas, b)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                exit()
