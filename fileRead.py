import customMatrix as mat
import struct


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


def readVer(fileName):
    if not str(fileName).endswith(".ver"):
        return []

    ObjList = []  # the list that contain all of the objects that's gonna be rendered
    # render object data format:
    #   \n
    #   Object Name
    #   unsigned short 1: number of vertices to read (does not include the first vertex, which is the "Origin" of the object), unsigned short 2: number of indices each vertex will have.
    #   a list of 4 bytes integers, which is read according the the rule above.
    #   unsigned short 1: number of sets of vertices to read (does not have an orgin vertex like the list above), unsigned short 2: number of indices each set will have, the last one is a 2 bytes unsigned short, which represent the area's color. Honesty I dont really know how a string fits there and do not overflow, perhaps this is only a pointer to the string, but then where does the pointer even points to? I do not know, as long as it works, I won't change this.
    #   a list of 4 bytes integers, which is read according the the rule above.

    # TODO: Adapting to the standard .obj file system would be wise, I think.
    # TODO: And also reduce number base (right now a cm in game would be about 20 to 30 int units, which is less messier to deal with in terms of number works, but since the computer is dealing with float points, shits gets pretty unprecise pretty quick)
    # EDIT: Bruh nvm I mutiplied everything with 0.01 at the end of file read.

    try:
        f = open(fileName, "rb")
        while f.readline() != b'eof':  # read the file and get info for objects block by block
            name = f.readline()  # the name of the object
            # asc = name.decode(encoding="ascii")  # read first line of the block as the object's name
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
            # for iv in fetchedv:
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
            # for ip in fetchedp:
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
        return ObjList
    except Exception:
        print("Error while trying to read .ver file")
