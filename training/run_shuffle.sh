#!/bin/bash -eux
#SBATCH -t 300:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=128
#SBATCH -J "LargeNet Shuffle"
#SBATCH -p normal
#SBATCH -A pc2-mitarbeiter
#SBATCH --mail-user slurm@kikashi.net

# Do not call this script in parallel!
set -o pipefail
{


module reset

# For the python scripts
module load math
module load numpy

# -----------------

cd ../python

OUTDIR=$(date "+%Y%m%d-%H%M%S")
RUNDIR=$(realpath "../../Shuffled")
UNCOMPRESSEDDIR=$(realpath "../../TrainingData/uncompressed/")
SHUFFLEDBASEDIR="$RUNDIR"/shuffleddata

mkdir -p "$RUNDIR"

python3 ./summarize_old_selfplay_files.py "$UNCOMPRESSEDDIR" \
        -num-parallel-processes 128 \
        -old-summary-file-to-assume-correct $RUNDIR/summary.json \
        -new-summary-file $RUNDIR/summary.json.tmp
mv -f $RUNDIR/summary.json.tmp $RUNDIR/summary.json

mkdir -p "$SHUFFLEDBASEDIR"/"$OUTDIR"

python shuffle.py "$UNCOMPRESSEDDIR" \
       -expand-window-per-row 0.0 \
       -taper-window-exponent 1.0 \
       -keep-target-rows 400000000 \
       -min-rows 3200000000 \
       -out-dir "$SHUFFLEDBASEDIR"/"$OUTDIR"/train \
       -out-tmp-dir "$RUNDIR"/shuffle_tmp/ \
       -approx-rows-per-out-file 1000000 \
       -num-processes 16 \
       -batch-size 1024 \
       -only-include-md5-path-prop-lbound 0.00 \
       -only-include-md5-path-prop-ubound 0.95 \
       -exclude-basename \
       -output-npz \
       -summary-file $RUNDIR/summary.json \
       -exclude ../../TrainingData/disabled_npzs.txt \
       -worker-group-size 1000000 \

# Just in case, give a little time for the filesystem
sleep 10
# rm if it already exists
rm -f "$SHUFFLEDBASEDIR"/current_tmp
ln -s $OUTDIR "$SHUFFLEDBASEDIR"/current_tmp
mv -Tf "$SHUFFLEDBASEDIR"/current_tmp "$SHUFFLEDBASEDIR"/current


exit 0
}
