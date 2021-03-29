#from distutils.core import setup
#from distutils.extension import Extension
from setuptools import setup
from setuptools import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy

#ext = Extension('glesLFR', sources=["glesLFRPyth.pyx","src\glesLFR.cpp","src\LFGenerator.cpp","src\stb_image.cpp","src\glad.c"], language="c++",)

#setup(name="glesLFR", ext_modules = cythonize([ext]),cmdclass = {'build_ext': build_ext})
ext_modules = [Extension("pyaos", 
              sources=["pyaos.pyx","../src/AOS.cpp","../src/glad.c","../src/image.cpp","../src/utils.cpp","../src/gl_utils.cpp"],
              libraries=["glfw3","assimp-vc141-mt","opengl32","kernel32","user32","shell32","gdi32","vcruntime","msvcrt","python37"],
              include_dirs=[numpy.get_include(),"../include"],
              library_dirs=["../lib"],
              language="c++",
              extra_compile_args=["-ggdb", "-lpthread","/INCLUDE:../include/","/link","/LIBPATH:../lib/", "-llibassimp.so","-Wall"]
              )
]


# Building
setup(
    name = "pyaos",
    ext_modules = ext_modules,
    #ext_modules = cythonize([ext_modules]),
    cmdclass = {'build_ext': build_ext},
    #include_dirs=[numpy.get_include(),"../include"]
    
)          

