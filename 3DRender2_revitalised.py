# import sys
import pygame
import struct
import math
import customMatrix as mat


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

# Fov = math.pi / 2.1
Fov = math.pi / 4

# TODO: Find out wtf this part is
SuppleFov = (math.pi / 2) - Fov
csSuppleRatio = math.cos(SuppleFov) / math.sin(SuppleFov)
csSuppleRatio1 = math.cos(math.pi / 4) / math.sin(math.pi / 4)
tanFov = math.tan(Fov)
tanFov1 = math.tan(math.pi / 4)

NearPlaneDistance = 0.1  # 1 / tanFov  # The distance between the camera and the near plane (or just the distance that planes will be clipped if it goes below)

print("55: " + str(math.tan(math.pi / 4)))

ObjList = []  # the list that contain all of the objects that's gonna be rendered
# render object data format:
#   \n
#   Object Name
#   unsigned short 1: number of vertices to read (does not include the first vertex, which is the "Origin" of the object), unsigned short 2: number of indices each vertex will have.
#   a list of 4 bytes integers, which is read according the the rule above.
#   unsigned short 1: number of sets of vertices to read (does not have an orgin vertex like the list above), unsigned short 2: number of indices each set will have, the last one is a 2 bytes unsigned short, which represent the area's color. Honesty I dont really know how a string fits there and do not overflow, perhaps this is only a pointer to the string, but then where does the pointer even points to? I do not know, as long as it works, I won't change this.
#   a list of 4 bytes integers, which is read according the the rule above.

# TODO: Adapting to the standard .obj file system would be wise I think.
# TODO: And also reduce number base (right now a cm in game would be about 20 to 30 int units, which is less messier to deal with in terms of number works, but since the computer is dealing with float points, shits gets pretty unprecise pretty quick) EDIT: Bruh nvm I mutiplied everything with 0.01 at the end of file read.

f = open("Vert.ver", "rb")
while f.readline() != b'eof':  # read the file and get info for objects block by block
    name = f.readline()  # the name of the object
    asc = name.decode(encoding="ascii")  # read first line of the block as the object's name
    print("72: " + str(asc.split()[0]))
    lim = (f.read(2)[0], f.read(2)[0])  # read 2 bytes as the number of vertices and 2 bytes as the number of dimensions (I guess I wanted to have 4d capabilities)
    print("74: " + str(lim))

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
        print(iv)
        print(" ")
    f.read(1)

    # Read lim like how it did above, but this time the lim is for the number of planes and the ammount of info in a tupple (3 ints for cords and 1 short for color, why did I specified this lol did I want to color squares?).
    lim = (f.read(2)[0], f.read(2)[0])
    print("93: " + str(lim))

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
        print(ip)
        print(" ")

    f.read(1)  # Read an extra character, if it's b'eof' then the loop will stop at the start of the next iteration

    print('\n')
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

# for i in ObjList:
#    for ii in i.perspectiveVertices:
#        print(ii)

# Old cube from before file read to object implementation.
cube1 = [[200, 200, 400], [200, -200, 400], [-200, -200, 400], [-200, 200, 400], [200, 200, 800], [200, -200, 800], [-200, -200, 800], [-200, 200, 800]]

# Old matrix operation before I made my own little matrix library.
# def vdotProduct(vector1,vector2):
#    if len(vector1) == len(vector2):
#        prod = 0
#        for i in range(len(vector1)):
#            prod += vector1[i] * vector2[i]
#        return prod
#    else: raise Exception("Vectors size differ")

# def MatrixMult(matrix1,matrix2):
#    if len(matrix1) == len(matrix2[0]):
#        Out = []
#        for i in range(len(matrix2)):
#            Out.append([0]* len(matrix1[0]))
#        for x1 in range(len(matrix1[0])):
#            row1 = [0] * len(matrix1)
#            for i in range(len(matrix1)):
#                row1[i] = matrix1[i][x1]
#            for y2 in range(len(matrix2)):
#                Out[y2][x1] = dotProduct(row1,matrix2[y2])
#        return Out
#    else: raise Exception("1st Argument's row is not the same length as 2nd Argument's column")

