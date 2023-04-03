#!/usr/bin/bash

ITERATIONS=1
DISABLE_OBSERVE_ITER=0

# Get config
CONFIG=$(jq '.' config.json)
PROCESS_NAME=$(echo $CONFIG | jq .process_name | tr -d '"')
APP_PATH=$(echo $CONFIG | jq '.app_path' | tr -d '"')
PRE_RUN_COMMAND=$(echo $CONFIG | jq '.pre_run_command' | tr -d '"')
RUN_COMMAND=$(echo $CONFIG | jq '.run_command' | tr -d '"')
IS_EXECUTABLE=$(echo $CONFIG | jq '.is_executable' | tr -d '"')
NOISE_TYPE=$(echo $CONFIG | jq '.noise' | tr -d '"')
APP_ISOL_CPU=$(echo $CONFIG | jq '.cpu_isolation')
ALL_CPUS=$(echo $CONFIG | jq '.all_cpus' | tr -d '"')

$PRE_RUN_COMMAND
PROCESS_PID=""
EGREP_PROCESS_PID=""

# Get number of CPUs
N_CPUS=$(lscpu | grep --max-count=1 "CPU(s)" | awk '{print $2}')
LAST_CPU=$(($N_CPUS-1))

# Get CPU isolation preference
if [[ $ALL_CPUS == *"yes"* ]]
then
    ALL_CPUS=1
elif test -z "$APP_ISOL_CPU"
then
    APP_ISOL_CPU=$LAST_CPU
    ALL_CPUS=0
elif [[ $APP_ISOL_CPU > $LAST_CPU ]]
then
    echo "You have $N_CPUS CPUs. CPU $APP_ISOL_CPU does not exist. Please select a CPU within the range (0-$LAST_CPU)."
    echo "Exiting..."
    exit
else
    ALL_CPUS=0
fi

# Check for noise preference
case $(echo "$NOISE_TYPE" | tr '[:upper:]' '[:lower:]') in
    *"cpu"* | *"memory"* | *"disk"* | *"io"*)
        NOISE_BOOL=1
        ;;
    *)
        NOISE_BOOL=0
        ;;
esac

# Compile thesis app
if [ "$PROCESS_NAME" = "thesis_app" ]; then
    make thesis_app
fi

# Store current time as a variable and create a new dir
SCRIPT_DIR=$PWD
OUTPUT_DIR="output"
[ ! -d "$SCRIPT_DIR/$OUTPUT_DIR" ] && mkdir "$SCRIPT_DIR/$OUTPUT_DIR" 
CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
mkdir "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME"

# Get standard CPU freq
CPU_FREQS=$(cat /proc/cpuinfo | grep "model name" | awk '{print $9}')
CPU0_FREQ=$(echo $CPU_FREQS | awk '{print $1}')

# Set static CPU freq
sudo cpupower frequency-set -d $CPU0_FREQ > /dev/null 2>&1
sudo cpupower frequency-set -u $CPU0_FREQ > /dev/null 2>&1

