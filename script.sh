#!/usr/bin/bash

# Store current time as a variable and create a new dir
CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
mkdir "output/$CURRENT_TIME"

# Start observability tools, store output in new dir
vmstat -t -w 1 > output/$CURRENT_TIME/vmstat.csv &
VMSTATPID=$!
mpstat -P ALL 1 > output/$CURRENT_TIME/mpstat.csv &
MPSTATPID=$!
pidstat 1 > output/$CURRENT_TIME/pidstat.csv &
PIDSTATPID=$!
iostat -t -xz 1 > output/$CURRENT_TIME/iostat_xz.txt &
IOSTATPID=$!
iostat -t -d 1 > output/$CURRENT_TIME/iostat_d.csv &
IOSTATDPID=$!
sar -m ALL 1 > output/$CURRENT_TIME/sar_m.txt &
SARMPID=$!
sar -n ALL 1 > output/$CURRENT_TIME/sar_n.txt &
SARNPID=$!
perf record -F 99 -a -g &
PERFPID=$!

# Run application
sudo perf stat -o output/$CURRENT_TIME/perfstat.txt make run > output/$CURRENT_TIME/app_output.txt 

# Stop observability tools
kill $PERFPID $VMSTATPID $MPSTATPID $PIDSTATPID $IOSTATPID $DSTATPID $SARMPID $SARNPID $IOSTATDPID

# Generate gprof data
make gprof > output/$CURRENT_TIME/gprof.txt
gprof thesis_app | gprof2dot | dot -Tpdf -o output/$CURRENT_TIME/gprof2dot.pdf
cp output/$CURRENT_TIME/gprof2dot.pdf ./

sleep 3
# Generate flamegraph
sudo perf script | ../FlameGraph/stackcollapse-perf.pl > ../FlameGraph/out.perf-folded
../FlameGraph/flamegraph.pl ../FlameGraph/out.perf-folded > ../FlameGraph/perf.svg
cp ../FlameGraph/perf.svg output/$CURRENT_TIME/
cp ../FlameGraph/perf.svg ./













# NOT USED STUFF

# gnome-terminal --tab -- bash -c "perf record -F 99 -a -g -- sleep 60; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidof thesis_app | xargs -I {} strace -p {}; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidof thesis_app | trace-cmd record -F 99 -p xargs -g -- sleep 30; /usr/bin/bash"

# gnome-terminal --tab -- bash -c "pidof thesis_app | xargs -I {} perf stat -p {} -g -- sleep 30 > perfstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidof thesis_app | xargs -I {} perf record --call-graph fp -p {} -g --running-time -- sleep 30; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "vmstat -t -w 1 >  output/'$CURRENT_TIME'/vmstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "mpstat -P ALL 1 > output/'$CURRENT_TIME'/mpstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidstat 1 > pidstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "iostat -xz 1 > iostat.txt; /usr/bin/bash"

# ../FlameGraph/flamegraph.pl --color=io --title="File I/O Time Flame Graph" --countname=us < out.stacks > out.svg

# dd if=/dev/zero of=/dev/null
# trace-cmd start -p wakeup_rt
# cat /sys/kernel/tracing/osnoise
# sar -n DEV 1
# sar -n TCP, ETCP 1
# free -m
# objdump -d thesis_app
# profile-bpfcc -F 99 -adf 60
# bpftrace bpfcode.bpf

# perf record -g -- /path/to/your/executable
# perf script | c++filt | gprof2dot.py -f perf | dot -Tpng -o output.png