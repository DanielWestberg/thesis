#!/usr/bin/bash

ITERATIONS=1
DISABLE_OBSERVE_ITER=0

# Get preferences
PREFERENCES=$(jq '.' preferences.json)
PROCESS_NAME=$(echo $PREFERENCES | jq .process_name | tr -d '"')
APP_PATH=$(echo $PREFERENCES | jq '.app_path' | tr -d '"')
RUN_COMMAND=$(echo $PREFERENCES | jq '.run_command' | tr -d '"')
NOISE_TYPE=$(echo $PREFERENCES | jq '.noise' | tr -d '"')
APP_ISOL_CPU=$(echo $PREFERENCES | jq '.cpu_isolation')
ALL_CPUS=$(echo $PREFERENCES | jq '.all_cpus' | tr -d '"')

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
OUTPUT_DIR="output"
CURRENT_TIME="$(date +%Y%m%d_%H%M%S)"
mkdir "$OUTPUT_DIR/$CURRENT_TIME"

# Get standard CPU freq
CPU_FREQS=$(cat /proc/cpuinfo | grep "model name" | awk '{print $9}')
CPU0_FREQ=$(echo $CPU_FREQS | awk '{print $1}')

# Set static CPU freq
sudo cpupower frequency-set -d $CPU0_FREQ
sudo cpupower frequency-set -u $CPU0_FREQ

