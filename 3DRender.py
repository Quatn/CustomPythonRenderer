# import sys
import pygame
import math
import customMatrix as mat
import renderer as cusB
import numpy as np
import fileRead as file


# TODO: Init these with a config file
Cursor_Enabled = True
Cursor_Type = 0
Cursor_Size = 12

Color_PrimaryMenuButton_Color = pygame.Color(10, 10, 20, a=20)
Color_PrimaryMenuButton_Color_Active = pygame.Color(200, 200, 200, a=20)

# Dont really know how to do this best tbh
# 0 = Running
# 1 = Paused
Gamestate = 0
key_Pause = pygame.K_p
Overlay_Pause_Rect = pygame.Rect((0, 0), (300, 300))
Overlay_Pause_Color = pygame.Color(200, 200, 200, a=20)

upKey_Overlay_Help = pygame.K_SLASH
Overlay_Help = False
Overlay_Help_Rect = pygame.Rect((0, 0), (300, 300))
Overlay_Help_Color = pygame.Color(200, 200, 200, a=200)

Overlay_FOV = True

key_LaserPointer = pygame.K_v
LaserPointer_State = 0

# init
pygame.init()
Resolution = (1440, 960)
ResolutionHalf = (int(Resolution[0] / 2), int(Resolution[1] / 2))
Canvas = pygame.display.set_mode(Resolution)
CanvasArr = np.eye(Resolution[0], Resolution[1])
CanvasArr = CanvasArr.astype(int)
pygame.pixelcopy.surface_to_array(CanvasArr, Canvas)
clock = pygame.time.Clock()
VCR_MONO = pygame.font.Font('VCR_OSD_MONO_1.001.ttf', 48)
VCR_MONO_SMALL = pygame.font.Font('VCR_OSD_MONO_1.001.ttf', 24)

# pointers that marks the vertices' edges for debug purposes
pointer = VCR_MONO.render('•', False, 'red')
pointer1 = VCR_MONO.render('•', False, 'gray')
pointer2 = VCR_MONO.render('•', False, 'yellow')
# numerated pointers
pointerNumerated = [VCR_MONO.render('0', False, 'yellow')]
for i in range(64):  # 64 bc the size of the array does not matter, and im too lazy to get the number of vertices lol
    pointerNumerated.append(VCR_MONO.render(str(i + 1), False, 'yellow'))

pointer_rect = pointer.get_rect(center=(0, 0))

CamPos = mat.Matrix(3, 1)  # position of the viewpoint
CamPos.setIndex((2, 0), -10)
CamAngle = mat.Matrix(3, 1)  # angle of the viewpoint
MoveSpeed = 0.1

# Fov = math.pi / 2.1
Fov = math.pi / 2

# # TODO: Find out wtf this part is. Look, it's been a while
# SuppleFov = (math.pi / 2) - Fov
# csSuppleRatio = math.cos(SuppleFov) / math.sin(SuppleFov)
# csSuppleRatio1 = math.cos(math.pi / 4) / math.sin(math.pi / 4)
# tanFov = math.tan(Fov)
# tanFov1 = math.tan(math.pi / 4)

NearPlaneDistance = 1  # 1 / tanFov  # The distance between the camera and the near plane (or just the distance that planes will be clipped if it goes below)
FarPlaneDistance = 100

# print("55: " + str(math.tan(math.pi / 4)))

ObjList = []  # the list that contain all of the objects that's gonna be rendered

for i in ObjList:
    for ii in i.vertices:
        ii.copyFrom(ii.constantMult(0.01))

for i in ObjList:
    for ii in i.perspectiveVertices:
        ii.copyFrom(ii.constantMult(0.01))


# Old cube from before file read to object implementation.
cube1 = [[200, 200, 400], [200, -200, 400], [-200, -200, 400], [-200, 200, 400], [200, 200, 800], [200, -200, 800], [-200, -200, 800], [-200, 200, 800]]


