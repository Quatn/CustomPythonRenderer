#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <python3.10/numpy/arrayobject.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int Ctest_listRange(int start, int end) {
	while (start < end) {
		printf("%i\n", start++);
	}
	return 0;
}

static PyObject* test_listRange(PyObject* self, PyObject *args) {
	int start, end;

	if (!PyArg_ParseTuple(args, "ii", &start, &end))
		return Py_None;

	return Py_BuildValue("i", Ctest_listRange(start, end));
}

static PyObject* test_ListNav(PyObject* self, PyObject *args) {
	int n, sizeH = -1, sizeV = -1, sum = 0;
	PyObject huh;

	if (!PyArg_ParseTuple(args, "iO!", &n, &PyList_Type, &huh))
		return Py_BuildValue("i", -1);

	sizeV = PyList_Size(PyTuple_GetItem(args, 1));
	sizeH = PyList_Size(PyList_GetItem(PyTuple_GetItem(args, 1), 0));

	//PyObject *b = Py_BuildValue("(ii)", 1, 1);
	//PyObject *c = PyTuple_GetItem(args, 1);

	printf("SizeV: %i\n", sizeV);
	printf("SizeH: %i\n", sizeH);
	printf("n: %i\n", n);

	for (int i = 0; i < sizeV; i++) {
		PyObject *fectedCol = PyList_GetItem(PyTuple_GetItem(args, 1), i);

		for (int ii = 0; ii < sizeH; ii++) {
			sum += PyLong_AsLong(PyList_GetItem(fectedCol, ii));
			PyList_SetItem(fectedCol, ii, Py_BuildValue("i", n));
		}
	}

	//printf("Is Tuple: %i\n", PyTuple_Check(c));
	//printf("Is Tuple: %i\n", PyTuple_Check(args));
	//Py_ssize_t a = PyTuple_Size(PyTuple_GetItem(args, 1));

	return Py_BuildValue("i", sum);
	//return Py_BuildValue("i", PyTuple_Size(&huh));
	//return Py_BuildValue("i", PyTuple_GetItem(&huh, 0));
	//return PyTuple_GetItem(&huh, 1);
}

static PyObject* numpyArr_ListNav(PyObject* self, PyObject* args) {
	int n, sizeH = -1, sizeV = -1;
	int64_t sum = 0;
	PyArrayObject *arr;

	if (!PyArg_ParseTuple(args, "iiO!", &n, &sizeV, &PyArray_Type, &arr))
		return Py_BuildValue("i", -1);

	//PyArray_Size(arr);
	sizeH = PyArray_SIZE(arr) / sizeV;
	//printf("V = %i, H = %i\n", sizeV, sizeH);
	int64_t *data = PyArray_DATA(arr);

	for (int i = 0; i < sizeV; i++) {
		//printf("%li\n", data[i * sizeH + n]);
		for (int ii = 0; ii < sizeH; ii++) {
			sum += data[i * sizeH + ii];
			data[i * sizeH + ii] = n;
		}
	}

	return Py_BuildValue("i", sum);
}


static PyObject* numpyArr_ListNav2(PyObject* self, PyObject* args) {
	int n, sizeH = -1, sizeV = -1;
	int64_t sum = 0;
	PyArrayObject *arr;

	if (!PyArg_ParseTuple(args, "iiO!", &n, &sizeV, &PyArray_Type, &arr))
		return Py_BuildValue("i", -1);

	//PyArray_Size(arr);
	sizeH = PyArray_SIZE(arr) / sizeV;
	printf("V = %i, H = %i\n", sizeV, sizeH);
	int64_t *data = PyArray_DATA(arr);

	for (int i = 0; i < sizeV * sizeV; i = i + sizeV) {
		//printf("%li\n", data[i * sizeH + n]);
		for (int ii = 0; ii < sizeH; ii++) {
			sum += data[i + ii];
			data[i + ii] = n;
		}
	}

	return Py_BuildValue("i", sum);
}


