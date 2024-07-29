import pygame
import mouse
import os
import pyautogui

winPos = 100
#os.environ["SDL_VIDEO_WINDOW_POS"]= "{},{}".format(winPos, winPos)

pygame.display.init()

running = True
pyautogui.FAILSAFE = False
screen_y = 640
screen_x = 400
pygame.display.set_mode((screen_y, screen_x))
#pyautogui.moveTo(winPos + screen_y / 2, winPos + screen_x / 2)
while running:
    pyautogui.moveRel(100, 100)
    pygame.event.get()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pygame.quit()
                exit()

