#!/bin/bash -eu
#SBATCH -A pc2-mitarbeiter
#SBATCH -t 60
#SBATCH -p gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --gres=gpu:a100:4
#SBATCH -J "T08_b38c768nbt_gelu_b80"

set -o pipefail
{

module reset
module load lang
module load math
module load numpy
module load system/CUDA/12.1.0
module load numlib/cuDNN/8.9.4.25-CUDA-12.1.0
# SGD for cuda12 via pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
module load devel/CMake/3.24.3-GCCcore-12.2.0 # Fix gdwarf error

# -----------------

cd ../python

BASEDIR=$(realpath "../../T08_b38c768nbt_gelu_b80")

./selfplay/train.sh \
	"$BASEDIR" \
	b38c768nbt-test \
	b38c768nbt-fson-gelu-rvglr-bnh \
	80 \
	trainonly \
	-lr-scale-auto \
	-samples-per-epoch 5000000 \
	-sleep-seconds-per-epoch 3 \
	-sub-epochs 1 \
	-swa-period-samples 200000 \
	-multi-gpus 0,1,2,3 \
	-use-fp16 \
	-no-repeat-files \

exit 0
}