static PyObject* drawSquare(PyObject* self, PyObject* args) {
	int n, sizeH = -1, sizeV = -1, fromX = 0, fromY = 0, toX = 0, toY = 0;
	PyObject *from, *to;
	PyArrayObject *arr;

	if (!PyArg_ParseTuple(args, "iiO!O!O!", &n, &sizeV, &PyTuple_Type, &from, &PyTuple_Type, &to, &PyArray_Type, &arr))
		return Py_BuildValue("i", -1);

	sizeH = PyArray_SIZE(arr) / sizeV;

	if (!PyArg_ParseTuple(from, "ii", &fromX, &fromY))
		return Py_BuildValue("i", -1);

	if (!PyArg_ParseTuple(to, "ii", &toX, &toY))
		return Py_BuildValue("i", -1);

	if (toX < sizeH)
		return Py_BuildValue("i", -1);

	//printf("V = %i, H = %i\n", sizeV, sizeH);

	int64_t *data = PyArray_DATA(arr);

	for (int i = fromY * sizeV; i < toY * sizeV; i += sizeV) {
		for (int ii = fromX; ii < toX; ii++) {
			data[i + ii] = n;
		}
	}

	return Py_BuildValue("i", 0);
}

static PyObject*  drawTriangle(PyObject* self, PyObject* args) {
	int sizeY = -1, color = 0;
	PyObject *triObj[3];
	PyArrayObject *Canvas;

	if (!PyArg_ParseTuple(args, "iO!O!O!O!i", &sizeY, &PyArray_Type, &Canvas
				, &PyList_Type, &triObj[0], &PyList_Type, &triObj[1], &PyList_Type, &triObj[2], &color))
		return Py_BuildValue("i", -1);

	//sizeX = PyArray_SIZE(Canvas) / sizeX;
	//printf("%i, %i", sizeX, sizeY);
	int tri[][2] = {{0, 0}, {0, 0}, {0, 0}};

	//if (!PyList_Check(&triObj[0]) || !PyList_Check(&triObj[1]) || !PyList_Check(&triObj[2]))
	//	return Py_BuildValue("i", -2);
	triObj[0] = PyTuple_GetItem(args, 2);
	triObj[1] = PyTuple_GetItem(args, 3);
	triObj[2] = PyTuple_GetItem(args, 4);

	tri[0][0] = PyLong_AsLong(PyList_GetItem(triObj[0], 0));
	tri[0][1] = PyLong_AsLong(PyList_GetItem(triObj[0], 1));

	tri[1][0] = PyLong_AsLong(PyList_GetItem(triObj[1], 0));
	tri[1][1] = PyLong_AsLong(PyList_GetItem(triObj[1], 1));

	tri[2][0] = PyLong_AsLong(PyList_GetItem(triObj[2], 0));
	tri[2][1] = PyLong_AsLong(PyList_GetItem(triObj[2], 1));
	
	int indTop = 0, indBot = 0, indSide = -1;

	if (tri[1][0] > tri[indTop][0])
		indTop = 1;

	if (tri[2][0] > tri[indTop][0])
		indTop = 2;

	if (tri[1][0] <= tri[indBot][0])
		indBot = 1;

	if (tri[2][0] <= tri[indBot][0])
		indBot = 2;

	indSide = 3 - indTop - indBot;

	//printf("\nT: %i\nB: %i\nS: %i\n", indTop, indBot, indSide);

	int spineVec[] = {tri[indTop][0] - tri[indBot][0], tri[indTop][1] - tri[indBot][1]};
	double spine_a = 0, spine_b = 0;
	//spine_inf = False
	if (spineVec[0] != 0) {
		spine_a = (double)spineVec[1] / (double)spineVec[0];
		spine_b = tri[indTop][1] - (spine_a * tri[indTop][0]);
	}

	int ribcageVec[] = {tri[indTop][0] - tri[indSide][0], tri[indTop][1] - tri[indSide][1]};
	double ribcage_a = 0, ribcage_b = 0;
	//ribcage_inf = False
	if (ribcageVec[0] != 0) {
		ribcage_a = (double)ribcageVec[1] / (double)ribcageVec[0];
		ribcage_b = tri[indTop][1] - (ribcage_a * tri[indTop][0]);
	}

	int femurVec[] = {tri[indSide][0] - tri[indBot][0], tri[indSide][1] - tri[indBot][1]};
	double femur_a = 0, femur_b = 0;
	//femur_inf = False
	if (femurVec[0] != 0) {
		femur_a = (double)femurVec[1] / (double)femurVec[0];
		femur_b = tri[indBot][1] - (femur_a * tri[indBot][0]);
	}

	double start, end;
	int i;
	int64_t *CanvasData = PyArray_DATA(Canvas);
	if (spineVec[0] != 0) {
		if (tri[indSide][1] < spine_a * tri[indSide][0] + spine_b) {
			i = tri[indBot][0];
			start = femur_a * i + femur_b;
			end = spine_a * i + spine_b;

			for (i = i; i < tri[indSide][0]; i++) {
				start = start + femur_a;
				end = end + spine_a;
				for (int pointer = (int)(i * sizeY + start); pointer <= (i * sizeY + end); pointer++) {
					CanvasData[pointer] = color;
					//Canvas.set_at((pointer, i), "green");
				}
			}

			start = ribcage_a * i + ribcage_b;
			end = spine_a * i + spine_b;
			for (i = i; i <= tri[indTop][0]; i++) {
				start = start + ribcage_a;
				end = end + spine_a;
				for (int pointer = (int)(i * sizeY + start); pointer <= (i * sizeY + end); pointer++) {
					CanvasData[pointer] = color;
					//Canvas.set_at((pointer, i), "green");
				}
			}
		}
		else {
			i = tri[indBot][0];
			//printf("case 2: bot %i side %i\n", i, tri[indSide][0]);
			start = spine_a * i + spine_b;
			end = femur_a * i + femur_b;

			for (i = i; i < tri[indSide][0]; i++) {
				//printf("start = %lf, end = %lf\n", start, end);
				start = start + spine_a;
				end = end + femur_a;
				for (int pointer = (int)(i * sizeY + start); pointer <= (i * sizeY + end); pointer++) {
					//printf("%i", pointer);
					CanvasData[pointer] = color;
					//Canvas.set_at((pointer, i), "green");
				}
			}

			start = spine_a * i + spine_b;
			end = ribcage_a * i + ribcage_b;
			for (i = i; i <= tri[indTop][0]; i++) {
				start = start + spine_a;
				end = end + ribcage_a;
				for (int pointer = (int)(i * sizeY + start); pointer <= (i * sizeY + end); pointer++) {
					//printf("%i\n", pointer);
					CanvasData[pointer] = color;
					//Canvas.set_at((pointer, i), "green");
				}
			}
		}
	}

	//for (int i = 0; i<3; i++) {
	//	CanvasData[tri[i][0] * sizeX + tri[i][1]] = 16711680;
	//}
	//printf("%i %i, %lf %lf, %lf %lf end", tri[indTop][0], tri[indTop][1], spine_a, spine_b, femur_a, femur_b);
	//printf("%lf %lf, %lf %lf, %lf %lf end", ribcage_a, ribcage_b, spine_a, spine_b, femur_a, femur_b);
	return Py_BuildValue("i", 0);
}