# test = MatrixMult([[3,4],[9,2],[1,5]] , [[1,2,3]])
# for i in test:
#    print(i)


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


# idk why this is here.
# connectedVerticies = [(0,0)]
# for i in range(len(Vertices)):
#    for ii in range(len(Vertices)):
#        if math.sqrt(math.pow(Vertices[i][0] - Vertices[ii][0],2) + pow(Vertices[i][1] - Vertices[ii][1],2) + pow(Vertices[i][2] - Vertices[ii][2],2)) < 410:
#            tempbool = 0
#            for iv in connectedVerticies:
#                if iv == (ii,i): tempbool = 1
#            if not tempbool: connectedVerticies.append((i,ii))
#
#
# SortedVertices = [0] * len(Vertices)
# for i in range(len(Vertices)):
#    SortedVertices[i] = i


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

# Loop begins .................................................................................................................
while True: 
    Canvas.fill('black')

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
            CamPos.setIndex((2, 0), CamPos(2, 0) + (math.sin(CamAngle(1, 0)) * 0.1))
            CamPos.setIndex((0, 0), CamPos(0, 0) + (math.cos(CamAngle(1, 0)) * 0.1))

        if keys[pygame.K_a]:
            CamPos.setIndex((2, 0), CamPos(2, 0) - (math.sin(CamAngle(1, 0)) * 0.1))
            CamPos.setIndex((0, 0), CamPos(0, 0) - (math.cos(CamAngle(1, 0)) * 0.1))

        if keys[pygame.K_w]:
            CamPos.setIndex((2, 0), CamPos(2, 0) + (math.cos(CamAngle(1, 0)) * 0.1))
            CamPos.setIndex((0, 0), CamPos(0, 0) - (math.sin(CamAngle(1, 0)) * 0.1))

        if keys[pygame.K_s]:
            CamPos.setIndex((2, 0), CamPos(2, 0) - (math.cos(CamAngle(1, 0)) * 0.1))
            CamPos.setIndex((0, 0), CamPos(0, 0) + (math.sin(CamAngle(1, 0)) * 0.1))

        if keys[pygame.K_e]:
            CamAngle.setColumn(0, [0, 0, 0])

# The older Camera movement behaviour that does not increment camera position based on the camera angle
#        if event.type == pygame.KEYDOWN:
#            if event.key == pygame.K_o:
#                tesV = tesV + 0.01
#            if event.key == pygame.K_i:
#                tesV = tesV - 0.01

    # Calculate the perspectiveVertices vector of an object such that its position relative to the camera is as if the camera is in [0, 0, 0] and facing the same direction as the X axis
    renderBuffer = []  # queue of planes to be rendered
    clippedPlanes = []  # renderBuffer after all of the clipping is done
    for i in ObjList:
        for ii in range(len(i.vertices)):
            i.perspectiveVertices[ii].copyFrom(mat.matrixSums(i.vertices[ii], CamPos.constantMult(-1)))
            i.perspectiveVertices[ii] = Rotate3Y(i.perspectiveVertices[ii], CamAngle(1, 0))
            i.perspectiveVertices[ii] = Rotate3X(i.perspectiveVertices[ii], CamAngle(0, 0))
            i.perspectiveVertices[ii] = Rotate3Z(i.perspectiveVertices[ii], CamAngle(2, 0))

