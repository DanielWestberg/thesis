#!/usr/bin/bash

APPNAME="thesis_app"

ITERATIONS=1

ALLCPUS=1
# MEMAPPITER=2
# DISKAPPITER=3
# CPUAPPITER=4

NOOBSERVEITER=0

MEMSTRESSITER=2
DISKSTRESSITER=3
CPUSTRESSITER=4
IOSTRESSITER=5

STRESSISOLCPU=2
APPISOLCPU=2

# Get number of CPUs
NCPUS=$(lscpu | grep --max-count=1 "CPU(s)" | awk '{print $2}')

# Store current time as a variable and create a new dir
OUTPUT_DIR="output"
CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
mkdir "$OUTPUT_DIR/$CURRENT_TIME"

for (( i=1; i<=$ITERATIONS; i++ ))
do
    echo "Run $i"
    mkdir "$OUTPUT_DIR/$CURRENT_TIME/$i"

    # Add noise to system
    if [[ $(expr $i % $ITERATIONS) = "$MEMSTRESSITER" ]]
    then
        echo "Starting memory stress..."
        stress -m 1 &
    fi
    
    if [[ $(expr $i % $ITERATIONS) = "$DISKSTRESSITER" ]]
    then
        echo "Starting disk stress..."
        stress -d 1 &
    fi

    if [[ $(expr $i % $ITERATIONS) = "$CPUSTRESSITER" ]]
    then
        echo "Starting cpu stress..."
        stress -c 1 &
    fi

    if [[ $(expr $i % $ITERATIONS) = "$IOSTRESSITER" ]]
    then
        echo "Starting I/O stress..."
        stress -i 1 &
    fi

    # Isolate CPU's
    # if [[ $ALLCPUS = 1 ]]
    # then
    #     echo -n "Using all CPU's 0-3..."
    #     sudo ./cgroup -0123 all &
    #     echo "done"
    # else
    #     echo -n "Isolating all processes to CPU's 0-2..."
    #     sudo ./cgroup -012 all &
    #     echo "done"
        
    #     echo -n "Isolating stress processes to CPU $STRESSISOLCPU..."
    #     for pid in $(ps ax | grep stress | awk '{print $1}'); do taskset -pc $STRESSISOLCPU $pid ; done
    #     echo "done"
    # fi


    if [[ $i != $NOOBSERVEITER ]]
    then
        # Start observability tools, store output in new dir
        echo -n "Starting observability tools..."
        # vmstat -t -w 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt &
        # VMSTATPID=$!
        # mpstat -P 0 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat0_raw.txt &
        # MPSTAT0PID=$!
        # mpstat -P 1 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat1_raw.txt &
        # MPSTAT1PID=$!
        # mpstat -P 2 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat2_raw.txt &
        # MPSTAT2PID=$!
        # mpstat -P 3 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat3_raw.txt &
        # MPSTAT3PID=$!
        # pidstat 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt &
        # PIDSTATPID=$!
        # iostat -txd -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_raw.txt &
        # IOSTATPID=$!
        # iostat -td -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_raw.txt &
        # IOSTATDPID=$!
        # sar -m ALL 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/sar_m_raw.txt &
        # SARMPID=$!
        # sar -n ALL 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/sar_n_raw.txt &
        # SARNPID=$!

        # if [[ $ALLCPUS = 1 ]]
        # then
            # perf stat record -d -d -d -v -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.data &
            # PERFSTATPID=$!
            # perf record -a -g -s -T -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            # PERFPID=$!
        # else
            # perf stat record -d -d -d -v -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.data &
            # PERFSTATPID=$!
            # perf record -a -g -s -T -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            # perf record -g -s -T -C $APPISOLCPU -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            # PERFPID=$!
        # fi
        perf sched record -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data &
        PERFSCHEDPID=$!
        
        echo "done"
    else
        echo "No observability tools"
    fi


    # Run application
    # if [[ $(expr $i % $MEMAPPITER) = "1" ]]
    # then
    #     echo -n "Running memory application on CPU $APPISOLCPU..."
    #     sudo taskset -c $APPISOLCPU make run_mem_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
    # elif [[ $(expr $i % $DISKAPPITER) = "2" ]]
    # then
    #     echo -n "Running disk application on CPU $APPISOLCPU..."
    #     sudo taskset -c $APPISOLCPU make run_disk_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
    # else
    #     echo -n "Running cpu application on CPU $APPISOLCPU..."
    #     sudo taskset -c $APPISOLCPU make run_cpu_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
    # fi

    if [[ $ALLCPUS = 1 ]]
    then
        echo -n "Running application on all CPU's..."
        # sudo make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
        # sudo perf sched record -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        sudo perf stat -a --per-core -ddd -A -B -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
    else
        echo -n "Running application on CPU $APPISOLCPU..."
        # sudo perf record -g -s -T -C $APPISOLCPU -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        # sudo perf sched record -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data taskset -c $APPISOLCPU make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        sudo perf stat -o $OUTPUT_DIR/$CURRENT_TIME/$i/perfstat.txt make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
        # sudo taskset -c $APPISOLCPU make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        # sudo taskset -c $APPISOLCPU make -C ../confd-basic/confd-basic-8.0.2.linux.x86_64/northbound-perf/ clean all start > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
    fi