static PyObject* version(PyObject* self) {
	return Py_BuildValue("s", "V1.1");
}

static PyMethodDef methDef[] = {
	{"test_listRange", test_listRange, METH_VARARGS, "Test Method, print all numbers between start and end"},
	{"version", (PyCFunction)version, METH_NOARGS, "Returns version"},
	{"test_ListNav", test_ListNav, METH_VARARGS, "Return sum of all values in a List and set all of them to n for benchmarking purpose"},
	{"numpyArr_ListNav", numpyArr_ListNav, METH_VARARGS, "Test Arr"},
	{"numpyArr_ListNav2", numpyArr_ListNav2, METH_VARARGS, "Same as V1 but I want to try optimizing (will deparallelize the process so I probably won't actually use it, I just want to see the effects)"},
	{"drawSquare", drawSquare, METH_VARARGS, "(int Decimal Color, int Verticle Size of Array, Tupple From position, Tupple To position, Array) Draws a square"},
	{"drawTriangle", drawTriangle, METH_VARARGS, "(int Verticle Size of Array, Array, 3 Tuples of the 3 points of the triangle, int color) Draws a square"},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef modlDef = {
	PyModuleDef_HEAD_INIT,
	"testModule",
	"Pls just work bruh this project has been delayed for too long",
	-1,
	methDef
};

PyMODINIT_FUNC PyInit_testModule(){
	PyObject* Mod = PyModule_Create(&modlDef);
	import_array();
	return Mod;
}
