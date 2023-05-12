#!/usr/bin/bash

DISABLE_OBSERVE_ITER=0

# Get config
CONFIG=$(jq '.' config.json)
PROCESS_NAME=$(echo $CONFIG | jq .process_name | tr -d '"')
APP_PATH=$(echo $CONFIG | jq '.app_path' | tr -d '"')
PRE_RUN_COMMAND=$(echo $CONFIG | jq '.pre_run_command' | tr -d '"')
RUN_COMMAND=$(echo $CONFIG | jq '.run_command' | tr -d '"')
IS_EXECUTABLE=$(echo $CONFIG | jq '.is_executable' | tr -d '"')
NOISE_TYPE=$(echo $CONFIG | jq '.noise_type' | tr -d '"')
NOISE_WORKERS=$(echo $CONFIG | jq '.noise_workers' | tr -d '"')
APP_ISOL_CPU=$(echo $CONFIG | jq '.cpu_isolation')
ALL_CPUS=$(echo $CONFIG | jq '.all_cpus' | tr -d '"')
PLOT_GRAPHS=$(echo $CONFIG | jq '.plot_graphs' | tr -d '"')
VERBOSE=$(echo $CONFIG | jq '.verbose' | tr -d '"')
ITERATIONS=$(echo $CONFIG | jq '.n_iterations' | tr -d '"')
SLEEP=$(echo $CONFIG | jq '.sleep' | tr -d '"')

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
    make thesis_app > /dev/null 2>&1
fi

# Store current time as a variable and create a new dir
SCRIPT_DIR=$PWD
OUTPUT_DIR="output"
[ ! -d "$SCRIPT_DIR/$OUTPUT_DIR" ] && sudo -u $SUDO_USER mkdir "$SCRIPT_DIR/$OUTPUT_DIR" 
CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
sudo -u $SUDO_USER mkdir "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME"
cp ./config.json $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME
echo $CURRENT_TIME > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/current_time.csv

# Get standard CPU freq
CPU_FREQS=$(cat /proc/cpuinfo | grep "model name" | awk '{print $9}')
CPU0_FREQ=$(echo $CPU_FREQS | awk '{print $1}')

# Set static CPU freq
echo -n "Setting CPU frequencies to static..."
sudo cpupower frequency-set -d $CPU0_FREQ > /dev/null 2>&1
sudo cpupower frequency-set -u $CPU0_FREQ > /dev/null 2>&1
echo "done"

