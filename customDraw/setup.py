from distutils.core import setup, Extension

modl = Extension("customDraw", sources=["customDraw.c"])

setup(name="PackageName",
      version="1",
      description="Draws Stuffs",
      ext_modules=[modl]
      )
