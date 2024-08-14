# import sys
import pygame
import struct
import math
import customMatrix as mat
import renderer as cusB
import numpy as np


class Shape:
    origin = None
    vertices = []
    perspectiveVertices = []
    planes = []
    render = False

    def __init__(self, name, origin):
        self.name = name
        self.origin = origin

    def __str__(self):
        return self.name


# init
pygame.init()
Resolution = (1440, 960)
Canvas = pygame.display.set_mode(Resolution)
CanvasArr = np.eye(Resolution[0], Resolution[1])
CanvasArr = CanvasArr.astype(int)
pygame.pixelcopy.surface_to_array(CanvasArr, Canvas)
clock = pygame.time.Clock()
VCR_MONO = pygame.font.Font('VCR_OSD_MONO_1.001.ttf', 48)

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
FarPlaneDistance = 40

# print("55: " + str(math.tan(math.pi / 4)))

ObjList = []  # the list that contain all of the objects that's gonna be rendered
# render object data format:
#   \n
#   Object Name
#   unsigned short 1: number of vertices to read (does not include the first vertex, which is the "Origin" of the object), unsigned short 2: number of indices each vertex will have.
#   a list of 4 bytes integers, which is read according the the rule above.
#   unsigned short 1: number of sets of vertices to read (does not have an orgin vertex like the list above), unsigned short 2: number of indices each set will have, the last one is a 2 bytes unsigned short, which represent the area's color. Honesty I dont really know how a string fits there and do not overflow, perhaps this is only a pointer to the string, but then where does the pointer even points to? I do not know, as long as it works, I won't change this.
#   a list of 4 bytes integers, which is read according the the rule above.

# TODO: Adapting to the standard .obj file system would be wise I think.
# TODO: And also reduce number base (right now a cm in game would be about 20 to 30 int units, which is less messier to deal with in terms of number works, but since the computer is dealing with float points, shits gets pretty unprecise pretty quick) 
# EDIT: Bruh nvm I mutiplied everything with 0.01 at the end of file read.

f = open("Vert.ver", "rb")
while f.readline() != b'eof':  # read the file and get info for objects block by block
    name = f.readline()  # the name of the object
    asc = name.decode(encoding="ascii")  # read first line of the block as the object's name
    # print("72: " + str(asc.split()[0]))
    lim = (f.read(2)[0], f.read(2)[0])  # read 2 bytes as the number of vertices and 2 bytes as the number of dimensions (I guess I wanted to have 4d capabilities)
    # print("74: " + str(lim))

    # Read an lim[1] ammount of ints as the origin of the object.
    origin = mat.Matrix(lim[1], 1)
    for i in range(lim[1]):
        origin.setIndex((i, 0), struct.unpack('i', f.read(4))[0])

    # Loop lim[0] times: Read lim[1] ammount of ints and put it in a tupple. Each tupple represent a vertex.
    fetchedv = []  # The vertex's coordinate.
    fetchedv2 = []  # A cloned version to store the position of the object relative to the player.
    for i in range(lim[0]):
        fetchedv.append(mat.Matrix(lim[1], 1))
        for ii in range(lim[1]):
            fetchedv[i].setIndex((ii, 0), struct.unpack('i', f.read(4))[0])
            fetchedv2.append(fetchedv[i].clone())
    for iv in fetchedv:
        iv
        # I'll clean this up, soon =)
        # print(iv)
        # print(" ")
    f.read(1)

    # Read lim like how it did above, but this time the lim is for the number of planes and the ammount of info in a tupple (3 ints for cords and 1 short for color, why did I specified this lol did I want to color squares?).
    lim = (f.read(2)[0], f.read(2)[0])
    # print("93: " + str(lim))

    # Loop lim[0] times: Read lim[1] ammount of ints and put it in a tupple. Each tupple represent a vertex.
    fetchedp = []
    fetchedp2 = []