#            Print the vertex's index in the same place it's at on the screen.
#            Canvas.blit(VCR_MONO.render(str(i.perspectiveVertices[0]), False, 'red'), (0,48 * 0))

        for ii in i.planes:

            # probably some vars that used to be in the cross product code
            # a = [i.perspectiveVertices[ii(0,0)](0,0) - i.perspectiveVertices[ii(1,0)](0,0), i.perspectiveVertices[ii(0,0)](1,0) - i.perspectiveVertices[ii(1,0)](1,0), i.perspectiveVertices[ii(0,0)](2,0) - i.perspectiveVertices[ii(1,0)](2,0)]
            # b = [i.perspectiveVertices[ii(1,0)](0,0) - i.perspectiveVertices[ii(2,0)](0,0), i.perspectiveVertices[ii(1,0)](1,0) - i.perspectiveVertices[ii(2,0)](1,0), i.perspectiveVertices[ii(1,0)](2,0) - i.perspectiveVertices[ii(2,0)](2,0)]
            # print(i.planes)

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
                            [i.perspectiveVertices[ii(0, 0)], i.perspectiveVertices[ii(1, 0)], i.perspectiveVertices[ii(2, 0)]]  # the 3 vertices
                            , ii(3, 0)  # the color of the plane
                            , i.perspectiveVertices[ii(0, 0)](2, 0) + i.perspectiveVertices[ii(1, 0)](2, 0) + i.perspectiveVertices[ii(2, 0)](2, 0)  # the combined z depth of the 3 vertices
                            ])

    # process the planes in the renderBuffer queue, this is where plane clipping happens.
    # TODO: Redo this part but instead of clipping by just reducing the line, actually finding the point of intercept and PERSONALLY set it as to not get unclean results
    i = 0
    while i < len(renderBuffer):
        # Clip the plane against the near plane
        inside = []
        outside = []
        for vertexIndex in range(renderBuffer[i][0].__len__()):
            if renderBuffer[i][0][vertexIndex](2, 0) < NearPlaneDistance:
                outside.append(vertexIndex)
            else:
                inside.append(vertexIndex)

        match inside.__len__():
            case 1:  # when there's only 1 vertex inside of the frustrum, meaning that the other 2 will have to be clipped
                # fuel = [[mat.Matrix(1, 1), mat.Matrix(1, 1), mat.Matrix(1, 1)], renderBuffer[i][1], renderBuffer[i][2]]  # the fuel for the queue-el
                fuel = [[mat.Matrix(1, 1), mat.Matrix(1, 1), mat.Matrix(1, 1)], 'red', renderBuffer[i][2]]  # Hardcoded color for debug purposes
                for vi in range(3):
                    fuel[0][vi].copyFrom(renderBuffer[i][0][vi])

                for outsideIndex in outside:
                    ratio = (NearPlaneDistance - renderBuffer[i][0][outsideIndex](2, 0)) / (renderBuffer[i][0][inside[0]](2, 0) - renderBuffer[i][0][outsideIndex](2, 0))  # the ratio between the portion of the line that's under the NearPlaneDistance compared to the whole line

                    # increments the x and y of the vertex with index = outsideIndex by the different between the vertex inside and it * ratio, and set z to the NearPlaneDistance
                    fuel[0][outsideIndex].setIndex((0, 0), renderBuffer[i][0][outsideIndex](0, 0) + (ratio * (renderBuffer[i][0][inside[0]](0, 0) - renderBuffer[i][0][outsideIndex](0, 0))))
                    fuel[0][outsideIndex].setIndex((1, 0), renderBuffer[i][0][outsideIndex](1, 0) + (ratio * (renderBuffer[i][0][inside[0]](1, 0) - renderBuffer[i][0][outsideIndex](1, 0))))
                    fuel[0][outsideIndex].setIndex((2, 0), NearPlaneDistance)

                renderBuffer.append(fuel)

            case 2:  # when there's 2 vertex inside of the frustrum, meaning that the last one will have to be clipped
                bruhMon = 0
                # Algorithm:
                # let i1 and i2 be the 2 vertex inside of the frustrum and o be the vertex outside
                # in any circumstances, we might get the input plane (renderBuffer[i][0]) as [i1, i2, o] (the order of the 3 vertex is arbitrary)
                # we copy the input plane into the loop, at the first loop fuel will be [i1, i2, o]
                # i1's index is the first insideIndex
                # after calculating the ratio between i1 and o, then use it to push o to the place that (I hope) is the point of interception between line(i1, o) and the near plane, we get a new vertex, which we will call alpha
                # we sanitise it be setting it's detph to NearPlaneDistance, making sure it will not be processed here again
                # we will set fuel to [i1, i2, alpha] and append it to renderBuffer, thus getting the first part of the quadrangle that we need
                # we now need the second part of the quadrangle, which will consist of i2, alpha, and the point of interception between line(i2, o) and the near plane, which we will call beta.
                # getting beta is the same as getting alpha, but because i've designed the vertex system that take a specific sequence of vertex to determine the front and back side of a plane, which I've forgotten and although it would be easy to just learn it again, it would means that I will have to countinue to hardcode that sequence in, will is an absolute pain if I want to change the sequence, so I'm gonna do stuffs like this to preserve the original sequence instead.
                # Anyways, since both vertices will include the vertex i2, and i1 to i2 and alpha to i2 should have the same orientation (just eyeball it lol), that means that [alpha, i2, beta] should have the same sequence as [i1, i2, o]
                # which is why at the end of the loop, we will set renderBuffer[i][0][insideIndex] (i1) to fuel[0][outside[0]] (alpha)

                # Update: Except this DOES NOT WORK, due to the fact that I designed the obj read system to read planes and vertices seperately inorder to re-use a vertex for multiple plane, which means that when I set renderBuffer[i][0][insideIndex] I also changed the vertex of some other plane, which alters them.
                # Which is why I'm going to copy renderBuffer[i][0][insideIndex] to an input vector.

                inputPlane = [mat.Matrix(1, 1), mat.Matrix(1, 1), mat.Matrix(1, 1)]
                for vi in range(3):
                    inputPlane[vi].copyFrom(renderBuffer[i][0][vi])

                for insideIndex in inside:
                    # fuel = [[], renderBuffer[i][1], renderBuffer[i][2]]  # the fuel for the queue-el
                    fuel = [[], 'green' if bruhMon == 0 else 'blue', renderBuffer[i][2]]  # Hardcoded colors for debug purposes
                    fuel[0] = [mat.Matrix(1, 1), mat.Matrix(1, 1), mat.Matrix(1, 1)]
                    fuel[0][0].copyFrom(inputPlane[0])
                    fuel[0][1].copyFrom(inputPlane[1])
                    fuel[0][2].copyFrom(inputPlane[2])

                    ratio = (NearPlaneDistance - inputPlane[outside[0]](2, 0)) / (inputPlane[insideIndex](2, 0) - inputPlane[outside[0]](2, 0))  # the ratio between the portion of the line that's under the NearPlaneDistance compared to the whole line

                    # increments the x and y of the vertex with index = outsideIndex by the different between the vertex inside and it * ratio, and set z to the NearPlaneDistance
