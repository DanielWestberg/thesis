#!/usr/bin/python3
import pandas as pd
import numpy as np
import os
import sys
import subprocess

def main(argv):
    path = f'/home/dwdd/thesis/output/{argv[0]}'
    n_cpus = int(argv[1])

    app_output_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'App time src',]
    runtime_df = pd.read_csv(f'{path}/app_outputs.csv', verbose=True, names=app_output_headers)

    runtime_headers = []
    if (n_cpus == 2):
        runtime_headers = ['Run', 'App time observed all cpus', 'Tot time observed all cpus', 'App time observed CPU 0', 'App time observed CPU 1', 'Tot time observed CPU 0', 'Tot time observed CPU 1', 'Idle time CPU 0', 'Idle time CPU 1', 'Idle % CPU 0', 'Idle % CPU 1']
    elif (n_cpus == 4):
        runtime_headers = ['Run', 'App time observed all cpus', 'Tot time observed all cpus', 'App time observed CPU 0', 'App time observed CPU 1', 'App time observed CPU 2', 'App time observed CPU 3', 'Tot time observed CPU 0', 'Tot time observed CPU 1', 'Tot time observed CPU 2', 'Tot time observed CPU 3', 'Idle time CPU 0', 'Idle time CPU 1', 'Idle time CPU 2', 'Idle time CPU 3', 'Idle % CPU 0', 'Idle % CPU 1', 'Idle % CPU 2', 'Idle % CPU 3']
    runtime_df = pd.read_csv(f'{path}/runtimes.csv', verbose=True, names=runtime_headers)
    runtime_df.set_index('Run')
    
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

    row1_runtime = runtime_df.iloc[[0]]
    row1_cpus = cpus_used_df.iloc[[0]]

    cpus = row1_cpus['CPUs_used'].item().replace("[", "").replace("]", "")

    cpus = cpus.split()
    for i, cpu in enumerate(cpus):
        cpus[i] = int(cpu[3:])

    n_cpus_used = len(cpus)


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

    if (n_cpus_used > 1):
        perf_stat_ic_headers = ['cpu','one','ic','unit','#', 'ipc', 'ins','per','cycle', 'multiplex']
        perf_stat_cycles_headers = ['cpu', 'one', 'cycles','unit', 'multiplex']
        perf_stat_mem_loads_headers = ['cpu','one','mem-loads','unit', 'multiplex']
        perf_stat_mem_stores_headers = ['cpu','one','mem-stores','unit', 'multiplex']
        perf_stat_cycle_stalls_total_headers = ['cpu','one','cycle-stalls','unit', 'multiplex']
        perf_stat_hw_interrupts_received_headers = ['cpu','one','interrupts','unit', 'multiplex']
        perf_stat_cache_misses_headers = ['cpu','one','cache-misses','unit','#','%', 'percentage', 'of' 'all', 'cache', 'refs', 'multiplex']
        perf_stat_branch_misses_headers = ['cpu','one','branch-misses','unit','#','%', 'of' 'all', 'branches', 'multiplex']
        perf_stat_page_faults_headers = ['cpu','one','page-faults','unit']

    else:
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


    # T = 1 / cpu_freq
    Ts = [1 / cpu_freqs[i] for i in range(n_cpus)]
    CTs_ideal = [0 for i in range(n_cpus)]
    CTs_stalls = [0 for i in range(n_cpus)]
    CT_TOT = 0
    if (n_cpus_used > 1):
        for i in range(n_cpus):
            ic = perf_stat_ic_df.loc[perf_stat_ic_df['cpu'] == f"S0-D0-C{i}", "ic"].item()
            ic = ''.join(ic.split())
            ic = int(ic)

            ipc = perf_stat_ic_df.loc[perf_stat_ic_df['cpu'] == f"S0-D0-C{i}", "ipc"].item()

            cycles = perf_stat_cycles_df.loc[perf_stat_ic_df['cpu'] == f"S0-D0-C{i}", "cycles"].item()
            cycles = ''.join(cycles.split())
            cycles = int(cycles)



            cycle_stalls_total = perf_stat_cycle_stalls_total_df.loc[perf_stat_ic_df['cpu'] == f"S0-D0-C{i}", "cycle-stalls"].item()
            cycle_stalls_total = ''.join(cycle_stalls_total.split())
            cycle_stalls_total = int(cycle_stalls_total)

        
            CTs_ideal[cpus[0]] = ic * (1/ipc) * Ts[cpus[0]]
            CTs_stalls[cpus[0]] = (cycles + cycle_stalls_total) * Ts[cpus[0]]

            print()
            print(f"CPU {i}")
            print(f"Theoretical time cycles:                    {cycles*Ts[cpus[0]]:.2f}")
            print(f"Theoretical time cycles + stalls:           {(cycles + cycle_stalls_total)*Ts[cpus[0]]:.2f}")
            print(f"Cycles:                                     {cycles}")
            print(f"Stall cycles:                               {cycle_stalls_total}")
            print(f"Stall cycles / cycles:                      {cycle_stalls_total / cycles}")
            CT_TOT += CTs_ideal[cpus[0]]

    else:
        ic = perf_stat_ic_df["ic"].item()
        ic = ''.join(ic.split())
        ic = int(ic)

        cycles = perf_stat_cycles_df["cycles"].item()
        cycles = ''.join(cycles.split())
        cycles = int(cycles)

        cycle_stalls_total = perf_stat_cycle_stalls_total_df["cycle-stalls"].item()
        cycle_stalls_total = ''.join(cycle_stalls_total.split())
        cycle_stalls_total = int(cycle_stalls_total)

        ipc = perf_stat_ic_df["ipc"].item()

        CTs_ideal[cpus[0]] = ic * (1/ipc) * Ts[cpus[0]]
        CTs_stalls[cpus[0]] = (cycles + cycle_stalls_total) * Ts[cpus[0]]

        t_ideal = (cycles - cycle_stalls_total)*Ts[cpus[0]]
        t_with_stalls = cycles*Ts[cpus[0]]
        slowdown = (time/t_ideal - 1) * 100

        app_runtime_on_cpu = perf_sched_summary_cpu_dfs_new[cpus[0]].loc[perf_sched_summary_cpu_dfs_new[cpus[0]]['process'].str.contains("thesis_app"), "run-time (ms)"].item() / (10**3)

        branch_misses = perf_stat_branch_misses_df.iloc[[0]]['branch-misses'].item()
        branch_misses_percent = perf_stat_branch_misses_df.iloc[[0]]['%'].item()
        
        print("\n-------- CPU --------")
        print(f"Theoretical CPU time incl. mem stalls:  {t_with_stalls:.2f} seconds")
        print(f"Theoretical ideal CPU time:             {t_ideal:.2f} seconds")
        print(f"Measured CPU time:                      {app_runtime_on_cpu:.2f} seconds")
        print(f"Wall time:                              {time:.2f} seconds")
        print(f"Diff time wall & ideal:                 {(time-t_ideal):.2f} seconds")
        print(f"Slowdown wall vs ideal:                 {slowdown:.2f}%")
        print(f"CPU freq:                               {cpu_freqs[0] / (10**9):.2f} GHz")
        print(f"Branch misses:                          {branch_misses}     ({branch_misses_percent} of total branch instructions)")


    
    mem_total = 1
    mem_used = 1
    mem_util = mem_used / mem_total * 100
    cache_misses = perf_stat_cache_misses_df.iloc[[0]]['cache-misses'].item()
    cache_misses_percent = perf_stat_cache_misses_df.iloc[[0]]['%'].item()
    mem_stores = perf_stat_mem_stores_df.iloc[[0]]['mem-stores'].item()
    mem_loads = perf_stat_mem_loads_df.iloc[[0]]['mem-loads'].item()
    page_faults = perf_stat_page_faults_df.iloc[[0]]['page-faults'].item()
    
    print("\n-------- Memory usage --------")
    print(f"Cache misses:                           {cache_misses}      ({cache_misses_percent}% of total cache references)")
    print(f"Memory stores:                          {mem_stores}")
    print(f"Memory loads:                           {mem_loads}")
    print(f"Page faults:                            {page_faults}")
    # l1_size = 32 * (10**3)
    # l2_size = 256 * (10**3)
    # l3_size = 4096 * (10**3)
    # page_faults = ''.join(page_faults.split())
    # page_faults = int(page_faults)
    # L1_dcache_loads = perf_stat_L1_dcache_loads_df['L1-dcache-loads'].item()
    # L1_dcache_loads = ''.join(L1_dcache_loads.split())
    # L1_dcache_loads = int(L1_dcache_loads)
    # L1_dcache_load_misses = perf_stat_L1_dcache_load_misses_df['L1-dcache-load-misses'].item()
    # L1_dcache_load_misses = ''.join(L1_dcache_load_misses.split())
    # L1_dcache_load_misses = int(L1_dcache_load_misses)
    # LLC_loads = perf_stat_LLC_loads_df['LLC-loads'].item()
    # LLC_loads = ''.join(LLC_loads.split())
    # LLC_loads = int(LLC_loads)
    # LLC_load_misses = perf_stat_LLC_load_misses_df['LLC-load-misses'].item()
    # LLC_load_misses = ''.join(LLC_load_misses.split())
    # LLC_load_misses = int(LLC_load_misses)
    # L1_icache_load_misses = perf_stat_L1_icache_load_misses_df['L1-icache-load-misses'].item()
    # L1_icache_load_misses = ''.join(L1_icache_load_misses.split())
    # L1_icache_load_misses = int(L1_icache_load_misses)

    # L1_dcache_accesses = L1_dcache_loads + L1_dcache_load_misses
    # LLC_accesses = LLC_loads + LLC_load_misses
    # h_L1d = L1_dcache_loads / L1_dcache_accesses
    # h_LLC = LLC_loads / LLC_accesses
    
    # # h_L1d = L1_dcache_loads / L1_dcache_loads
    # # h_LLC = LLC_loads / LLC_loads

    # print(f"page faults:            {page_faults}")
    # print(f"L1_dcache_loads:        {L1_dcache_loads}")
    # print(f"L1_dcache_load_misses:  {L1_dcache_load_misses}")
    # print(f"LLC_loads:              {LLC_loads}")
    # print(f"LLC_load_misses:        {LLC_load_misses}")
    # print(f"L1_icache_load_misses:  {L1_icache_load_misses}")
    # print(f"\nL1_dcache hit rate:     {(h_L1d*100):.2f}%")
    # print(f"LLC hit rate:           {(h_LLC*100):.2f}%")


    # cache_speed_mbs = 8738.89
    # disk_speed_mbs = 522.22
    

    # memory_accesses = 0.3(?) * ic (= n_hit + n_miss)???
    # h_miss = n_miss / (n_hit + n_miss)
    # p_miss = time to fetch block from next level of memory hierarchy + time to load into the cache
    # time to fetch block = latency to get first item + transfer time for each successive item (assume interleaved memory)
    # amat = t_hit + (h_miss * p_miss)
    # c_memory_stall =  memory_accesses x h_miss x p_miss

    # Memory Stall Clock cycles ( for write-back cache ) :
        # Memory Stall Clock-cycles = Read Stall-cycles + Write Stall-cycles = memory_accesses x h_miss x p_miss
        # Read-Write Cycle = ( Read/Programs ) X Read miss rate X read miss penalty
        # Write-Stall Cycle = ( Write/Programs ) X Write miss rate X Write miss penalty + Write Buffer Stalls

    # Memory Stall Clock cycles ( for write-through cache ) :
        # Assume write buffer stalls are negligible. Every access (read/write) treated similar.
        # Memory Stall Clock-cycles = ( Memory Access/Program ) X Miss Rate X Miss Penalties
        # Memory Stall Clock-cycles = (Instructions/Program ) X ( Misses/Instructions ) X Miss Penalties

    # UNKNOWNS:
        # p_miss



    print("\n-------- CPU utilization --------")

    tot_cpu_utils = [0 for i in range(n_cpus)]
    app_cpu_utils = [0 for i in range(n_cpus*2)]
    tot_plus_idle = [0 for i in range(n_cpus)]
    app_mean = [0, 0]
    for cpu in range(n_cpus):
        tot_plus_idle[cpu] = row1_runtime[f'Tot time observed CPU {cpu}'].item() + row1_runtime[f'Idle time CPU {cpu}'].item()
        tot_cpu_utils[cpu] = row1_runtime[f'Tot time observed CPU {cpu}'].item() / tot_plus_idle[cpu] * 100
        app_cpu_utils[cpu] = row1_runtime[f'App time observed CPU {cpu}'].item() / row1_runtime[f'Tot time observed CPU {cpu}'].item() * 100
        app_cpu_utils[cpu + n_cpus] = row1_runtime[f'App time observed CPU {cpu}'].item() / tot_plus_idle[cpu] * 100        
        if (cpu in cpus):
            app_mean[0] += app_cpu_utils[cpu]
            app_mean[1] += app_cpu_utils[cpu + n_cpus]
    
    app_mean[0] = app_mean[0] / len(cpus)
    app_mean[1] = app_mean[1] / len(cpus)

    print(f"CPU(s) used for application: {cpus}\n")
    for i, tot_cpu_util in enumerate(tot_cpu_utils):
        print(f"Active time CPU{i}: {'{0:.2f}'.format(row1_runtime[f'Tot time observed CPU {i}'].item())} seconds (100% of active, {'{0:.2f}'.format(tot_cpu_util)}% of total)")

    print()
    for i in range(n_cpus):
        print(f"App time CPU{i}:    {'{0:.2f}'.format(row1_runtime[f'App time observed CPU {i}'].item())} seconds ({'{0:.2f}'.format(app_cpu_utils[i])}% of active, {'{0:.2f}'.format(app_cpu_utils[i + n_cpus])}% of total)")
    
    print()  
    for i in range(n_cpus):
        print(f"idle time CPU{i}:   {'{0:.2f}'.format(row1_runtime[f'Idle time CPU {i}'].item())} seconds (0% of active, {row1_runtime[f'Idle % CPU {i}'].item()}% of total)")
        
    cpu_util_score = app_cpu_utils[cpus[0] + n_cpus] - row1_runtime[f'Idle % CPU {cpus[0]}'].item()

    print("\nTop five processes used during app runtime:")
    for i in range(n_cpus):
        print(f"\nCPU{i}")
        print(perf_sched_summary_cpu_dfs_new[i].head())
    print()

    print("\n-------- I/O --------")
    print(f"Number of hardware interrupts:          {perf_stat_hw_interrupts_received_df['hw_interrupts'].item()}")

    print("\n-------- SCORES --------")

    print(f"CPU time score (without mem stalls):    {((t_ideal/time)*100):.2f}")
    print(f"CPU time score (with mem stalls):       {((t_with_stalls/time)*100):.2f}")
    print(f"CPU utilization score:                  {(cpu_util_score):.2f}")
    print(f"Memory score:                           not yet implemented")
    # print(f"Memory score:                           {(100 - mem_util):.2f}")
    print()

if __name__ == "__main__":
   main(sys.argv[1:])