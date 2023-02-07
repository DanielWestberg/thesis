#!/usr/bin/bash

# Store current time as a variable and create a new dir
OUTPUT_DIR="output"
CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
mkdir "$OUTPUT_DIR/$CURRENT_TIME"

for (( i=1; i<=$1; i++ ))
do 
    echo "Run $i"
    mkdir "$OUTPUT_DIR/$CURRENT_TIME/$i"

    # Start observability tools, store output in new dir
    echo -n "Starting observability tools..."
    vmstat -t -w 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt &
    VMSTATPID=$!
    mpstat -P ALL 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat_raw.txt &
    MPSTATPID=$!
    pidstat 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt &
    PIDSTATPID=$!
    iostat -txd -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_raw.txt &
    IOSTATPID=$!
    iostat -td -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_raw.txt &
    IOSTATDPID=$!
    sar -m ALL 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/sar_m_raw.txt &
    SARMPID=$!
    sar -n ALL 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/sar_n_raw.txt &
    SARNPID=$!
    perf record -F 99 -a -g &
    PERFPID=$!
    echo "done"

    # Run application
    echo -n "Running application..."
    sudo perf stat -o $OUTPUT_DIR/$CURRENT_TIME/$i/perfstat.txt make run > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
    echo "done"

    # Stop observability tools
    echo -n "Stopping observability tools..."
    kill $PERFPID $VMSTATPID $MPSTATPID $PIDSTATPID $IOSTATPID $DSTATPID $SARMPID $SARNPID $IOSTATDPID
    echo "done"

    # Generate gprof data
    echo -n "Generating gprof data..."
    make gprof > $OUTPUT_DIR/$CURRENT_TIME/$i/gprof.txt
    gprof thesis_app | gprof2dot | dot -Tpdf -o $OUTPUT_DIR/$CURRENT_TIME/$i/gprof2dot.pdf
    cp $OUTPUT_DIR/$CURRENT_TIME/$i/gprof2dot.pdf ./
    echo "done"

    sleep 1
    # Generate flamegraph
    echo -n "Generating flame graph..."
    sudo perf script | ../FlameGraph/stackcollapse-perf.pl > ../FlameGraph/out.perf-folded
    ../FlameGraph/flamegraph.pl ../FlameGraph/out.perf-folded > ../FlameGraph/perf.svg
    cp ../FlameGraph/perf.svg $OUTPUT_DIR/$CURRENT_TIME/$i/
    cp ../FlameGraph/perf.svg ./
    echo "done"

    # Format output data to csv
    echo -n "Formatting output to csv..."
    
    # Format vmstat
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt | sed 's/\s\+/,/g' | egrep -v "procs|buff" > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    
    # Format mpstat
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat_raw.txt | sed 's/\s\+/,/g' | grep . | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat.csv
    
    # Format pidstat
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep "thesis_app" | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    
    # Format iostat -xd
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_raw.txt | grep . | egrep -v "Linux|Device" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv
    grep ':' < $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv | xargs -I {} echo -e "{}\n{}\n{}" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_time.csv
    sed -i '/:/d' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv
    paste $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv
    sed -i 's/\s\+/,/g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv
    rm $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv

    # Format iostat -d
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_raw.txt | grep . | egrep -v "Linux|Device" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv
    grep ':' < $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv | xargs -I {} echo -e "{}\n{}\n{}" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_time.csv
    sed -i '/:/d' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv
    paste $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv
    sed -i 's/\s\+/,/g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv
    rm $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv
    
    # sadf  $OUTPUT_DIR/$CURRENT_TIME/$i/sar_m_raw.txt
    
    # Format thesis_app output
    egrep -v "./|gcc" < $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt > $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    
    # Append to file containing all iterations
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv >> $OUTPUT_DIR/$CURRENT_TIME/runtimes.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/vmstat.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/pidstat.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv >> $OUTPUT_DIR/$CURRENT_TIME/iostat_xd.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv >> $OUTPUT_DIR/$CURRENT_TIME/iostat_d.csv
    echo "done"

done












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