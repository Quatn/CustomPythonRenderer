# import sys
import os
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

Color_PrimaryMenuButton_Color = pygame.Color(150, 150, 150, a=20)
Color_PrimaryMenuButton_Color_Active = pygame.Color(220, 220, 220, a=20)

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

key_FileBrowser = pygame.K_SEMICOLON
Overlay_FileBrowser = False
Overlay_FileBrowser_Color = pygame.Color(200, 200, 200, a=20)
Overlay_FileBrowserSearchBar_Color = pygame.Color(100, 100, 100, a=20)

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


# Pause screen
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
            if event.type == pygame.MOUSEBUTTONDOWN:
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


# File browser
class FileBrowser:
    specialCharMap = dict((key, val) for key, val in zip((c for c in "`1234567890-=[];'\\,./"), (C for C in "~!@#$%^&*()_+{}:\"|<>?")))

    Overlay_FileBrowser_Surface_Size = (Resolution[0] - 400, Resolution[1] - 300)
    Overlay_FileBrowser_Surface_DisplayPos = ((Resolution[0] - Overlay_FileBrowser_Surface_Size[0]) / 2, (Resolution[1] - Overlay_FileBrowser_Surface_Size[1]) / 2)
    Overlay_FileBrowser_Surface = pygame.Surface(Overlay_FileBrowser_Surface_Size)
    Overlay_FileBrowser_TitleText = VCR_MONO_SMALL.render("Browse file", False, 'red')

    Overlay_FileBrowserSearchBarButton_Size = (22, 22)
    Overlay_FileBrowserSearchBar_Rect = pygame.Rect((6, 32), (Overlay_FileBrowser_Surface_Size[0] - Overlay_FileBrowserSearchBarButton_Size[0] - 18, 48))

    Overlay_FileBrowser_Sprite_SearchButton = pygame.image.load('./assets/sprites/menu/FIleBrowser_searchButton.png').convert_alpha()
    Overlay_FileBrowser_Sprite_ClearButton = pygame.image.load('./assets/sprites/menu/FIleBrowser_clearButton.png').convert_alpha()
    Overlay_FileBrowser_Sprite_FolderIcon = pygame.image.load('./assets/sprites/menu/FIleBrowser_folderIcon.png').convert_alpha()
    Overlay_FileBrowserSearchButton_Rect = pygame.Rect((Overlay_FileBrowser_Surface_Size[0] - Overlay_FileBrowserSearchBar_Rect[0] - Overlay_FileBrowserSearchBarButton_Size[0], Overlay_FileBrowserSearchBar_Rect[1]), Overlay_FileBrowserSearchBarButton_Size)
    Overlay_FileBrowserClearButton_Rect = pygame.Rect((Overlay_FileBrowser_Surface_Size[0] - Overlay_FileBrowserSearchBar_Rect[0] - Overlay_FileBrowserSearchBarButton_Size[0], Overlay_FileBrowserSearchBar_Rect[1] + Overlay_FileBrowserSearchBarButton_Size[1] + 4), Overlay_FileBrowserSearchBarButton_Size)

    Overlay_FileBrowserButton_Size = (Overlay_FileBrowser_Surface_Size[0] - 20, 32)
    Overlay_FileBrowser_Sprite_LeftButton = pygame.image.load('./assets/sprites/menu/FIleBrowser_pageButton_left.png').convert_alpha()
    Overlay_FileBrowser_Sprite_RightButton = pygame.image.load('./assets/sprites/menu/FIleBrowser_pageButton_right.png').convert_alpha()

    Overlay_FileBrowserPageButton_Size = (30, 30)
    Overlay_FileBrowserPageButton_Left_Rect = pygame.Rect((Overlay_FileBrowser_Surface_Size[0] / 2 - 40 - 15, Overlay_FileBrowser_Surface_Size[1] - 32), Overlay_FileBrowserPageButton_Size)
    Overlay_FileBrowserPageButton_Right_Rect = pygame.Rect((Overlay_FileBrowser_Surface_Size[0] / 2 + 40 - 15, Overlay_FileBrowser_Surface_Size[1] - 32), Overlay_FileBrowserPageButton_Size)

    Overlay_FileBrowserMessageButton_Size = (172, 52)
    Overlay_FileBrowserMessageButton_Back_Rect = pygame.Rect((Overlay_FileBrowser_Surface_Size[0] / 2 - 120 - Overlay_FileBrowserMessageButton_Size[0] / 2, Overlay_FileBrowser_Surface_Size[1] / 2 + 92), Overlay_FileBrowserMessageButton_Size)
    Overlay_FileBrowserMessageButton_Back_Text_Rendered = VCR_MONO.render("Back", False, "white")
    Overlay_FileBrowserMessageButton_Close_Rect = pygame.Rect((Overlay_FileBrowser_Surface_Size[0] / 2 + 120 - Overlay_FileBrowserMessageButton_Size[0] / 2, Overlay_FileBrowser_Surface_Size[1] / 2 + 92), Overlay_FileBrowserMessageButton_Size)
    Overlay_FileBrowserMessageButton_Close_Text_Rendered = VCR_MONO.render("Close", False, "white")

    def __init__(self):
        self.pathContent = []
        self.dirTupple = []
        self.fileTupple = []
        self.dir = "."
        self.displayDir = ""

        self.page = 0
        self.pageSize = 15

        # Yea this thing is not a search bar but whatever it's easier to imagine what it is
        self.searchBarFocus = False
        self.validPath = True

        self.message = ""
        self.showMessage = False

    def __call__(self, dir):
        self.validPath = os.path.lexists(dir)

        if (self.validPath):
            self.dir = os.path.realpath(dir)
            self.displayDir = self.dir
        else:
            self.displayDir = dir
            self.dir = ""

        pygame.mouse.set_visible(True)
        self.Subroutine_FileBrowser_init()
        self.getFiles()
        self.Subroutine_FileBrowser_loop()
        pygame.mouse.set_visible(False)

    def Subroutine_FileBrowser_init(self):
        self.Overlay_FileBrowser_Surface.fill(Overlay_FileBrowser_Color)
        self.Overlay_FileBrowser_Surface.blit(VCR_MONO_SMALL.render("Browse files", False, 'white'), (20, 0))
        pygame.draw.rect(self.Overlay_FileBrowser_Surface, Overlay_FileBrowserSearchBar_Color, self.Overlay_FileBrowserSearchBar_Rect)
        self.Overlay_FileBrowser_Surface.blit(VCR_MONO_SMALL.render(self.displayDir + ("|" if self.searchBarFocus else ""), False, 'white' if self.validPath else 'red'), (self.Overlay_FileBrowserSearchBar_Rect.topleft[0] + 12, self.Overlay_FileBrowserSearchBar_Rect.topleft[1] + 12))

    def getFiles(self):
        self.pathContent = os.listdir(self.dir) if self.validPath else []
        self.dirTupple = tuple(x for x in self.pathContent if os.path.isdir(self.dir + "/" + x))
        self.fileTupple = tuple(x for x in self.pathContent if not os.path.isdir(self.dir + "/" + x))
        self.pathContent = (("..",) if self.validPath else ()) + self.dirTupple + self.fileTupple
        self.page = 0
        self.showMessage = False

    def Subroutine_FileBrowser_loop(self):
        nCont = True
        while nCont:
            Cur = pygame.mouse.get_pos()
            pageIndex = self.page * self.pageSize
            checkHover = tuple(True if (Cur[0] > self.Overlay_FileBrowser_Surface_DisplayPos[0] + 10 and
                                        Cur[0] < self.Overlay_FileBrowser_Surface_DisplayPos[0] + self.Overlay_FileBrowser_Surface_Size[0] - 10 and
                                        Cur[1] > self.Overlay_FileBrowser_Surface_DisplayPos[1] + 64 + 36 * (count + 1) and
                                        Cur[1] < self.Overlay_FileBrowser_Surface_DisplayPos[1] + 64 + 36 * (count + 1) + 32
                                        ) else False
                               for count in range(min(self.pageSize, len(self.pathContent) - pageIndex))
                               )

            countLine = 0

            hoveredEntry = ""
            msg_Back_Hover = False
            msg_Close_Hover = False
            if self.showMessage:
                # Display message
                render = VCR_MONO_SMALL.render(self.message, False, 'white')
                self.Overlay_FileBrowser_Surface.blit(render, ((self.Overlay_FileBrowser_Surface_Size[0] - render.get_width()) / 2, self.Overlay_FileBrowser_Surface_Size[1] / 2))
                msg_Back_Hover = True if (Cur[0] < self.Overlay_FileBrowserMessageButton_Back_Rect.bottomright[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                          Cur[1] < self.Overlay_FileBrowserMessageButton_Back_Rect.bottomright[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1] and
                                          Cur[0] > self.Overlay_FileBrowserMessageButton_Back_Rect.topleft[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                          Cur[1] > self.Overlay_FileBrowserMessageButton_Back_Rect.topleft[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1]
                                          ) else False
                pygame.draw.rect(self.Overlay_FileBrowser_Surface, Color_PrimaryMenuButton_Color_Active if msg_Back_Hover else Color_PrimaryMenuButton_Color, self.Overlay_FileBrowserMessageButton_Back_Rect)
                self.Overlay_FileBrowser_Surface.blit(self.Overlay_FileBrowserMessageButton_Back_Text_Rendered, (self.Overlay_FileBrowserMessageButton_Back_Rect.topleft[0] + 30, self.Overlay_FileBrowserMessageButton_Back_Rect.topleft[1] + 3))

                msg_Close_Hover = True if (Cur[0] < self.Overlay_FileBrowserMessageButton_Close_Rect.bottomright[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                           Cur[1] < self.Overlay_FileBrowserMessageButton_Close_Rect.bottomright[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1] and
                                           Cur[0] > self.Overlay_FileBrowserMessageButton_Close_Rect.topleft[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                           Cur[1] > self.Overlay_FileBrowserMessageButton_Close_Rect.topleft[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1]
                                           ) else False
                pygame.draw.rect(self.Overlay_FileBrowser_Surface, Color_PrimaryMenuButton_Color_Active if msg_Close_Hover else Color_PrimaryMenuButton_Color, self.Overlay_FileBrowserMessageButton_Close_Rect)
                self.Overlay_FileBrowser_Surface.blit(self.Overlay_FileBrowserMessageButton_Close_Text_Rendered, (self.Overlay_FileBrowserMessageButton_Close_Rect.topleft[0] + 15, self.Overlay_FileBrowserMessageButton_Close_Rect.topleft[1] + 3))
            else:
                # Display file entries
                for entry in self.pathContent[pageIndex:pageIndex + self.pageSize]:
                    pygame.draw.rect(self.Overlay_FileBrowser_Surface, Color_PrimaryMenuButton_Color_Active if checkHover[countLine] else Color_PrimaryMenuButton_Color, pygame.Rect((10, 64 + 36 * (countLine + 1)), self.Overlay_FileBrowserButton_Size))
                    if (pageIndex + countLine < len(self.dirTupple) + 1):
                        self.Overlay_FileBrowser_Surface.blit(self.Overlay_FileBrowser_Sprite_FolderIcon, (12, 64 + 36 * (countLine + 1) + 2))
                        self.Overlay_FileBrowser_Surface.blit(VCR_MONO_SMALL.render(entry, False, 'white'), (40, 64 + 36 * (countLine + 1) + 2))
                    else:
                        self.Overlay_FileBrowser_Surface.blit(VCR_MONO_SMALL.render(entry, False, '#59e5ad' if entry.endswith(".ver") else 'white'), (12, 64 + 36 * (countLine + 1) + 2))
                    if checkHover[countLine]:
                        hoveredEntry = entry
                    countLine = countLine + 1
                    if (countLine > 13):
                        break

            self.Overlay_FileBrowser_Surface.blit(VCR_MONO_SMALL.render(str(self.page + 1), False, 'white'), ((self.Overlay_FileBrowser_Surface_Size[0] - 12) / 2, self.Overlay_FileBrowser_Surface_Size[1] - 28))

            left_Hover = False
            if (self.page > 0):
                left_Hover = True if (Cur[0] < self.Overlay_FileBrowserPageButton_Left_Rect.bottomright[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                      Cur[1] < self.Overlay_FileBrowserPageButton_Left_Rect.bottomright[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1] and
                                      Cur[0] > self.Overlay_FileBrowserPageButton_Left_Rect.topleft[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                      Cur[1] > self.Overlay_FileBrowserPageButton_Left_Rect.topleft[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1]
                                      ) else False
                pygame.draw.rect(self.Overlay_FileBrowser_Surface, Color_PrimaryMenuButton_Color_Active if left_Hover else Color_PrimaryMenuButton_Color, self.Overlay_FileBrowserPageButton_Left_Rect)
                self.Overlay_FileBrowser_Surface.blit(self.Overlay_FileBrowser_Sprite_LeftButton, (self.Overlay_FileBrowserPageButton_Left_Rect.topleft[0] + 3, self.Overlay_FileBrowserPageButton_Left_Rect.topleft[1] + 3))

            right_Hover = False
            if (pageIndex + self.pageSize < len(self.pathContent)):
                right_Hover = True if (Cur[0] < self.Overlay_FileBrowserPageButton_Right_Rect.bottomright[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                       Cur[1] < self.Overlay_FileBrowserPageButton_Right_Rect.bottomright[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1] and
                                       Cur[0] > self.Overlay_FileBrowserPageButton_Right_Rect.topleft[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                       Cur[1] > self.Overlay_FileBrowserPageButton_Right_Rect.topleft[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1]
                                       ) else False
                pygame.draw.rect(self.Overlay_FileBrowser_Surface, Color_PrimaryMenuButton_Color_Active if right_Hover else Color_PrimaryMenuButton_Color, self.Overlay_FileBrowserPageButton_Right_Rect)
                self.Overlay_FileBrowser_Surface.blit(self.Overlay_FileBrowser_Sprite_RightButton, (self.Overlay_FileBrowserPageButton_Right_Rect.topleft[0] + 3, self.Overlay_FileBrowserPageButton_Right_Rect.topleft[1] + 3))


            SearchButton_Hover = True if (Cur[0] < self.Overlay_FileBrowserSearchButton_Rect.bottomright[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                          Cur[1] < self.Overlay_FileBrowserSearchButton_Rect.bottomright[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1] and
                                          Cur[0] > self.Overlay_FileBrowserSearchButton_Rect.topleft[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                          Cur[1] > self.Overlay_FileBrowserSearchButton_Rect.topleft[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1]
                                          ) else False
            pygame.draw.rect(self.Overlay_FileBrowser_Surface, Color_PrimaryMenuButton_Color_Active if SearchButton_Hover else Color_PrimaryMenuButton_Color, self.Overlay_FileBrowserSearchButton_Rect)
            self.Overlay_FileBrowser_Surface.blit(self.Overlay_FileBrowser_Sprite_SearchButton, (self.Overlay_FileBrowserSearchButton_Rect.topleft[0] -1, self.Overlay_FileBrowserSearchButton_Rect.topleft[1] - 1))

            ClearButton_Hover = True if (Cur[0] < self.Overlay_FileBrowserClearButton_Rect.bottomright[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                         Cur[1] < self.Overlay_FileBrowserClearButton_Rect.bottomright[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1] and
                                         Cur[0] > self.Overlay_FileBrowserClearButton_Rect.topleft[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                         Cur[1] > self.Overlay_FileBrowserClearButton_Rect.topleft[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1]
                                         ) else False
            pygame.draw.rect(self.Overlay_FileBrowser_Surface, Color_PrimaryMenuButton_Color_Active if ClearButton_Hover else Color_PrimaryMenuButton_Color, self.Overlay_FileBrowserClearButton_Rect)
            self.Overlay_FileBrowser_Surface.blit(self.Overlay_FileBrowser_Sprite_ClearButton, (self.Overlay_FileBrowserClearButton_Rect.topleft[0] - 1, self.Overlay_FileBrowserClearButton_Rect.topleft[1] - 1))

            Canvas.blit(self.Overlay_FileBrowser_Surface, self.Overlay_FileBrowser_Surface_DisplayPos)

            SearchBar_Hover = True if (Cur[0] < self.Overlay_FileBrowserSearchBar_Rect.bottomright[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                       Cur[1] < self.Overlay_FileBrowserSearchBar_Rect.bottomright[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1] and
                                       Cur[0] > self.Overlay_FileBrowserSearchBar_Rect.topleft[0] + self.Overlay_FileBrowser_Surface_DisplayPos[0] and
                                       Cur[1] > self.Overlay_FileBrowserSearchBar_Rect.topleft[1] + self.Overlay_FileBrowser_Surface_DisplayPos[1]
                                       ) else False

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.searchBarFocus = True if (SearchBar_Hover) else False

                    if (left_Hover):
                        self.page = self.page - 1

                    if (right_Hover):
                        self.page = self.page + 1

                    if (SearchButton_Hover or msg_Back_Hover):
                        self.validPath = os.path.lexists(self.displayDir)
                        self.dir = os.path.realpath(self.displayDir) if (self.validPath) else ""
                        self.displayDir = self.dir if self.validPath else self.displayDir
                        self.getFiles()

                    if (ClearButton_Hover):
                        self.validPath = False
                        self.dir = self.displayDir = ""

                    if (msg_Close_Hover):
                        nCont = False
                        break

                    if (len(hoveredEntry) > 0):
                        hoveredEntryCanon = self.displayDir + "/" + hoveredEntry
                        if (os.path.isdir(hoveredEntryCanon)):
                            self.validPath = os.path.lexists(hoveredEntryCanon)
                            self.dir = os.path.realpath(hoveredEntryCanon) if (self.validPath) else ""
                            self.displayDir = self.dir if self.validPath else self.displayDir
                            self.getFiles()
                        else:
                            print("Opening " + hoveredEntryCanon)
                            if hoveredEntry.endswith(".ver"):
                                result = file.readVer(hoveredEntryCanon)
                                if (result is not None):
                                    if (len(result) > 0):
                                        self.message = "Read " + hoveredEntry + " successfully!"
                                        global ObjList
                                        ObjList = ObjList + result
                                        print(ObjList)
                                    else:
                                        self.message = "File corrupted or did not contain any models."
                            else:
                                self.message = "Unsupported file extension."
                            self.showMessage = True

                    # print(self.searchBarFocus)
                    self.Subroutine_FileBrowser_init()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    # print(pygame.key.name(event.key))
                    if (self.searchBarFocus):
                        keys = pygame.key.get_pressed()
                        if event.key == pygame.K_ESCAPE:
                            self.searchBarFocus = False
                            # print(self.searchBarFocus)

                        elif event.key == pygame.K_BACKSPACE:
                            self.displayDir = self.displayDir[0:len(self.displayDir) - 1]

                        elif event.key == pygame.K_RETURN:
                            self.validPath = os.path.lexists(self.displayDir)
                            self.dir = os.path.realpath(self.displayDir) if (self.validPath) else ""
                            self.displayDir = self.dir if self.validPath else self.displayDir
                            self.getFiles()

                        else:
                            k = pygame.key.name(event.key)
                            if (len(k) == 1):
                                if keys[pygame.K_LSHIFT]:
                                    self.displayDir = self.displayDir + (k.upper() if k.isalpha() else (FileBrowser.specialCharMap[k]))
                                else:
                                    self.displayDir = self.displayDir + k

                        self.Subroutine_FileBrowser_init()

                    else:
                        if event.key == key_FileBrowser:
                            nCont = False

            pygame.display.update()
            clock.tick(30)


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
ExitingMenu = False
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
        if (not ExitingMenu):
            CamAngle.setIndex((0, 0), CamAngle(0, 0) + (Cur[0] / 180 * math.pi / 2))
            if CamAngle(0, 0) > (math.pi / 2):
                CamAngle.setIndex((0, 0), math.pi / 2)
            if CamAngle(0, 0) < -(math.pi / 2):
                CamAngle.setIndex((0, 0), -math.pi / 2)
            CamAngle.setIndex((1, 0), CamAngle(1, 0) - (Cur[1] / 180 * math.pi / 2))
        else:
            ExitingMenu = False

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
        ExitingMenu = True
        Gamestate = 0

    if (Overlay_FileBrowser):
        fb = FileBrowser()
        fb(".")
        ExitingMenu = True
        Overlay_FileBrowser = False

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

                if event.key == key_FileBrowser:
                    Overlay_FileBrowser = not Overlay_FileBrowser

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
