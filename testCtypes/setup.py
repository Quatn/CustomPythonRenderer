from distutils.core import setup, Extension

modl = Extension("testModule", sources=["cEx.c"])

setup(name="PackageName",
    version="1",
    description="LbronJams",
      ext_modules=[modl]
      )
