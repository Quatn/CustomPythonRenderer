import pygame
import random

pygame.init()
Resolution = (1440, 960)
Canvas = pygame.display.set_mode(Resolution)
print(pygame.PixelArray(Canvas))
clock = pygame.time.Clock()
VCR_MONO = pygame.font.Font('VCR_OSD_MONO_1.001.ttf', 48)

tri = [[300, 300], [600, 300], [900, 450]]

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

print(indTop)
print(indBot)

while True:
    Canvas.fill("Black")
    # pygame.draw.polygon(Canvas, "red" if ribcage_a < 0 else "blue", tri)
    pygame.draw.line(Canvas, "green", tri[indTop], tri[indBot])

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

    if not spine_inf:
        pygame.draw.circle(Canvas, "white", (spine_a * tri[indSide][1] - spine_b, tri[indSide][1]), 3)
        pygame.draw.circle(Canvas, "green" if tri[indSide][0] < spine_a * tri[indSide][1] - spine_b else "purple", tri[indSide], 10)

        if tri[indSide][0] < spine_a * tri[indSide][1] - spine_b:
            for ii in range(tri[indSide][1] - tri[indTop][1]):
                i = tri[indTop][1] + ii
                start = int(ribcage_a * i - ribcage_b)
                end = int(spine_a * i - spine_b)
                for iii in range(end - start):
                    # Canvas.set_at((start + iii, i), "blue")
                    i
        else:
            i = tri[indTop][1]
            start = spine_a * i - spine_b
            end = ribcage_a * i - ribcage_b
            while i <= tri[indSide][1]:
                start = start + spine_a
                end = end + ribcage_a
                pointer = int(start)
                while pointer <= end:
                    # Canvas.set_at((pointer, i), "red")
                    pointer = pointer + 1
                i = i + 1

    clock.tick()
    Canvas.blit(VCR_MONO.render(str(clock.get_fps()), False, 'red'), (0, 0))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pygame.quit()
                exit()

            if event.key == pygame.K_o or True:
                for i in range(3):
                    tri[i][0] = random.randrange(0, Resolution[0])
                    tri[i][1] = random.randrange(0, Resolution[1])

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
    clock.tick(30)