#                         print("bruhMon2: " + str(insideIndex))
#                         print("AA: ")
#                         print(inputPlane[insideIndex])
#                         print("BB: ")
#                         print(fuel[0])
#                         for matacs in fuel[0]:
#                             print(matacs)
                    fuel[0][outside[0]].setIndex((0, 0), inputPlane[outside[0]](0, 0) + (ratio * (inputPlane[insideIndex](0, 0) - inputPlane[outside[0]](0, 0))))
                    fuel[0][outside[0]].setIndex((1, 0), inputPlane[outside[0]](1, 0) + (ratio * (inputPlane[insideIndex](1, 0) - inputPlane[outside[0]](1, 0))))
                    fuel[0][outside[0]].setIndex((2, 0), NearPlaneDistance)
#                         print("CC: ")
#                         for matacs in fuel[0]:
#                             print(matacs)

                    renderBuffer.append(fuel.copy())
                    # print("394: " + str(bruhMon) + " " +)

                    inputPlane[insideIndex] = fuel[0][outside[0]]

                    bruhMon = bruhMon + 1

            case 3:
                clippedPlanes.append(renderBuffer[i])

        i = i + 1

#     for ii in clippedPlanes:
#         for iii in ii[0]:
#             print("421: " + str(iii))

    if keys[pygame.K_m]:
        for ii in clippedPlanes:
            for iii in ii[0]:
                print("425: " + str(iii))
        pygame.quit()
        exit()


