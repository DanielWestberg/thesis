#!/usr/bin/python3
import pandas as pd
import numpy as np
import os
import sys

def main(argv):
    path = f'/home/dwdd/thesis/output/{argv[0]}'

    runtime_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'App time src', 'App time observed all cpus', 'Tot time observed all cpus', 'App time observed CPU 0', 'App time observed CPU 1', 'App time observed CPU 2', 'App time observed CPU 3', 'Tot time observed CPU 0', 'Tot time observed CPU 1', 'Tot time observed CPU 2', 'Tot time observed CPU 3', 'Idle time CPU 0', 'Idle time CPU 1', 'Idle time CPU 2', 'Idle time CPU 3', 'Idle % CPU 0', 'Idle % CPU 1', 'Idle % CPU 2', 'Idle % CPU 3']
    runtime_df = pd.read_csv(f'{path}/runtimes.csv', verbose=True, names=runtime_headers)
    runtime_df.set_index('Run')

    perf_sched_summary_cpu0_headers = ['comm', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    perf_sched_summary_cpu0_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu0.csv', verbose=True, names=perf_sched_summary_cpu0_headers)
    aggregation_functions = {'comm': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    perf_sched_summary_cpu0_df_new = perf_sched_summary_cpu0_df.groupby(perf_sched_summary_cpu0_df['comm'], as_index=False).aggregate(aggregation_functions)
    perf_sched_summary_cpu0_df_new = perf_sched_summary_cpu0_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

    perf_sched_summary_cpu1_headers = ['comm', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    perf_sched_summary_cpu1_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu1.csv', verbose=True, names=perf_sched_summary_cpu1_headers)
    aggregation_functions = {'comm': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    perf_sched_summary_cpu1_df_new = perf_sched_summary_cpu1_df.groupby(perf_sched_summary_cpu1_df['comm'], as_index=False).aggregate(aggregation_functions)
    perf_sched_summary_cpu1_df_new = perf_sched_summary_cpu1_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

    perf_sched_summary_cpu2_headers = ['comm', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    perf_sched_summary_cpu2_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu2.csv', verbose=True, names=perf_sched_summary_cpu2_headers)
    aggregation_functions = {'comm': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    perf_sched_summary_cpu2_df_new = perf_sched_summary_cpu2_df.groupby(perf_sched_summary_cpu2_df['comm'], as_index=False).aggregate(aggregation_functions)
    perf_sched_summary_cpu2_df_new = perf_sched_summary_cpu2_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

    perf_sched_summary_cpu3_headers = ['comm', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    perf_sched_summary_cpu3_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu3.csv', verbose=True, names=perf_sched_summary_cpu3_headers)
    aggregation_functions = {'comm': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    perf_sched_summary_cpu3_df_new = perf_sched_summary_cpu3_df.groupby(perf_sched_summary_cpu3_df['comm'], as_index=False).aggregate(aggregation_functions)
    perf_sched_summary_cpu3_df_new = perf_sched_summary_cpu3_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

    cpus_used_headers = ['Run', 'CPUs_used']
    cpus_used_df = pd.read_csv(f'{path}/cpus_used.csv', verbose=True, names=cpus_used_headers)

    row1_runtime = runtime_df.iloc[[0]]
    row1_cpus = cpus_used_df.iloc[[0]]

    cpus = row1_cpus['CPUs_used'].item().replace("[", "").replace("]", "")

    cpus = cpus.split()
    for i, cpu in enumerate(cpus):
        cpus[i] = int(cpu[3:])

    # n_cpus = len(cpus.split())
    n_cpus = int(argv[1])

    tot_cpu_utils = [0 for i in range(n_cpus)]
    app_cpu_utils = [0 for i in range(n_cpus*2)]
    tot_plus_idle = [0 for i in range(n_cpus)]
    app_mean = [0, 0]
    for cpu in range(n_cpus):
        tot_plus_idle[cpu] = row1_runtime[f'Tot time observed CPU {cpu}'].item() + row1_runtime[f'Idle time CPU {cpu}'].item()
        tot_cpu_utils[cpu] = row1_runtime[f'Tot time observed CPU {cpu}'].item() / tot_plus_idle[cpu] * 100
        app_cpu_utils[cpu] = row1_runtime[f'App time observed CPU {cpu}'].item() / row1_runtime[f'Tot time observed CPU {cpu}'].item() * 100
        app_cpu_utils[cpu+4] = row1_runtime[f'App time observed CPU {cpu}'].item() / tot_plus_idle[cpu] * 100        
        if (cpu in cpus):
            app_mean[0] += app_cpu_utils[cpu]
            app_mean[1] += app_cpu_utils[cpu+4]
    
    app_mean[0] = app_mean[0] / len(cpus)
    app_mean[1] = app_mean[1] / len(cpus)

    print(f"\nobserved app runtime:         {'{0:.2f}'.format(row1_runtime['App time observed all cpus'].item())} seconds")
    print(f"observed accumulated runtime: {'{0:.2f}'.format(row1_runtime['Tot time observed all cpus'].item())} seconds")
    print(f"CPU(s) used: {cpus}\n")
    for i, tot_cpu_util in enumerate(tot_cpu_utils):
        print(f"Active time CPU {i}: {'{0:.2f}'.format(row1_runtime[f'Tot time observed CPU {i}'].item())} seconds (100% util of active, {'{0:.2f}'.format(tot_cpu_util)}% of total)")

    print()
    for i in range(n_cpus):
        print(f"App time CPU {i}:   {'{0:.2f}'.format(row1_runtime[f'App time observed CPU {i}'].item())} seconds ({'{0:.2f}'.format(app_cpu_utils[i])}% util of active, {'{0:.2f}'.format(app_cpu_utils[i+4])}% of total)")
    print(f"Mean app time of all used CPUs:  ({'{0:.2f}'.format(app_mean[0])}% util of active, {'{0:.2f}'.format(app_mean[1])}% of total)")
    
    print()  
    for i in range(n_cpus):
        print(f"idle time CPU {i}:  {'{0:.2f}'.format(row1_runtime[f'Idle time CPU {i}'].item())} seconds (0% util of active, {row1_runtime[f'Idle % CPU {i}'].item()}% of total)")
    
    print()  
    for i in range(n_cpus):
        print(f"Total time CPU {i}:  {'{0:.2f}'.format(tot_plus_idle[i])} seconds")
    print("-----------------------------------------")
    print(perf_sched_summary_cpu0_df_new.head())
    print("-----------------------------------------")
    print(perf_sched_summary_cpu1_df_new.head())
    print("-----------------------------------------")
    print(perf_sched_summary_cpu2_df_new.head())
    print("-----------------------------------------")
    print(perf_sched_summary_cpu3_df_new.head())




    # cpu_freq = 2.6 * 10^9
    # T = 1 / cpu_freq
    # IC = 100
    # IPC = 2.5
    # CPI = 1 / IPC
    # CT = IC * CPI * T
    # t = 



















    # vmstat_headers = ['Run', 'runnable processes', 'ps blckd wait for I/O', 'tot swpd used', 'free', 'buff', 'cache', 'mem swapped in/s', 'mem swapped out/s', 'from block device (KiB/s)', 'to block device (KiB/s)', 'interrupts/s', 'cxt switch/s', 'user time', 'system time', 'idle time', 'wait io time', 'stolen time', 'Date', 'Time']
    # vmstat_df = pd.read_csv(f'{path}/vmstat.csv', verbose=True, names=vmstat_headers)
    # vmstat_df['Time'] = pd.to_datetime(vmstat_df['Time'])
    # vmstat_df['seconds'] = vmstat_df['Time'].dt.strftime("%M:%S")
    # vmstat_df.set_index('seconds')

    # mpstat0_headers = ['Run', 'Time', 'CPU', '"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle']
    # mpstat0_df = pd.read_csv(f'{path}/mpstat0.csv', verbose=True, names=mpstat0_headers)
    # mpstat0_df['Time'] = pd.to_datetime(mpstat0_df['Time'])
    # mpstat0_df['seconds'] = mpstat0_df['Time'].dt.strftime("%M:%S")
    # mpstat0_df.set_index('seconds')

    # mpstat1_headers = ['Run', 'Time', 'CPU', '"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle']
    # mpstat1_df = pd.read_csv(f'{path}/mpstat1.csv', verbose=True, names=mpstat1_headers)
    # mpstat1_df['Time'] = pd.to_datetime(mpstat1_df['Time'])
    # mpstat1_df['seconds'] = mpstat1_df['Time'].dt.strftime("%M:%S")
    # mpstat1_df.set_index('seconds')

    # mpstat2_headers = ['Run', 'Time', 'CPU', '"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle']
    # mpstat2_df = pd.read_csv(f'{path}/mpstat2.csv', verbose=True, names=mpstat2_headers)
    # mpstat2_df['Time'] = pd.to_datetime(mpstat2_df['Time'])
    # mpstat2_df['seconds'] = mpstat2_df['Time'].dt.strftime("%M:%S")
    # mpstat2_df.set_index('seconds')

    # mpstat3_headers = ['Run', 'Time', 'CPU', '"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle']
    # mpstat3_df = pd.read_csv(f'{path}/mpstat3.csv', verbose=True, names=mpstat3_headers)
    # mpstat3_df['Time'] = pd.to_datetime(mpstat3_df['Time'])
    # mpstat3_df['seconds'] = mpstat3_df['Time'].dt.strftime("%M:%S")
    # mpstat3_df.set_index('seconds')

    # pidstat_headers = ['Run', 'Time', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
    # pidstat_df = pd.read_csv(f'{path}/pidstat.csv', verbose=True, names=pidstat_headers)
    # pidstat_df['Time'] = pd.to_datetime(pidstat_df['Time'])
    # pidstat_df['seconds'] = pidstat_df['Time'].dt.strftime("%M:%S")
    # pidstat_df.set_index('seconds')

    # iostat_d_headers = ['Run', 'Date', 'Time', 'Device', 'tps', 'kB_read/s', 'kB_wrtn/s', 'kB_dscrded/s', 'kB_read', 'kB_wrtn', 'kB_dscrded']
    # iostat_d_df = pd.read_csv(f'{path}/iostat_d.csv', verbose=True, names=iostat_d_headers)
    # iostat_d_df['Time'] = pd.to_datetime(iostat_d_df['Time'])
    # iostat_d_df['seconds'] = iostat_d_df['Time'].dt.strftime("%M:%S")
    # iostat_d_df.set_index('Time')

    # iostat_xd_headers = ['Run', 'Date', 'Time', 'Device', 'read reqs per s', 'rkB/s', 'rrqm/s', '"%"rrqm', 'r_await', 'rareq-sz', 'write reqs per s', 'wkB/s', 'wrqm/s', '"%"wrqm',\
    #                     'w_await', 'wareq-sz', 'd/s', 'dkB/s', 'drqm/s', '"%"drqm', 'd_await', 'dareq-sz', 'f/s', 'f_await', 'aqu-sz', '"%"util']
    # iostat_xd_df = pd.read_csv(f'{path}/iostat_xd.csv', verbose=True, names=iostat_xd_headers)
    # iostat_xd_df['Time'] = pd.to_datetime(iostat_xd_df['Time'])
    # iostat_xd_df['seconds'] = iostat_xd_df['Time'].dt.strftime("%M:%S")
    # iostat_xd_df.set_index('seconds')

    # score = runtime_df['tot time src'] 

if __name__ == "__main__":
   main(sys.argv[1:])