# --bpf-counters
    echo "done"

    # Stop observability tools
    if [[ $i != $NOOBSERVEITER ]]
    then
        echo -n "Stopping observability tools..."
        kill $PERFPID $PERFSCHEDPID $VMSTATPID $MPSTAT0PID $MPSTAT1PID $MPSTAT2PID $MPSTAT3PID $PIDSTATPID $IOSTATPID $DSTATPID $SARMPID $SARNPID $IOSTATDPID
        # kill $PERFPID $PERFSTATPID $VMSTATPID $MPSTAT0PID $MPSTAT1PID $MPSTAT2PID $MPSTAT3PID $PIDSTATPID $IOSTATPID $DSTATPID $SARMPID $SARNPID $IOSTATDPID
        echo "done"
    fi

    echo "Stopping stress..."
    for pid in $(pidof stress); do kill $pid ; done
    echo "done"

    # Generate gprof data
    # echo -n "Generating gprof data..."
    # make gprof > $OUTPUT_DIR/$CURRENT_TIME/$i/gprof.txt
    # gprof thesis_app | gprof2dot | dot -Tpdf -o $OUTPUT_DIR/$CURRENT_TIME/$i/gprof2dot.pdf
    # cp $OUTPUT_DIR/$CURRENT_TIME/$i/gprof2dot.pdf ./
    # echo "done"

    sleep 1
    # Generate flamegraph
    if [[ $i != $NOOBSERVEITER ]]
    then
        echo -n "Generating flame graph..."
        cd $OUTPUT_DIR/$CURRENT_TIME/$i/
        sudo perf script -i perf.data | ../../../../FlameGraph/stackcollapse-perf.pl > ../../../../FlameGraph/out.perf-folded
        cd ../../../
        ../FlameGraph/flamegraph.pl ../FlameGraph/out.perf-folded > ../FlameGraph/perf.svg
        cp ../FlameGraph/perf.svg $OUTPUT_DIR/$CURRENT_TIME/$i/
        echo "done"
    fi

    echo -n "Generating scheduling time history..."
    sudo perf sched timehist -MVwn -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw.txt
    sudo perf sched timehist -s -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt

    for (( CPU=0; CPU<$NCPUS; CPU++ ))
    do
        sudo perf sched timehist -MVwn --cpu=$CPU -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_cpu$CPU.txt
        sudo perf sched timehist -s --cpu=$CPU -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt
        sudo perf sched timehist -MVwnI --cpu=$CPU -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_idle_cpu$CPU.txt

        tail -n +6 $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | egrep -v "Terminated tasks|Idle stats|idle for|Total number|Total run|Total scheduling" | awk '{$1=$1;print}' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.csv
    done
    
    sudo perf sched timehist -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | grep "thesis_app" > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_thesis_app.txt
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_thesis_app.txt | awk '!seen[$2]++' | awk '{print $2}' | awk 'BEGIN { ORS = " " } { print }' > $OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
    echo "done"

    cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "seconds time elapsed" | awk '{print $1}' > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_time.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | egrep -v "started on|Performance counter|time elapsed" | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.csv

    # # Format output data to csv
    # echo -n "Formatting output to csv..."
    
    # # Format vmstat
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt | sed 's/\s\+/,/g' | egrep -v "procs|buff" > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    # sed -i -e "s/^/$i/" $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    
    # # Format mpstat
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat0_raw.txt | sed 's/\s\+/,/g' | grep . | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat0.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat0.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat1_raw.txt | sed 's/\s\+/,/g' | grep . | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat1.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat1.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat2_raw.txt | sed 's/\s\+/,/g' | grep . | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat2.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat2.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat3_raw.txt | sed 's/\s\+/,/g' | grep . | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat3.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat3.csv
    
    # # Format pidstat
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep $APPNAME | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # # if [[ $i = $MEMAPPITER ]]
    # # then
    # #     sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep "mem_app" | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # #     sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # # elif [[ $i = $DISKAPPITER ]]
    # # then
    # #     sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep "disk_app" | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # #     sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # # else
    # #     sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep "cpu_app" | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # #     sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # # fi
    
    # # Format iostat -xd
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_raw.txt | grep . | egrep -v "Linux|Device" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv
    # grep ':' < $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv | xargs -I {} echo -e "{}\n{}\n{}" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_time.csv
    # sed -i '/:/d' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv
    # paste $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv
    # sed -i 's/\s\+/,/g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv
    # rm $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_temp.csv

    # # Format iostat -d
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_raw.txt | grep . | egrep -v "Linux|Device" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv
    # grep ':' < $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv | xargs -I {} echo -e "{}\n{}\n{}" > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_time.csv
    # sed -i '/:/d' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv
    # paste $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv
    # sed -i 's/\s\+/,/g' $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv
    # rm $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_time.csv $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_temp.csv

    # sadf  $OUTPUT_DIR/$CURRENT_TIME/$i/sar_m_raw.txt

    if [[ $APPNAME = "thesis_app" ]]
    then
        # Format app output
        egrep -v "./|gcc" < $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt > $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
        # App time all CPUs
        cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep $APPNAME | awk -v N=4 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        # Total time all CPUs
        cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "Total run time" | awk -v N=5 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        # App time per CPU
        if [[ $ALLCPUS = 1 ]]
        then
            for (( CPU=0; CPU<$NCPUS; CPU++ ))
            do
                cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep $APPNAME | awk -v N=4 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
            done
        else
            for (( CPU=0; CPU<$NCPUS; CPU++ ))
            do
                if [[ $APPISOLCPU = $CPU ]]
                then
                    cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep $APPNAME | awk -v N=4 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
                else
                    echo 0 | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
                fi
            done
        fi
        # Total time per CPU
        for (( CPU=0; CPU<$NCPUS; CPU++ ))
        do
            cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep -w "Total run time" | awk -v N=5 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        done
        # Idle time per CPU
        cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "idle for" | awk -v N=5 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "idle for" | awk -v N=8 '{print $N}' | rev | cut -c3- | rev | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        # Append to file containing all iterations
        sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv >> $OUTPUT_DIR/$CURRENT_TIME/runtimes.csv
        sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv >> $OUTPUT_DIR/$CURRENT_TIME/cpus_used.csv
    fi

    # Append to file containing all iterations
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/vmstat.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat0.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat0.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat1.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat1.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat2.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat2.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat3.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat3.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/pidstat.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv >> $OUTPUT_DIR/$CURRENT_TIME/iostat_xd.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv >> $OUTPUT_DIR/$CURRENT_TIME/iostat_d.csv
    echo "done"
    echo ""

done

echo -n "Resetting CPU isolations..."
# sudo ./cgroup -r &
echo "done"

python3 ./benchmark.py $CURRENT_TIME $NCPUS





# NOT USED STUFF

# ps ax | grep stress | awk '{print $1}' | xargs -I {} cgroup -q {}
# for i in $(ps ax | grep stress | awk '{print $1}'); do taskset -cp 3 $i ; done

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