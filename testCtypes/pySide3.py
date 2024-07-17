import testModule as tm
import time
import numpy as np
import random
import pygame

pygame.init()
Resolution = (1440, 960)
Canvas = pygame.display.set_mode(Resolution)
VCR_MONO = pygame.font.Font('VCR_OSD_MONO_1.001.ttf', 48)
VCR_MONO_32 = pygame.font.Font('VCR_OSD_MONO_1.001.ttf', 32)
clock = pygame.time.Clock()

x = 1000
y = 1000
n = 10


def quickCenterBlit(msg, color, center):
    Msg = VCR_MONO.render(msg, False, color)
    Msg_rect = Msg.get_rect(center=center)
    Canvas.blit(Msg, Msg_rect.topleft)


def quickCenterBlit32(msg, color, center):
    Msg = VCR_MONO_32.render(msg, False, color)
    Msg_rect = Msg.get_rect(center=center)
    Canvas.blit(Msg, Msg_rect.topleft)


def awaitSpace():
    nCont = True
    while nCont:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    nCont = False
        clock.tick(30)


quickCenterBlit('Benchmark drawing using Python vs C', 'white', (Resolution[0] / 2, Resolution[1] / 2 - 32))
quickCenterBlit('Press space to continue', 'white', (Resolution[0] / 2, Resolution[1] / 2 + 32))
pygame.display.update()

awaitSpace()

# First Test ============