rotateXMatrix = mat.Matrix(3, 3)
rotateXMatrix.setIndex((0, 0), 1)


# Rotate a 3D vector in the x axis
def Rotate3X(vertex, radian):
    if vertex.height == 3:
        rotateXMatrix.setColumn(1, [0, math.cos(radian), math.sin(radian)])
        rotateXMatrix.setColumn(2, [0, -math.sin(radian), math.cos(radian)])
        return mat.matrixMult(rotateXMatrix, vertex)
    else:
        raise Exception("Inputed vertex was not 3D")


rotateYMatrix = mat.Matrix(3, 3)
rotateYMatrix.setIndex((1, 1), 1)


# Rotate a 3D vector in the y axis
def Rotate3Y(vertex, radian):
    if vertex.height == 3:
        rotateYMatrix.setColumn(0, [math.cos(radian), 0, -math.sin(radian)])
        rotateYMatrix.setColumn(2, [math.sin(radian), 0, math.cos(radian)])
        return mat.matrixMult(rotateYMatrix, vertex)
    else:
        raise Exception("Inputed vertex was not 3D")


rotateZMatrix = mat.Matrix(3, 3)
rotateZMatrix.setIndex((2, 2), 1)


def Rotate3Z(vertex, radian):
    if vertex.height == 3:
        rotateXMatrix.setColumn(0, [math.cos(radian), math.sin(radian), 0])
        rotateXMatrix.setColumn(1, [-math.sin(radian), math.cos(radian), 0])
        return mat.matrixMult(rotateXMatrix, vertex)
    else:
        raise Exception("Inputed vertex was not 3D")


def stringToDecColor(color):
    match color:
        case 'black':
            return 0
        case 'blue':
            return 255
        case 'green':
            return 65280
        case 'red':
            return 16711680
        case 'yellow':
            return 16776960
        case 'purple':
            return 16711935
        case 'cyan':
            return 65535
        case 'white':
            return 16777215
        case 'pink':
            return 16716947

    if str(color).startswith('#'):
        return int(str(color).removeprefix('#'), 16)
    return 0
    # return int(255)


# 3D to 2D projection matrix that simply cuts the Z axis of a vector
Projev = mat.Matrix(2, 3)
Projev.setIndex((0, 0), 1)
Projev.setIndex((1, 1), 1)

# Absolutely no clue why I put a second identical matrix here bruh.
Projev2 = mat.Matrix(2, 3)
Projev2.setIndex((0, 0), 1)
Projev2.setIndex((1, 1), 1)

pygame.mouse.set_pos(Resolution[0] / 2, Resolution[1] / 2)  # Drag the mouse cursor to the middle of the screen
pygame.mouse.set_visible(False)
Cur = pygame.mouse.get_pos()

verticesClipBuffer = [0, 0, []]


def awaitSpace():
    pygame.mouse.set_visible(True)
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
    pygame.mouse.set_visible(False)


Overlay_Pause_Rect = pygame.Rect((Resolution[0] / 2 - 150, 300), (300, 100))
Overlay_Pause_TextSurface = pygame.Surface((Resolution[0] - 400, Resolution[1] - 300), pygame.SRCALPHA)
Overlay_Pause_TextSurface.blit(VCR_MONO.render("Paused", False, 'white'), (Overlay_Pause_Rect.topleft[0] + 64, Overlay_Pause_Rect.topleft[1] + 26))

Overlay_Pause_ResumeButton_Rect = pygame.Rect((Resolution[0] / 2 - 150, 450), (300, 100))
Overlay_Pause_ResumeButton_TextSurface = pygame.Surface((Resolution[0] - 400, Resolution[1] - 300), pygame.SRCALPHA)
Overlay_Pause_ResumeButton_TextSurface.blit(VCR_MONO.render("Resume", False, 'white'), (Overlay_Pause_ResumeButton_Rect.topleft[0] + 64, Overlay_Pause_ResumeButton_Rect.topleft[1] + 26))