# Comment info: I don't know what this is and why it is commented here lol.
#    for i in range(lim[0]):
#        fetchedp.append([0]*lim[1])

    # Operate like vertex position read, just with an extra color index at the end.
    for i in range(lim[0]):
        fetchedp.append(mat.Matrix(lim[1], 1))
        for ii in range(lim[1] - 1):
            fetchedp[i].setIndex((ii, 0), struct.unpack('i', f.read(4))[0])
        temp = ''
        test = struct.unpack('H', f.read(2))[0]
        for ii in range(test):
            temp = temp + f.read(1).decode(encoding="ascii")
        fetchedp[i].setIndex((lim[1] - 1, 0), temp)
    for ip in fetchedp:
        ip
        # print(ip)
        # print(" ")

    f.read(1)  # Read an extra character, if it's b'eof' then the loop will stop at the start of the next iteration

    # print('\n')
    temp = Shape(name.decode(encoding="ascii").split()[0], origin)
    temp.vertices = fetchedv
    temp.perspectiveVertices = fetchedv2
    temp.planes = fetchedp
    ObjList.append(temp)
f.close()

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


# Rotate a 3D vector in the x axis
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

# Absolutely no clue why there a second identical matrix here bruh.
Projev2 = mat.Matrix(2, 3)
Projev2.setIndex((0, 0), 1)
Projev2.setIndex((1, 1), 1)

pygame.mouse.set_pos(Resolution[0] / 2, Resolution[1] / 2)  # Drag the mouse cursor to the middle of the screen
pygame.mouse.set_visible(False)
Cur = pygame.mouse.get_pos()

verticesClipBuffer = [0, 0, []]


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


# Loop begins .................................................................................................................
ColorMode = 0
cusB.setColorMode(ColorMode)

Overlay_Help = False
Overlay_Help_Alpha = 0.7
Overlay_FOV = True
while True: 
    Canvas.fill('black')
    pygame.pixelcopy.surface_to_array(CanvasArr, Canvas)
    DepthBuffer = np.full((Resolution[0], Resolution[1]), float(FarPlaneDistance))
#     print(CanvasArr)
#     print(DepthBuffer)
#     DepthBuffer = DepthBuffer.astype(int)

    # Check cursor displacement and rotate the camera angle vector accordingly
    Cur = (pygame.mouse.get_pos()[1] - Resolution[1] / 2, pygame.mouse.get_pos()[0] - Resolution[0] / 2)
    if Cur != (0, 0):
        CamAngle.setIndex((0, 0), CamAngle(0, 0) + (Cur[0] / 180 * math.pi / 2))
        if CamAngle(0, 0) > (math.pi / 2):
            CamAngle.setIndex((0, 0), math.pi / 2)
        if CamAngle(0, 0) < -(math.pi / 2):
            CamAngle.setIndex((0, 0), -math.pi / 2)

        CamAngle.setIndex((1, 0), CamAngle(1, 0) - (Cur[1] / 180 * math.pi / 2))
        pygame.mouse.set_pos(Resolution[0] / 2, Resolution[1] / 2)

    # Camera movement
    keys = pygame.key.get_pressed()
    for i in ObjList:
        if keys[pygame.K_i]:
            for ii in range(len(i.vertices)):
                i.vertices[ii] = Rotate3X(i.vertices[ii], 0.1)

        if keys[pygame.K_k]:
            for ii in range(len(i.vertices)):
                i.vertices[ii] = Rotate3X(i.vertices[ii], -0.1)

        if keys[pygame.K_l]:
            for ii in range(len(i.vertices)):
                i.vertices[ii] = Rotate3Y(i.vertices[ii], 0.1)

        if keys[pygame.K_j]:
            for ii in range(len(i.vertices)):
                i.vertices[ii] = Rotate3Y(i.vertices[ii], -0.1)

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
    if (ColorMode == 1):
        Canvas.blit(VCR_MONO.render("Depth view", False, 'red'), (0, 0))

    # Finish draw
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFTBRACKET:
                if Fov > 0.175:  # 10 deg
                    Fov = Fov - 0.1745329

            if event.key == pygame.K_RIGHTBRACKET:
                if Fov < 2.96:
                    Fov = Fov + 0.1745329

            if event.key == pygame.K_1:
                if (cusB.setColorMode(1) == 0):
                    ColorMode = 1

            if event.key == pygame.K_0:
                if (cusB.setColorMode(0) == 0):
                    ColorMode = 0

            if event.key == pygame.K_p:
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
