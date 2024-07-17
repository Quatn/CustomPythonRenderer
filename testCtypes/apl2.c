#define PY_SSIZE_T_CLEAN
#include <stdio.h>
#include <python3.10/Python.h>
#include <python3.10/tupleobject.h>
#include <python3.10/modsupport.h>


int main2() {
	printf("Hello World 2!");
	return 0;
}

int main() {
	printf("Hello World 3!");
	main2();
	return 0;
}


int test1(PyObject *args) {
	char *buffer;
	PyObject a;
	//PyObject_Length(args);
	
	//PyTuple_GetItem(args, 0);
	
    if (!PyArg_ParseTuple(args, "s", &buffer))
       return 0;
	printf("%c", *buffer);
	return 1;
}