Overlay_Pause_QuitButton_Rect = pygame.Rect((Resolution[0] / 2 - 150, 550), (300, 100))
Overlay_Pause_QuitButton_TextSurface = pygame.Surface((Resolution[0] - 400, Resolution[1] - 300), pygame.SRCALPHA)
Overlay_Pause_QuitButton_TextSurface.blit(VCR_MONO.render("Quit", False, 'white'), (Overlay_Pause_QuitButton_Rect.topleft[0] + 64, Overlay_Pause_QuitButton_Rect.topleft[1] + 26))


def Subroutine_Pause():
    pygame.draw.rect(Canvas, Overlay_Pause_Color, Overlay_Pause_Rect)
    Canvas.blit(Overlay_Pause_TextSurface, (0, 0))

    frezeFrame = Canvas.copy()
    pygame.mouse.set_visible(True)
    nCont = True
    while nCont:
        Canvas.blit(frezeFrame, (0, 0))
        Cur = pygame.mouse.get_pos()

        ResumeButton_Hover = True if (Cur[0] < Overlay_Pause_ResumeButton_Rect.bottomright[0] and
                                      Cur[1] < Overlay_Pause_ResumeButton_Rect.bottomright[1] and
                                      Cur[0] > Overlay_Pause_ResumeButton_Rect.topleft[0] and
                                      Cur[1] > Overlay_Pause_ResumeButton_Rect.topleft[1]
                                      ) else False

        QuitButton_Hover = True if (Cur[0] < Overlay_Pause_QuitButton_Rect.bottomright[0] and
                                    Cur[1] < Overlay_Pause_QuitButton_Rect.bottomright[1] and
                                    Cur[0] > Overlay_Pause_QuitButton_Rect.topleft[0] and
                                    Cur[1] > Overlay_Pause_QuitButton_Rect.topleft[1]
                                    ) else False

        if (ResumeButton_Hover):
            pygame.draw.rect(Canvas, Color_PrimaryMenuButton_Color_Active, Overlay_Pause_ResumeButton_Rect)
        else:
            pygame.draw.rect(Canvas, Color_PrimaryMenuButton_Color, Overlay_Pause_ResumeButton_Rect)
        Canvas.blit(Overlay_Pause_ResumeButton_TextSurface, (0, 0))

        if (QuitButton_Hover):
            pygame.draw.rect(Canvas, Color_PrimaryMenuButton_Color_Active, Overlay_Pause_QuitButton_Rect)
        else:
            pygame.draw.rect(Canvas, Color_PrimaryMenuButton_Color, Overlay_Pause_QuitButton_Rect)
        Canvas.blit(Overlay_Pause_QuitButton_TextSurface, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if (ResumeButton_Hover):
                    nCont = False

                if (QuitButton_Hover):
                    pygame.quit()
                    exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == key_Pause:
                    nCont = False

        pygame.display.update()
        clock.tick(30)
    pygame.mouse.set_visible(False)


# Loop begin .................................................................................................................
ColorMode_Texts = (
    VCR_MONO.render("Depth view", False, 'red'),
    )

Overlay_NoModelWarning = True
Overlay_NoModelWarning_Text = VCR_MONO_SMALL.render("Currently not displaying any models, press \";\" to load a model.", False, 'red')

Overlay_Help_DisplayText = VCR_MONO.render("Press \"?\" for control", False, 'red')
Overlay_Help = False
Overlay_Help_Rect = pygame.Rect((200, 150), (Resolution[0] - 400, Resolution[1] - 300))
Overlay_Help_TextSurface = pygame.Surface((Resolution[0] - 400, Resolution[1] - 300), pygame.SRCALPHA)
Overlay_Help_TextSurface.blit(VCR_MONO.render("WASD: Movement", False, 'red'), (0, 0))
Overlay_Help_TextSurface.blit(VCR_MONO.render("IJKL: Precise aim", False, 'red'), (0, 48))
Overlay_Help_TextSurface.blit(VCR_MONO.render("P: Pause", False, 'red'), (0, 48 * 2))
Overlay_Help_TextSurface.blit(VCR_MONO.render("1-9: Special view modes", False, 'red'), (0, 48 * 4))
Overlay_Help_TextSurface.blit(VCR_MONO.render(";: Load objects from file", False, 'red'), (0, 48 * 5))
Overlay_Help_TextSurface.blit(VCR_MONO.render("V: Laser pointer", False, 'red'), (0, 48 * 6))

Overlay_FOV = True
ColorMode = 0
cusB.setColorMode(ColorMode)
while True:
    Canvas.fill('black')
    pygame.pixelcopy.surface_to_array(CanvasArr, Canvas)
    DepthBuffer = np.full((Resolution[0], Resolution[1]), float(10000))
#     print(CanvasArr)
#     print(DepthBuffer)
#     DepthBuffer = DepthBuffer.astype(int)

    keys = pygame.key.get_pressed()
    # Check cursor displacement and rotate the camera angle vector accordingly
    Cur = pygame.mouse.get_pos()
    Cur = [Cur[1] - Resolution[1] / 2, Cur[0] - Resolution[0] / 2]
    if keys[pygame.K_i]:
        Cur[0] = Cur[0] - 0.1

    if keys[pygame.K_k]:
        Cur[0] = Cur[0] + 0.1

    if keys[pygame.K_l]:
        Cur[1] = Cur[1] + 0.1

    if keys[pygame.K_j]:
        Cur[1] = Cur[1] - 0.1

    if Cur != [0, 0]:
        CamAngle.setIndex((0, 0), CamAngle(0, 0) + (Cur[0] / 180 * math.pi / 2))
        if CamAngle(0, 0) > (math.pi / 2):
            CamAngle.setIndex((0, 0), math.pi / 2)
        if CamAngle(0, 0) < -(math.pi / 2):
            CamAngle.setIndex((0, 0), -math.pi / 2)

        CamAngle.setIndex((1, 0), CamAngle(1, 0) - (Cur[1] / 180 * math.pi / 2))
        pygame.mouse.set_pos(Resolution[0] / 2, Resolution[1] / 2)
    # Camera movement

    for i in ObjList:
        # if keys[pygame.K_i]:
        #     for ii in range(len(i.vertices)):
        #         i.vertices[ii] = Rotate3X(i.vertices[ii], 0.1)

        # if keys[pygame.K_k]:
        #     for ii in range(len(i.vertices)):
        #         i.vertices[ii] = Rotate3X(i.vertices[ii], -0.1)

        # if keys[pygame.K_l]:
        #     for ii in range(len(i.vertices)):
        #         i.vertices[ii] = Rotate3Y(i.vertices[ii], 0.1)

        # if keys[pygame.K_j]:
        #     for ii in range(len(i.vertices)):
        #         i.vertices[ii] = Rotate3Y(i.vertices[ii], -0.1)

        if keys[pygame.K_d]:
            CamPos.setIndex((2, 0), CamPos(2, 0) + (math.sin(CamAngle(1, 0)) * MoveSpeed))
            CamPos.setIndex((0, 0), CamPos(0, 0) + (math.cos(CamAngle(1, 0)) * MoveSpeed))

        if keys[pygame.K_a]:
            CamPos.setIndex((2, 0), CamPos(2, 0) - (math.sin(CamAngle(1, 0)) * MoveSpeed))
            CamPos.setIndex((0, 0), CamPos(0, 0) - (math.cos(CamAngle(1, 0)) * MoveSpeed))

        if keys[pygame.K_w]:
            CamPos.setIndex((2, 0), CamPos(2, 0) + (math.cos(CamAngle(1, 0)) * MoveSpeed))
            CamPos.setIndex((0, 0), CamPos(0, 0) - (math.sin(CamAngle(1, 0)) * MoveSpeed))

        if keys[pygame.K_s]:
            CamPos.setIndex((2, 0), CamPos(2, 0) - (math.cos(CamAngle(1, 0)) * MoveSpeed))
            CamPos.setIndex((0, 0), CamPos(0, 0) + (math.sin(CamAngle(1, 0)) * MoveSpeed))

        if keys[pygame.K_e]:
            CamAngle.setColumn(0, [0, 0, 0])

    # Calculate the perspectiveVertices vector of an object such that its position relative to the camera is as if the camera is in [0, 0, 0] and facing the same direction as the X axis
    renderBuffer = []  # queue of planes to be rendered
    for i in ObjList:
        for ii in range(len(i.vertices)):
            i.perspectiveVertices[ii].copyFrom(mat.matrixSums(i.vertices[ii], CamPos.constantMult(-1)))
            i.perspectiveVertices[ii] = Rotate3Y(i.perspectiveVertices[ii], CamAngle(1, 0))
            i.perspectiveVertices[ii] = Rotate3X(i.perspectiveVertices[ii], CamAngle(0, 0))
            i.perspectiveVertices[ii] = Rotate3Z(i.perspectiveVertices[ii], CamAngle(2, 0))

#            Print the vertex's index in the same place it's at on the screen.
#            Canvas.blit(VCR_MONO.render(str(i.perspectiveVertices[0]), False, 'red'), (0,48 * 0))

        for ii in i.planes:

            # Why am I like this.
            # dot product between a point in the plane (index 0, which also is a vector from [0, 0, 0] to the point) with the normal of the plane (cross product between the vector from index 0 to 1 and index 0 to 2). If the normal and the index 0 vector is facing in the same general direction (dot product >= 0), don't render because that means that we are looking at the "back" of that plane. Although I might have fucked up some where because this is rendering when dot product is >= 0, and it's working.
            if mat.dotProduct(i.perspectiveVertices[ii(0, 0)]
                              , mat.crossProduct(mat.matrixSums(i.perspectiveVertices[ii(0, 0)]
                                                                , i.perspectiveVertices[ii(1, 0)].constantMult(-1))  # vector from vertex 0 to vertex 1
                                                 , mat.matrixSums(i.perspectiveVertices[ii(0, 0)]
                                                                  , i.perspectiveVertices[ii(2, 0)].constantMult(-1)))  # vector from vertex 0 to vertex 2
                              ) >= 0:
                # Encapsulate infos into a tupple cus wtf is a object amirite?
                renderBuffer.append([
                    [i.perspectiveVertices[ii(0, 0)].getColumn(0), i.perspectiveVertices[ii(1, 0)].getColumn(0), i.perspectiveVertices[ii(2, 0)].getColumn(0)]  # the 3 vertices
                    , stringToDecColor(ii(3, 0))  # the color of the plane
                    , i.perspectiveVertices[ii(0, 0)](2, 0) + i.perspectiveVertices[ii(1, 0)](2, 0) + i.perspectiveVertices[ii(2, 0)](2, 0)  # the combined z depth of the 3 vertices
                    ])

    # Sort the toBeRenderd buffer based on the planes' z depth
#    for ii in range(len(renderBuffer)):
#        for iii in range(len(renderBuffer) - ii):
#            if renderBuffer[ii][2] <= renderBuffer[iii + ii][2]:
#                sWitch = renderBuffer[iii + ii]
#                renderBuffer[iii + ii] = renderBuffer[ii]
#                renderBuffer[ii] = sWitch

    processedRB = []
    for ii in renderBuffer:
        processedRB.append(tuple([
            tuple(num for num in ii[0][0]),
            tuple(num for num in ii[0][1]),
            tuple(num for num in ii[0][2]),
            ii[1]
            ]))

    # cusD.draw3DTriangles(Resolution[1], CanvasArr, processedRB, NearPlaneDistance, FarPlaneDistance, Fov)
    # cusB.draw3DTriangles(Resolution[1], CanvasArr, processedRB, NearPlaneDistance, FarPlaneDistance, Fov)
    cusB.draw3DTriangles(Resolution[1], CanvasArr, processedRB, NearPlaneDistance, FarPlaneDistance, DepthBuffer , Fov)
    # print(DepthBuffer)
    pygame.pixelcopy.array_to_surface(Canvas, CanvasArr)

    # Draw overlays
    if (ColorMode != 0):
        Canvas.blit(ColorMode_Texts[ColorMode - 1], (0, 0))
    elif Overlay_NoModelWarning:
        Canvas.blit(Overlay_NoModelWarning_Text, (0, 0))

    if (Gamestate == 1):
        Subroutine_Pause()
        Gamestate = 0

    if (LaserPointer_State == 1):
        Canvas.blit(VCR_MONO_SMALL.render("Depth: " + str(str(DepthBuffer[ResolutionHalf[0], ResolutionHalf[1]])), False, 'white'), (0, Resolution[1] - 26))

    if Overlay_Help:
        pygame.draw.rect(Canvas, Overlay_Help_Color, Overlay_Help_Rect)
        Canvas.blit(Overlay_Help_TextSurface, (200, 150))
    else:
        Canvas.blit(Overlay_Help_DisplayText, (Resolution[0] - Overlay_Help_DisplayText.get_size()[0], Resolution[1] - 48))

    if Cursor_Enabled and not Overlay_Help:
        match Cursor_Type:
            case 0:
                for dim in range(2):
                    inc_x = dim
                    inc_y = 1 - dim
                    for stroke in range(2):
                        if dim == 0:
                            cur = [ResolutionHalf[0] + stroke, int((Resolution[1] - Cursor_Size) / 2) + 1]
                        else:
                            cur = [int((Resolution[0] - Cursor_Size) / 2) + 1, ResolutionHalf[1] + stroke]

                        for pixel in range(Cursor_Size):
                            # print(0xffffff - CanvasArr[cur[0], cur[1]])
                            Canvas.set_at(cur, int(0xffffff - CanvasArr[cur[0], cur[1]]))
                            # Canvas.set_at(cur, 16776960)
                            cur[0] = cur[0] + inc_x
                            cur[1] = cur[1] + inc_y

    # Finish draw
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if keys[pygame.K_LSHIFT]:
            if event.type == pygame.KEYDOWN:
                if event.key == upKey_Overlay_Help:
                    Overlay_Help = not Overlay_Help
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    if Fov > 0.175:  # 10 deg
                        Fov = Fov - 0.1745329

                if event.key == pygame.K_RIGHTBRACKET:
                    if Fov < 2.96:
                        Fov = Fov + 0.1745329

                if event.key == key_Pause:
                    if Gamestate == 1:
                        Gamestate = 0
                    else:
                        Gamestate = 1

                if event.key == key_LaserPointer:
                    if LaserPointer_State == 1:
                        LaserPointer_State = 0
                    else:
                        LaserPointer_State = 1

                if event.key == pygame.K_1:
                    if (cusB.setColorMode(1) == 0):
                        ColorMode = 1

                if event.key == pygame.K_0:
                    if (cusB.setColorMode(0) == 0):
                        ColorMode = 0

                if event.key == pygame.K_SLASH:
                    CAL = 20
                    f = open("log.txt", "w")
                    f.write(str(len(DepthBuffer)))
                    f.write("\n")
                    f.write(str().ljust(CAL))
                    for itr in range(Resolution[0]):
                        f.write(str(itr).ljust(CAL))

                    f.write("\n")
                    for itr in range(Resolution[1]):
                        f.write(str(itr).ljust(CAL))
                        for itr1 in range(Resolution[0]):
                            f.write(str(DepthBuffer[itr1][itr]).ljust(CAL))
                        f.write("\n")
                    f.close()
                    pygame.quit()
                    exit()
    clock.tick(60)