for (( i=1; i<=$ITERATIONS; i++ ))
do
    echo "Run $i"
    mkdir "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i"

    if [ $NOISE_BOOL = 1 ]; then
        # Add noise to system
        CPU_FLAG=""
        MEM_FLAG=""
        DISK_FLAG=""
        IO_FLAG=""
        if [[ $NOISE_TYPE == *"cpu"* ]]
        then
            CPU_FLAG="-c 1"
        fi

        if [[ $NOISE_TYPE == *"memory"* ]]
        then
            MEM_FLAG="-m 1"
        fi
        
        if [[ $NOISE_TYPE == *"disk"* ]]
        then
            DISK_FLAG="-d 1"
        fi

        if [[ $NOISE_TYPE == *"io"* ]]
        then
            IO_FLAG="-i 1"
        fi
        echo "Starting $NOISE_TYPE stress..."
        stress $CPU_FLAG $MEM_FLAG $DISK_FLAG $IO_FLAG &
    fi

    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        # Start observability tools, store output in new dir
        echo -n "Starting observability tools..."
        vmstat -t -w 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt &
        VMSTAT_PID=$!
        pidstat 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt &
        PIDSTAT_PID=$!
        pidstat 1 -r > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt &
        PIDSTAT_MEM_PID=$!
        iostat -txd -p sda 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_raw.txt &
        IOSTAT_PID=$!
        iostat -td -p sda 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_raw.txt &
        IOSTATD_PID=$!

        if [[ $ALL_CPUS = 1 ]]
        then
            perf record -a -g -s -T -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            PERF_PID=$!
        else
            perf record -g -s -T -C $APP_ISOL_CPU -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            PERF_PID=$!
        fi

        perf sched record -g -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data &
        PERF_SCHED_PID=$!
        
        echo "done"
    else
        echo "No observability tools"
    fi

    # Get cpu freq before running application
    cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $4}' > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpu_freq.csv

    # Run application
    cd $APP_PATH

    if [[ $IS_EXECUTABLE == "yes" ]]
    then
        if [[ $ALL_CPUS = 1 ]]
        then
            echo -n "Running $RUN_COMMAND in $PWD on all CPU's. Retrieving stats for $PROCESS_NAME..."
            perf stat -a --per-core -e cycles,instructions,cycle_activity.stalls_total,cycle_activity.cycles_mem_any,hw_interrupts.received,cache-misses,cache-references,branch-misses,branch-instructions,mem-stores,mem-loads,page-faults \
                -A -B -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt $RUN_COMMAND > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        else
            echo -n "Running $RUN_COMMAND in $PWD on CPU $APP_ISOL_CPU. Retrieving stats for $PROCESS_NAME..."
            perf stat \
                -e cycles,instructions,cycle_activity.stalls_total,cycle_activity.cycles_mem_any,hw_interrupts.received,cache-misses,cache-references,branch-misses,branch-instructions,mem-stores,mem-loads,page-faults \
                -B -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt taskset -c $APP_ISOL_CPU $RUN_COMMAND > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        fi
    else
        PROCESS_PID=$(pidof $PROCESS_NAME)
        EGREP_PROCESS_PID="|$PROCESS_PID"
        echo "Isolating $PROCESS_NAME on CPU $APP_ISOL_CPU."
        taskset -acp $APP_ISOL_CPU $PROCESS_PID
        echo "done"
        sleep 1
        echo "Retrieving stats for $PROCESS_NAME..."
        perf stat \
            -e cycles,instructions,cycle_activity.stalls_total,cycle_activity.cycles_mem_any,hw_interrupts.received,cache-misses,cache-references,branch-misses,branch-instructions,mem-stores,mem-loads,page-faults \
            -B -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt --pid=$PROCESS_PID &
        PERF_STAT_PID=$!
        echo "Running $RUN_COMMAND..."
        $RUN_COMMAND
        kill -INT $PERF_STAT_PID
    fi
    echo "done"
    
    # Get cpu freq after running application
    cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $4}' >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpu_freq.csv

    # Stop observability tools
    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        echo -n "Stopping observability tools..."
        kill $PERF_PID $PERF_SCHED_PID $VMSTAT_PID $MPSTAT0PID $MPSTAT1PID $MPSTAT2PID $MPSTAT3PID $PIDSTAT_PID $PIDSTAT_MEM_PID $IOSTAT_PID $IOSTATD_PID
        echo "done"
    fi

    # Stop stress
    if [ $NOISE_BOOL = 1 ]; then
        echo "Stopping stress..."
        for pid in $(pidof stress); do kill $pid ; done
        echo "done"
    fi

    sleep 1
    # Generate flamegraph
    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        echo -n "Generating flame graph..."
        cd $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/
        sudo perf script -i perf.data | ../../../../FlameGraph/stackcollapse-perf.pl > ../../../../FlameGraph/out.perf-folded
        cd ../../../
        ../FlameGraph/flamegraph.pl ../FlameGraph/out.perf-folded > ../FlameGraph/perf.svg
        cp ../FlameGraph/perf.svg $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/
        echo "done"
    fi

    echo -n "Generating scheduling time history..."
    sudo perf sched timehist -MVwn -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw.txt > /dev/null 2>&1
    sudo perf sched timehist -s -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt > /dev/null 2>&1

    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        sudo perf sched timehist -MVwn --cpu=$CPU -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_cpu$CPU.txt > /dev/null 2>&1
        sudo perf sched timehist -s --cpu=$CPU -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt > /dev/null 2>&1
        sudo perf sched timehist -MVwnI --cpu=$CPU -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_idle_cpu$CPU.txt > /dev/null 2>&1

        tail -n +6 $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | egrep -v "Terminated tasks|Idle stats|idle for|Total number|Total run|Total scheduling" | awk '{$1=$1;print}' \
            | while read -a line; do if [[ "${#line[@]}" -ge 10 ]] ; then index="$(("${#line[@]}"-9))" ; else index=0 ; fi; echo "${line[@]:$index}" >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/temp_perf_sched_summary_cpu$CPU.txt ; done
        sleep 1
        sed 's/\s\+/,/g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/temp_perf_sched_summary_cpu$CPU.txt | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.csv
    done
    
    sudo perf sched timehist -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | egrep "$PROCESS_NAME$EGREP_PROCESS_PID" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_$PROCESS_NAME.txt
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_$PROCESS_NAME.txt | awk '!seen[$2]++' | awk '{print $2}' | awk 'BEGIN { ORS = " " } { print }' > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
    echo "done"

    # Format output data to csv
    echo -n "Formatting output to csv..."
    touch $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_time.csv
    touch $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_percent.csv
    
    # Format perf stat
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "seconds time elapsed" | awk '{print $1}' > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_time.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "seconds user" | awk '{print $1}' > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_time_user.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "seconds sys" | awk '{print $1}' > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_time_sys.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "cycles" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | egrep -v "ref-cycles|cycle_activity" | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_cycles.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "instructions" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | egrep -v "branch"  | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_ic.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "mem-loads" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_mem_loads.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "mem-stores" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_mem_stores.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "cycle_activity.stalls_total" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_cycle_stalls_total.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "hw_interrupts.received" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_hw_interrupts_received.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "cache-misses" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_cache_misses.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "branch-misses" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_branch_misses.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt | grep "page-faults" | awk '{$1=$1};1' | sed 's/\s\+/,/g' | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat_page_faults.csv

    # Format vmstat
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt | sed 's/\s\+/,/g' | egrep -v "procs|buff" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    sed -i -e "s/^/$i/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv    
    
    # Format pidstat
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep $PROCESS_NAME | egrep -v "Linux|%" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt | sed 's/\s\+/,/g' | egrep "$PROCESS_NAME$EGREP_PROCESS_PID" | egrep -v "Linux|%" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    
    if [[ $PROCESS_NAME = "thesis_app" ]]
    then
        # Format app output
        egrep -v "gcc" < $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    else
        echo "0,0,0,0" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    fi

    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
    
    # App time all CPUs
    cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | egrep "$PROCESS_NAME$EGREP_PROCESS_PID" | awk -v N=4 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/runtime_app_all_cpus.csv
    
    # Total time all CPUs
    cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "Total run time" | awk -v N=5 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/runtime_tot_all_cpus.csv
    
    # App time per CPU
    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        if test -z "$(cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | egrep "$PROCESS_NAME$EGREP_PROCESS_PID")"; then
            echo 0 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/runtime_app_cpu$CPU.csv
        else
            cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | egrep "$PROCESS_NAME$EGREP_PROCESS_PID" | awk '{print $4}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/runtime_app_cpu$CPU.csv
        fi
    done

    # Total time per CPU
    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep -w "Total run time" | awk '{print $5}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/runtime_tot_cpu$CPU.csv
    done

    # Idle time and % per CPU
    cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "idle for" | awk '{print $5}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_time.csv
    cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "idle for" | awk '{print $8}' | rev | cut -c3- | rev > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_percent.csv
    
    # Append to file containing all iterations
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/app_outputs.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/cpus_used.csv

    # Append to file containing all iterations
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/vmstat.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_mem.csv
    
    echo "done"
    
done

echo -n "Resetting CPU isolations..."
sudo ./cgroup -r > /dev/null 2>&1
echo "done"

echo -n "Resetting CPU frequencies..."
sudo cpupower frequency-set -d 0GHz > /dev/null 2>&1
sudo cpupower frequency-set -u 4GHz > /dev/null 2>&1
echo "done"

python3 ./score.py "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME" $N_CPUS
# python3 ./plots.py $CURRENT_TIME $N_CPUS
