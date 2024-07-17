import pygame
import sys
import math

pygame.init()
Resolution = (1440, 960)
Canvas = pygame.display.set_mode(Resolution)
clock = pygame.time.Clock()

VCR_MONO = pygame.font.Font('VCR_OSD_MONO_1.001.ttf', 48)
pointer = VCR_MONO.render('+', False, 'red')
pointer1 = VCR_MONO.render('+', False, 'gray')
pointer2 = VCR_MONO.render('+', False, 'yellow')
pointerNumerated = [VCR_MONO.render('0', False, 'yellow')]
for i in range(8):
    pointerNumerated.append(VCR_MONO.render(str(i+1), False, 'yellow'))

pointer_rect = pointer.get_rect(center = (0, 0))

Vertices = [[200,200,200],[200,-200,200],[-200,-200,200],[-200,200,200],[200,200,-200],[200,-200,-200],[-200,-200,-200],[-200,200,-200]]

def dotProduct(vector1,vector2):
    if len(vector1) == len(vector2):
        prod = 0
        for i in range(len(vector1)):
            prod += vector1[i] * vector2[i]
        return prod
    else: raise Exception("Vectors size differ")

def MatrixMult(matrix1,matrix2):
    if len(matrix1) == len(matrix2[0]):
        Out = []
        for i in range(len(matrix2)):
            Out.append([0]* len(matrix1[0]))
        for x1 in range(len(matrix1[0])):
            row1 = [0] * len(matrix1)
            for i in range(len(matrix1)):
                row1[i] = matrix1[i][x1]
            for y2 in range(len(matrix2)):
                Out[y2][x1] = dotProduct(row1,matrix2[y2])
        return Out
    else: raise Exception("1st Argument's row is not the same length as 2nd Argument's column")

test = MatrixMult([[3,4],[9,2],[1,5]] , [[1,2,3]])
for i in test:
    print(i)

a = [[1,2,3,4],[5,6,7,8]]
b = [[1,2],[3,4],[5,6],[7,8]] 
print(MatrixMult(b,a))

def Rotate3X(vertex,radian):
    if len(vertex[0]) == 3:
        Out = MatrixMult([[1,0,0], [0,math.cos(radian),math.sin(radian)], [0,-math.sin(radian),math.cos(radian)]], vertex)
        return Out
    else: raise Exception("Inputed vertex was not 3D")

def Rotate3Y(vertex,radian):
    if len(vertex[0]) == 3:
        Out = MatrixMult([[math.cos(radian),0,-math.sin(radian)], [0,1,0], [math.sin(radian),0,math.cos(radian)]], vertex)
        return Out
    else: raise Exception("Inputed vertex was not 3D")

test2 = MatrixMult([[1,0],[0,1],[0,0]], [Vertices[0]])[0]
for i in test2:
    print(math.floor(i))

#connectedVerticies = [(0,0)]
#for i in range(len(Vertices)):
#    for ii in range(len(Vertices)):
#        if math.sqrt(math.pow(Vertices[i][0] - Vertices[ii][0],2) + pow(Vertices[i][1] - Vertices[ii][1],2) + pow(Vertices[i][2] - Vertices[ii][2],2)) < 410:
#            tempbool = 0
#            for iv in connectedVerticies:
#                if iv == (ii,i): tempbool = 1
#            if not tempbool: connectedVerticies.append((i,ii))
#
tesV = 0
point = [0] * len(Vertices)
#
#SortedVertices = [0] * len(Vertices)
#for i in range(len(Vertices)):
#    SortedVertices[i] = i

planes = [[0, 1, 2], [2, 3, 0], [6, 5, 4], [4, 7, 6], [5, 1, 0], [0, 4, 5], [6, 7, 3], [3, 2, 6], [0, 3, 7], [7, 4, 0], [6, 2, 1], [1, 5, 6]]
planesColors = ['white','#c4c4c4','yellow','#ccc627','red','#ad1d00','blue','#0d0093','green','#0d9600','orange','#cc6600']
colorCycle = -1
while True:
    Canvas.fill('black') 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

#        if event.type == pygame.KEYDOWN:
#            if event.key == pygame.K_o:
#                tesV = tesV + 0.01
#            if event.key == pygame.K_i:
#                tesV = tesV - 0.01
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        for i in range(len(Vertices)):
            Vertices[i] = Rotate3X([Vertices[i]], 0.1)[0]

    if keys[pygame.K_s]:
        for i in range(len(Vertices)):
            Vertices[i] = Rotate3X([Vertices[i]], -0.1)[0]

    if keys[pygame.K_d]:
        for i in range(len(Vertices)):
            Vertices[i] = Rotate3Y([Vertices[i]], 0.1)[0]

    if keys[pygame.K_a]:
        for i in range(len(Vertices)):
            Vertices[i] = Rotate3Y([Vertices[i]], -0.1)[0]

    for i in range(len(Vertices)):
        point[i] = MatrixMult([[1,0],[0,1],[tesV,0]], [Vertices[i]])[0]
        pointer_rect.bottomright =(Resolution[0]/2+point[i][0],Resolution[1]/2+point[i][1]) 
        if Vertices[i][2] > 0: Canvas.blit(pointer,pointer_rect.center)
        else: Canvas.blit(pointer1,pointer_rect.center)

    for i in planes:
        a = [Vertices[i[0]][0] - Vertices[i[1]][0], Vertices[i[0]][1] - Vertices[i[1]][1], Vertices[i[0]][2] - Vertices[i[1]][2]]
        b = [Vertices[i[1]][0] - Vertices[i[2]][0], Vertices[i[1]][1] - Vertices[i[2]][1], Vertices[i[1]][2] - Vertices[i[2]][2]]
        colorCycle = colorCycle + 1
        if colorCycle >= len(planesColors): colorCycle = 0

        if a[0] * b[1] - a[1] * b[0] < 0:
            temp = (Resolution[0]/2,Resolution[1]/2)
            pygame.draw.polygon(Canvas,planesColors[colorCycle],[(temp[0]+point[i[0]][0], temp[1]+point[i[0]][1]), (temp[0]+point[i[1]][0], temp[1]+point[i[1]][1]), (temp[0]+point[i[2]][0], temp[1]+point[i[2]][1])])
#            pygame.draw.line(Canvas,'White',(Resolution[0]/2+point[i[0]][0],Resolution[1]/2+point[i[0]][1]),(Resolution[0]/2+point[i[1]][0],Resolution[1]/2+point[i[1]][1]))
#            pygame.draw.line(Canvas,'White',(Resolution[0]/2+point[i[1]][0],Resolution[1]/2+point[i[1]][1]),(Resolution[0]/2+point[i[2]][0],Resolution[1]/2+point[i[2]][1]))
#            pygame.draw.line(Canvas,'White',(Resolution[0]/2+point[i[0]][0],Resolution[1]/2+point[i[0]][1]),(Resolution[0]/2+point[i[2]][0],Resolution[1]/2+point[i[2]][1]))

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
    clock.tick(30)