Canvas.fill('black')
Canvas.blit(VCR_MONO.render("First test: Fill the screen", False, "white"), [0, 0])
Canvas.blit(VCR_MONO.render("Results:", False, "white"), [0, 48 + 20])
Canvas.blit(VCR_MONO.render("Python:", False, "white"), [0 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render("C:", False, "white"), [0 + 32, 144 + 20])
quickCenterBlit32("Python code will turn the screen to green", "white", (Resolution[0] / 2, Resolution[1] / 2 - 24))
quickCenterBlit32("C code will turn the screen to blue", "white", (Resolution[0] / 2, Resolution[1] / 2 + 24))
quickCenterBlit('Press space to start test', 'white', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()

awaitSpace()

pyTime = -1
start = time.time()
for i in range(Resolution[0]):
    for ii in range(Resolution[1]):
        Canvas.set_at((i, ii), "green")
end = time.time()
quickCenterBlit('(Test completed, press space to continue)', 'purple', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()
pyTime = end - start

awaitSpace()

Canvas.fill('black')
Canvas.blit(VCR_MONO.render("First test: Fill the screen", False, "white"), [0, 0])
Canvas.blit(VCR_MONO.render("Results:", False, "white"), [0, 48 + 20])
Canvas.blit(VCR_MONO.render("Python:", False, "white"), [0 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render(str(pyTime) + "s", False, "yellow"), [196 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render("C:", False, "white"), [0 + 32, 144 + 20])
quickCenterBlit32("Python code will turn the screen to green", "white", (Resolution[0] / 2, Resolution[1] / 2 - 24))
quickCenterBlit32("C code will turn the screen to blue", "white", (Resolution[0] / 2, Resolution[1] / 2 + 24))
quickCenterBlit('Press space to continue', 'white', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()

awaitSpace()

# Not counting array copy process for pure looping speed test
Canvas_Arr = np.eye(Resolution[0], Resolution[1])
Canvas_Arr = Canvas_Arr.astype(int)
pygame.pixelcopy.surface_to_array(Canvas_Arr, Canvas)

cTime = -1
start = time.time()
tm.drawSquare(255, Resolution[0], (0, 0), Resolution, Canvas_Arr)
pygame.pixelcopy.array_to_surface(Canvas, Canvas_Arr)
end = time.time()
quickCenterBlit('(Test completed, press space to continue)', 'red', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()
cTime = end - start

awaitSpace()

Canvas.fill('black')
Canvas.blit(VCR_MONO.render("First test: Fill the screen", False, "white"), [0, 0])
Canvas.blit(VCR_MONO.render("Results:", False, "white"), [0, 48 + 20])
Canvas.blit(VCR_MONO.render("Python:", False, "white"), [0 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render(str(pyTime) + "s", False, "yellow"), [196 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render("C:", False, "white"), [0 + 32, 144 + 20])
Canvas.blit(VCR_MONO.render(str(cTime) + "s", False, "yellow"), [196 + 32, 144 + 20])
quickCenterBlit('Press space to go to next test', 'white', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()

awaitSpace()

# Second Test ============

Canvas.fill('black')
Canvas.blit(VCR_MONO.render("Second test: Change color of the screen gradually", False, "white"), [0, 0])
Canvas.blit(VCR_MONO.render("Results:", False, "white"), [0, 48 + 20])
Canvas.blit(VCR_MONO.render("Python:", False, "white"), [0 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render("C:", False, "white"), [0 + 32, 144 + 20])
quickCenterBlit32("Python code will change the screen from red to yellow", "white", (Resolution[0] / 2, Resolution[1] / 2 - 24))
quickCenterBlit32("C code will change the screen from red to purple", "white", (Resolution[0] / 2, Resolution[1] / 2 + 24))
quickCenterBlit('Press space to start test', 'white', (Resolution[0] / 2, Resolution[1] - 96))
quickCenterBlit32('Warning: Usually takes about 90 seconds to complete', 'red', (Resolution[0] / 2, Resolution[1] - 48))
pygame.display.update()

awaitSpace()

pyTime = -1
start = time.time()
for c in range(255):
    color = 16711680 + (256 * c)
    for i in range(Resolution[0]):
        for ii in range(Resolution[1]):
            Canvas.set_at((i, ii), color)
    Canvas.blit(VCR_MONO.render(str(c + 1), False, "black"), [0, 0])
    pygame.display.update()
end = time.time()
quickCenterBlit('(Test completed, press space to continue)', 'blue', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()
pyTime = end - start

awaitSpace()

Canvas.fill('black')
Canvas.blit(VCR_MONO.render("Second test: Change color of the screen gradually", False, "white"), [0, 0])
Canvas.blit(VCR_MONO.render("Results:", False, "white"), [0, 48 + 20])
Canvas.blit(VCR_MONO.render("Python:", False, "white"), [0 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render(str(pyTime) + "s", False, "yellow"), [196 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render("C:", False, "white"), [0 + 32, 144 + 20])
quickCenterBlit32("Python code will change the screen from red to yellow", "white", (Resolution[0] / 2, Resolution[1] / 2 - 24))
quickCenterBlit32("C code will change the screen from red to purple", "white", (Resolution[0] / 2, Resolution[1] / 2 + 24))
quickCenterBlit('Press space to continue', 'white', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()

awaitSpace()

# Not counting array copy process for pure looping speed test
Canvas_Arr = np.eye(Resolution[0], Resolution[1])
Canvas_Arr = Canvas_Arr.astype(int)
pygame.pixelcopy.surface_to_array(Canvas_Arr, Canvas)

cTime = -1
start = time.time()
for c in range(255):
    color = 16711680 + c
    tm.drawSquare(color, Resolution[0], (0, 0), Resolution, Canvas_Arr)
    pygame.pixelcopy.array_to_surface(Canvas, Canvas_Arr)
    Canvas.blit(VCR_MONO.render(str(c + 1), False, "black"), [0, 0])
    pygame.display.update()
end = time.time()
quickCenterBlit('(Test completed, press space to continue)', 'green', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()
cTime = end - start

awaitSpace()

Canvas.fill('black')
Canvas.blit(VCR_MONO.render("Second test: Change color of the screen gradually", False, "white"), [0, 0])
Canvas.blit(VCR_MONO.render("Results:", False, "white"), [0, 48 + 20])
Canvas.blit(VCR_MONO.render("Python:", False, "white"), [0 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render(str(pyTime) + "s", False, "yellow"), [196 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render("C:", False, "white"), [0 + 32, 144 + 20])
Canvas.blit(VCR_MONO.render(str(cTime) + "s", False, "yellow"), [196 + 32, 144 + 20])
quickCenterBlit('Press space to go to next test', 'white', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()

awaitSpace()

# Final Test ============

Canvas.fill('black')
Canvas.blit(VCR_MONO.render("Final test: Draw triangles", False, "white"), [0, 0])
Canvas.blit(VCR_MONO.render("Results:", False, "white"), [0, 48 + 20])
Canvas.blit(VCR_MONO.render("Python:", False, "white"), [0 + 32, 96 + 20])
Canvas.blit(VCR_MONO.render("C:", False, "white"), [0 + 32, 144 + 20])
quickCenterBlit32("Both algorithms will draw random triangles on the screen", "white", (Resolution[0] / 2, Resolution[1] / 2 - 24))
quickCenterBlit32("Python's triangles are green, C's triangles are blue", "white", (Resolution[0] / 2, Resolution[1] / 2 + 24))
quickCenterBlit32("Press O to generate a random triangle", "white", (Resolution[0] / 2, Resolution[1] / 2 + 72))
quickCenterBlit32("Press P to toggle debug line (made using python code)", "white", (Resolution[0] / 2, Resolution[1] / 2 + 128))
quickCenterBlit('Press space to start test', 'white', (Resolution[0] / 2, Resolution[1] - 64))
pygame.display.update()

awaitSpace()

# Python triangle draw -----------------------------------------------------------

tri = [[300, 300], [600, 300], [900, 450]]

debugLines = False
cont = True
while cont:
    indTop = 0
    indBot = 0
    indSide = -1

    if tri[1][1] < tri[indTop][1]:
        indTop = 1

    if tri[1][1] >= tri[indBot][1]:
        indBot = 1

    if tri[2][1] < tri[indTop][1]:
        indTop = 2

    if tri[2][1] >= tri[indBot][1]:
        indBot = 2

    indSide = 3 - indTop - indBot

    # Flipped X and Y axis to draw vertically
    spineVec = [tri[indBot][1] - tri[indTop][1], tri[indBot][0] - tri[indTop][0]]
    spine_inf = False
    spine_a = 0
    spine_b = 0
    if spineVec[0] == 0:
        spine_inf = True
    else:
        spine_a = spineVec[1] / spineVec[0]
        spine_b = (spine_a * tri[indTop][1]) - tri[indTop][0]

    ribcageVec = [tri[indSide][1] - tri[indTop][1], tri[indSide][0] - tri[indTop][0]]
    ribcage_inf = False
    ribcage_a = 0
    ribcage_b = 0
    if ribcageVec[0] == 0:
        ribcage_inf = True
    else:
        ribcage_a = ribcageVec[1] / ribcageVec[0]
        ribcage_b = (ribcage_a * tri[indTop][1]) - tri[indTop][0]

    femurVec = [tri[indBot][1] - tri[indSide][1], tri[indBot][0] - tri[indSide][0]]
    femur_inf = False
    femur_a = 0
    femur_b = 0
    if femurVec[0] == 0:
        femur_inf = True
    else:
        femur_a = femurVec[1] / femurVec[0]
        femur_b = (femur_a * tri[indBot][1]) - tri[indBot][0]

    Canvas.fill("Black")
    # pygame.draw.polygon(Canvas, "red" if ribcage_a < 0 else "blue", tri)
    # pygame.draw.line(Canvas, "green", tri[indTop], tri[indBot])

    i = 0
    if debugLines:
        while i < Resolution[1]:
            p = spine_a * i - spine_b
            if p < Resolution[0] and p > -1:
                Canvas.set_at((int(p), i), "yellow")

            p = ribcage_a * i - ribcage_b
            if p < Resolution[0] and p > -1:
                Canvas.set_at((int(p), i), "blue")

            p = femur_a * i - femur_b
            if p < Resolution[0] and p > -1:
                Canvas.set_at((int(p), i), "red")

            i = i + 1

    if not spine_inf:
        # pygame.draw.circle(Canvas, "white", (spine_a * tri[indSide][1] - spine_b, tri[indSide][1]), 3)
        # pygame.draw.circle(Canvas, "green" if tri[indSide][0] < spine_a * tri[indSide][1] - spine_b else "purple", tri[indSide], 10)

        # 2 different ways of looping, I put both of them here to compare there efficiency
        if tri[indSide][0] < spine_a * tri[indSide][1] - spine_b:
            for ii in range(tri[indSide][1] - tri[indTop][1]):
                i = tri[indTop][1] + ii
                start = int(ribcage_a * i - ribcage_b)
                end = int(spine_a * i - spine_b)
                for iii in range(end - start):
                    Canvas.set_at((start + iii, i), "green")

            for ii in range(tri[indBot][1] - tri[indSide][1]):
                i = tri[indSide][1] + ii
                start = int(femur_a * i - femur_b)
                end = int(spine_a * i - spine_b)
                for iii in range(end - start):
                    Canvas.set_at((start + iii, i), "green")

        else:
            i = tri[indTop][1]

            start = spine_a * i - spine_b
            end = ribcage_a * i - ribcage_b
            while i < tri[indSide][1]:
                start = start + spine_a
                end = end + ribcage_a
                pointer = int(start)
                while pointer <= end:
                    Canvas.set_at((pointer, i), "green")
                    pointer = pointer + 1
                i = i + 1

            start = spine_a * i - spine_b
            end = femur_a * i - femur_b
            while i <= tri[indBot][1]:
                start = start + spine_a
                end = end + femur_a
                pointer = int(start)
                while pointer <= end:
                    Canvas.set_at((pointer, i), "green")
                    pointer = pointer + 1
                i = i + 1

    clock.tick()
    Canvas.blit(VCR_MONO.render("FPS: " + str(clock.get_fps()), False, 'red'), (0, 0))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                debugLines = not debugLines

            if event.key == pygame.K_n:
                tri = [[300, 300], [300, 900], [900, 600]]

            if event.key == pygame.K_m:
                tri = [[900, 300], [900, 900], [300, 600]]

            if event.key == pygame.K_o:
                for i in range(3):
                    tri[i][0] = random.randrange(0, Resolution[0])
                    tri[i][1] = random.randrange(0, Resolution[1])
            if event.key == pygame.K_SPACE:
                cont = False
    # clock.tick(30)

# -------------------------------------------------------------------------------------

Canvas.fill('black')
quickCenterBlit('Press space to go to C version', 'white', (Resolution[0] / 2, Resolution[1] / 2))
pygame.display.update()

awaitSpace()

Canvas_Arr = np.eye(Resolution[0], Resolution[1])
Canvas_Arr = Canvas_Arr.astype(int)
pygame.pixelcopy.surface_to_array(Canvas_Arr, Canvas)
tri = [[300, 300], [600, 300], [900, 450]]

debugLines = False
cont = True
while cont:
    Canvas.fill('black')
    if debugLines:
        indTop = 0
        indBot = 0
        indSide = -1

        if tri[1][1] < tri[indTop][1]:
            indTop = 1

        if tri[1][1] >= tri[indBot][1]:
            indBot = 1

        if tri[2][1] < tri[indTop][1]:
            indTop = 2

        if tri[2][1] >= tri[indBot][1]:
            indBot = 2

        indSide = 3 - indTop - indBot

        # Flipped X and Y axis to draw vertically
        spineVec = [tri[indBot][1] - tri[indTop][1], tri[indBot][0] - tri[indTop][0]]
        spine_inf = False
        spine_a = 0
        spine_b = 0
        if spineVec[0] == 0:
            spine_inf = True
        else:
            spine_a = spineVec[1] / spineVec[0]
            spine_b = (spine_a * tri[indTop][1]) - tri[indTop][0]

        ribcageVec = [tri[indSide][1] - tri[indTop][1], tri[indSide][0] - tri[indTop][0]]
        ribcage_inf = False
        ribcage_a = 0
        ribcage_b = 0
        if ribcageVec[0] == 0:
            ribcage_inf = True
        else:
            ribcage_a = ribcageVec[1] / ribcageVec[0]
            ribcage_b = (ribcage_a * tri[indTop][1]) - tri[indTop][0]

        femurVec = [tri[indBot][1] - tri[indSide][1], tri[indBot][0] - tri[indSide][0]]
        femur_inf = False
        femur_a = 0
        femur_b = 0
        if femurVec[0] == 0:
            femur_inf = True
        else:
            femur_a = femurVec[1] / femurVec[0]
            femur_b = (femur_a * tri[indBot][1]) - tri[indBot][0]

        i = 0
        while i < Resolution[1]:
            p = spine_a * i - spine_b
            if p < Resolution[0] and p > -1:
                Canvas.set_at((int(p), i), "yellow")

            p = ribcage_a * i - ribcage_b
            if p < Resolution[0] and p > -1:
                Canvas.set_at((int(p), i), "blue")

            p = femur_a * i - femur_b
            if p < Resolution[0] and p > -1:
                Canvas.set_at((int(p), i), "red")
            i = i + 1

    pygame.pixelcopy.surface_to_array(Canvas_Arr, Canvas)
    tm.drawTriangle(Resolution[1], Canvas_Arr, tri[0], tri[1], tri[2], 255)
    pygame.pixelcopy.array_to_surface(Canvas, Canvas_Arr)

    clock.tick()
    Canvas.blit(VCR_MONO.render("FPS: " + str(clock.get_fps()), False, 'red'), (0, 0))

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                debugLines = not debugLines

            if event.key == pygame.K_n:
                tri = [[300, 300], [300, 900], [900, 600]]

            if event.key == pygame.K_m:
                tri = [[900, 300], [900, 900], [300, 600]]

            if event.key == pygame.K_o:
                for i in range(3):
                    tri[i][0] = random.randrange(0, Resolution[0])
                    tri[i][1] = random.randrange(0, Resolution[1])
            if event.key == pygame.K_SPACE:
                cont = False

Canvas.fill('black')
quickCenterBlit('Press Q to quit', 'white', (Resolution[0] / 2, Resolution[1] / 2))
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
    clock.tick(30)
