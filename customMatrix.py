class Matrix:
    Content = []
    height = 0
    width = 0

    def __init__(self, height, width):
        self.Content = []
        self.height = height
        self.width = width

        for i in range(width):
            self.Content.append([0])
            for ii in range(height - 1):
                self.Content[i].append(0)

    def __call__(self, y, x):
        '''Get value of a specific index, same as calling the variable'''
        if x < len(self.Content) and y < len(self.Content[0]):
            return self.Content[x][y]
        else: raise Exception(f"getIndex exception: tried to get value of index {str((y, x))} of a Matrix with size {str((len(self.Content[0]), len(self.Content)))} (mat:\n{str(self)})")

    def getSize(self):
        return (self.height, self.width)

    def copyFrom(self, anotherMatrix):
        '''Deep copy from anotherMatrix'''
        self.height = anotherMatrix.height
        self.width = anotherMatrix.width

        self.Content = []

        for i in range(self.width):
            self.Content.append([])
            newCol = anotherMatrix.getColumn(i)
            for ii in range(self.height):
                self.Content[i].append(newCol[ii])

    def getIndex(self, y, x):
        '''Get value of a specific index, same as just calling the variable'''
        if x < self.width and y < self.height:
            return self.Content[x][y]
        else: raise Exception(f"getIndex exception: tried to get value of index {str((y, x))} of a Matrix with size {str((self.height, self.width))}")

    def setIndex(self, cord, val):
        '''Set value for a specific index'''
        if cord[0] < self.height and cord[1] < self.width:
            self.Content[cord[1]][cord[0]] = val
        else: raise Exception(f"setIndex exception: tried to put value into index {str((cord[1], cord[0]))} of a Matrix with size {str((self.height, self.width))}")

    def getColumn(self, x):
        '''Return a list with all of the elements in a specific collumn'''
        if x < self.height:
            return list(i for i in self.Content[x])
        else: raise Exception(f"getColumn exception: tried to get collumn {str(x)} of a Matrix that has {str(self.height)} collumns")

    def setColumn(self, x, newColumn):
        '''Set a collumn of the Matrix to a newColumn'''
        if x < self.height and len(newColumn) == len(self.Content[x]):
            self.Content[x] = newColumn
        else: raise Exception(f"setColumn exception: tried to put a collumn with size {str(len(newColumn))} into collumn number {str(x)} of a Matrix with size {str((self.height, self.width))}")

    def getRow(self, y):
        '''Return a list with all of the elements in a specific row'''
        if y < self.height:
            temp = []
            for i in range(self.width):
                temp.append(self.Content[i][y])
            return temp
        else: raise Exception(f"getRows exception: tried to get row {str(y)} of a Matrix that has {str(self.height)} rows")

    def setRow(self, y, newRow):
        '''Set a row of the Matrix to a newRow'''
        if y < self.height and len(newRow) == self.width:
            for i in range(self.width):
                self.Content[i][y] = newRow[i]
        else: raise Exception(f"setRows exception: tried to put a row with size {str(len(newRow))} into row number {str(y)} of a Matrix with size {str((self.height, self.width))}")

    def constantMult(self, constant):
        Out = Matrix(self.height, self.width)
        for i in range(self.height):
            for ii in range(self.width):
                Out.Content[ii][i] = self.Content[ii][i] * constant
        return Out

    def clone(self):
        Out = Matrix(self.height, self.width)
        Out.Content = self.Content
        return Out

    def __str__(self):
        Out = ""
        for i in range(self.height):
            Out = Out + str(self.getRow(i)) + "\n"
        return Out
   

def makeIdentityMatrix(size):
    Out = Matrix(size,size)
    for i in range(size):
        Out.setIndex((i,i),1)
    return Out

def matrixSums(matrix1, matrix2):
    if matrix1.getSize() == matrix2.getSize():
        temp = Matrix(matrix1.height, matrix2.width)
        for i in range(matrix1.height):
            for ii in range(matrix1.width):
                temp.setIndex((i, ii), matrix1(i,ii) + matrix2(i,ii))
        return temp
    else: raise Exception(f"matrixSums exception: tried to sums {matrix1.getSize()} matrix and {matrix2.getSize()} matrix")

def dotProduct(matrix1,matrix2):
    if matrix1.getSize() == matrix2.getSize():
        prod = 0
        for i in range(matrix1.width):
            for ii in range(matrix1.height):
                prod += matrix1(ii,i) * matrix2(ii,i)
        return prod
    else: raise Exception("Matrices size differs")

def matrixMult(matrix1,matrix2):
    if matrix1.width == matrix2.height:
        Out = Matrix(matrix1.height,matrix2.width)
        for i in range(matrix1.height):
            for ii in range(matrix2.width):
                Out.setIndex((i,ii), vdotProduct(matrix1.getRow(i),matrix2.getColumn(ii)))
        return Out
    else: raise Exception("1st Matrix's width is not the same length as 2nd Matrix's height")

def vdotProduct(vector1,vector2):
    if len(vector1) == len(vector2):
        prod = 0
        for i in range(len(vector1)):
            prod += vector1[i] * vector2[i]
        return prod
    else: raise Exception("Vectors size differ")

def crossProduct(vector1,vector2):
    if vector1.height == 3 and vector2.height == 3 and vector1.width == 1 and vector2.width == 1:
        Out = Matrix(3,1)
        Out.setIndex((0,0), (vector1(1,0) * vector2(2,0)) - (vector1(2,0) * vector2(1,0)))
        Out.setIndex((1,0), (vector1(2,0) * vector2(0,0)) - (vector1(0,0) * vector2(2,0)))
        Out.setIndex((2,0), (vector1(0,0) * vector2(1,0)) - (vector1(1,0) * vector2(0,0)))
        return Out
    else: raise Exception("Inputed vectors contain something other than 1x3 Matrices (3d Vectors): {}")
