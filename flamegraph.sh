#!/bin/bash
sudo perf script | ../FlameGraph/stackcollapse-perf.pl > ../FlameGraph/out.perf-folded
../FlameGraph/flamegraph.pl ../FlameGraph/out.perf-folded > ../FlameGraph/perf.svg 
google-chrome ../FlameGraph/perf.svg &