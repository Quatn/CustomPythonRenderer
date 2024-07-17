from distutils.core import setup, Extension

modl = Extension("renderer", sources=["renderer.c"])

setup(name="renderer",
      version="1",
      description="Custom-made C 3D renderer, split from the older version I made to include a depth buffer (which changed how the lib clip triangles a bit)",
      ext_modules=[modl]
      )