#             renderable = 0
#             notClip = []
#             clip = []
# 
#             # Check if the 3 vertices of a plane is within the pyramid of view, put the planes that need clipping inside the clip[] and increments renderable, the rest inside notClip[]
#             if renderBuffer[ii][0][0](2, 0) <= 0 or abs(renderBuffer[ii][0][0](0, 0) / renderBuffer[ii][0][0](2, 0)) - tanFov1 > 0.02:
#                 clip.append(renderBuffer[ii][0][0])
#                 renderable = renderable + 1
#             else:
#                 notClip.append(renderBuffer[ii][0][0])
# 
#             if renderBuffer[ii][0][1](2, 0) <= 0 or abs(renderBuffer[ii][0][1](0, 0) / renderBuffer[ii][0][1](2, 0)) - tanFov1 > 0.02:
#                 clip.append(renderBuffer[ii][0][1])
#                 renderable = renderable + 1
#             else:
#                 notClip.append(renderBuffer[ii][0][1])
# 
#             if renderBuffer[ii][0][2](2, 0) <= 0 or abs(renderBuffer[ii][0][2](0, 0) / renderBuffer[ii][0][2](2, 0)) - tanFov1 > 0.02:
#                 clip.append(renderBuffer[ii][0][2])
#                 renderable = renderable + 1
#             else:
#                 notClip.append(renderBuffer[ii][0][2])
# 
# #               Older logic, I guess
# #                if i.perspectiveVertices[ii(0,0)](2,0) > 0:
# #                    notClip.append(i.perspectiveVertices[ii(0,0)])
# #                    renderable = renderable + 1
# #                else: clip.append(i.perspectiveVertices[ii(0,0)])
# #
# #                if i.perspectiveVertices[ii(1,0)](2,0) > 0:
# #                    notClip.append(i.perspectiveVertices[ii(1,0)])
# #                    renderable = renderable + 1
# #                else: clip.append(i.perspectiveVertices[ii(1,0)])
# #
# #                if i.perspectiveVertices[ii(2,0)](2,0) > 0:
# #                    notClip.append(i.perspectiveVertices[ii(2,0)])
# #                    renderable = renderable + 1
# #                else: clip.append(i.perspectiveVertices[ii(2,0)])
# 
#             #                            ((abs(clip[0](0,0)) - (clip[0](2,0) * tanFov)) / ((zdiff * csSuppleRatio) + xdiff))
# 
#             # Jesus Fucking Christ
#             nestSwitch = 0  # I guess I wanted to see when the case 0 is active (case 0 is nesting shits)
#             match renderable:
#                 case 0:
#                     nestSwitch = 1
# 
#                     renderable = 0
#                     notClip = []
#                     clip = []
# 
#                     if renderBuffer[ii][0][0](2, 0) <= 0 or abs(renderBuffer[ii][0][0](1, 0) / renderBuffer[ii][0][0](2, 0)) - tanFov1 > 0.02:
#                         clip.append(renderBuffer[ii][0][0])
#                         renderable = renderable + 1
#                     else:
#                         notClip.append(renderBuffer[ii][0][0])
# 
#                     if renderBuffer[ii][0][1](2, 0) <= 0 or abs(renderBuffer[ii][0][1](1, 0) / renderBuffer[ii][0][1](2, 0)) - tanFov1 > 0.02:
#                         clip.append(renderBuffer[ii][0][1])
#                         renderable = renderable + 1
#                     else:
#                         notClip.append(renderBuffer[ii][0][1])
# 
#                     if renderBuffer[ii][0][2](2, 0) <= 0 or abs(renderBuffer[ii][0][2](1, 0) / renderBuffer[ii][0][2](2, 0)) - tanFov1 > 0.02:
#                         clip.append(renderBuffer[ii][0][2])
#                         renderable = renderable + 1
#                     else:
#                         notClip.append(renderBuffer[ii][0][2])
# 
#                     match renderable:
#                         case 0:
#                             toBeRenderd.append([notClip, renderBuffer[ii][1], renderBuffer[ii][2]])
# 
#                         case 1:
#                             verticesClipBuffer = [0, 0, []]
#                             _i = 0
#                             for iii in notClip:
#                                 zdiff = abs(clip[0](2, 0) - iii(2, 0))
#                                 xdiff = abs(clip[0](1, 0) - iii(1, 0))
#                                 verticesClipBuffer[_i] = mat.matrixSums(clip[0], mat.matrixSums(iii, clip[0].constantMult(-1)).constantMult(((abs(clip[0](1, 0)) - (clip[0](2, 0) * tanFov1)) / ((zdiff * csSuppleRatio1) + xdiff))))
#                                 _i = _i + 1
# 
#                             toBeRenderd.append([[verticesClipBuffer[0], verticesClipBuffer[1], notClip[0]], "orange", renderBuffer[ii][2]])
#                             toBeRenderd.append([[verticesClipBuffer[1], notClip[0], notClip[1]], "light blue", renderBuffer[ii][2]])
#                     #               Debug
#                     #                for itemp in range(len(ii)):
#                     #                    minZofPlane = min(minZofPlane, i.perspectiveVertices[itemp][2])
#                         case 2:
#                             verticesClipBuffer = [0, 0, []]
#                             _i = 0
#                             for iii in clip:
#                                 zdiff = abs(iii(2, 0) - notClip[0](2, 0))
#                                 xdiff = abs(iii(1, 0) - notClip[0](1, 0))
#                                 verticesClipBuffer[_i] = mat.matrixSums(iii, mat.matrixSums(notClip[0], iii.constantMult(-1)).constantMult(((abs(iii(1, 0)) - (iii(2, 0) * tanFov1)) / ((zdiff * csSuppleRatio1) + xdiff))))
#                                 _i = _i + 1
# 
#                             toBeRenderd.append([[verticesClipBuffer[0], verticesClipBuffer[1], notClip[0]], "gray", renderBuffer[ii][2]])
#                 case 1:
#                     verticesClipBuffer = [0, 0, []]
#                     _i = 0
#                     for iii in notClip:
#                         zdiff = abs(clip[0](2, 0) - iii(2, 0))
#                         xdiff = abs(clip[0](0, 0) - iii(0, 0))
#                         verticesClipBuffer[_i] = mat.matrixSums(clip[0], mat.matrixSums(iii, clip[0].constantMult(-1)).constantMult(((abs(clip[0](0, 0)) - (clip[0](2, 0) * tanFov1)) / ((zdiff * csSuppleRatio1) + xdiff))))
#                         _i = _i + 1
# 
#                     renderBuffer.append([[verticesClipBuffer[0], verticesClipBuffer[1], notClip[0]], "red", renderBuffer[ii][2]])
#                     renderBuffer.append([[verticesClipBuffer[1], notClip[0], notClip[1]], "blue", renderBuffer[ii][2]])
# 
#                 case 2:
#                     verticesClipBuffer = [0, 0, []]
#                     _i = 0
#                     for iii in clip:
#                         zdiff = abs(iii(2, 0) - notClip[0](2, 0))
#                         xdiff = abs(iii(0, 0) - notClip[0](0, 0))
#                         verticesClipBuffer[_i] = mat.matrixSums(iii, mat.matrixSums(notClip[0], iii.constantMult(-1)).constantMult(((abs(iii(0, 0)) - (iii(2, 0) * tanFov1)) / ((zdiff * csSuppleRatio1) + xdiff))))
#                         _i = _i + 1
# 
#                     renderBuffer.append([[verticesClipBuffer[0], verticesClipBuffer[1], notClip[0]], "gray", renderBuffer[ii][2]])
# 
#             ii = ii + 1
#             if ii > 1000:
#                 print("480:" + str(renderable))
#                 print("481:" + str(nestSwitch))
#                 raise Exception("Stuck in a loop")