for (( i=1; i<=$ITERATIONS; i++ ))
do
    echo "Run $i"
    mkdir "$OUTPUT_DIR/$CURRENT_TIME/$i"

    if [ $NOISE_BOOL = 1 ]; then
        # Add noise to system
        if [ "$NOISE_TYPE" = "cpu" ]
        then
            echo "Starting cpu stress..."
            stress -c 1 &
        fi

        if [ "$NOISE_TYPE" = "memory" ]
        then
            echo "Starting memory stress..."
            stress -m 1 &
        fi
        
        if [ "$NOISE_TYPE" = "disk" ]
        then
            echo "Starting disk stress..."
            stress -d 1 &
        fi

        if [ "$NOISE_TYPE" = "io" ]
        then
            echo "Starting I/O stress..."
            stress -i 1 &
        fi
    fi

    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        # Start observability tools, store output in new dir
        echo -n "Starting observability tools..."
        vmstat -t -w 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt &
        VMSTAT_PID=$!
        pidstat 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt &
        PIDSTAT_PID=$!
        pidstat 1 -r > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt &
        PIDSTAT_MEM_PID=$!
        iostat -txd -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_xd_raw.txt &
        IOSTAT_PID=$!
        iostat -td -p sda 1 > $OUTPUT_DIR/$CURRENT_TIME/$i/iostat_d_raw.txt &
        IOSTATD_PID=$!

        if [[ $ALL_CPUS = 1 ]]
        then
            perf record -a -g -s -T -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            PERF_PID=$!
        else
            perf record -g -s -T -C $APP_ISOL_CPU -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf.data &
            PERF_PID=$!
        fi

        perf sched record -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data &
        PERF_SCHED_PID=$!
        
        echo "done"
    else
        echo "No observability tools"
    fi

    # Get cpu freq before running application
    cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $4}' > $OUTPUT_DIR/$CURRENT_TIME/$i/cpu_freq.csv
    
    # Run application
    if [[ $ALL_CPUS = 1 ]]
    then
        echo -n "Running application on all CPU's..."
        if [[ $RUN_COMMAND == *"make"* ]]
        then
            sudo perf stat -a --per-core -e cycles,instructions,ref-cycles,cycle_activity.stalls_total,cycle_activity.stalls_mem_any,cycle_activity.cycles_mem_any,i915/actual-frequency/ -A -B -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt $RUN_COMMAND -C $APP_PATH > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        else
            sudo perf stat -a --per-core -e cycles,instructions,ref-cycles,cycle_activity.stalls_total,cycle_activity.stalls_mem_any,cycle_activity.cycles_mem_any,i915/actual-frequency/ -A -B -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt "$APP_PATH$COMMAND" > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        fi
    else
        echo -n "Running application on CPU $APP_ISOL_CPU..."
        if [[ $RUN_COMMAND == *"make"* ]]
        then
            sudo perf stat \
                -e cycles,instructions,ref-cycles,cycle_activity.stalls_total,cycle_activity.stalls_mem_any,cycle_activity.cycles_mem_any,i915/actual-frequency/ -B -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt taskset -c $APP_ISOL_CPU $RUN_COMMAND -C $APP_PATH > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        else
            sudo perf stat \
                -e cycles,instructions,ref-cycles,cycle_activity.stalls_total,cycle_activity.stalls_mem_any,cycle_activity.cycles_mem_any,i915/actual-frequency/ -B -o $OUTPUT_DIR/$CURRENT_TIME/$i/perf_stat.txt taskset -c $APP_ISOL_CPU "$APP_PATH$RUN_COMMAND" > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt
        fi
    fi
    echo "done"
    
    # Get cpu freq after running application
    cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $4}' >> $OUTPUT_DIR/$CURRENT_TIME/$i/cpu_freq.csv

    # Stop observability tools
    if [[ $i != $DISABLE_OBSERVE_ITER ]]
    then
        echo -n "Stopping observability tools..."
        kill $PERF_PID $PERF_SCHED_PID $VMSTAT_PID $MPSTAT0PID $MPSTAT1PID $MPSTAT2PID $MPSTAT3PID $PIDSTAT_PID $PIDSTAT_MEM_PID $IOSTAT_PID $IOSTATD_PID
        echo "done"
    fi

    # Stop stress
    echo "Stopping stress..."
    for pid in $(pidof stress); do kill $pid ; done
    echo "done"

    sleep 1
    # Generate flamegraph
    if [[ $i != $DISABLE_OBSERVE_ITER ]]
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

    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        sudo perf sched timehist -MVwn --cpu=$CPU -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_cpu$CPU.txt
        sudo perf sched timehist -s --cpu=$CPU -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt
        sudo perf sched timehist -MVwnI --cpu=$CPU -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | sudo dd of=$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_idle_cpu$CPU.txt

        tail -n +6 $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | egrep -v "Terminated tasks|Idle stats|idle for|Total number|Total run|Total scheduling" | awk '{$1=$1;print}' | sed 's/\s\+/,/g' | grep . > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.csv
    done
    

    sudo perf sched timehist -i $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched.data | grep "thesis_app" > $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_thesis_app.txt
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_raw_thesis_app.txt | awk '!seen[$2]++' | awk '{print $2}' | awk 'BEGIN { ORS = " " } { print }' > $OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
    echo "done"

    # Format output data to csv
    echo -n "Formatting output to csv..."
    touch $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    
    # Format perf stat
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
        
    # Format vmstat
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat_raw.txt | sed 's/\s\+/,/g' | egrep -v "procs|buff" > $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    sed -i -e "s/^/$i/" $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    
    
    # Format pidstat
    # sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep $PROCESS_NAME | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    # sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    sed -r 's/[,]+/./g' $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt | sed 's/\s\+/,/g' | grep $PROCESS_NAME | egrep -v "Linux|%" > $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    
    if [[ $PROCESS_NAME = "thesis_app" ]]
    then
        # Format app output
        egrep -v "gcc" < $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    else
        echo "0,0,0,0" > $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    fi

    echo "$i" > $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    sed -i -e "s/^/$i,/" $OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
    
    # App time all CPUs
    cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep $PROCESS_NAME | awk -v N=4 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    # Total time all CPUs
    cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "Total run time" | awk -v N=5 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    
    # App time per CPU
    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        if test -z "$(cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep $PROCESS_NAME)"; then
            echo 0 | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        else
            cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep $PROCESS_NAME | awk -v N=4 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
        fi
    done

    # Total time per CPU
    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep -w "Total run time" | awk -v N=5 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    done
    # Idle time per CPU
    cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "idle for" | awk -v N=5 '{print $N}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    cat $OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary.txt | grep -w "idle for" | awk -v N=8 '{print $N}' | rev | cut -c3- | rev | xargs -I {} sudo sed -i -e 's/$/,{}/' $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv
    # Append to file containing all iterations
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv >> $OUTPUT_DIR/$CURRENT_TIME/app_outputs.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/runtime.csv >> $OUTPUT_DIR/$CURRENT_TIME/runtimes.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv >> $OUTPUT_DIR/$CURRENT_TIME/cpus_used.csv

    # Append to file containing all iterations
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/vmstat.csv
    # sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv >> $OUTPUT_DIR/$CURRENT_TIME/pidstat.csv
    sudo cat $OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv >> $OUTPUT_DIR/$CURRENT_TIME/pidstat_mem.csv
    
    echo "done"
    echo ""

done

echo -n "Resetting CPU frequencies..."
sudo cpupower frequency-set -d 0GHz
sudo cpupower frequency-set -u 4GHz
echo "done"

python3 ./benchmark.py $CURRENT_TIME $N_CPUS
python3 ./plots.py $CURRENT_TIME $N_CPUS
