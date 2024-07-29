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

	printf("Function called\n");
	fflush(stdout);

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
	//printf("Testest %lf\n", DepthBufferData[0]);

	sizeX = PyArray_SIZE(Canvas) / sizeY;
	halfSizeX = sizeX / 2;
	halfSizeY = sizeY / 2;

	HFOV /= 2;
	tanHFOV = tan(HFOV);
	VFOV = atan2(halfSizeX, sizeX / tanHFOV);
	tanVFOV = tan(VFOV);

	printf("Done Init\n");
// 	printf("%f\n", HFOV);
// 	printf("%f\n", VFOV);
	fflush(stdout);

	int nIndsInNear = 0, nIndsInFar = 0;  //Number of indices that's further than the near plane and nearer than the far plane, mostly used as control vars
	int numOfTris = PyList_Size(thirdArg);  //Number of triangles to process
											//
	double tri[][3] = {{0., 0., 0.}, {0., 0., 0.}, {0., 0., 0.}};
	for (int triNum = 0; triNum < numOfTris; triNum++) {

		printf("Grand loop: %i\n", triNum);
		PyObject *tupleData = PyList_GetItem(thirdArg, triNum);
		PyObject *triMatArr[] = {PyTuple_GetItem(tupleData, 0),
			PyTuple_GetItem(tupleData, 1),
			PyTuple_GetItem(tupleData, 2)};

		int color = PyLong_AsLong(PyTuple_GetItem(tupleData, 3));

		//printf("Check3");
		//tri[0][0] = PyFloat_AsDouble(PyObject *);
		tri[0][0] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[0], 0));
		tri[0][1] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[0], 1));
		tri[0][2] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[0], 2));

		//printf("Check4");
		tri[1][0] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[1], 0));
		tri[1][1] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[1], 1));
		tri[1][2] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[1], 2));

		tri[2][0] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[2], 0));
		tri[2][1] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[2], 1));
		tri[2][2] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[2], 2));

		printf("Done get triangle data\n");
		fflush(stdout);

		//Clip the triangle againts the near plane
		//int nIndsInNear = 0;
		nIndsInNear = 0;
		for(int i = 0; i<3 ; i++) if (tri[i][2] > nearPlaneDistance) nIndsInNear++;

		//Where the 2 triangles from the result of clipping the current triangle go to, depend on nIndsInNear there might only be 1 result so the other index will be unused
		//Predefine just to be a bit safer
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
		//printf("nIndsInNear: %i\n", nIndsInNear);
		printf("Againts near plane case: %i\n", nIndsInNear);
		fflush(stdout);
		switch (nIndsInNear) {
			case 1: 
				{
					printf("c0-");
					fflush(stdout);

					int outSideInd[2], inSideInd = 0;

					printf("initial");
					endl;
					for(int i = 0; i<3 ; i++) {
						for(int ii = 0; ii<3 ; ii++) {
							printf("%lf ", tri[i][ii]);
						}
						endl;
					}


					printf("c1-");
					fflush(stdout);
					//Kinda dumb var optimize
					for(int i = 0; i<3 ; i++) if (tri[i][2] <= nearPlaneDistance) outSideInd[inSideInd++] = i;
					printf("The two outSideInd: %i %i", outSideInd[0], outSideInd[1]);
					inSideInd = 3 - outSideInd[0] - outSideInd[1];

					if (inSideInd + outSideInd[0] + outSideInd[1] != 3) {
						printf("\nASSUMED INDICES DOES NOT TOTAL TO 3\n");
						fflush(stdout);
					}

					printf("c2-");
					fflush(stdout);

					for(int i = 0; i<3 ; i++) triClippedNear[0][inSideInd][i] = tri[inSideInd][i];

					printf("c3-");
					fflush(stdout);
					for(int i = 0; i<2; i++) {
						double ratio = (nearPlaneDistance - tri[outSideInd[i]][2]) / (tri[inSideInd][2] - tri[outSideInd[i]][2]);
						printf("b0\nDataA: i: %i, outSideInd: %i, inSideInd: %i, ratio: %lf\n", i, outSideInd[i], inSideInd, ratio);
						fflush(stdout);

						triClippedNear[0][outSideInd[i]][0] = tri[outSideInd[i]][0] + ratio * (tri[inSideInd][0] - tri[outSideInd[i]][0]);
						triClippedNear[0][outSideInd[i]][1] = tri[outSideInd[i]][1] + ratio * (tri[inSideInd][1] - tri[outSideInd[i]][1]);
						triClippedNear[0][outSideInd[i]][2] = nearPlaneDistance;

						printf("paff");
						endl;
						for(int ii = 0; ii<3 ; ii++) printf("%lf ", triClippedNear[0][outSideInd[i]][ii]);


					}
					printf("c4\n");
					fflush(stdout);
				}
				break;

			case 2:
				{
					int outSideInd = 0, inSideInd[2];

					//Kinda dumb var optimize
					for(int i = 0; i<3 ; i++) if (tri[i][2] > nearPlaneDistance) inSideInd[outSideInd++] = i;
					outSideInd = 3 - inSideInd[0] - inSideInd[1];
					if (outSideInd + inSideInd[0] + inSideInd[1] != 3) {
						printf("\nASSUMED INDICES DOES NOT TOTAL TO 3\n");
					}

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
		
		/*
		 * Debug
		for(int nearTriNum = 0; nearTriNum < ((nIndsInNear == 2)? 2: 1); nearTriNum++) {
			for(int i = 0; i < 3; i++)
				for(int ii = 0; ii < 3; ii++)
					printf("nearTriNum %i: [%i %i] = %i\n", nearTriNum, i, ii, triClippedNear[nearTriNum][i][ii]);
		}
		*/
		printf("\nDone clipping triangle %i againts the Near plane\n", triNum);
		fflush(stdout);

		//Another predefine, just in case
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
// 			printf("\ncc2\n");
// 			fflush(stdout);
			//int nIndsInFar = 0;
			nIndsInFar = 0;
			for(int i = 0; i<3 ; i++) if (triClippedNear[nearTriNum][i][2] < farPlaneDistance) nIndsInFar++;
// 			printf("\ncc3\n");

			printf("nearTriNum: %i, againts far plane case: %i\n", nearTriNum, nIndsInFar);


			endl;
			printf("puff\n");
			for(int i = 0; i<3 ; i++) {
				for(int ii = 0; ii<3 ; ii++) {
					printf("%lf ", triClippedNear[nearTriNum][i][ii]);
				}
				endl;
			}
			// 			printf("c-3");
			switch (nIndsInFar) {
				case 1: 
					{
						printf("p-2\n");
						printf("c1-");
						endl;
						fflush(stdout);
						int outSideInd[2], inSideInd = 0;

						for(int i = 0; i<3 ; i++) if (triClippedNear[nearTriNum][i][2] >= farPlaneDistance) outSideInd[inSideInd++] = i;
						inSideInd = 3 - outSideInd[0] - outSideInd[1];


						if (inSideInd + outSideInd[0] + outSideInd[1] != 3 || inSideInd < 0 || inSideInd > 2) {
							printf("\nASSUMED INDICES DOES NOT TOTAL TO 3\n");
							//printf("%i, %i, %i\n", inSideInd, outSideInd[0], outSideInd[1]);
							fflush(stdout);
						}

						printf("c2-");
						fflush(stdout);
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][inSideInd][i] = triClippedNear[nearTriNum][inSideInd][i];

						printf("c3-");
						printf("\n");
						fflush(stdout);
						for(int i = 0; i<2; i++) {
							double ratio = (triClippedNear[nearTriNum][outSideInd[i]][2] - farPlaneDistance) / (triClippedNear[nearTriNum][outSideInd[i]][2] - triClippedNear[nearTriNum][inSideInd][2]);
							printf("b0\nDataB: nearTriNum: %i, i: %i, outSideInd: %i, inSideInd: %i, ratio: %lf\n", nearTriNum, i, outSideInd[i], inSideInd, ratio);
							fflush(stdout);

							triClippedAll[triFarCount][outSideInd[i]][0] = triClippedNear[nearTriNum][outSideInd[i]][0] + ratio * (triClippedNear[nearTriNum][inSideInd][0] - triClippedNear[nearTriNum][outSideInd[i]][0]);
							printf("%lf ", triClippedAll[triFarCount][outSideInd[i]][0]);
							fflush(stdout);

							triClippedAll[triFarCount][outSideInd[i]][1] = triClippedNear[nearTriNum][outSideInd[i]][1] + ratio * (triClippedNear[nearTriNum][inSideInd][1] - triClippedNear[nearTriNum][outSideInd[i]][1]);
							printf("%lf ", triClippedAll[triFarCount][outSideInd[i]][1]);
							fflush(stdout);

							triClippedAll[triFarCount][outSideInd[i]][2] = farPlaneDistance;
							printf("%lf", triClippedAll[triFarCount][outSideInd[i]][2]);
							fflush(stdout);

							endl;

						}

						printf("c4\n");
						fflush(stdout);
						//for(int ti = 0; ti < 3; ti++)
						//	for(int tii = 0; tii < 3; tii++)
						//		printf("fn %i: [%i %i] = %i\n", triFarCount, ti, tii, triClippedNear[triFarCount][ti][tii]);
						triFarCount++;
					}
					break;

				case 2:
					{
						int outSideInd = 0, inSideInd[2];

						//Kinda dumb var optimize
						for(int i = 0; i<3 ; i++) if (triClippedNear[nearTriNum][i][2] < farPlaneDistance) inSideInd[outSideInd++] = i;
						outSideInd = 3 - inSideInd[0] - inSideInd[1];

						if (outSideInd + inSideInd[0] + inSideInd[1] != 3) {
							printf("\nASSUMED INDICES DOES NOT TOTAL TO 3\n");
							fflush(stdout);
						}

						//printf("in1: %i, in2: %i, o: %i", inSideInd[0], inSideInd[1], outSideInd);

						double alpha[2][3];
						for(int i = 0; i<2; i++) {
							double ratio = (farPlaneDistance - triClippedNear[nearTriNum][inSideInd[i]][2]) / (triClippedNear[nearTriNum][outSideInd][2] - triClippedNear[nearTriNum][inSideInd[i]][2]);
							//printf("ratio: %lf\n", ratio);

							alpha[i][0] = triClippedNear[nearTriNum][inSideInd[i]][0] + ratio * (triClippedNear[nearTriNum][outSideInd][0] - triClippedNear[nearTriNum][inSideInd[i]][0]);
							//printf("test1: %i, test2: %i\n", triClippedNear[nearTriNum][outSideInd][0] /*- triClippedNear[nearTriNum][inSideInd[i]][0]*/, alpha[i][0]);
							alpha[i][1] = triClippedNear[nearTriNum][inSideInd[i]][1] + ratio * (triClippedNear[nearTriNum][outSideInd][1] - triClippedNear[nearTriNum][inSideInd[i]][1]);
							alpha[i][2] = farPlaneDistance;

							//for(int ii = 0; ii<3 ; ii++) printf("%lf, ", alpha[i][ii]);
						}

						//for(int ti = 0; ti < 2; ti++)
						//	for(int tii = 0; tii < 3; tii++)
						//		printf("alpha [%i %i]: %i\n", ti, tii, alpha[ti][tii]);

						//{i1, i2, alpha1}
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][0][i] = triClippedNear[nearTriNum][inSideInd[0]][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][1][i] = triClippedNear[nearTriNum][inSideInd[1]][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount][2][i] = alpha[0][i];

						//{alpha1, alpha2, i2}
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount + 1][0][i] = alpha[0][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount + 1][1][i] = alpha[1][i];
						for(int i = 0; i<3 ; i++) triClippedAll[triFarCount + 1][2][i] = triClippedNear[nearTriNum][inSideInd[1]][i];

						/*
						for(int ti = 0; ti < 3; ti++)
							for(int tii = 0; tii < 3; tii++)
								printf("fn1 %i: [%i %i] = %i\n", triFarCount, ti, tii, triFar[triFarCount][ti][tii]);

						for(int ti = 0; ti < 3; ti++)
							for(int tii = 0; tii < 3; tii++)
							printf("fn2 %i: [%i %i] = %i\n", triFarCount + 1, ti, tii, triFar[triFarCount + 1][ti][tii]);
						*/
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

		printf("\nDone clipping triangle %i againts the Far plane\n", triNum);
		fflush(stdout);

		//Transfer trianlge cords to screen pixel positions and Apply perspective
		int tri2D[triFarCount][3][3];
		for (int i = 0; i < triFarCount; i++)
			for (int ii = 0; ii < 3; ii++) {
				tri2D[i][ii][0] = triClippedAll[i][ii][0] / ( tanHFOV * (double)triClippedAll[i][ii][2] ) * halfSizeX + halfSizeX;
				tri2D[i][ii][1] = triClippedAll[i][ii][1] / ( tanVFOV * (double)triClippedAll[i][ii][2] ) * halfSizeY + halfSizeY;
				tri2D[i][ii][2] = triClippedAll[i][ii][2];
			}

		//2D draw
		//printf("Check Cut\n");

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

			//printf("Check6");
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
		printf("\n--End log for triangle %i--\n\n", triNum);
		fflush(stdout);
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
