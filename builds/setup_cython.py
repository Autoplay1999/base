from setuptools import setup
from Cython.Build import cythonize
import os

# Professional Cython Build Configuration
# Ref: CC-OPT-NATIVE

setup(
    name="Build Utils",
    ext_modules=cythonize(
        "build_utils.py",
        compiler_directives={
            'language_level': "3",
            'always_allow_keywords': True,
        },
        quiet=True
    ),
)
