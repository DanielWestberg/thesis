#!/usr/bin/bash

SCRIPT_DIR=$PWD
OUTPUT_DIR="output"
CURRENT_TIME=$1

CONFIG=$(jq '.' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/config.json)
PROCESS_NAME=$(echo $CONFIG | jq .process_name | tr -d '"')
PLOT_GRAPHS=$(echo $CONFIG | jq '.plot_graphs' | tr -d '"')
VERBOSE=$(echo $CONFIG | jq '.verbose' | tr -d '"')
ITERATIONS=$(echo $CONFIG | jq '.n_iterations' | tr -d '"')

N_CPUS=$(lscpu | grep --max-count=1 "CPU(s)" | awk '{print $2}')
PROCESS_PID=$(cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/process_pid.txt)
EGREP_PROCESS_PID="|$PROCESS_PID"

if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/app_outputs.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/app_outputs.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/cpus_used.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/cpus_used.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/vmstat.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/vmstat.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/sar_r.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/sar_r.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_mem.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_mem.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/sar_r_average.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/sar_r_average.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_average.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_average.csv
fi
if test -f "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_mem_average.csv"; then
    rm $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_mem_average.csv
fi

echo ""
echo -n "Formatting output to csv..."

for (( i=1; i<=$ITERATIONS; i++ ))
do
    # Format output data to csv
    sudo -u $SUDO_USER touch $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_time.csv
    sudo -u $SUDO_USER touch $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_percent.csv
    
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
    echo "$i" >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv
    
    # Format sar
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r_raw.txt | sed 's/\s\+/,/g' | egrep -v "Linux|Average|%" | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r.csv
    echo "$i" >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r.csv
    
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r_raw.txt | sed 's/\s\+/,/g' | grep "Average" | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r_average.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r_average.csv

    # Format pidstat
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep $PROCESS_NAME | egrep -v "Linux|Average|%" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    echo "$i" >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv
    
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | egrep -v "Linux|Average|%" | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_all.csv
    
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_raw.txt | sed 's/\s\+/,/g' | grep "Average" | egrep -v "Linux|%" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_average.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_average.csv
    
    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt | sed 's/\s\+/,/g' | egrep "$PROCESS_NAME$EGREP_PROCESS_PID" | egrep -v "Linux|Average|%" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv
    echo "$i" >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv

    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt | sed 's/\s\+/,/g' | egrep -v "Linux|Average|%" | grep . > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_all.csv

    sed -r 's/[,]+/./g' $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_raw.txt | sed 's/\s\+/,/g' | grep "Average" | egrep -v "Linux|%" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_average.csv
    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_average.csv
    
    if [[ $PROCESS_NAME = "thesis_app" ]]
    then
        # Format app output
        egrep -v "gcc" < $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.txt > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    else
        echo "0,0,0,0" > $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    fi

    sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv
    
    if test -z "$(cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv | grep ',')"; then
        sed -i -e "s/^/$i,/" $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv
    fi

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
    sudo -u $SUDO_USER touch "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_time.csv"
    sudo -u $SUDO_USER touch "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_percent.csv"
    for (( CPU=0; CPU<$N_CPUS; CPU++ ))
    do
        if test -z "$(cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep -w 'idle for')"; then
            cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep -w "Total run time" | awk '{print $5}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_time.csv
            echo 100 >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_percent.csv
        else
            cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep -w "idle for" | awk '{print $5}' | xargs -I {} echo -e "scale=6; {}/1000" | bc -l >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_time.csv
            cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/perf_sched_summary_cpu$CPU.txt | grep -w "idle for" | awk '{print $8}' | rev | cut -c3- | rev >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/idle_percent.csv
        fi
    done
    
    # Append to file containing all iterations
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/app_output.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/app_outputs.csv
    echo " " >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/cpus_used.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/cpus_used.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/cpus_used.csv

    # Append to file containing all iterations
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/vmstat.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/vmstat.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/sar_r.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_mem.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/sar_r_average.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/sar_r_average.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_average.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_average.csv
    sudo cat $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/$i/pidstat_mem_average.csv >> $SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME/pidstat_mem_average.csv
    
done
echo "done"

sudo -u $SUDO_USER python3 $SCRIPT_DIR/summary.py "$SCRIPT_DIR/$OUTPUT_DIR/$CURRENT_TIME" $PROCESS_NAME $N_CPUS $PLOT_GRAPHS $VERBOSE no
