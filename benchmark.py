#!/usr/bin/python3
import pandas as pd
import numpy as np
import os
import sys
import subprocess
# from cpuinfo import get_cpu_info

def main(argv):
    path = f'/home/dwdd/thesis/output/{argv[0]}'
    n_cpus = int(argv[1])

    runtime_headers = []
    if (n_cpus == 2):
        runtime_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'App time src', 'App time observed all cpus', 'Tot time observed all cpus', 'App time observed CPU 0', 'App time observed CPU 1', 'Tot time observed CPU 0', 'Tot time observed CPU 1', 'Idle time CPU 0', 'Idle time CPU 1', 'Idle % CPU 0', 'Idle % CPU 1']
    elif (n_cpus == 4):
        runtime_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'App time src', 'App time observed all cpus', 'Tot time observed all cpus', 'App time observed CPU 0', 'App time observed CPU 1', 'App time observed CPU 2', 'App time observed CPU 3', 'Tot time observed CPU 0', 'Tot time observed CPU 1', 'Tot time observed CPU 2', 'Tot time observed CPU 3', 'Idle time CPU 0', 'Idle time CPU 1', 'Idle time CPU 2', 'Idle time CPU 3', 'Idle % CPU 0', 'Idle % CPU 1', 'Idle % CPU 2', 'Idle % CPU 3']
    runtime_df = pd.read_csv(f'{path}/runtimes.csv', verbose=True, names=runtime_headers)
    runtime_df.set_index('Run')

    perf_sched_summary_cpu0_headers = ['process', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    perf_sched_summary_cpu0_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu0.csv', verbose=True, names=perf_sched_summary_cpu0_headers)
    aggregation_functions = {'process': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    perf_sched_summary_cpu0_df_new = perf_sched_summary_cpu0_df.groupby(perf_sched_summary_cpu0_df['process'], as_index=False).aggregate(aggregation_functions)
    perf_sched_summary_cpu0_df_new = perf_sched_summary_cpu0_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

    perf_sched_summary_cpu1_headers = ['process', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    perf_sched_summary_cpu1_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu1.csv', verbose=True, names=perf_sched_summary_cpu1_headers)
    aggregation_functions = {'process': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    perf_sched_summary_cpu1_df_new = perf_sched_summary_cpu1_df.groupby(perf_sched_summary_cpu1_df['process'], as_index=False).aggregate(aggregation_functions)
    perf_sched_summary_cpu1_df_new = perf_sched_summary_cpu1_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

    # perf_sched_summary_cpu2_headers = ['process', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    # perf_sched_summary_cpu2_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu2.csv', verbose=True, names=perf_sched_summary_cpu2_headers)
    # aggregation_functions = {'process': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    # perf_sched_summary_cpu2_df_new = perf_sched_summary_cpu2_df.groupby(perf_sched_summary_cpu2_df['process'], as_index=False).aggregate(aggregation_functions)
    # perf_sched_summary_cpu2_df_new = perf_sched_summary_cpu2_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

    # perf_sched_summary_cpu3_headers = ['process', 'parent', 'sched-in', 'run-time', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations', 'NaN']
    # perf_sched_summary_cpu3_df = pd.read_csv(f'{path}/1/perf_sched_summary_cpu3.csv', verbose=True, names=perf_sched_summary_cpu3_headers)
    # aggregation_functions = {'process': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
    # perf_sched_summary_cpu3_df_new = perf_sched_summary_cpu3_df.groupby(perf_sched_summary_cpu3_df['process'], as_index=False).aggregate(aggregation_functions)
    # perf_sched_summary_cpu3_df_new = perf_sched_summary_cpu3_df_new.sort_values(by=['run-time', 'sched-in'], ascending=False)

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
    # cpu_freq = 2.6 * (10**9)

    perf_stat_ic_headers = []
    perf_stat_cycles_headers = []
    # perf_stat_page_faults_headers = []
    # perf_stat_L1_dcache_loads_headers = []
    # perf_stat_L1_dcache_load_misses_headers = []
    # perf_stat_LLC_loads_headers = []
    # perf_stat_LLC_load_misses_headers = []
    # perf_stat_L1_icache_load_misses = []

    if (n_cpus_used > 1):
        perf_stat_ic_headers = ['cpu','one','ic','unit','#', 'ipc', 'ins','per','cycle']
        perf_stat_cycles_headers = ['cpu', 'one', 'cycles','unit']
        perf_stat_ref_cycles_headers = ['cpu','one','ref-cycles','unit']
        perf_stat_mem_loads_headers = ['cpu','one','mem-loads','unit']
        perf_stat_mem_stores_headers = ['cpu','one','mem-stores','unit']
        perf_stat_cycle_stalls_total_headers = ['cpu','one','cycle-stalls','unit']
        perf_stat_cycle_stalls_mem_any_headers = ['cpu','one','cycle-stalls','unit']

        # perf_stat_page_faults_headers = ['cpu','page-faults','unit','#', 'freq', 'Ghz']
        # perf_stat_L1_dcache_loads_headers = ['cpu','cycles','unit','#', 'freq', 'Ghz','%']
        # perf_stat_L1_dcache_load_misses_headers = ['cpu', 'L1-dcache-load-misses','unit','#', 'percent', 'of', 'all', 'L1-dcache', 'accesses','%']
        # perf_stat_LLC_loads_headers = ['cpu', 'LLC-loads','unit','#', 'M/sec', 'Ghz','%']
        # perf_stat_LLC_load_misses_headers = ['cpu', 'LLC-load-misses','unit','#', 'percent', 'of', 'all', 'LL-cache', 'accesses','%']
        # perf_stat_L1_icache_load_misses = ['cpu','L1-icache-load-misses','unit','%']
    else:
        perf_stat_ic_headers = ['ic','unit','#', 'ipc', 'ins','per','cycle']
        perf_stat_cycles_headers = ['cycles','unit']
        perf_stat_ref_cycles_headers = ['ref-cycles','unit']
        perf_stat_mem_loads_headers = ['mem-loads','unit']
        perf_stat_mem_stores_headers = ['mem-stores','unit']
        perf_stat_cycle_stalls_total_headers = ['cycle-stalls','unit']
        perf_stat_cycle_stalls_mem_any_headers = ['cycle-stalls','unit']

        # perf_stat_page_faults_headers = ['page-faults','unit','#', 'freq', 'Ghz']
        # perf_stat_L1_dcache_loads_headers = ['L1-dcache-loads','unit','#', 'G/sec', 'Ghz','%']
        # perf_stat_L1_dcache_load_misses_headers = ['L1-dcache-load-misses','unit','#', 'percent', 'of', 'all', 'L1-dcache', 'accesses','%']
        # perf_stat_LLC_loads_headers = ['LLC-loads','unit','#', 'M/sec', 'Ghz','%']
        # perf_stat_LLC_load_misses_headers = ['LLC-load-misses','unit','#', 'percent', 'of', 'all', 'LL-cache', 'accesses','%']
        # perf_stat_L1_icache_load_misses = ['L1-icache-load-misses','unit','%']

    perf_stat_ic_df = pd.read_csv(f'{path}/1/perf_stat_ic.csv', verbose=True, names=perf_stat_ic_headers).drop(columns=['unit', '#', 'ins', 'per', 'cycle'])
    perf_stat_cycles_df = pd.read_csv(f'{path}/1/perf_stat_cycles.csv', verbose=True, names=perf_stat_cycles_headers).drop(columns=['unit'])
    perf_stat_ref_cycles_df = pd.read_csv(f'{path}/1/perf_stat_ref_cycles.csv', verbose=True, names=perf_stat_ref_cycles_headers).drop(columns=['unit'])
    perf_stat_mem_loads_df = pd.read_csv(f'{path}/1/perf_stat_mem_loads.csv', verbose=True, names=perf_stat_mem_loads_headers).drop(columns=['unit'])
    perf_stat_mem_stores_df = pd.read_csv(f'{path}/1/perf_stat_mem_stores.csv', verbose=True, names=perf_stat_mem_stores_headers).drop(columns=['unit'])
    perf_stat_cycle_stalls_total_df = pd.read_csv(f'{path}/1/perf_stat_cycle_stalls_total.csv', verbose=True, names=perf_stat_cycle_stalls_total_headers).drop(columns=['unit'])
    perf_stat_cycle_stalls_mem_any_df = pd.read_csv(f'{path}/1/perf_stat_cycle_stalls_mem_any.csv', verbose=True, names=perf_stat_cycle_stalls_mem_any_headers).drop(columns=['unit'])
    
    # perf_stat_page_faults_df = pd.read_csv(f'{path}/1/perf_stat_page_faults.csv', verbose=True, names=perf_stat_page_faults_headers).drop(columns=['unit', '#', 'Ghz'])
    # perf_stat_L1_dcache_loads_df = pd.read_csv(f'{path}/1/perf_stat_L1_dcache_loads.csv', verbose=True, names=perf_stat_L1_dcache_loads_headers).drop(columns=['unit', '#', 'Ghz'])
    # perf_stat_L1_dcache_load_misses_df = pd.read_csv(f'{path}/1/perf_stat_L1_dcache_load_misses.csv', verbose=True, names=perf_stat_L1_dcache_load_misses_headers).drop(columns=['unit', '#', 'percent', 'of', 'all', 'L1-dcache', 'accesses'])
    # perf_stat_LLC_loads_df = pd.read_csv(f'{path}/1/perf_stat_LLC_loads.csv', verbose=True, names=perf_stat_LLC_loads_headers).drop(columns=['unit', '#', 'Ghz'])
    # perf_stat_LLC_load_misses_df = pd.read_csv(f'{path}/1/perf_stat_LLC_load_misses.csv', verbose=True, names=perf_stat_LLC_load_misses_headers).drop(columns=['unit', '#', 'percent', 'of', 'all', 'LL-cache', 'accesses'])
    # perf_stat_L1_icache_load_misses_df = pd.read_csv(f'{path}/1/perf_stat_L1_icache_load_misses.csv', verbose=True, names=perf_stat_L1_icache_load_misses).drop(columns=['unit'])
 

    # perf_stat_headers = ['CPU','metric','unit','something','#','1.000','whacka','doodle','dooo']
    # perf_stat_df = pd.read_csv(f'{path}/1/perf_stat.csv', verbose=True, names=perf_stat_headers)

    # cpu_info = get_cpu_info()
    # print(cpu_info)

    # subprocess.run(["cat" "/proc/cpuinfo" | "grep", "Hz"])
    # subprocess.run(["lscpu"])
    

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

            ref_cycles = perf_stat_ref_cycles_df.loc[perf_stat_ic_df['cpu'] == f"S0-D0-C{i}", "ref-cycles"].item()
            ref_cycles = ''.join(ref_cycles.split())
            ref_cycles = int(ref_cycles)

            T_ref = 1 / (2.6 * 10**9)

            cycle_stalls_total = perf_stat_cycle_stalls_total_df.loc[perf_stat_ic_df['cpu'] == f"S0-D0-C{i}", "cycle-stalls"].item()
            cycle_stalls_total = ''.join(cycle_stalls_total.split())
            cycle_stalls_total = int(cycle_stalls_total)

            cycle_stalls_mem_any = perf_stat_cycle_stalls_mem_any_df.loc[perf_stat_ic_df['cpu'] == f"S0-D0-C{i}", "cycle-stalls"].item()
            cycle_stalls_mem_any = ''.join(cycle_stalls_mem_any.split())
            cycle_stalls_mem_any = int(cycle_stalls_mem_any)
        
            CTs_ideal[cpus[0]] = ic * (1/ipc) * Ts[cpus[0]]
            CTs_stalls[cpus[0]] = (cycles + cycle_stalls_total) * Ts[cpus[0]]



            print()
            print(f"CPU {i}")
            print(f"Theoretical time cycles:                    {cycles*Ts[cpus[0]]:.2f}")
            print(f"Theoretical time ref cycles:                {ref_cycles*T_ref:.2f}")
            print(f"Theoretical time cycles + stalls:           {(cycles + cycle_stalls_total)*Ts[cpus[0]]:.2f}")
            print(f"Theoretical time cycles + stalls mem:       {(cycles + cycle_stalls_mem_any)*Ts[cpus[0]]:.2f}")
            print(f"Theoretical time ref cycles + stalls:       {(ref_cycles*T_ref + cycle_stalls_total*Ts[cpus[0]]):.2f}")
            print(f"Theoretical time ref cycles + stalls mem:   {(ref_cycles*T_ref + cycle_stalls_mem_any*Ts[cpus[0]]):.2f}")
            print(f"Cycles:                                     {cycles}")
            print(f"Ref cycles:                                 {ref_cycles}")
            print(f"Stall cycles:                               {cycle_stalls_total}")
            print(f"Stall cycles / cycles:                      {cycle_stalls_total / cycles}")
            print(f"Stall cycles / ref cycles:                  {cycle_stalls_total / ref_cycles}")
            CT_TOT += CTs_ideal[cpus[0]]

    else:
        ic = perf_stat_ic_df["ic"].item()
        ic = ''.join(ic.split())
        ic = int(ic)

        cycles = perf_stat_cycles_df["cycles"].item()
        cycles = ''.join(cycles.split())
        cycles = int(cycles)

        ref_cycles = perf_stat_ref_cycles_df["ref-cycles"].item()
        ref_cycles = ''.join(ref_cycles.split())
        ref_cycles = int(ref_cycles)

        T_ref = 1 / (2.6 * 10**9)

        cycle_stalls_total = perf_stat_cycle_stalls_total_df["cycle-stalls"].item()
        cycle_stalls_total = ''.join(cycle_stalls_total.split())
        cycle_stalls_total = int(cycle_stalls_total)

        cycle_stalls_mem_any = perf_stat_cycle_stalls_mem_any_df["cycle-stalls"].item()
        cycle_stalls_mem_any = ''.join(cycle_stalls_mem_any.split())
        cycle_stalls_mem_any = int(cycle_stalls_mem_any)

        ipc = perf_stat_ic_df["ipc"].item()

        # print(f"ic {ic}")
        # print(f"ipc {ipc}")
        # print(f"cpi {1/ipc}")
        # print(f"freq {cpu_freqs[i]}")
        # print(f"T {Ts[i]}")
        # print()
    
        CTs_ideal[cpus[0]] = ic * (1/ipc) * Ts[cpus[0]]
        CTs_stalls[cpus[0]] = (cycles + cycle_stalls_total) * Ts[cpus[0]]

        ideal = (cycles - cycle_stalls_total)*Ts[cpus[0]]
        with_stalls = cycles*Ts[cpus[0]]
        slowdown = (time/ideal - 1) * 100

        app_runtime_on_cpu = perf_sched_summary_cpu1_df_new.loc[perf_sched_summary_cpu1_df_new['process'].str.contains("thesis_app"), "run-time"].item() / (10**3)

        print("\n-------- CPU --------")
        print(f"Theoretical CPU time:       {with_stalls:.2f}")
        print(f"Theoretical ideal CPU time: {ideal:.2f}")
        print(f"Measured CPU time:          {app_runtime_on_cpu:.2f} seconds")
        print(f"Wall time:                  {time:.2f} seconds")
        print(f"Diff time wall & ideal:     {(time-ideal):.2f} seconds")
        print(f"Slowdown:                   {slowdown:.2f}%")
        print(f"CPU freq:                   {cpu_freqs[0] / (10**9):.2f} GHz")
        print(f"CPU score:                  {((ideal/time)*100):.2f}")


        # CT_TOT += CTs_ideal[cpus[0]]
        # slowdown = (time/CT_TOT - 1) * 100
    
        
        # print(f"CT per CPU: {CTs_ideal}")
        # print(f"CT per CPU: {CTs_stalls}")
        # print()

        # print(f"Theoretical ideal time: {CT_TOT:.2f} seconds")
        # print(f"Diff time:              {(time-CT_TOT):.2f} seconds")
    
    # IC = 100
    # IPC = 2.5
    # CPI = 1 / IPC
    # CT = IC * CPI * T
    # t = 

    mem_total = 1
    mem_used = 1
    mem_util = mem_used / mem_total * 100
    print("\n-------- Memory usage --------")
    print(f"Memory score:         {(100 - mem_util):.2f}")


    # print("\n-------- Cache performance --------")

    # l1_size = 32 * (10**3)
    # l2_size = 256 * (10**3)
    # l3_size = 4096 * (10**3)
    # page_faults = perf_stat_page_faults_df['page-faults'].item()
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

    # print(f"\nobserved app runtime:         {'{0:.2f}'.format(row1_runtime['App time observed all cpus'].item())} seconds")
    # print(f"observed accumulated runtime: {'{0:.2f}'.format(row1_runtime['Tot time observed all cpus'].item())} seconds")
    print(f"CPU(s) used for application: {cpus}\n")
    for i, tot_cpu_util in enumerate(tot_cpu_utils):
        print(f"Active time CPU{i}: {'{0:.2f}'.format(row1_runtime[f'Tot time observed CPU {i}'].item())} seconds (100% of active, {'{0:.2f}'.format(tot_cpu_util)}% of total)")

    print()
    for i in range(n_cpus):
        print(f"App time CPU{i}:    {'{0:.2f}'.format(row1_runtime[f'App time observed CPU {i}'].item())} seconds ({'{0:.2f}'.format(app_cpu_utils[i])}% of active, {'{0:.2f}'.format(app_cpu_utils[i + n_cpus])}% of total)")
    # print(f"Mean app time of all used CPUs:  ({'{0:.2f}'.format(app_mean[0])}% util of active, {'{0:.2f}'.format(app_mean[1])}% of total)")
    
    print()  
    for i in range(n_cpus):
        print(f"idle time CPU{i}:   {'{0:.2f}'.format(row1_runtime[f'Idle time CPU {i}'].item())} seconds (0% of active, {row1_runtime[f'Idle % CPU {i}'].item()}% of total)")
    
    # print()  
    # for i in range(n_cpus):
    #     print(f"Total time CPU{i}:  {'{0:.2f}'.format(tot_plus_idle[i])} seconds")
    
    
    print("\nTop five processes used during app runtime:")
    print("\nCPU0")
    print(perf_sched_summary_cpu0_df_new.head())
    print("\nCPU1")
    print(perf_sched_summary_cpu1_df_new.head())
    # print("\nCPU2")
    # print(perf_sched_summary_cpu2_df_new.head())
    # print("\nCPU3")
    # print(perf_sched_summary_cpu3_df_new.head())
    print()



    # print("\n-------- Other stats --------")

    # vmstat_headers = ['Run', 'runnable processes', 'ps blckd wait for I/O', 'tot swpd used', 'free', 'buff', 'cache', 'mem swapped in/s', 'mem swapped out/s', 'from block device (KiB/s)', 'to block device (KiB/s)', 'interrupts/s', 'cxt switch/s', 'user time', 'system time', 'idle time', 'wait io time', 'stolen time', 'Date', 'Time']
    # vmstat_df = pd.read_csv(f'{path}/vmstat.csv', verbose=True, names=vmstat_headers)
    # vmstat_df['Time'] = pd.to_datetime(vmstat_df['Time'])
    # vmstat_df['seconds'] = vmstat_df['Time'].dt.strftime("%M:%S")
    # vmstat_df.set_index('seconds')
    # print(vmstat_df.head())

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

    # pidstat_headers = ['Run', 'Time', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'processand']
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