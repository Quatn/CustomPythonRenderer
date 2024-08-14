import struct
f = open("Vert.ver", "wb")


# --0
# f.write(b'\nA single plane\n')  # Obj name
# f.write(struct.pack('HH', 3, 3))  # Read format: 3 tupple (+1 Origin), each have 3 indices.
# Inv = [[0, 0, 650], [200, 200, 850], [200, -200, 850], [-200, -200, 850]]  # ind 0: Origin, the rest are [x, y, z] of the vertices.
# for i in Inv:
#    for ii in i:
#        f.write(struct.pack('i', ii))
# f.write(b'\n')
#
# f.write(struct.pack('HH', 1, 4))  # Read format: 1 tupple, each have 4 indices.
# Inp = [[2, 1, 0, 'white']]  # Apply color to the area between the indices whose index are stored in the first 3 numbers of a tupple, the 4th index of that tupple specifies the color.
# for i in Inp:
#    for ii in range(3):
#        f.write(struct.pack('i', i[ii]))
#    f.write(struct.pack('H', len(i[3])))
#    f.write(bytes(i[3], 'ascii'))
# f.write(b'\n')
#
# f.write(b'\nSingle plane 2\n')  # Obj name
# f.write(struct.pack('HH', 3, 3))  # Read format: 3 tupple (+1 Origin), each have 3 indices.
# Inv = [[0, 0, 650], [-500, 200, 850], [-500, -200, 850], [-300, -200, 850]]  # ind 0: Origin, the rest are [x, y, z] of the vertices.
# for i in Inv:
#    for ii in i:
#        f.write(struct.pack('i', ii))
# f.write(b'\n')
#
# f.write(struct.pack('HH', 1, 4))  # Read format: 1 tupple, each have 4 indices.
# Inp = [[0, 1, 2, 'red']]  # Apply color to the area between the indices whose index are stored in the first 3 numbers of a tupple, the 4th index of that tupple specifies the color.
# for i in Inp:
#    for ii in range(3):
#        f.write(struct.pack('i', i[ii]))
#    f.write(struct.pack('H', len(i[3])))
#    f.write(bytes(i[3], 'ascii'))
# f.write(b'\n')

# # --1
# f.write(b'\ncube1\n')
# f.write(struct.pack('HH',8,3))
# Inv =[[0,0,650],[200,200,850],[200,-200,850],[-200,-200,850],[-200,200,850],[200,200,450],[200,-200,450],[-200,-200,450],[-200,200,450]]
# for i in Inv:
#  for ii in i:
#      f.write(struct.pack('i',ii))
# f.write(b'\n')
# #
# f.write(struct.pack('HH',12,4))
# Inp = [[0, 1, 2,'white'], [2, 3, 0,'#c4c4c4'], [6, 5, 4,'yellow'], [4, 7, 6,'#ccc627'], [5, 1, 0,'red'], [0, 4, 5,'#ad1d00'], [6, 7, 3,'blue'], [3, 2, 6,'#0d0093'], [0, 3, 7,'green'], [7, 4, 0,'#0d9600'], [6, 2, 1,'orange'], [1, 5, 6,'#cc6600']]
# for i in Inp:
#  for ii in range(3):
#      f.write(struct.pack('i',i[ii]))
#  f.write(struct.pack('H',len(i[3])))
#  f.write(bytes(i[3],'ascii'))
# f.write(b'\n')
# #
# --2
# f.write(b'\nBlandCube\n')
# f.write(struct.pack('HH',8,3))
# Inv = [[0,0,200],[200,200,400],[200,-200,400],[-200,-200,400],[-200,200,400],[200,200,0],[200,-200,0],[-200,-200,0],[-200,200,0]]
# for i in Inv:
#     for ii in i:
#         f.write(struct.pack('i',ii))
# f.write(b'\n')
# #
# f.write(struct.pack('HH',12,4))
# Inp = [[0, 1, 2,'white'], [2, 3, 0,'#c4c4c4'], [6, 5, 4,'white'], [4, 7, 6,'#c4c4c4'], [5, 1, 0,'white'], [0, 4, 5,'#c4c4c4'], [6, 7, 3,'white'], [3, 2, 6,'#c4c4c4'], [0, 3, 7,'white'], [7, 4, 0,'#c4c4c4'], [6, 2, 1,'white'], [1, 5, 6,'#c4c4c4']]
# for i in Inp:
#     for ii in range(3):
#         f.write(struct.pack('i',i[ii]))
#     f.write(struct.pack('H',len(i[3])))
#     print(len(i[3]))
#     f.write(bytes(i[3],'ascii'))
# f.write(b'\n')
#
# --3
# f.write(b'\nTestArch\n')
# f.write(struct.pack('HH', 16, 3))
# Inv = [[250, 0, 650], [225, 200, 450], [225, -200, 450], [650, 200, 450], [650, -200, 450], [450, 300, 450], [350, 250, 450], [-200, 275, 450], [-200, 450, 450], [225, 200, 850], [225, -200, 850], [650, 200, 850], [650, -200, 850], [450, 300, 850], [350, 250, 850], [-200, 275, 850], [-200, 450, 850]]
# for i in Inv:
#    for ii in i:
#        f.write(struct.pack('i', ii))
# f.write(b'\n')
##
# f.write(struct.pack('HH', 28, 4))
# Inp = [[2, 0, 1, 'white'], [1 , 3 , 2, 'white'], [0, 2, 4, '#c4c4c4'], [4, 5, 2, '#c4c4c4'], [7, 6, 5, 'yellow'], [5, 4, 7, 'yellow'], [9, 8, 10, '#ccc627'], [10, 11, 9, 'red'], [12, 10, 8, '#ad1d90'], [10, 13, 12, 'blue'], [13, 14, 15, '#0d0093'], [15, 12, 13, 'green'], [1, 9, 11, 'green'], [11, 3, 1, 'green'], [3, 11, 10, 'blue'], [10, 2, 3, 'blue'], [4, 2, 10, 'yellow'], [10, 12, 4, 'yellow'], [4, 15, 7, 'red'], [15, 4, 12, 'red'], [7, 15, 14, 'purple'], [14, 6, 7, 'purple'], [5, 13, 8, 'orange'], [8, 0, 5, 'orange'], [14, 13, 5, 'pink'], [5, 6, 14, 'pink'], [9, 1, 0, 'white'], [0, 8, 9, 'white']]
# for i in Inp:
#    for ii in range(3):
#        f.write(struct.pack('i', i[ii]))
#    f.write(struct.pack('H', len(i[3])))
#    f.write(bytes(i[3], 'ascii'))
# f.write(b'\n')

