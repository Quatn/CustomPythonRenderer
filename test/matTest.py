import customMatrix
import pyautogui as hj

a = customMatrix.Matrix(3, 1)
b = customMatrix.Matrix(3, 2)

a.setIndex((1, 0), 2)

a.setIndex((1, 0), 10)


b.setColumn(1, [1, 2, 3])

b.setRow(1, [8, 9])

test = [1, 2, 3, 4]

test2 = test.copy()

test2[2] = 9

print(test)
print(test2)
