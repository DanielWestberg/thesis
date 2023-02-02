#!/bin/bash
sudo perf script | ../FlameGraph/stackcollapse-perf.pl > ../FlameGraph/out.perf-folded
../FlameGraph/flamegraph.pl ../FlameGraph/out.perf-folded > ../FlameGraph/perf.svg
# ../FlameGraph/flamegraph.pl --color=io --title="File I/O Time Flame Graph" --countname=us < out.stacks > out.svg
google-chrome ../FlameGraph/perf.svg &

xdg-open gprof2dot.pdf