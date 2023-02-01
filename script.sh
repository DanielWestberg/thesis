#!/bin/bash

CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
mkdir "output/$CURRENT_TIME"

# gnome-terminal --tab -- bash -c "perf record -F 99 -a -g -- sleep 60; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidof thesis_app | xargs -I {} strace -p {}; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidof thesis_app | trace-cmd record -F 99 -p xargs -g -- sleep 30; /usr/bin/bash"

# gnome-terminal --tab -- bash -c "pidof thesis_app | xargs -I {} perf stat -p {} -g -- sleep 30 > perfstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidof thesis_app | xargs -I {} perf record --call-graph fp -p {} -g --running-time -- sleep 30; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "vmstat -t -w 1 >  output/'$CURRENT_TIME'/vmstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "mpstat -P ALL 1 > output/'$CURRENT_TIME'/mpstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "pidstat 1 > pidstat.txt; /usr/bin/bash"
# gnome-terminal --tab -- bash -c "iostat -xz 1 > iostat.txt; /usr/bin/bash"

perf record -F 99 -a -g &
PERFPID=$!
vmstat -t -w 1 > output/$CURRENT_TIME/vmstat.txt &
VMSTATPID=$!
mpstat -P ALL 1 > output/$CURRENT_TIME/mpstat.txt &
MPSTATPID=$!
pidstat 1 > output/$CURRENT_TIME/pidstat.txt &
PIDSTATPID=$!
iostat -xz 1 > output/$CURRENT_TIME/iostat.txt &
IOSTATPID=$!

sudo perf stat -o output/$CURRENT_TIME/perfstat.txt -- make run > output/$CURRENT_TIME/app_output.txt 

# wait $!
# while pidof thesis_app != null; do echo "Waiting for app to finish..."; done

kill $PERFPID $VMSTATPID $MPSTATPID $PIDSTATPID $IOSTATPID

# dd if=/dev/zero of=/dev/null
# trace-cmd start -p wakeup_rt
# cat /sys/kernel/tracing/osnoise
# sar -n DEV 1
# sar -n TCP, ETCP 1
# free -m
# objdump -d thesis_app
# profile-bpfcc -F 99 -adf 60
# bpftrace bpfcode.bpf