# Problably some debug stuffs, idk anymore.
#        for ii in toBeRenderd:
#            for iii in ii[0]:
#                projectedRenderable.append(MatrixMult([[1,0],[0,1],[0,0]], [i.vertices[ii]])[0])
#            pointer_rect.bottomright =(Resolution[0]/2+point[ii][0],Resolution[1]/2+point[ii][1])
#            if i.vertices[ii][2] > 0: Canvas.blit(pointer1,pointer_rect.center)
#            else: Canvas.blit(pointer1,pointer_rect.center)

#    for ii in range(len(toBeRenderd)):
#            Canvas.blit(VCR_MONO.render(str(toBeRenderd[ii][0][0]), False, 'red'), (0,48 * ii))

    # Sort the toBeRenderd buffer based on the planes' z depth
    for ii in range(len(clippedPlanes)):
        for iii in range(len(clippedPlanes) - ii):
            if clippedPlanes[ii][2] <= clippedPlanes[iii + ii][2]:
                sWitch = clippedPlanes[iii + ii]
                clippedPlanes[iii + ii] = clippedPlanes[ii]
                clippedPlanes[ii] = sWitch

#     for ii in clippedPlanes:
#         print("577: " + str(ii[0]))
#         for iii in range(len(ii[0])):
#             print("579: " + str(ii[0][iii]))

    # Apply perspective to the processed vertices using tanFov and the depth of the vertex and translating that to the 2D plane. If the clipped plane somehow still have a z depth below 0, divide it by 10000 instead of infinite.
    transformedPlanes = []
    for ii in range(len(clippedPlanes)):
