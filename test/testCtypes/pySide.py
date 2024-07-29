import ctypes

yo = ctypes.cdll.LoadLibrary("./apl2.so")
# yo.test1.argtype = ctypes.POINTER(ctypes.py_object)
yo.main()

a = int(3)
b = [a, 4]


def testest(a):
    print(a)


print(yo.test1(ctypes.py_object(b)))
