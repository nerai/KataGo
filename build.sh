#!/bin/bash

cd cpp

module reset

module load devel/CMake/3.23.1-GCCcore-11.3.0

# fuer GNU assembler as
# NICHT neuere GCC version als 11 wegen CUDA.
module load tools/binutils/2.38-GCCcore-11.3.0

module load numlib
# Auf login nodes reicht numlib/cuDNN nicht aus, man muss das modul direkt angeben
ml cuDNN/8.4.1.50-CUDA-11.7.0

cmake . -DNO_GIT_REVISION=1 -DBUILD_DISTRIBUTED=0 -DUSE_BACKEND=CUDA -DCMAKE_CXX_FLAGS='-march=native'
# Fehler zu libzip: Kann vermutlich ignoriert werden.
make

./katago version