#         print("588: " + str(ii))
#         print("589: " + str(clippedPlanes[ii][0]))
        transformedPlanes.append([[], clippedPlanes[ii][1]])
        for iii in range(3):
            if clippedPlanes[ii][0][iii](2, 0) > 0:
                Projev.setIndex((0, 0), Resolution[0] / (tanFov * clippedPlanes[ii][0][iii](2, 0)))
            else:
                Projev.setIndex((0, 0), 10000)
            Projev.setIndex((1, 1), Resolution[0] / (tanFov * clippedPlanes[ii][0][iii](2, 0)))
#             print("596: " + str(transformedPlanes[ii]))
            transformedPlanes[ii][0].append(mat.matrixMult(Projev, clippedPlanes[ii][0][iii]))

# Was I ok?
# temp[0]+(ii[0][0](0,0))/ii[0][0](2,0) if temp[0]+(ii[0][0](0,0))/ii[0][0](2,0) < 1000 else 1000, temp[1]+(ii[0][0](1,0))/ii[0][0](2,0) if temp[1]+(ii[0][0](1,0))/ii[0][0](2,0) < 1000 else 1000), 
# temp[0]+(ii[0][1](0,0))/ii[0][0](2,0) if temp[0]+(ii[0][1](0,0))/ii[0][1](2,0) < 1000 else 1000, temp[1]+(ii[0][1](1,0))/ii[0][1](2,0) if temp[1]+(ii[0][1](1,0))/ii[0][1](2,0) < 1000 else 1000), 
# temp[0]+(ii[0][2](0,0))/ii[0][2](2,0) if temp[0]+(ii[0][2](0,0))/ii[0][2](2,0) < 1000 else 1000, temp[1]+(ii[0][2](1,0))/ii[0][2](2,0) if temp[1]+(ii[0][2](1,0))/ii[0][2](2,0) < 1000 else 1000)
#            (temp[0]+ii[0][0](0,0), temp[1]+ii[0][0](1,0)), (temp[0]+ii[0][1](0,0), temp[1]+ii[0][1](1,0)), (temp[0]+ii[0][2](0,0), temp[1]+ii[0][2](1,0))

    # Draws the product on the screen
    for ii in transformedPlanes:
        temp = (Resolution[0] / 2, Resolution[1] / 2)  # why...
        pygame.draw.polygon(Canvas, ii[1], [ (temp[0]+ii[0][0](0, 0), temp[1]+ii[0][0](1, 0)), (temp[0]+ii[0][1](0, 0), temp[1]+ii[0][1](1, 0)), (temp[0]+ii[0][2](0, 0), temp[1]+ii[0][2](1, 0)) ])

    Canvas.blit(VCR_MONO.render(str(len(renderBuffer)), False, 'red'), (0, 0))
    Canvas.blit(VCR_MONO.render(str(len(clippedPlanes)), False, 'red'), (0, 48))

