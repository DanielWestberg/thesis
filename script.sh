#!/usr/bin/bash

APPNAME="thesis_app"

ITERATIONS=1

ALLCPUS=0
# MEMAPPITER=2
# DISKAPPITER=3
# CPUAPPITER=4

NOOBSERVEITER=0

MEMSTRESSITER=2
DISKSTRESSITER=3
CPUSTRESSITER=4
IOSTRESSITER=5

STRESSISOLCPU=2
APPISOLCPU=1

if ! test -f "./hardinfo.txt"; then
    echo "Benchmarking using hardinfo, please do not click or move the mouse"
    hardinfo -r > ./hardinfo.txt
    echo "done"
fi
if ! test -f "./perf_bench_all.txt"; then
    echo "Benchmarking using perf bench all, please do not click or move the mouse"
    # sudo perf bench mem all > ./perf_bench_mem_all.txt
    echo "done"
fi
if ! test -f "./cache_disk_speed.txt"; then
    echo "Benchmarking cache and disk speed, please do not click or move the mouse"
    # Get cache and disk read speed
    for (( i=1; i<=3; i++ ))
    do
        sudo hdparm -Tt /dev/$DISKNAME >> ./cache_disk_speed.txt
    done
    echo "done"
fi

make thesis_app

# Get number of CPUs
NCPUS=$(lscpu | grep --max-count=1 "CPU(s)" | awk '{print $2}')

# Get disk name
DISKNAME=$(lsblk | grep disk | awk '{print $1}')

# Store current time as a variable and create a new dir
OUTPUT_DIR="output"
CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
mkdir "$OUTPUT_DIR/$CURRENT_TIME"

# Get standard CPU freq for each CPU
CPU_FREQS=$(cat /proc/cpuinfo | grep "model name" | awk '{print $9}')

cpu0_freq=$(echo $CPU_FREQS | awk '{print $1}')

# Set static CPU freq
sudo cpupower frequency-set -d $cpu0_freq
sudo cpupower frequency-set -u $cpu0_freq

# for freq in $CPU_FREQS; do freqs+=$freq ; done
# echo ${freqs[0]}
# for freq in $freqs; do echo $freq ; done

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
        vmstat -t -w 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt &
        VMSTATPID=$!
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
        pidstat 1 -r > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt &
        PIDSTATMEMPID=$!
        # iostat -txd -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_raw.txt &
        # IOSTATPID=$!
        # iostat -td -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_raw.txt &
        # IOSTATDPID=$!
        # sar -m ALL 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/sar_m_raw.txt &
        # SARMPID=$!
        # sar -n ALL 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/sar_n_raw.txt &
        # SARNPID=$!

        if [[ $ALLCPUS = 1 ]]
        then
            perf record -a -g -s -T -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            PERFPID=$!
        else
            perf record -g -s -T -C $APPISOLCPU -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            PERFPID=$!
        fi
        # perf stat record -d -d -d -v -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.data &
        # PERFSTATPID=$!
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

    cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $4}' > $OUTPUT_DIR/$CURRENT_TIME/$i/cpu_freq.csv

    if [[ $ALLCPUS = 1 ]]
    then
        echo -n "Running application on all CPU's..."
        # sudo make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
        # sudo perf sched record -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        sudo time perf stat -a --per-core -ddd -A -B -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt ./thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
    else
        echo -n "Running application on CPU $APPISOLCPU..."
        # sudo perf record -g -s -T -C $APPISOLCPU -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        # sudo perf sched record -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data taskset -c $APPISOLCPU make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        sudo perf stat \
            -e cycles,instructions,ref-cycles,cycle_activity.stalls_total,cycle_activity.stalls_mem_any,cycle_activity.cycles_mem_any,i915/actual-frequency/ -B -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt taskset -c $APPISOLCPU ./thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
        # sudo taskset -c $APPISOLCPU make run_thesis_app > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        # sudo taskset -c $APPISOLCPU make -C ../confd-basic/confd-basic-8.0.2.linux.x86_64/northbound-perf/ clean all start > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt 
    fi
# --bpf-counters
    echo "done"
    cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $4}' >> $OUTPUT_DIR/$CURRENT_TIME/$i/cpu_freq.csv

    # Stop observability tools
    if [[ $i != $NOOBSERVEITER ]]
    then
        echo -n "Stopping observability tools..."
        kill $PERFPID $PERFSTATPID $PERFSCHEDPID $VMSTATPID $MPSTAT0PID $MPSTAT1PID $MPSTAT2PID $MPSTAT3PID $PIDSTATPID $PIDSTATMEMPID $IOSTATPID $DSTATPID $SARMPID $SARNPID $IOSTATDPID
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

    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "seconds time elapsed" | awk '{print $1}' > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_time.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "seconds user" | awk '{print $1}' > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_time_user.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "seconds sys" | awk '{print $1}' > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_time_sys.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "cycles" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | egrep -v "ref-cycles|cycle_activity" | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_cycles.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "instructions" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_ic.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "ref-cycles" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_ref_cycles.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "mem-loads" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_mem_loads.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "mem-stores" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_mem_stores.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "cycle_activity.stalls_total" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_cycle_stalls_total.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "cycle_activity.stalls_mem_any" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_cycle_stalls_mem_any.csv
    
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "page-faults" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_page_faults.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "branches" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_branches.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "branch-misses" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_branch_misses.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "L1-dcache-loads" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_L1_dcache_loads.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "L1-dcache-load-misses" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_L1_dcache_load_misses.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "LLC-loads" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_LLC_loads.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "LLC-load-misses" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_LLC_load_misses.csv
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "L1-icache-load-misses" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_L1_icache_load_misses.csv


    # # Format output data to csv
    # echo -n "Formatting output to csv..."
    
    # # Format vmstat
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt | sed 's/\s\+/,/g' | egrep -v "procs|buff" > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    sed -i -e "s/^/$i/" $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    
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
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt | sed 's/\s\+/,/g' | grep $APPNAME | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    
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
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat0.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat0.csv
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat1.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat1.csv
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat2.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat2.csv
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/mpstat3.csv >> $OUTPUT_DIR/$CURRENT_TIME/mpstat3.csv
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/pidstat.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv >> $OUTPUT_DIR/$CURRENT_TIME/pidstat_mem.csv
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd.csv >> $OUTPUT_DIR/$CURRENT_TIME/iostat_xd.csv
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d.csv >> $OUTPUT_DIR/$CURRENT_TIME/iostat_d.csv
    echo "done"
    echo ""

done

echo -n "Resetting CPU isolations..."
# sudo ./cgroup -r &
echo "done"

echo -n "Resetting CPU frequencies..."
sudo cpupower frequency-set -d 0GHz
sudo cpupower frequency-set -u 4GHz
echo "done"


python3 ./benchmark.py $CURRENT_TIME $NCPUS
python3 ./plots.py $CURRENT_TIME $NCPUS
