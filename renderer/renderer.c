#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define PI 3.14159265358979323846
#define endl printf("\n")
#include <math.h>
#include <Python.h>
#include <python3.10/numpy/arrayobject.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define NUM_OF_COLOR_MODES 2
#define COLOR_MODE_DEFAULT 0
#define COLOR_MODE_DEPTH 1
#define COLOR_MODE_DEPTH_MULT 2

static int colorMode = COLOR_MODE_DEFAULT;

static PyObject* setColorMode(PyObject* self, PyObject* args) {
	int mode = 0;
	if (!PyArg_ParseTuple(args, "i", &mode)) return Py_BuildValue("i", -1);

	if (mode < NUM_OF_COLOR_MODES) {
		colorMode = mode;
		return Py_BuildValue("i", 0);
	}
	return Py_BuildValue("i", 1);
}

static int colorFunc(int color, int depth) {
	switch (colorMode) {
		case COLOR_MODE_DEFAULT:
			return color;
			break;
		case COLOR_MODE_DEPTH:
			color = ((int)(depth * COLOR_MODE_DEPTH_MULT)) & 0xff;
			color |= (color << 8) | (color << 16);
			color = 0x999999 - color;
			return (color > 0xffffff)? 0xffffff: color;
			break;
	}
	return 0;
}

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
	int numOfTris = PyList_Size(thirdArg);  // Number of triangles to process

	for (int tri_no = 0; tri_no < numOfTris; ++tri_no) {
		/* Logic for the vertex shader */
		double tri[][3] = {{0., 0., 0.}, {0., 0., 0.}, {0., 0., 0.}};  // The raw triangle data that was passed from the python application.

		// Get data from the tupple and put it in tri[]
		PyObject *tupleData = PyList_GetItem(thirdArg, tri_no);
		PyObject *triMatArr[] = {PyTuple_GetItem(tupleData, 0),
			PyTuple_GetItem(tupleData, 1),
			PyTuple_GetItem(tupleData, 2)};

		int color = PyLong_AsLong(PyTuple_GetItem(tupleData, 3));

		for (int i = 0; i < 3; ++i) {
			tri[i][0] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[i], 0));
			tri[i][1] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[i], 1));
			tri[i][2] = PyFloat_AsDouble(PyTuple_GetItem(triMatArr[i], 2));
		}

		int nIndsInNear = 0;  // Number of vertices that's in (further than) the Near plane (inside of the view frustrum, as far as the Near plane is concerned)
		// Get data from the tupple and put it in tri[]
		for(int i = 0; i<3 ; ++i) if (tri[i][2] > nearPlaneDistance) nIndsInNear++;

		// The resulting triangles from clipping the original triangle againts the Near plane (there can be at most 2 triangles).
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

		// Clip the original triangle based on nIndsInNear
		switch (nIndsInNear) {
			case 1: 
				{
					// The Indices of the 2 outside vertices and the index of the one vertex that's inside
					int outSideInd[2], inSideInd = 0;

					// Determine the 2 outside vertices' indices
					for(int i = 0; i<3 ; ++i) if (tri[i][2] <= nearPlaneDistance) outSideInd[inSideInd++] = i;
					// Determine the inside vertex's index
					inSideInd = 3 - outSideInd[0] - outSideInd[1];

					// Put the inside vertex in triClippedNear at the same index
					for(int i = 0; i<3 ; ++i) triClippedNear[0][inSideInd][i] = tri[inSideInd][i];

					// Put the 2 outside vertices in triClippedNear at the same index
					for(int i = 0; i<2; ++i) {
						// Trigonometry
						double ratio = (nearPlaneDistance - tri[outSideInd[i]][2]) / (tri[inSideInd][2] - tri[outSideInd[i]][2]);

						triClippedNear[0][outSideInd[i]][0] = tri[outSideInd[i]][0] + ratio * (tri[inSideInd][0] - tri[outSideInd[i]][0]);
						triClippedNear[0][outSideInd[i]][1] = tri[outSideInd[i]][1] + ratio * (tri[inSideInd][1] - tri[outSideInd[i]][1]);
						triClippedNear[0][outSideInd[i]][2] = nearPlaneDistance;
					}
				}
				break;

			case 2:
				{
					// The Indices of the 2 inside vertices and the index of the one vertex that's outside
					int outSideInd = 0, inSideInd[2];

					// Determine the 2 inside vertices' indices
					for(int i = 0; i<3 ; ++i) if (tri[i][2] > nearPlaneDistance) inSideInd[outSideInd++] = i;
					// Determine the outside vertex's index
					outSideInd = 3 - inSideInd[0] - inSideInd[1];

					// The 2 points of contact between the triangle's outline and the Near plane
					double alpha[2][3];
					for(int i = 0; i<2; ++i) {
						double ratio = (tri[inSideInd[i]][2] - nearPlaneDistance) / (tri[inSideInd[i]][2] - tri[outSideInd][2]);

						alpha[i][0] = tri[inSideInd[i]][0] + ratio * (tri[outSideInd][0] - tri[inSideInd[i]][0]);
						alpha[i][1] = tri[inSideInd[i]][1] + ratio * (tri[outSideInd][1] - tri[inSideInd[i]][1]);
						alpha[i][2] = nearPlaneDistance;
					}

					//{i1, i2, alpha1}
					for(int i = 0; i<3 ; ++i) triClippedNear[0][0][i] = tri[inSideInd[0]][i];
					for(int i = 0; i<3 ; ++i) triClippedNear[0][1][i] = tri[inSideInd[1]][i];
					for(int i = 0; i<3 ; ++i) triClippedNear[0][2][i] = alpha[0][i];

					//{alpha1, alpha2, i2}
					for(int i = 0; i<3 ; ++i) triClippedNear[1][0][i] = alpha[0][i];
					for(int i = 0; i<3 ; ++i) triClippedNear[1][1][i] = alpha[1][i];
					for(int i = 0; i<3 ; ++i) triClippedNear[1][2][i] = tri[inSideInd[1]][i];
				}
				break;

			case 3:
				// Does not clip anything
				for(int i = 0; i<3 ; ++i) 
					for(int ii = 0; ii<3 ; ++ii) 
						triClippedNear[0][i][ii] = tri[i][ii];
				break;

			default: continue;
		}

		// The resulting triangles from clipping the triangles that was already clipped againts the Near plane, againts the Far plane (there can be at most 4 triangles)
		// (Triangles that are completely inside of the view frustrum)
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
		int triFarCount = 0;  // Counting var for triClippedAll, is incremented everytime a triangle is put in triClippedAll

		for(int nearTriNum = 0; nearTriNum < ((nIndsInNear == 2)? 2: 1); nearTriNum++) {
			int nIndsInFar = 0;  // Number of vertices that's in (nearer than) the Far plane (inside of the view frustrum, as far as the Far plane is concerned)
			for(int i = 0; i<3 ; ++i) if (triClippedNear[nearTriNum][i][2] < farPlaneDistance) nIndsInFar++;

			// Clip the triangles based on nIndsInFar, uses roughly the same logic and math as clipping the with the Near plane
			switch (nIndsInFar) {
				case 1: 
					{
						int outSideInd[2], inSideInd = 0;

						for(int i = 0; i<3 ; ++i) if (triClippedNear[nearTriNum][i][2] >= farPlaneDistance) outSideInd[inSideInd++] = i;
						inSideInd = 3 - outSideInd[0] - outSideInd[1];

						for(int i = 0; i<3 ; ++i) triClippedAll[triFarCount][inSideInd][i] = triClippedNear[nearTriNum][inSideInd][i];

						for(int i = 0; i<2; ++i) {
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

						for(int i = 0; i<3 ; ++i) if (triClippedNear[nearTriNum][i][2] < farPlaneDistance) inSideInd[outSideInd++] = i;
						outSideInd = 3 - inSideInd[0] - inSideInd[1];

						double alpha[2][3];
						for(int i = 0; i<2; ++i) {
							double ratio = (farPlaneDistance - triClippedNear[nearTriNum][inSideInd[i]][2]) / (triClippedNear[nearTriNum][outSideInd][2] - triClippedNear[nearTriNum][inSideInd[i]][2]);

							alpha[i][0] = triClippedNear[nearTriNum][inSideInd[i]][0] + ratio * (triClippedNear[nearTriNum][outSideInd][0] - triClippedNear[nearTriNum][inSideInd[i]][0]);
							alpha[i][1] = triClippedNear[nearTriNum][inSideInd[i]][1] + ratio * (triClippedNear[nearTriNum][outSideInd][1] - triClippedNear[nearTriNum][inSideInd[i]][1]);
							alpha[i][2] = farPlaneDistance;
						}

						//{i1, i2, alpha1}
						for(int i = 0; i<3 ; ++i) triClippedAll[triFarCount][0][i] = triClippedNear[nearTriNum][inSideInd[0]][i];
						for(int i = 0; i<3 ; ++i) triClippedAll[triFarCount][1][i] = triClippedNear[nearTriNum][inSideInd[1]][i];
						for(int i = 0; i<3 ; ++i) triClippedAll[triFarCount][2][i] = alpha[0][i];

						//{alpha1, alpha2, i2}
						for(int i = 0; i<3 ; ++i) triClippedAll[triFarCount + 1][0][i] = alpha[0][i];
						for(int i = 0; i<3 ; ++i) triClippedAll[triFarCount + 1][1][i] = alpha[1][i];
						for(int i = 0; i<3 ; ++i) triClippedAll[triFarCount + 1][2][i] = triClippedNear[nearTriNum][inSideInd[1]][i];

						triFarCount += 2;
					}
					break;

				case 3:
					for(int i = 0; i<3 ; ++i) 
						for(int ii = 0; ii<3 ; ++ii) 
							triClippedAll[triFarCount][i][ii] = triClippedNear[nearTriNum][i][ii];
					triFarCount++;
					break;

				default: continue;
			}
		}
		if (triFarCount < 1) continue;

		// Transfer trianlge coords to screen pixel positions and Apply perspective

		// These two used to be one var, but when I changed from using int vertices to double vertices the old var became "too accurate"
		// So for example if a line goes very straight upward then it will not stop at wher it needed to stop because of the incrementive triangle drawing
		// tldr: triPerspective is the atual representation of the triangle that have been transform into the 2D plane, according to the perspective of the camera (it still carries the z value for computational purpose).
		// tri2D is the int value of where position on the pixel screenm used purely for draw, not computing because it is not accurate.
		double triPerspective[triFarCount][3][3];
		int tri2D[triFarCount][3][2];

		for (int i = 0; i < triFarCount; ++i)
			for (int ii = 0; ii < 3; ++ii) {
				triPerspective[i][ii][0] = triClippedAll[i][ii][0] / ( tanHFOV * triClippedAll[i][ii][2] ) * halfSizeX + halfSizeX;
				triPerspective[i][ii][1] = triClippedAll[i][ii][1] / ( tanVFOV * triClippedAll[i][ii][2] ) * halfSizeY + halfSizeY;
				triPerspective[i][ii][2] = triClippedAll[i][ii][2];
				tri2D[i][ii][0] = triPerspective[i][ii][0];
				tri2D[i][ii][1] = triPerspective[i][ii][1];
			}

		/* Logic for the fragment shader */
		for (int d = 0; d < triFarCount; ++d) {
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

			double spineVec_pers[] = {triPerspective[d][indTop][0] - triPerspective[d][indBot][0], triPerspective[d][indTop][1] - triPerspective[d][indBot][1], triPerspective[d][indTop][2] - triPerspective[d][indBot][2]};
			double spineVec[] = {tri2D[d][indTop][0] - tri2D[d][indBot][0], tri2D[d][indTop][1] - tri2D[d][indBot][1]};
			double spine_a = 0, spine_b = 0;
			if (spineVec[0] != 0) {
				spine_a = spineVec[1] / spineVec[0];
				spine_b = tri2D[d][indTop][1] - (spine_a * tri2D[d][indTop][0]);
			}

			// Currently unused
			// double ribcageVec_pers[] = {triPerspective[d][indTop][0] - triPerspective[d][indSide][0], triPerspective[d][indTop][1] - triPerspective[d][indSide][1], triPerspective[d][indTop][2] - triPerspective[d][indSide][2]};
			double ribcageVec[] = {tri2D[d][indTop][0] - tri2D[d][indSide][0], tri2D[d][indTop][1] - tri2D[d][indSide][1]};
			double ribcage_a = 0, ribcage_b = 0;
			if (ribcageVec[0] != 0) {
				ribcage_a = ribcageVec[1] / ribcageVec[0];
				ribcage_b = tri2D[d][indTop][1] - (ribcage_a * tri2D[d][indTop][0]);
			}

			double femurVec_pers[] = {triPerspective[d][indSide][0] - triPerspective[d][indBot][0], triPerspective[d][indSide][1] - triPerspective[d][indBot][1], triPerspective[d][indSide][2] - triPerspective[d][indBot][2]};
			double femurVec[] = {tri2D[d][indSide][0] - tri2D[d][indBot][0], tri2D[d][indSide][1] - tri2D[d][indBot][1]};
			double femur_a = 0, femur_b = 0;
			if (femurVec[0] != 0) {
				femur_a = femurVec[1] / femurVec[0];
				femur_b = tri2D[d][indBot][1] - (femur_a * tri2D[d][indBot][0]);
			}

			// double start, end, startZ, endZ, startZDelta, endZDelta, z, zDelta, depth;
			// int x_screen, safeStart, safeEnd, yChunk;
			// double y_inc = 1. / sizeY;
			if (spineVec[0] != 0) {
				// a(x − x0) + b(y − y0) + c(z − z0) = 0
				// a/c(x − x0) + b/c(y − y0) - z0 = -z
				// let ax0/c + by0/c + z0 = dz
				// dz - ax/c + by/c = z
				//Dupplicate since the normal vector has already been calculated by the python part but I will keep it like this for now since it makes this module more verstile
				//The direction, as well as the component of the normal is ignored here

				/*
				[i, femur_x, spine_x]
				[j, femur_y, spine_y]
				[k, femur_z, spine_z]

				normalVec = 
				[
					femur_y * spine_z - femur_z * spine_y,
					- femur_x * spine_z + femur_z * spine_x,
					femur_x * spine_y - femur_y * spine_x
				]
				*/
				double normalVec[] = {
					femurVec_pers[1] * spineVec_pers[2] - femurVec_pers[2] * spineVec_pers[1],
					femurVec_pers[2] * spineVec_pers[0] - femurVec_pers[0] * spineVec_pers[2],
					femurVec_pers[0] * spineVec_pers[1] - femurVec_pers[1] * spineVec_pers[0],
				};

				// normalVec[0] /= sizeX;
				// normalVec[1] /= sizeY;

				//(ax0 + by0)/c + z0
				double dz = (normalVec[0] * (triPerspective[d][indTop][0] - halfSizeX) + normalVec[1] * (triPerspective[d][indTop][1] - halfSizeY)) / normalVec[2] 
					+ triPerspective[d][indTop][2];

				double ac = normalVec[0] / normalVec[2];
				double bc = normalVec[1] / normalVec[2];

				if (tri2D[d][indSide][1] < spine_a * tri2D[d][indSide][0] + spine_b) {
					int x_screen = (tri2D[d][indBot][0] > 0)? tri2D[d][indBot][0]: 0;
					double start = femur_a * x_screen + femur_b;
					double end = spine_a * x_screen + spine_b;

					for (x_screen = x_screen; x_screen < ((tri2D[d][indSide][0] < sizeX)? tri2D[d][indSide][0] : sizeX); ++x_screen) {
						int yChunk = x_screen * sizeY;
						int y_screen = (start > 0)? start : 0;
						int safeStart = yChunk + y_screen;
						int safeEnd = yChunk + ((end < sizeY)? end : sizeY);

						// double x = (double)(x_screen - halfSizeX) / sizeX;
						// double y = (double)(y_screen - halfSizeY) / sizeY;

						int x = x_screen - halfSizeX;
						int y = y_screen - halfSizeY;
						double z = dz - ac * x - bc * y;
						for (int pointer = safeStart; pointer < safeEnd; ++pointer) {
							// ax/c + by/c - dz = z
							// z = dz - ac * x - bc * y; but since only y itterate
							z -= bc;

							// double depth = sqrt(x * x + y * y + z * z);

							if (z < DepthBufferData[pointer]) {
								CanvasData[pointer] = colorFunc(color, z);
								DepthBufferData[pointer] = z;
							}
							// y += y_inc;
							++y;
						}
						start = start + femur_a;
						end = end + spine_a;
					}

					start = ribcage_a * x_screen + ribcage_b;
					end = spine_a * x_screen + spine_b;
					for (x_screen = x_screen; x_screen < ((tri2D[d][indTop][0] < sizeX)? tri2D[d][indTop][0] : sizeX); ++x_screen) {
						int yChunk = x_screen * sizeY;
						int y_screen = (start > 0)? start : 0;
						int safeStart = yChunk + y_screen;
						int safeEnd = yChunk + ((end < sizeY)? end : sizeY);

						// double x = (double)(x_screen - halfSizeX) / sizeX;
						// double y = (double)(y_screen - halfSizeY) / sizeY;

						int x = x_screen - halfSizeX;
						int y = y_screen - halfSizeY;
						double z = dz - ac * x - bc * y;
						for (int pointer = safeStart; pointer < safeEnd; ++pointer) {
							// ax/c + by/c - dz = z
							z -= bc;

							// double depth = sqrt(x * x + y * y + z * z);

							if (z < DepthBufferData[pointer]) {
								CanvasData[pointer] = colorFunc(color, z);
								DepthBufferData[pointer] = z;
							}
							// y += y_inc;
							++y;
						}
						start = start + ribcage_a;
						end = end + spine_a;
					}
				}
				else {
					int x_screen = (tri2D[d][indBot][0] > 0)? tri2D[d][indBot][0]: 0;
					double start = spine_a * x_screen + spine_b;
					double end = femur_a * x_screen + femur_b;

					for (x_screen = x_screen; x_screen < ((tri2D[d][indSide][0] < sizeX)? tri2D[d][indSide][0] : sizeX); ++x_screen) {
						int yChunk = x_screen * sizeY;
						int y_screen = (start > 0)? start : 0;
						int safeStart = yChunk + y_screen;
						int safeEnd = yChunk + ((end < sizeY)? end : sizeY);

						// double x = (double)(x_screen - halfSizeX) / sizeX;
						// double y = (double)(y_screen - halfSizeY) / sizeY;

						int x = x_screen - halfSizeX;
						int y = y_screen - halfSizeY;
						double z = dz - ac * x - bc * y;
						for (int pointer = safeStart; pointer < safeEnd; ++pointer) {
							// ax/c + by/c - dz = z
							z -= bc;

							// double depth = sqrt(x * x + y * y + z * z);

							if (z < DepthBufferData[pointer]) {
								CanvasData[pointer] = colorFunc(color, z);
								DepthBufferData[pointer] = z;
							}
							// y += y_inc;
							++y;
						}
						start = start + spine_a;
						end = end + femur_a;
					}

					start = spine_a * x_screen + spine_b;
					end = ribcage_a * x_screen + ribcage_b;
					for (x_screen = x_screen; x_screen < ((tri2D[d][indTop][0] < sizeX)? tri2D[d][indTop][0] : sizeX); ++x_screen) {
						int yChunk = x_screen * sizeY;
						int y_screen = (start > 0)? start : 0;
						int safeStart = yChunk + y_screen;
						int safeEnd = yChunk + ((end < sizeY)? end : sizeY);

						// double x = (double)(x_screen - halfSizeX) / sizeX;
						// double y = (double)(y_screen - halfSizeY) / sizeY;

						int x = x_screen - halfSizeX;
						int y = y_screen - halfSizeY;
						double z = dz - ac * x - bc * y;
						for (int pointer = safeStart; pointer < safeEnd; ++pointer) {
							// ax/c + by/c - dz = z
							z -= bc;

							// double depth = sqrt(x * x + y * y + z * z);

							if (z < DepthBufferData[pointer]) {
								CanvasData[pointer] = colorFunc(color, z);
								DepthBufferData[pointer] = z;
							}
							// y += y_inc;
							++y;
						}
						start = start + spine_a;
						end = end + ribcage_a;
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
	{"setColorMode", setColorMode, METH_VARARGS, "Sets the color mode for the renderer"},
	{"draw3DTriangles", draw3DTriangles, METH_VARARGS, "(int - Size of the triangles array, np.array - Canvas array, List - List of Triangles (each have 3 tupples and an int containing the triangle's color), double - nearPlaneDistance, double - farPlaneDistance, double - Horizontal FOV) Draws a list of triangles"},
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
