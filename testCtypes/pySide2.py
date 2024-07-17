import testModule as tm
import time
import numpy as np

x = 1000
y = 1000
# print(tm.version())

# start = time.time()
# tm.test_listRange(1, 8000)
# end = time.time()
# print("ExecTime: " + str(end - start))
#
# start = time.time()
# for i in range(8000):
#     print(i)
# end = time.time()
# print("ExecTime: " + str(end - start))

tet = list(list(i for i in range(y)) for _ in range(x))
tet[3][3] = 4
n = 10

start = time.time()
print("C Sums: " + str(tm.test_ListNav(n, tet)))
end = time.time()
print("C ExecTime: " + str(end - start))
print("C tet:")
print(tet)


tet = list(list(i for i in range(y)) for _ in range(x))
tet[3][3] = 4
sum = 0

start = time.time()
for i in range(len(tet)):
    for ii in range(len(tet[0])):
        sum = sum + tet[i][ii]
        tet[i][ii] = n
end = time.time()
print("P ExecTime: " + str(end - start))
print("P Sums:" + str(sum))
print("Py tet:")
print(tet)


tet = list(list(i for i in range(y)) for _ in range(x))
tet[3][3] = 4
sum = 0
tetN = np.array(tet)

start = time.time()
print("C2 Sums: " + str(tm.numpyArr_ListNav(n, y, tetN)))
end = time.time()
print("C2 ExecTime: " + str(end - start))
print("C2 tet:")
print(tetN)


tet = list(list(i for i in range(y)) for _ in range(x))
tet[3][3] = 4
sum = 0
tetN = np.array(tet)

start = time.time()
print("C3 Sums: " + str(tm.numpyArr_ListNav2(n, y, tetN)))
end = time.time()
print("C3 ExecTime: " + str(end - start))
print("C3 tet:")
print(tetN)
