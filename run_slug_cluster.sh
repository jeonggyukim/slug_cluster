#!/usr/bin/env bash
#
# Simple script to run the slug problem: cluster_logMXX
# See section 11 of the SLUG manual. 
#

export SLUG_DIR="/data/slug2"

min=20
max=30
step=2
nproc=5 # number of threads
curdir=$(pwd)

cd $SLUG_DIR

for i in $(seq $min $step $max)
do
    ii=$(printf "%02d" $i)
    param="${curdir}/cluster_logM${ii}.param"

    echo $param
    ## run simulation
    python $SLUG_DIR/bin/slug.py -nt -n $nproc $param
done
