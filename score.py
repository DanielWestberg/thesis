#!/usr/bin/python3
import pandas as pd
import os
import sys

def main(argv):
    path = argv[0]
    n_cpus = int(argv[1])
    f = open(os.devnull, 'w')
    old_stdout = sys.stdout
    sys.stdout = f

    # Read CSV files
    app_output_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'App time src',]
    app_output_df = pd.read_csv(f'{path}/app_outputs.csv', verbose=True, names=app_output_headers)

    runtime_app_all_cpus_headers = ['test']
    runtime_tot_all_cpus_headers = ['test']
    idle_time_headers = ['test']
    idle_percent_headers = ['test']
    runtime_app_cpu_headers = []
    runtime_tot_cpu_headers = []
    runtime_app_cpu_df = {}
    runtime_tot_cpu_df = {}

    for cpu in range(n_cpus):
        runtime_app_cpu_headers.append([f"test"])
        runtime_tot_cpu_headers.append([f"test"])
        runtime_app_cpu_df[f'cpu {cpu}'] = pd.read_csv(f'{path}/1/runtime_app_cpu{cpu}.csv', verbose=True, names=runtime_app_cpu_headers[cpu], on_bad_lines='skip')
        runtime_tot_cpu_df[f'cpu {cpu}'] = pd.read_csv(f'{path}/1/runtime_tot_cpu{cpu}.csv', verbose=True, names=runtime_tot_cpu_headers[cpu], on_bad_lines='skip')

    runtime_app_all_cpus_df = pd.read_csv(f'{path}/1/runtime_app_all_cpus.csv', verbose=True, names=runtime_app_all_cpus_headers, on_bad_lines='skip')
    runtime_tot_all_cpus_df = pd.read_csv(f'{path}/1/runtime_tot_all_cpus.csv', verbose=True, names=runtime_tot_all_cpus_headers, on_bad_lines='skip')
    idle_time_df = pd.read_csv(f'{path}/1/idle_time.csv', verbose=True, names=idle_time_headers)
    idle_percent_df = pd.read_csv(f'{path}/1/idle_percent.csv', verbose=True, names=idle_percent_headers)
        
    perf_sched_summary_cpu_headers = ['process', 'parent', 'sched-in', 'run-time (ms)', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    perf_sched_summary_cpu_dfs = []
    perf_sched_summary_cpu_dfs_new = []
    for i in range(n_cpus):
        perf_sched_summary_cpu_dfs.append(pd.read_csv(f'{path}/1/perf_sched_summary_cpu{i}.csv', verbose=True, names=perf_sched_summary_cpu_headers))
        aggregation_functions = {'process': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time (ms)': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
        perf_sched_summary_cpu_dfs_new.append(perf_sched_summary_cpu_dfs[i].groupby(perf_sched_summary_cpu_dfs[i]['process'], as_index=False).aggregate(aggregation_functions))
        perf_sched_summary_cpu_dfs_new[i] = perf_sched_summary_cpu_dfs_new[i].sort_values(by=['run-time (ms)', 'sched-in'], ascending=False)

    pidstat_mem_df = []
    if (os.path.isfile(f'{path}/pidstat_mem.csv')):
        pidstat_mem_headers = ['Run', 'Time', 'UID', 'PID', 'minflt/s', 'majflt/s', 'VSZ', 'RSS', '"%"MEM', 'Command']
        pidstat_mem_df = pd.read_csv(f'{path}/pidstat_mem.csv', verbose=True, names=pidstat_mem_headers)
        pidstat_mem_df['Time'] = pd.to_datetime(pidstat_mem_df['Time'])
        pidstat_mem_df['seconds'] = pidstat_mem_df['Time'].dt.strftime("%M:%S")
        pidstat_mem_df.set_index('seconds')

    cpus_used_headers = ['Run', 'CPUs_used']
    cpus_used_df = pd.read_csv(f'{path}/cpus_used.csv', verbose=True, names=cpus_used_headers)

    time = 0
    with open(f'{path}/1/perf_stat_time.csv', 'r') as perf_stat_time:
        time = perf_stat_time.read()
    time = float(time)

    cpu_freqs = [0 for i in range(n_cpus)]
    with open(f'{path}/1/cpu_freq.csv', 'r') as cpu_freq_file:
        lines = cpu_freq_file.readlines()
        for i in range(len(lines)):
            cpu_freqs[i % n_cpus] += float(lines[i])
    
    for i in range(len(cpu_freqs)):
        cpu_freqs[i] = cpu_freqs[i] / 2 * (10**6)

    perf_stat_ic_headers = []
    perf_stat_cycles_headers = []

    perf_stat_ic_headers = ['ic','unit','#', 'ipc', 'ins','per','cycle', 'multiplex']
    perf_stat_cycles_headers = ['cycles','unit', 'multiplex']
    perf_stat_mem_loads_headers = ['mem-loads','unit', 'multiplex']
    perf_stat_mem_stores_headers = ['mem-stores','unit', 'multiplex']
    perf_stat_cycle_stalls_total_headers = ['cycle-stalls','unit', 'multiplex']
    perf_stat_hw_interrupts_received_headers = ['hw_interrupts','unit', 'multiplex']
    perf_stat_cache_misses_headers = ['cache-misses','unit','#','%', 'percentage', 'of', 'all', 'cache', 'refs', 'multiplex']
    perf_stat_branch_misses_headers = ['branch-misses','unit','#','%', 'of', 'all', 'branches', 'multiplex']
    perf_stat_page_faults_headers = ['page-faults','unit']

    perf_stat_ic_df = pd.read_csv(f'{path}/1/perf_stat_ic.csv', verbose=True, names=perf_stat_ic_headers).drop(columns=['unit', '#', 'ins', 'per', 'cycle'])
    perf_stat_cycles_df = pd.read_csv(f'{path}/1/perf_stat_cycles.csv', verbose=True, names=perf_stat_cycles_headers).drop(columns=['unit'])
    perf_stat_mem_loads_df = pd.read_csv(f'{path}/1/perf_stat_mem_loads.csv', verbose=True, names=perf_stat_mem_loads_headers).drop(columns=['unit'])
    perf_stat_mem_stores_df = pd.read_csv(f'{path}/1/perf_stat_mem_stores.csv', verbose=True, names=perf_stat_mem_stores_headers).drop(columns=['unit'])
    perf_stat_cycle_stalls_total_df = pd.read_csv(f'{path}/1/perf_stat_cycle_stalls_total.csv', verbose=True, names=perf_stat_cycle_stalls_total_headers).drop(columns=['unit'])
    perf_stat_hw_interrupts_received_df = pd.read_csv(f'{path}/1/perf_stat_hw_interrupts_received.csv', verbose=True, names=perf_stat_hw_interrupts_received_headers).drop(columns=['unit'])
    perf_stat_cache_misses_df = pd.read_csv(f'{path}/1/perf_stat_cache_misses.csv', verbose=True, names=perf_stat_cache_misses_headers).drop(columns=['unit','#','percentage', 'of', 'all', 'cache', 'refs'])
    perf_stat_branch_misses_df = pd.read_csv(f'{path}/1/perf_stat_branch_misses.csv', verbose=True, names=perf_stat_branch_misses_headers).drop(columns=['unit','#','of', 'all', 'branches'])
    perf_stat_page_faults_df = pd.read_csv(f'{path}/1/perf_stat_page_faults.csv', verbose=True, names=perf_stat_page_faults_headers).drop(columns=['unit'])


    # Get CPUs used
    row1_cpus = cpus_used_df.iloc[[0]]

    cpus = row1_cpus['CPUs_used'].item().replace("[", "").replace("]", "")

    cpus = cpus.split()
    for i, cpu in enumerate(cpus):
        cpus[i] = int(cpu[3:])

    n_cpus_used = len(cpus)


    # Declare empty variables
    Ts = [1 / cpu_freqs[i] for i in range(n_cpus)]
    CTs_ideal = [0 for i in range(n_cpus)]
    CTs_stalls = [0 for i in range(n_cpus)]
    CT_TOT = 0

    # Parse instruction count
    ic = perf_stat_ic_df["ic"].item()
    ic = ''.join(ic.split())
    ic = int(ic)

    # Parse app CPU cycles
    cycles = perf_stat_cycles_df["cycles"].item()
    cycles = ''.join(cycles.split())
    cycles = int(cycles)

    # Parse app CPU stall cycles
    cycle_stalls_total = perf_stat_cycle_stalls_total_df["cycle-stalls"].item()
    cycle_stalls_total = ''.join(cycle_stalls_total.split())
    cycle_stalls_total = int(cycle_stalls_total)

    # Get app IPC
    ipc = perf_stat_ic_df["ipc"].item()


    # CPU time calculations
    CTs_ideal[cpus[0]] = ic * (1/ipc) * Ts[cpus[0]]
    CTs_stalls[cpus[0]] = (cycles + cycle_stalls_total) * Ts[cpus[0]]

    t_ideal = (cycles - cycle_stalls_total)*Ts[cpus[0]]
    t_with_stalls = cycles*Ts[cpus[0]]
    slowdown = (time/t_ideal - 1) * 100

    tot_cpu_utils = [0 for i in range(n_cpus)]
    app_cpu_utils = [0 for i in range(n_cpus*2)]
    tot_plus_idle = [0 for i in range(n_cpus)]
    app_mean = [0, 0]
    tot_runtime_app_cpu = {}
    tot_runtime_all_cpus = 0
    for cpu in range(n_cpus):
        tot_runtime_app_cpu[f'cpu {cpu}'] = 0
        for i, row in runtime_app_cpu_df[f'cpu {cpu}'].iterrows():
            tot_runtime_app_cpu[f'cpu {cpu}'] += row['test'].item()
        tot_plus_idle[cpu] = runtime_tot_cpu_df[f'cpu {cpu}'].iloc[[0]]['test'].item() + idle_time_df.iloc[[cpu]]['test'].item()
        tot_cpu_utils[cpu] = runtime_tot_cpu_df[f'cpu {cpu}'].iloc[[0]]['test'].item() / tot_plus_idle[cpu] * 100
        app_cpu_utils[cpu] = tot_runtime_app_cpu[f'cpu {cpu}'] / runtime_tot_cpu_df[f'cpu {cpu}'].iloc[[0]]['test'].item() * 100
        app_cpu_utils[cpu + n_cpus] = tot_runtime_app_cpu[f'cpu {cpu}'] / tot_plus_idle[cpu] * 100        
        if (cpu in cpus):
            app_mean[0] += app_cpu_utils[cpu]
            app_mean[1] += app_cpu_utils[cpu + n_cpus]
        tot_runtime_all_cpus += tot_runtime_app_cpu[f'cpu {cpu}']
    
    app_mean[0] = app_mean[0] / len(cpus)
    app_mean[1] = app_mean[1] / len(cpus)

    # Branch misses
    branch_misses = perf_stat_branch_misses_df.iloc[[0]]['branch-misses'].item()
    branch_misses_percent = perf_stat_branch_misses_df.iloc[[0]]['%'].item()

    # Memory
    mem_total = 1
    mem_used = 1
    mem_util = mem_used / mem_total * 100
    cache_misses = perf_stat_cache_misses_df.iloc[[0]]['cache-misses'].item()
    cache_misses_percent = perf_stat_cache_misses_df.iloc[[0]]['%'].item()
    mem_stores = perf_stat_mem_stores_df.iloc[[0]]['mem-stores'].item()
    mem_loads = perf_stat_mem_loads_df.iloc[[0]]['mem-loads'].item()
    page_faults = perf_stat_page_faults_df.iloc[[0]]['page-faults'].item()
    
    sys.stdout = old_stdout

    print("\n----------------------- CPU utilization -----------------------")

    print(f"CPU(s) used for application: {cpus}\n")
    for i, tot_cpu_util in enumerate(tot_cpu_utils):
        print(f"Active time CPU{i}: {'{0:.2f}'.format(runtime_tot_cpu_df[f'cpu {i}'].iloc[[0]]['test'].item())} seconds (100% of active, {'{0:.2f}'.format(tot_cpu_util)}% of total)")
    
    print()
    for i in range(n_cpus):
        print(f"App time CPU{i}:    {'{0:.2f}'.format(tot_runtime_app_cpu[f'cpu {i}'])} seconds ({'{0:.2f}'.format(app_cpu_utils[i])}% of active, {'{0:.2f}'.format(app_cpu_utils[i + n_cpus])}% of total)")
    
    print()
    for i in range(n_cpus):
        print(f"idle time CPU{i}:   {'{0:.2f}'.format(idle_time_df.iloc[[i]]['test'].item())} seconds (0% of active, {idle_percent_df.iloc[[i]]['test'].item()}% of total)")
        
    cpu_util_score = app_cpu_utils[cpus[0] + n_cpus] - idle_percent_df.iloc[[cpus[0]]]['test'].item()

    print("\n\nTop five processes with the highest runtime during app runtime:")
    for i in range(n_cpus):
        print(f"\nCPU{i}")
        print(perf_sched_summary_cpu_dfs_new[i].head())
    print()

    print("\n----------------------- CPU time -----------------------")
    print(f"Theoretical ideal CPU time:                 {t_ideal:.2f} seconds")
    print(f"Theoretical CPU time incl. stall cycles:    {t_with_stalls:.2f} seconds")
    print(f"Actual CPU time:                            {tot_runtime_all_cpus:.2f} seconds")
    print(f"Wall time:                                  {time:.2f} seconds")
    print(f"Diff time wall & ideal:                     {(time-t_ideal):.2f} seconds")
    print(f"Slowdown wall vs ideal:                     {slowdown:.2f}%")
    print(f"CPU freq:                                   {cpu_freqs[0] / (10**9):.2f} GHz")
    print(f"Branch misses:                              {branch_misses}     ({branch_misses_percent} of total branch instructions)")
    
    print("\n----------------------- Memory -----------------------")
    print(f"Cache misses:                           {cache_misses}      ({cache_misses_percent}% of total cache references)")
    print(f"Memory stores:                          {mem_stores}")
    print(f"Memory loads:                           {mem_loads}")
    print(f"Page faults:                            {page_faults}")

    print("\n----------------------- I/O -----------------------")
    print(f"Number of hardware interrupts:          {perf_stat_hw_interrupts_received_df['hw_interrupts'].item()}")

    print("\n----------------------- SCORES -----------------------")
    print(f"CPU time score (ideal):                 {((t_ideal/time)*100):.2f}")
    print(f"CPU time score (with mem stalls):       {((t_with_stalls/time)*100):.2f}")
    print(f"CPU utilization score:                  {(cpu_util_score):.2f}")
    print(f"Memory score:                           not yet implemented")
    # print(f"Memory score:                           {(100 - mem_util):.2f}")
    print()

if __name__ == "__main__":
   main(sys.argv[1:])