#   Debug...?
#    Canvas.blit(VCR_MONO.render(str(CamAngle), False, 'red'), (0,0))

# Old drawing logic and also a bit of a custom line drawing function I was gonna write myself, but then I got lazy and though I would not be able to reinvent the wheel good enough, so I just left it here
#    for ii in ObjList:
#        if ii.name == 'TestArch':
#            for iii in range(len(ii.perspectiveVertices)):
#                point = mat.matrixMult(Projev, ii.perspectiveVertices[iii])
#                pointer_rect.bottomright =(Resolution[0]/2+point(0,0) if Resolution[0]/2+point(0,0) < Resolution[0] else Resolution[0], Resolution[1]/2+point(1,0) if Resolution[0]/2+point(0,0) < Resolution[0] else Resolution[0]) 
#                if ii.perspectiveVertices[iii](2,0) > 0: Canvas.blit(pointerNumerated[iii],pointer_rect.center)
#                else: Canvas.blit(pointerNumerated[iii],pointer_rect.center)
#
#            Canvas.blit(VCR_MONO.render(str(mat.crossProduct(ObjList[0].perspectiveVertices[0], mat.matrixSums(ObjList[0].perspectiveVertices[0], ObjList[0].perspectiveVertices[1].constantMult(-1)))), False, 'red'), (0,0))

#    Canvas.blit(VCR_MONO.render(str( ObjList[0].perspectiveVertices[0]), False, 'red'), (0,0))

#    for i in toBeRenderd:
#        pygame.draw.line(Canvas,'White',(Resolution[0]/2+i[0][0][0][0],Resolution[1]/2+i[0][0][0][1]),(Resolution[0]/2+i[0][1][0][0],Resolution[1]/2+i[0][1][0][1]))
#        pygame.draw.line(Canvas,'White',(Resolution[0]/2+i[0][1][0][0],Resolution[1]/2+i[0][1][0][1]),(Resolution[0]/2+i[0][2][0][0],Resolution[1]/2+i[0][2][0][1]))
#        pygame.draw.line(Canvas,'White',(Resolution[0]/2+i[0][2][0][0],Resolution[1]/2+i[0][2][0][1]),(Resolution[0]/2+i[0][0][0][0],Resolution[1]/2+i[0][0][0][1]))

#            pointer_rect.bottomright =(Resolution[0]/2+point[i[1]][0],Resolution[1]/2+point[i[1]][1])
#            Canvas.blit(pointer2,pointer_rect.center)

#    i = 1
#    while i < len(Vertices):
#        while Vertices[SortedVertices[i]][2] < Vertices[SortedVertices[i]-1][2]:
#            SortedVertices[i] = SortedVertices[i] + SortedVertices[i-1]
#            SortedVertices[i-1] = SortedVertices[i] - SortedVertices[i-1]
#            SortedVertices[i] = SortedVertices[i] - SortedVertices[i-1]
#            i = i - 1
#            print(i)
#            if i < 1: break
#        i = i + 1
#        print(SortedVertices)
#    for i in SortedVertices:
#        print(Vertices[i][2])
#    print("loop break")
#    for i in connectedVerticies:
#        pygame.draw.line(Canvas,'White',(Resolution[0]/2+point[i[0]][0],Resolution[1]/2+point[i[0]][1]),(Resolution[0]/2+point[i[1]][0],Resolution[1]/2+point[i[1]][1]))

#    x = 0
#    y = 0
#    while x <= targetX:
#        #while y < targetY:
#        #    Canvas.fill('white',((x,y),(1,1)))
#        #    y = y + 1
#
#        Canvas.fill('white',((x,y),(1,drawStep)))
#        y = y + drawStep
#        x = x + 1
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                for i in clippedPlanes:
                    for ii in i[0]:
                        print(ii)
                pygame.quit()
                exit()
    clock.tick(30)
