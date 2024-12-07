#!/bin/bash -eu

set -o pipefail
{

module reset
module load lang
module load Python

# -----------------

flock -n _uncompress.lock ./_uncompress.py || echo Already running

exit 0
}