# --4
f.write(b'\nIntersectingPlane\n')
f.write(struct.pack('HH', 6, 3))
Inv = [[0, 0, 400], [400, 400, 400], [400, -400, 400], [-400, -400, -400], [400, -400, -400], [-400, -400, 400], [-400, 400, 400]]
for i in Inv:
    for ii in i:
        f.write(struct.pack('i', ii))
f.write(b'\n')
#
f.write(struct.pack('HH', 4, 4))
Inp = [[0, 2, 1, 'white'], [2, 0 , 1, 'yellow'], [4, 5, 3, 'red'], [5, 4, 3, 'blue']]
for i in Inp:
    for ii in range(3):
        f.write(struct.pack('i', i[ii]))
    f.write(struct.pack('H', len(i[3])))
    print(len(i[3]))
    f.write(bytes(i[3], 'ascii'))
f.write(b'\n')

f.write(b'eof')
f.close()

f = open("Vert.ver", "rb")
while f.readline() != b'eof':
    name = f.readline()
    asc = name.decode(encoding="ascii")
    print(asc.split()[0])
    lim = (f.read(2)[0], f.read(2)[0])
    print(lim)

    origin = []
    for i in range(lim[1]):
        origin.append(struct.unpack('i', f.read(4))[0])

    fetchedv = []
    for i in range(lim[0]):
        fetchedv.append([0] * lim[1])

    for i in range(lim[0]):
        for ii in range(lim[1]):
            temp = struct.unpack('i', f.read(4))[0]
            fetchedv[i][ii] = temp
    print(fetchedv)
    f.read(1)

    lim = (f.read(2)[0], f.read(2)[0])
    print(lim)
    fetchedp = []
    for i in range(lim[0]):
        fetchedp.append([0] * lim[1])

    for i in range(lim[0]):
        for ii in range(lim[1] - 1):
            temp = struct.unpack('i', f.read(4))[0]
            fetchedp[i][ii] = temp
        temp = ''
        test = struct.unpack('H', f.read(2))[0]
        for ii in range(test):
            temp = temp + f.read(1).decode(encoding="ascii")
        fetchedp[i][lim[1] - 1] = temp
    print(fetchedp)
    f.read(1)
    print('\n')
f.close()