for (( i=1; i<=$ITERATIONS; i++ ))
do
    echo ""
    echo "Run $i"
    sudo -u $SUDO_USER mkdir "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i"

    if [ $NOISE_BOOL = 1 ]; then
        # Add noise to system
        CPU_FLAG=""
        MEM_FLAG=""
        DISK_FLAG=""
        IO_FLAG=""
        if [[ $NOISE_TYPE == *"cpu"* ]]
        then
            CPU_FLAG="-c $NOISE_WORKERS"
        fi

        if [[ $NOISE_TYPE == *"memory"* ]]
        then
            MEM_FLAG="-m $NOISE_WORKERS"
        fi
        
        if [[ $NOISE_TYPE == *"disk"* ]]
        then
            DISK_FLAG="-d $NOISE_WORKERS"
        fi

        if [[ $NOISE_TYPE == *"io"* ]]
        then
            IO_FLAG="-i $NOISE_WORKERS"
        fi
        echo "Starting $NOISE_TYPE stress..."
        stress $CPU_FLAG $MEM_FLAG $DISK_FLAG $IO_FLAG &
        echo "done"
    fi

    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        # Start observation tools, store output in new dir
        echo -n "Starting observation tools..."
        vmstat -twn 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt &
        VMSTAT_PID=$!
        sar -r ALL 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r_raw.txt &
        SAR_R_PID=$!
        sar -m ALL 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_m_raw.txt &
        SAR_M_PID=$!
        pidstat 1 > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt &
        PIDSTAT_PID=$!
        pidstat 1 -r > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt &
        PIDSTAT_MEM_PID=$!

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
        echo "No observation tools"
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
            perf stat -e cycles,instructions,cycle_activity.stalls_total,cycle_activity.cycles_mem_any,hw_interrupts.received,cache-misses,cache-references,branch-misses,branch-instructions,mem-stores,mem-loads,page-faults \
                -B -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt $RUN_COMMAND > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        else
            echo -n "Running $RUN_COMMAND in $PWD on CPU $APP_ISOL_CPU. Retrieving stats for $PROCESS_NAME..."
            perf stat \
                -e cycles,instructions,cycle_activity.stalls_total,cycle_activity.cycles_mem_any,hw_interrupts.received,cache-misses,cache-references,branch-misses,branch-instructions,mem-stores,mem-loads,page-faults \
                -B -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt taskset -c $APP_ISOL_CPU $RUN_COMMAND > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        fi
    else
        PROCESS_PID=$(pidof $PROCESS_NAME)
        echo $PROCESS_PID > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/process_pid.txt
        EGREP_PROCESS_PID="|$PROCESS_PID"
        if [[ $ALL_CPUS = 0 ]]
        then
            echo "Isolating $PROCESS_NAME on CPU $APP_ISOL_CPU."
            taskset -acp $APP_ISOL_CPU $PROCESS_PID > /dev/null 2>&1
            echo "done"
        fi
        sleep 1
        echo "Retrieving stats for $PROCESS_NAME..."
        perf stat \
            -e cycles,instructions,cycle_activity.stalls_total,cycle_activity.cycles_mem_any,hw_interrupts.received,cache-misses,cache-references,branch-misses,branch-instructions,mem-stores,mem-loads,page-faults \
            -B -o $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt --pid=$PROCESS_PID &
        PERF_STAT_PID=$!
        echo "Running $RUN_COMMAND..."
        $RUN_COMMAND > /dev/null 2>&1
        kill -INT $PERF_STAT_PID
    fi
    echo "done"
    
    # Get cpu freq after running application
    cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $4}' >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpu_freq.csv

    # Stop observation tools
    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        echo -n "Stopping observation tools..."
        kill $PERF_PID $PERF_SCHED_PID $VMSTAT_PID
        kill -INT $SAR_R_PID $SAR_M_PID $PIDSTAT_PID $PIDSTAT_MEM_PID
        echo "done"
    fi

    cd $SCRIPT_DIR

    # Stop stress
    if [ $NOISE_BOOL = 1 ]; then
        echo "Stopping stress..."
        for pid in $(pidof stress); do kill $pid ; done
        echo "done"
    fi

    sleep 2
    # Generate flamegraph
    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        echo -n "Generating flame graph..."
        sudo perf script -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf.data | $SCRIPT_DIR/FlameGraph/stackcollapse-perf.pl > $SCRIPT_DIR/FlameGraph/out.perf-folded
        $SCRIPT_DIR/FlameGraph/flamegraph.pl $SCRIPT_DIR/FlameGraph/out.perf-folded > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf.svg
        echo "done"
    fi

    echo -n "Generating scheduling time history..."
    sudo perf sched timehist -s -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt > /dev/null 2>&1

    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        sudo perf sched timehist -s --cpu=$CPU -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt > /dev/null 2>&1

        tail -n +6 $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | egrep -v "Terminated tasks|Idle stats|idle for|idle entire time window|Total number|Total run|Total scheduling" | awk '{$1=$1;print}' \
            | while read -a line; do if [[ "${#line[@]}" -ge 10 ]] ; then index="$(("${#line[@]}"-9))" ; else index=0 ; fi; echo "${line[@]:$index}" >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/temp_perf_sched_summary_cpu$CPU.txt ; done
        sleep 1
        sed 's/\s\+/,/g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/temp_perf_sched_summary_cpu$CPU.txt | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.csv
    done
    
    sudo perf sched timehist -i $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | egrep "$PROCESS_NAME$EGREP_PROCESS_PID" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_$PROCESS_NAME.txt
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_$PROCESS_NAME.txt | awk '!seen[$2]++' | awk '{print $2}' | awk 'BEGIN { ORS = " " } { print }' > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
    echo "done"
    
    echo -n "Removing redundant files..."
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf.data
    echo "done"

    echo -n "Waiting for $SLEEP seconds..."
    sleep $SLEEP
    echo "done"
done

echo -n "Resetting CPU isolations..."
sudo $SCRIPT_DIR/cgroup -r > /dev/null 2>&1
echo "done"

echo -n "Resetting CPU frequencies..."
sudo cpupower frequency-set -d 0GHz > /dev/null 2>&1
sudo cpupower frequency-set -u 4GHz > /dev/null 2>&1
echo "done"

$SCRIPT_DIR/format.sh $CURRENT_TIME
