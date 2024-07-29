#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define PI 3.14159265358979323846
#define endl printf("\n")
#include <math.h>
#include <Python.h>
#include <python3.10/numpy/arrayobject.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static PyObject*  draw3DTriangles(PyObject* self, PyObject* args) {
	int sizeY = -1, sizeX = -1, halfSizeX = 1, halfSizeY = 1;
	double HFOV = 1, VFOV = 1, tanHFOV = 1, tanVFOV = 1, nearPlaneDistance = -1, farPlaneDistance = -1;
	PyObject *thirdArg;
	PyArrayObject *Canvas, *DepthBuffer;

	if (!PyArg_ParseTuple(args, "iO!O!ddO!d",
				&sizeY
				, &PyArray_Type, &Canvas
				, &PyList_Type, &thirdArg
				, &nearPlaneDistance
				, &farPlaneDistance
				, &PyArray_Type, &DepthBuffer
				, &HFOV
			))
		return Py_BuildValue("i", -1);

	thirdArg = PyTuple_GetItem(args, 2);

	if (PyList_Size(thirdArg) < 1)
		return Py_BuildValue("i", -2);

	if (PyArray_SIZE(Canvas) != PyArray_SIZE(DepthBuffer)) 
		return Py_BuildValue("i", -2);

	int64_t *CanvasData = PyArray_DATA(Canvas);
	double *DepthBufferData = PyArray_DATA(DepthBuffer);

	sizeX = PyArray_SIZE(Canvas) / sizeY;
	halfSizeX = sizeX / 2;
	halfSizeY = sizeY / 2;

	HFOV /= 2;
	tanHFOV = tan(HFOV);
	VFOV = atan2(halfSizeX, sizeX / tanHFOV);
	tanVFOV = tan(VFOV);

	int nIndsInNear = 0, nIndsInFar = 0;  //Number of indices that's further than the near plane and nearer than the far plane, mostly used as control vars
	int numOfTris = PyList_Size(thirdArg);  //Number of triangles to process

	double tri[][3] = {{0., 0., 0.}, {0., 0., 0.}, {0., 0., 0.}};
	for (int triNum = 0; triNum < numOfTris; triNum++) {

		PyObject *tupleData = PyList_GetItem(thirdArg, triNum);
		PyObject *triMatArr[] = {PyTuple_GetItem(tupleData, 0),
			PyTuple_GetItem(tupleData, 1),
			PyTuple_GetItem(tupleData, 2)};

		int color = PyLong_AsLong(PyTuple_GetItem(tupleData, 3));

		tri[0][0] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[0], 0));
		tri[0][1] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[0], 1));
		tri[0][2] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[0], 2));

		tri[1][0] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[1], 0));
		tri[1][1] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[1], 1));
		tri[1][2] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[1], 2));

		tri[2][0] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[2], 0));
		tri[2][1] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[2], 1));
		tri[2][2] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[2], 2));

		nIndsInNear = 0;
		for(int i = 0; i<3 ; i++) if (tri[i][2] > nearPlaneDistance) nIndsInNear++;

		double triClippedNear[][3][3] = 
		{
			{
				{0, 0, 0},
				{0, 0, 0},
				{0, 0, 0}
			}
			,
			{
				{0, 0, 0},
				{0, 0, 0},
				{0, 0, 0}
			}
		};  
		switch (nIndsInNear) {
			case 1: 
				{
					int outSideInd[2], inSideInd = 0;

					//Kinda dumb var optimize
					for(int i = 0; i<3 ; i++) if (tri[i][2] <= nearPlaneDistance) outSideInd[inSideInd++] = i;
					inSideInd = 3 - outSideInd[0] - outSideInd[1];

					for(int i = 0; i<3 ; i++) triClippedNear[0][inSideInd][i] = tri[inSideInd][i];

					for(int i = 0; i<2; i++) {
						double ratio = (nearPlaneDistance - tri[outSideInd[i]][2]) / (tri[inSideInd][2] - tri[outSideInd[i]][2]);

						triClippedNear[0][outSideInd[i]][0] = tri[outSideInd[i]][0] + ratio * (tri[inSideInd][0] - tri[outSideInd[i]][0]);
						triClippedNear[0][outSideInd[i]][1] = tri[outSideInd[i]][1] + ratio * (tri[inSideInd][1] - tri[outSideInd[i]][1]);
						triClippedNear[0][outSideInd[i]][2] = nearPlaneDistance;
					}
				}
				break;

			case 2:
				{
					int outSideInd = 0, inSideInd[2];

					//Kinda dumb var optimize
					for(int i = 0; i<3 ; i++) if (tri[i][2] > nearPlaneDistance) inSideInd[outSideInd++] = i;
					outSideInd = 3 - inSideInd[0] - inSideInd[1];

					double alpha[2][3];
					for(int i = 0; i<2; i++) {
						double ratio = (tri[inSideInd[i]][2] - nearPlaneDistance) / (tri[inSideInd[i]][2] - tri[outSideInd][2]);

						alpha[i][0] = tri[inSideInd[i]][0] + ratio * (tri[outSideInd][0] - tri[inSideInd[i]][0]);
						alpha[i][1] = tri[inSideInd[i]][1] + ratio * (tri[outSideInd][1] - tri[inSideInd[i]][1]);
						alpha[i][2] = nearPlaneDistance;
					}

					//{i1, i2, alpha1}
					for(int i = 0; i<3 ; i++) triClippedNear[0][0][i] = tri[inSideInd[0]][i];
					for(int i = 0; i<3 ; i++) triClippedNear[0][1][i] = tri[inSideInd[1]][i];
					for(int i = 0; i<3 ; i++) triClippedNear[0][2][i] = alpha[0][i];

					//{alpha1, alpha2, i2}
					for(int i = 0; i<3 ; i++) triClippedNear[1][0][i] = alpha[0][i];
					for(int i = 0; i<3 ; i++) triClippedNear[1][1][i] = alpha[1][i];
					for(int i = 0; i<3 ; i++) triClippedNear[1][2][i] = tri[inSideInd[1]][i];
				}
				break;

			case 3:
					for(int i = 0; i<3 ; i++) 
						for(int ii = 0; ii<3 ; ii++) 
							triClippedNear[0][i][ii] = tri[i][ii];
				break;

			default: continue;
		}

		//Clip the triangles that have been clipped againts the near plane, againts the far plane
		double triClippedAll[][3][3] = 
		{
			{
				{0, 0, 0},
				{0, 0, 0},
				{0, 0, 0}
			}
			,
			{
				{0, 0, 0},
				{0, 0, 0},
				{0, 0, 0}
			}
			,
			{
				{0, 0, 0},
				{0, 0, 0},
				{0, 0, 0}
			}
			,
			{
				{0, 0, 0},
				{0, 0, 0},
				{0, 0, 0}
			}
		};
		int triFarCount = 0;

		//If nIndsInNear is 2, clip both of the triangle in triClippedNear, else only clip the first one (since the second index is unsed)
		for(int nearTriNum = 0; nearTriNum < ((nIndsInNear == 2)? 2: 1); nearTriNum++) {
			nIndsInFar = 0;
			for(int i = 0; i<3 ; i++) if (triClippedNear[nearTriNum][i][2] < farPlaneDistance) nIndsInFar++;

			switch (nIndsInFar) {
				case 1: 
					{
						int outSideInd[2], inSideInd = 0;

						for(int i = 0; i<3 ; i++) if (triClippedNear[nearTriNum][i][2] >= farPlaneDistance) outSideInd[inSideInd++] = i;
						inSideInd = 3 - outSideInd[0] - outSideInd[1];

						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][inSideInd][i] = triClippedNear[nearTriNum][inSideInd][i];

						for(int i = 0; i<2; i++) {
							double ratio = (triClippedNear[nearTriNum][outSideInd[i]][2] - farPlaneDistance) / (triClippedNear[nearTriNum][outSideInd[i]][2] - triClippedNear[nearTriNum][inSideInd][2]);

							triClippedAll[triFarCount][outSideInd[i]][0] = triClippedNear[nearTriNum][outSideInd[i]][0] + ratio * (triClippedNear[nearTriNum][inSideInd][0] - triClippedNear[nearTriNum][outSideInd[i]][0]);
							triClippedAll[triFarCount][outSideInd[i]][1] = triClippedNear[nearTriNum][outSideInd[i]][1] + ratio * (triClippedNear[nearTriNum][inSideInd][1] - triClippedNear[nearTriNum][outSideInd[i]][1]);
							triClippedAll[triFarCount][outSideInd[i]][2] = farPlaneDistance;
						}
						triFarCount++;
					}
					break;

				case 2:
					{
						int outSideInd = 0, inSideInd[2];

						//Kinda dumb var optimize
						for(int i = 0; i<3 ; i++) if (triClippedNear[nearTriNum][i][2] < farPlaneDistance) inSideInd[outSideInd++] = i;
						outSideInd = 3 - inSideInd[0] - inSideInd[1];

						double alpha[2][3];
						for(int i = 0; i<2; i++) {
							double ratio = (farPlaneDistance - triClippedNear[nearTriNum][inSideInd[i]][2]) / (triClippedNear[nearTriNum][outSideInd][2] - triClippedNear[nearTriNum][inSideInd[i]][2]);

							alpha[i][0] = triClippedNear[nearTriNum][inSideInd[i]][0] + ratio * (triClippedNear[nearTriNum][outSideInd][0] - triClippedNear[nearTriNum][inSideInd[i]][0]);
							alpha[i][1] = triClippedNear[nearTriNum][inSideInd[i]][1] + ratio * (triClippedNear[nearTriNum][outSideInd][1] - triClippedNear[nearTriNum][inSideInd[i]][1]);
							alpha[i][2] = farPlaneDistance;
						}

						//{i1, i2, alpha1}
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][0][i] = triClippedNear[nearTriNum][inSideInd[0]][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][1][i] = triClippedNear[nearTriNum][inSideInd[1]][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][2][i] = alpha[0][i];

						//{alpha1, alpha2, i2}
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount + 1][0][i] = alpha[0][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount + 1][1][i] = alpha[1][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount + 1][2][i] = triClippedNear[nearTriNum][inSideInd[1]][i];

						triFarCount += 2;
					}
					break;

				case 3:
					for(int i = 0; i<3 ; i++) 
						for(int ii = 0; ii<3 ; ii++) 
							triClippedAll[triFarCount][i][ii] = triClippedNear[nearTriNum][i][ii];
					triFarCount++;
					break;

				default: continue;
			}
		}
		if (triFarCount < 1) continue;

		//Transfer trianlge cords to screen pixel positions and Apply perspective
		int tri2D[triFarCount][3][3];
		for (int i = 0; i < triFarCount; i++)
			for (int ii = 0; ii < 3; ii++) {
				tri2D[i][ii][0] = triClippedAll[i][ii][0] / ( tanHFOV * (double)triClippedAll[i][ii][2] ) * halfSizeX + halfSizeX;
				tri2D[i][ii][1] = triClippedAll[i][ii][1] / ( tanVFOV * (double)triClippedAll[i][ii][2] ) * halfSizeY + halfSizeY;
				tri2D[i][ii][2] = triClippedAll[i][ii][2];
			}

		for (int d = 0; d < triFarCount; d++) {
			int indTop = 0, indBot = 0, indSide = -1;

			if (tri2D[d][1][0] > tri2D[d][indTop][0])
				indTop = 1;

			if (tri2D[d][2][0] > tri2D[d][indTop][0])
				indTop = 2;

			if (tri2D[d][1][0] <= tri2D[d][indBot][0])
				indBot = 1;

			if (tri2D[d][2][0] <= tri2D[d][indBot][0])
				indBot = 2;

			indSide = 3 - indTop - indBot;

			int spineVec[] = {tri2D[d][indTop][0] - tri2D[d][indBot][0], tri2D[d][indTop][1] - tri2D[d][indBot][1], tri2D[d][indTop][2] - tri2D[d][indBot][2]};
			double spine_a = 0, spine_b = 0;
			if (spineVec[0] != 0) {
				spine_a = (double)spineVec[1] / (double)spineVec[0];
				spine_b = tri2D[d][indTop][1] - (spine_a * tri2D[d][indTop][0]);
			}

			int ribcageVec[] = {tri2D[d][indTop][0] - tri2D[d][indSide][0], tri2D[d][indTop][1] - tri2D[d][indSide][1], tri2D[d][indTop][2] - tri2D[d][indSide][2]};
			double ribcage_a = 0, ribcage_b = 0;
			if (ribcageVec[0] != 0) {
				ribcage_a = (double)ribcageVec[1] / (double)ribcageVec[0];
				ribcage_b = tri2D[d][indTop][1] - (ribcage_a * tri2D[d][indTop][0]);
			}

			int femurVec[] = {tri2D[d][indSide][0] - tri2D[d][indBot][0], tri2D[d][indSide][1] - tri2D[d][indBot][1], tri2D[d][indSide][2] - tri2D[d][indBot][2]};
			double femur_a = 0, femur_b = 0;
			if (femurVec[0] != 0) {
				femur_a = (double)femurVec[1] / (double)femurVec[0];
				femur_b = tri2D[d][indBot][1] - (femur_a * tri2D[d][indBot][0]);
			}

			double start, end;
			int i, safeStart, safeEnd, yChunk;
			if (spineVec[0] != 0) {
				if (tri2D[d][indSide][1] < spine_a * tri2D[d][indSide][0] + spine_b) {
					i = (tri2D[d][indBot][0] > 0)? tri2D[d][indBot][0]: 0;
					start = femur_a * i + femur_b;
					end = spine_a * i + spine_b;

					for (i = i; i < ((tri2D[d][indSide][0] < sizeX)? tri2D[d][indSide][0] : sizeX); i++) {
						start = start + femur_a;
						end = end + spine_a;
						yChunk = i * sizeY;
						safeStart = yChunk + ((start > 0)? start : 0);
						safeEnd = yChunk + ((end < sizeY)? end : sizeY);
						for (int pointer = safeStart; pointer < safeEnd; pointer++) {
							CanvasData[pointer] = color;
						}
					}

					start = ribcage_a * i + ribcage_b;
					end = spine_a * i + spine_b;
					for (i = i; i < ((tri2D[d][indTop][0] < sizeX)? tri2D[d][indTop][0] : sizeX); i++) {
						start = start + ribcage_a;
						end = end + spine_a;
						yChunk = i * sizeY;
						safeStart = yChunk + ((start > 0)? start : 0);
						safeEnd = yChunk + ((end < sizeY)? end : sizeY);
						for (int pointer = safeStart; pointer < safeEnd; pointer++) {
							CanvasData[pointer] = color;
						}
					}
				}
				else {
					i = (tri2D[d][indBot][0] > 0)? tri2D[d][indBot][0]: 0;
					start = spine_a * i + spine_b;
					end = femur_a * i + femur_b;

					for (i = i; i < ((tri2D[d][indSide][0] < sizeX)? tri2D[d][indSide][0] : sizeX); i++) {
						start = start + spine_a;
						end = end + femur_a;
						yChunk = i * sizeY;
						safeStart = yChunk + ((start > 0)? start : 0);
						safeEnd = yChunk + ((end < sizeY)? end : sizeY);
						for (int pointer = safeStart; pointer < safeEnd; pointer++) {
							CanvasData[pointer] = color;
						}
					}

					start = spine_a * i + spine_b;
					end = ribcage_a * i + ribcage_b;
					for (i = i; i < ((tri2D[d][indTop][0] < sizeX)? tri2D[d][indTop][0] : sizeX); i++) {
						start = start + spine_a;
						end = end + ribcage_a;
						yChunk = i * sizeY;
						safeStart = yChunk + ((start > 0)? start : 0);
						safeEnd = yChunk + ((end < sizeY)? end : sizeY);
						for (int pointer = safeStart; pointer < safeEnd; pointer++) {
							CanvasData[pointer] = color;
						}
					}
				}
			}
		}
	}
	return Py_BuildValue("i", 0);
}


static PyObject* version(PyObject* self) {
	return Py_BuildValue("s", "V1.3");
}


static PyMethodDef methDef[] = {
	{"version", (PyCFunction)version, METH_NOARGS, "Returns version"},
	{"draw3DTriangles", draw3DTriangles, METH_VARARGS, "(int Verticle Size of Array, Array, 3 Tuples of the 3 points of the triangle, int color) Draws a list of triangles"},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef modlDef = {
	PyModuleDef_HEAD_INIT,
	"renderer",
	"Custom-made C 3D renderer, split from the older version I made to include a depth buffer (which changed how the lib clip triangles a bit)",
	-1,
	methDef
};

PyMODINIT_FUNC PyInit_renderer(){
	PyObject* Mod = PyModule_Create(&modlDef);
	import_array();
	return Mod;
}
