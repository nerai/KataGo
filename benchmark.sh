#!/bin/bash

module reset
module load tools/binutils/2.38-GCCcore-11.3.0
module load numlib
module load cuDNN

cd cpp
#./katago benchmark -config ./evalclient.cfg
./katago benchmark -v 200000 -time 10 -t 100,200,400,800,1000

