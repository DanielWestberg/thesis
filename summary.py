#!/usr/bin/python3
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import webbrowser
import texttable
import latextable
import os
import sys

def corr(wall_time_series, stall_time_series, ideal_time_series, pearson_corr_df, spearman_corr_df, params, df):
    for param in params:
        pearson_corr_df.at[param, 'Wall time'] = stats.pearsonr(wall_time_series, df[param])[0]            
        spearman_corr_df.at[param, 'Wall time'] = stats.spearmanr(wall_time_series, df[param])[0]
        pearson_corr_df.at[param, 'Stall time'] = stats.pearsonr(stall_time_series, df[param])[0]            
        spearman_corr_df.at[param, 'Stall time'] = stats.spearmanr(stall_time_series, df[param])[0]
        pearson_corr_df.at[param, 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, df[param])[0]            
        spearman_corr_df.at[param, 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, df[param])[0]
    return pearson_corr_df, spearman_corr_df

def main(argv):
    path = argv[0]
    if (path[-1] == "/"):
        path = path[:-1]
    all_iterations = True
    if (path[-22] == "o" and path[-17] == "t" and path[-7] == "_"):
        all_iterations = True
    elif (path[-2] == "/" or path[-3] == "/" or path[-4] == "/" or path[-5] == "/" or path[-6] == "/" or path[-7] == "/"):
        all_iterations = False
    else:
        print("Invalid input, exiting...")
        exit()
    process_name = argv[1]
    n_cpus = int(argv[2])
    plot_graphs = (argv[3] == "yes")
    verbose = (argv[4] == "yes")
    only_graphs = (argv[5] == "yes")
    save_graphs = (argv[6] == "yes")
    f = open(os.devnull, 'w')

    print("Loading stats, please wait...")
    old_stdout = sys.stdout
    
    if (all_iterations and not only_graphs):
        if os.path.exists(f"{path}/times.csv"):
            os.remove(f"{path}/times.csv")
        
        if os.path.exists(f"{path}/scores.csv"):
            os.remove(f"{path}/scores.csv")
        
        if os.path.exists(f"{path}/misses_percent.csv"):
            os.remove(f"{path}/misses_percent.csv")
        
        if os.path.exists(f"{path}/hw_interrupts.csv"):
            os.remove(f"{path}/hw_interrupts.csv")
        
        if os.path.exists(f"{path}/ipc.csv"):
            os.remove(f"{path}/ipc.csv")
        
        if os.path.exists(f"{path}/page_faults.csv"):
            os.remove(f"{path}/page_faults.csv")
        
        if os.path.exists(f"{path}/mem_loads_stores.csv"):
            os.remove(f"{path}/mem_loads_stores.csv")
        
        for i in range(n_cpus):
            if os.path.exists(f"{path}/top_five_processes_cpu{i}.csv"):
                os.remove(f"{path}/top_five_processes_cpu{i}.csv")

        for run_iter, _ in enumerate(os.walk(path)):
            sys.stdout = f
            if (run_iter == 0):
                continue

            # Read CSV files
            app_output_headers = ['Run', 'Memory time', 'Disk time', 'Calc time', 'App time src']
            app_output_df = pd.read_csv(f'{path}/app_outputs.csv', verbose=True, names=app_output_headers)

            idle_time_headers = ['test']
            idle_percent_headers = ['test']
            runtime_app_cpu_headers = []
            runtime_tot_cpu_headers = []
            runtime_app_cpu_df = {}
            runtime_tot_cpu_df = {}

            for cpu in range(n_cpus):
                runtime_app_cpu_headers.append([f"test"])
                runtime_tot_cpu_headers.append([f"test"])
                runtime_app_cpu_df[f'cpu {cpu}'] = pd.read_csv(f'{path}/{run_iter}/runtime_app_cpu{cpu}.csv', verbose=True, names=runtime_app_cpu_headers[cpu], on_bad_lines='skip')
                runtime_tot_cpu_df[f'cpu {cpu}'] = pd.read_csv(f'{path}/{run_iter}/runtime_tot_cpu{cpu}.csv', verbose=True, names=runtime_tot_cpu_headers[cpu], on_bad_lines='skip')

            idle_time_df = pd.read_csv(f'{path}/{run_iter}/idle_time.csv', verbose=True, names=idle_time_headers)
            idle_percent_df = pd.read_csv(f'{path}/{run_iter}/idle_percent.csv', verbose=True, names=idle_percent_headers)
                
            perf_sched_summary_cpu_headers = ['process', 'parent', 'sched-in', 'run-time (ms)', 'min-run', 'avg-run', 'max-run', 'stddev' ,'migrations']
            perf_sched_summary_cpu_dfs = []
            perf_sched_summary_cpu_dfs_new = []
            for i in range(n_cpus):
                perf_sched_summary_cpu_dfs.append(pd.read_csv(f'{path}/{run_iter}/perf_sched_summary_cpu{i}.csv', verbose=True, names=perf_sched_summary_cpu_headers))
                aggregation_functions = {'process': 'first', 'parent': 'first', 'sched-in': 'sum', 'run-time (ms)': 'sum', 'min-run': 'min', 'avg-run': 'mean', 'max-run': 'max', 'stddev': 'mean'}
                perf_sched_summary_cpu_dfs_new.append(perf_sched_summary_cpu_dfs[i].groupby(perf_sched_summary_cpu_dfs[i]['process'], as_index=False).aggregate(aggregation_functions))
                perf_sched_summary_cpu_dfs_new[i] = perf_sched_summary_cpu_dfs_new[i].sort_values(by=['run-time (ms)', 'sched-in'], ascending=False)
                perf_sched_summary_cpu_dfs_new[i]['Run'] = run_iter

            pidstat_mem_df = []
            if (os.path.isfile(f'{path}/pidstat_mem.csv')):
                pidstat_mem_headers = ['Run', 'Time', 'UID', 'PID', 'minflt/s', 'majflt/s', 'VSZ', 'RSS', '"%"MEM', 'Command']
                pidstat_mem_df = pd.read_csv(f'{path}/pidstat_mem.csv', verbose=True, names=pidstat_mem_headers)
                pidstat_mem_df['Time'] = pd.to_datetime(pidstat_mem_df['Time'])
                pidstat_mem_df['seconds'] = pidstat_mem_df['Time'].dt.strftime("%H:%M:%S")
                pidstat_mem_df.set_index('seconds')

            cpus_used_headers = ['Run', 'CPUs_used']
            cpus_used_df = pd.read_csv(f'{path}/cpus_used.csv', verbose=True, names=cpus_used_headers)

            wall_time = 0
            with open(f'{path}/{run_iter}/perf_stat_time.csv', 'r') as perf_stat_time:
                wall_time = perf_stat_time.read()
            wall_time = float(wall_time)

            cpu_freqs = [0 for i in range(n_cpus)]
            with open(f'{path}/{run_iter}/cpu_freq.csv', 'r') as cpu_freq_file:
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

            perf_stat_ic_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_ic.csv', verbose=True, names=perf_stat_ic_headers).drop(columns=['unit', '#', 'ins', 'per', 'cycle'])
            perf_stat_cycles_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_cycles.csv', verbose=True, names=perf_stat_cycles_headers).drop(columns=['unit'])
            perf_stat_mem_loads_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_mem_loads.csv', verbose=True, names=perf_stat_mem_loads_headers).drop(columns=['unit'])
            perf_stat_mem_stores_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_mem_stores.csv', verbose=True, names=perf_stat_mem_stores_headers).drop(columns=['unit'])
            perf_stat_cycle_stalls_total_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_cycle_stalls_total.csv', verbose=True, names=perf_stat_cycle_stalls_total_headers).drop(columns=['unit'])
            perf_stat_hw_interrupts_received_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_hw_interrupts_received.csv', verbose=True, names=perf_stat_hw_interrupts_received_headers).drop(columns=['unit'])
            perf_stat_cache_misses_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_cache_misses.csv', verbose=True, names=perf_stat_cache_misses_headers).drop(columns=['unit','#','percentage', 'of', 'all', 'cache', 'refs'])
            perf_stat_branch_misses_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_branch_misses.csv', verbose=True, names=perf_stat_branch_misses_headers).drop(columns=['unit','#','of', 'all', 'branches'])
            perf_stat_page_faults_df = pd.read_csv(f'{path}/{run_iter}/perf_stat_page_faults.csv', verbose=True, names=perf_stat_page_faults_headers).drop(columns=['unit'])


            # Get CPUs used
            row1_cpus = cpus_used_df.iloc[[run_iter-1]]

            cpus_used = row1_cpus['CPUs_used'].item().replace("[", "").replace("]", "")

            cpus_used = cpus_used.split()
            for i, cpu in enumerate(cpus_used):
                cpus_used[i] = int(cpu[3:])

            # Declare empty variables
            Ts = [1 / cpu_freqs[i] for i in range(n_cpus)]

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
            t_ideal = (cycles - cycle_stalls_total)*Ts[0]
            t_stall = cycle_stalls_total*Ts[0]
            t_with_stalls = cycles*Ts[0]
            slowdown = (wall_time/t_ideal - 1) * 100

            tools_dfs = []
            tools = "pidstat|perf|vmstat|mpstat|iostat|sar"

            tools_cpu_time = [0 for i in range(n_cpus)]
            tools_cpu_utils = [0 for i in range(n_cpus*2)]
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
                if (cpu in cpus_used and app_cpu_utils[cpu] == 0.00):
                    cpus_used.remove(cpu)
                if (cpu in cpus_used):
                    app_mean[0] += app_cpu_utils[cpu]
                    app_mean[1] += app_cpu_utils[cpu + n_cpus]
                tot_runtime_all_cpus += tot_runtime_app_cpu[f'cpu {cpu}']
                tools_dfs.append(perf_sched_summary_cpu_dfs_new[cpu][perf_sched_summary_cpu_dfs_new[cpu]['process'].str.contains(tools)==True])
                tools_cpu_time[cpu] = tools_dfs[cpu]['run-time (ms)'].sum() / (10**3)
                tools_cpu_utils[cpu] = tools_cpu_time[cpu] / runtime_tot_cpu_df[f'cpu {cpu}'].iloc[[0]]['test'].item() * 100
                tools_cpu_utils[cpu + n_cpus] = tools_cpu_time[cpu] / tot_plus_idle[cpu] * 100        
            
            app_mean[0] = app_mean[0] / len(cpus_used)
            app_mean[1] = app_mean[1] / len(cpus_used)

            # Branch misses
            branch_misses = perf_stat_branch_misses_df.iloc[[0]]['branch-misses'].item()
            branch_misses_percent = perf_stat_branch_misses_df.iloc[[0]]['%'].item().replace('%', '')

            # Memory
            mem_total = 1
            mem_used = 1
            mem_util = mem_used / mem_total * 100
            cache_misses = perf_stat_cache_misses_df.iloc[[0]]['cache-misses'].item()
            cache_misses_percent = perf_stat_cache_misses_df.iloc[[0]]['%'].item()
            mem_stores = perf_stat_mem_stores_df.iloc[[0]]['mem-stores'].item()
            mem_loads = perf_stat_mem_loads_df.iloc[[0]]['mem-loads'].item()
            page_faults = perf_stat_page_faults_df.iloc[[0]]['page-faults'].item()
            
            ################# SUMMARY ONE ITERATION #################
            sys.stdout = old_stdout
            
            if os.path.exists(f"{path}/{run_iter}/summary.txt"):
                os.remove(f"{path}/{run_iter}/summary.txt")

            summary_file = open(f'{path}/{run_iter}/summary.txt', 'a')

            print(f"\n###################### RUN {run_iter} ######################", file = summary_file)

            print("\n----------------------- CPU utilization -----------------------", file = summary_file)

            print(f"CPU(s) used for application: {cpus_used}\n", file = summary_file)
            for i, tot_cpu_util in enumerate(tot_cpu_utils):
                print(f"Active time CPU{i}: {'{0:.2f}'.format(runtime_tot_cpu_df[f'cpu {i}'].iloc[[0]]['test'].item())} seconds (100% of active, {'{0:.2f}'.format(tot_cpu_util)}% of total)", file = summary_file)
            
            print("", file = summary_file)
            for i in range(n_cpus):
                print(f"App time CPU{i}:    {'{0:.2f}'.format(tot_runtime_app_cpu[f'cpu {i}'])} seconds ({'{0:.2f}'.format(app_cpu_utils[i])}% of active, {'{0:.2f}'.format(app_cpu_utils[i + n_cpus])}% of total)", file = summary_file)
            
            print("", file = summary_file)
            for i in range(n_cpus):
                print(f"Tools time CPU{i}:  {'{0:.2f}'.format(tools_cpu_time[i])} seconds ({'{0:.2f}'.format(tools_cpu_utils[i])}% of active, {'{0:.2f}'.format(tools_cpu_utils[i + n_cpus])}% of total)", file = summary_file)
            
            print("", file = summary_file)
            for i in range(n_cpus):
                print(f"idle time CPU{i}:   {'{0:.2f}'.format(idle_time_df.iloc[[i]]['test'].item())} seconds (0% of active, {idle_percent_df.iloc[[i]]['test'].item()}% of total)", file = summary_file)
            
            cpu_util_score = 0
            for cpu in cpus_used:
                cpu_util_score += app_cpu_utils[cpu + n_cpus]
                # cpu_util_score += app_cpu_utils[cpu + n_cpus] - idle_percent_df.iloc[[cpu]]['test'].item()            
            cpu_util_score = cpu_util_score / len(cpus_used)

            idle_score = 0
            for cpu in cpus_used:
                idle_score += idle_percent_df.iloc[[cpu]]['test'].item()
            idle_score = idle_score / len(cpus_used)


            print("\n\nTop five processes with the highest runtime during app runtime:", file = summary_file)
            for i in range(n_cpus):
                print(f"\nCPU{i}", file = summary_file)
                print(perf_sched_summary_cpu_dfs_new[i].head(), file = summary_file)
            print("", file = summary_file)

            print("\n----------------------- CPU time -----------------------", file = summary_file)
            print(f"Theoretical ideal CPU time:                 {t_ideal:.2f} seconds", file = summary_file)
            print(f"Stall time:                                 {t_stall:.2f} seconds", file = summary_file)
            print(f"Theoretical CPU time incl. stall cycles:    {t_with_stalls:.2f} seconds", file = summary_file)
            print(f"Actual CPU time:                            {tot_runtime_all_cpus:.2f} seconds", file = summary_file)
            print(f"Wall time:                                  {wall_time:.2f} seconds", file = summary_file)
            print(f"Diff time wall & ideal:                     {(wall_time-t_ideal):.2f} seconds", file = summary_file)
            print(f"Slowdown wall vs ideal:                     {slowdown:.2f}%", file = summary_file)
            print(f"CPU freq:                                   {cpu_freqs[0] / (10**9):.2f} GHz", file = summary_file)
            print(f"IPC:                                        {ipc}", file = summary_file)
            print(f"Branch misses:                              {branch_misses}     ({branch_misses_percent}% of total branch instructions)", file = summary_file)
            
            print("\n----------------------- Memory -----------------------", file = summary_file)
            print(f"Cache misses:                           {cache_misses}      ({cache_misses_percent}% of total cache references)", file = summary_file)
            print(f"Memory stores:                          {mem_stores}", file = summary_file)
            print(f"Memory loads:                           {mem_loads}", file = summary_file)
            print(f"Page faults:                            {page_faults}", file = summary_file)

            print("\n----------------------- I/O -----------------------", file = summary_file)
            print(f"Number of hardware interrupts:          {perf_stat_hw_interrupts_received_df['hw_interrupts'].item()}", file = summary_file)

            print("\n----------------------- SCORES -----------------------", file = summary_file)
            print(f"Score (ideal/wall):            {((t_ideal/wall_time)*100):.2f}   (0 = bad, lots of stalls and noise. 100 = good, no stall cycles or noise)", file = summary_file)
            # print(f"CPU time score (ideal/actual):          {((t_ideal/tot_runtime_all_cpus)*100):.2f}   (0 = bad, lots of stall cycles. 100 = good, no stall cycles)", file = summary_file)
            # print(f"CPU time score (incl. stalls/wall):     {((t_with_stalls/wall_time)*100):.2f}   (0 = bad, lots of noise. 100 = good, no noise)", file = summary_file)
            # print(f"CPU time score (incl. stalls/actual):   {((t_with_stalls/tot_runtime_all_cpus)*100):.2f}   (0 = bad, lots of noise. 100 = good, no noise)", file = summary_file)
            # print(f"CPU time score (actual/wall):           {((tot_runtime_all_cpus/wall_time)*100):.2f}   (0 = bad, lots of noise. 100 = good, no noise)", file = summary_file)
            # print(f"CPU utilization score:                  {(cpu_util_score):.2f}   (0 = bad, CPU idle or used for other processes. 100 = good, CPU only used for app)", file = summary_file)
            # print(f"CPU idle score:                         {(idle_score):.2f}   (0 = good, CPU not idle. 100 = bad, CPU idle)", file = summary_file)
            # print(f"Memory score:                           not yet implemented", file = summary_file)
            # print(f"Memory score:                           {(100 - mem_util):.2f}", file = summary_file)
            print("", file = summary_file)

            summary_file.close()

            times_file = open(f"{path}/times.csv", "a")
            times_file.write(f"{run_iter},{t_ideal},{t_stall},{t_with_stalls},{tot_runtime_all_cpus},{wall_time}\n")
            times_file.close()

            scores_file = open(f"{path}/scores.csv", "a")
            # scores_file.write(f"{run_iter},{(t_ideal/wall_time)*100},{(t_ideal/tot_runtime_all_cpus)*100},{(t_with_stalls/wall_time)*100},{(t_with_stalls/tot_runtime_all_cpus)*100},{(tot_runtime_all_cpus/wall_time)*100},{cpu_util_score},{idle_score}\n")
            # scores_file.write(f"{run_iter},{(t_ideal/tot_runtime_all_cpus)*100},{(tot_runtime_all_cpus/wall_time)*100},{cpu_util_score},{idle_score}\n")
            scores_file.write(f"{run_iter},{(t_ideal/wall_time)*100},{cpu_util_score},{idle_score}\n")
            scores_file.close()
            
            misses_percent_file = open(f"{path}/misses_percent.csv", "a")
            misses_percent_file.write(f"{run_iter},{cache_misses_percent},{branch_misses_percent}\n")
            misses_percent_file.close()
            
            hw_interrupts_file = open(f"{path}/hw_interrupts.csv", "a")
            hw_interrupts_file.write(f"{run_iter},{int(''.join(perf_stat_hw_interrupts_received_df['hw_interrupts'].item().split()))}\n")
            hw_interrupts_file.close()
            
            ipc_file = open(f"{path}/ipc.csv", "a")
            ipc_file.write(f"{run_iter},{ipc}\n")
            ipc_file.close()

            page_faults_file = open(f"{path}/page_faults.csv", "a")
            page_faults_file.write(f"{run_iter},{page_faults}\n")
            page_faults_file.close()

            mem_loads_stores_file = open(f"{path}/mem_loads_stores.csv", "a")
            mem_loads_stores_file.write(f"{run_iter},{mem_loads},{mem_stores}\n")
            mem_loads_stores_file.close()

            for i in range(n_cpus):
                top_five_processes_file = open(f"{path}/top_five_processes_cpu{i}.csv", "a")
                for j in range(3):
                    top_five_processes_file.write(f"{run_iter},{i},{perf_sched_summary_cpu_dfs_new[i].iloc[j]['process'].split('[')[0]},{perf_sched_summary_cpu_dfs_new[i].iloc[j]['run-time (ms)']}\n")
                top_five_processes_file.close()
    
    if (all_iterations):
        summary_table = texttable.Texttable()
        summary_table.set_cols_align(["c","c","c","c","c","c","c"])
        summary_table.set_cols_valign(["m","m","m","m","m","m","m"])
        pearson_table = texttable.Texttable()
        pearson_table.set_cols_align(["c","c","c","c"])
        pearson_table.set_cols_valign(["m","m","m","m"])
        spearman_table = texttable.Texttable()
        spearman_table.set_cols_align(["c","c","c","c"])
        spearman_table.set_cols_valign(["m","m","m","m"])
        rows = [["Value", "Mean", "Min", "Max", "Std", "Worst iteration", "Best iteration"]]
        rows_pearson = [["Param", "Wall time", "Stall time", "Ideal time"]]
        rows_spearman = [["Param", "Wall time", "Stall time", "Ideal time"]]

        params = ['Wall time', 'Ideal CPU time', 'Stall time', 'Actual CPU time', 'App mem %', 'App CPU %', 'Idle CPU',\
                  'Cache misses %', 'Branch misses %', 'HW interrupts', 'IPC', 'Page faults', 'Mem loads', 'Mem stores', \
                  'kbmemfree', 'kbavail', 'kbmemused', '"%"memused', 'kbbuffers', 'kbcached', 'kbcommit', '"%"commit', \
                  'kbactive', 'kbinact', 'kbdirty', 'kbanonpg', 'kbslab', 'kbkstack', 'kbpgtbl', 'kbvmused']
        pearson_corr_df = pd.DataFrame(index=params, columns=['Wall time'])
        pearson_corr_df = pearson_corr_df.fillna(np.nan)
        spearman_corr_df = pearson_corr_df.copy()
        wall_time_series = []
        stall_time_series = []
        ideal_time_series = []

        ################# SUMMARY ALL ITERATIONS #################
        # print(f"\n###################### SUMMARY ######################\n")

        if (os.path.isfile(f'{path}/times.csv')):
            # print("\n----------------------- TIMES -----------------------")
            times_headers = ['Run', 'Ideal CPU time', 'Stall time', 'Ideal CPU time with stall cycles', 'Actual CPU time', 'Wall time']
            times_df = pd.read_csv(f'{path}/times.csv', names=times_headers)
            # print(times_df[['Ideal CPU time', 'Stall time', 'Actual CPU time', 'Wall time']].describe().applymap('{:,.2f}'.format))
            # print()
            # print(f"Run iteration with highest ideal CPU time:  {times_df.loc[times_df['Ideal CPU time'] == times_df['Ideal CPU time'].max(), 'Run'].iloc[0]}")
            # print(f"Run iteration with highest stall time:      {times_df.loc[times_df['Stall time'] == times_df['Stall time'].max(), 'Run'].iloc[0]}")
            # print(f"Run iteration with highest actual CPU time: {times_df.loc[times_df['Actual CPU time'] == times_df['Actual CPU time'].max(), 'Run'].iloc[0]}")
            # print(f"Run iteration with highest wall time:       {times_df.loc[times_df['Wall time'] == times_df['Wall time'].max(), 'Run'].iloc[0]}")
            # print()

            wall_time_series = times_df['Wall time']
            stall_time_series = times_df['Stall time']
            ideal_time_series = times_df['Ideal CPU time']

            pearson_corr_df.at['Wall time', 'Wall time'] = stats.pearsonr(wall_time_series, times_df['Wall time'])[0]
            pearson_corr_df.at['Ideal CPU time', 'Wall time'] = stats.pearsonr(wall_time_series, times_df['Ideal CPU time'])[0]
            pearson_corr_df.at['Stall time', 'Wall time'] = stats.pearsonr(wall_time_series, times_df['Stall time'])[0]
            pearson_corr_df.at['Actual CPU time', 'Wall time'] = stats.pearsonr(wall_time_series, times_df['Actual CPU time'])[0]
            spearman_corr_df.at['Wall time', 'Wall time'] = stats.spearmanr(wall_time_series, times_df['Wall time'])[0]
            spearman_corr_df.at['Ideal CPU time', 'Wall time'] = stats.spearmanr(wall_time_series, times_df['Ideal CPU time'])[0]
            spearman_corr_df.at['Stall time', 'Wall time'] = stats.spearmanr(wall_time_series, times_df['Stall time'])[0]
            spearman_corr_df.at['Actual CPU time', 'Wall time'] = stats.spearmanr(wall_time_series, times_df['Actual CPU time'])[0]
            
            pearson_corr_df.at['Wall time', 'Stall time'] = stats.pearsonr(stall_time_series, times_df['Wall time'])[0]
            pearson_corr_df.at['Ideal CPU time', 'Stall time'] = stats.pearsonr(stall_time_series, times_df['Ideal CPU time'])[0]
            pearson_corr_df.at['Stall time', 'Stall time'] = stats.pearsonr(stall_time_series, times_df['Stall time'])[0]
            pearson_corr_df.at['Actual CPU time', 'Stall time'] = stats.pearsonr(stall_time_series, times_df['Actual CPU time'])[0]
            spearman_corr_df.at['Wall time', 'Stall time'] = stats.spearmanr(stall_time_series, times_df['Wall time'])[0]
            spearman_corr_df.at['Ideal CPU time', 'Stall time'] = stats.spearmanr(stall_time_series, times_df['Ideal CPU time'])[0]
            spearman_corr_df.at['Stall time', 'Stall time'] = stats.spearmanr(stall_time_series, times_df['Stall time'])[0]
            spearman_corr_df.at['Actual CPU time', 'Stall time'] = stats.spearmanr(stall_time_series, times_df['Actual CPU time'])[0]
            
            pearson_corr_df.at['Wall time', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, times_df['Wall time'])[0]
            pearson_corr_df.at['Ideal CPU time', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, times_df['Ideal CPU time'])[0]
            pearson_corr_df.at['Stall time', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, times_df['Stall time'])[0]
            pearson_corr_df.at['Actual CPU time', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, times_df['Actual CPU time'])[0]
            spearman_corr_df.at['Wall time', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, times_df['Wall time'])[0]
            spearman_corr_df.at['Ideal CPU time', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, times_df['Ideal CPU time'])[0]
            spearman_corr_df.at['Stall time', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, times_df['Stall time'])[0]
            spearman_corr_df.at['Actual CPU time', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, times_df['Actual CPU time'])[0]

            rows.append(["Wall time", times_df['Wall time'].mean(), times_df['Wall time'].min(), times_df['Wall time'].max(), times_df['Wall time'].std(), times_df.loc[times_df['Wall time'] == times_df['Wall time'].max(), 'Run'].iloc[0], times_df.loc[times_df['Wall time'] == times_df['Wall time'].min(), 'Run'].iloc[0]])
            rows.append(["Ideal CPU time", times_df['Ideal CPU time'].mean(), times_df['Ideal CPU time'].min(), times_df['Ideal CPU time'].max(), times_df['Ideal CPU time'].std(), times_df.loc[times_df['Ideal CPU time'] == times_df['Ideal CPU time'].max(), 'Run'].iloc[0], times_df.loc[times_df['Ideal CPU time'] == times_df['Ideal CPU time'].min(), 'Run'].iloc[0]])
            rows.append(["Actual CPU time", times_df['Actual CPU time'].mean(), times_df['Actual CPU time'].min(), times_df['Actual CPU time'].max(), times_df['Actual CPU time'].std(), times_df.loc[times_df['Actual CPU time'] == times_df['Actual CPU time'].max(), 'Run'].iloc[0], times_df.loc[times_df['Actual CPU time'] == times_df['Actual CPU time'].min(), 'Run'].iloc[0]])
            rows.append(["Stall time", times_df['Stall time'].mean(), times_df['Stall time'].min(), times_df['Stall time'].max(), times_df['Stall time'].std(), times_df.loc[times_df['Stall time'] == times_df['Stall time'].max(), 'Run'].iloc[0], times_df.loc[times_df['Stall time'] == times_df['Stall time'].min(), 'Run'].iloc[0]])
        
        # if (os.path.isfile(f'{path}/scores.csv')):
            # print("\n----------------------- SCORE -----------------------")
            # scores_headers = ['Run', 'Score', 'CPU utilization score', 'CPU idle score']
            # scores_df = pd.read_csv(f'{path}/scores.csv', names=scores_headers)
            # print(scores_df[['Score']].describe().applymap('{:,.2f}'.format))
            # print()
            # print(f"Run iteration with the lowest score: {scores_df.loc[scores_df['Score'] == scores_df['Score'].min(), 'Run'].iloc[0]}")
            # print()
            # pearson_corr_df.at['Score', 'Wall time'] = stats.pearsonr(wall_time_series, scores_df['Score'])[0]
            # spearman_corr_df.at['Score', 'Wall time'] = stats.spearmanr(wall_time_series, scores_df['Score'])[0]
            
            # pearson_corr_df.at['Score', 'Stall time'] = stats.pearsonr(stall_time_series, scores_df['Score'])[0]
            # spearman_corr_df.at['Score', 'Stall time'] = stats.spearmanr(stall_time_series, scores_df['Score'])[0]
            
            # pearson_corr_df.at['Score', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, scores_df['Score'])[0]
            # spearman_corr_df.at['Score', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, scores_df['Score'])[0]

            # rows.append(["Score", scores_df['Score'].mean(), scores_df['Score'].min(), scores_df['Score'].max(), scores_df['Score'].std(), scores_df.loc[scores_df['Score'] == scores_df['Score'].min(), 'Run'].iloc[0], scores_df.loc[scores_df['Score'] == scores_df['Score'].max(), 'Run'].iloc[0]])

        if (os.path.isfile(f'{path}/scores.csv')):
            # print("\n----------------------- CPU UTILIZATION -----------------------")
            scores_headers = ['Run', 'CPU time score', 'App CPU utilization', 'Idle CPU']
            scores_df = pd.read_csv(f'{path}/scores.csv', names=scores_headers)
            # print(scores_df[['App CPU utilization', 'Idle CPU']].describe().applymap('{:,.2f}'.format))
            # print()
            # print(f"Run iteration with the lowest app CPU utilization:  {scores_df.loc[scores_df['App CPU utilization'] == scores_df['App CPU utilization'].min(), 'Run'].iloc[0]}")
            # print(f"Run iteration with the highest idle CPU percentage: {scores_df.loc[scores_df['Idle CPU'] == scores_df['Idle CPU'].max(), 'Run'].iloc[0]}")
            # print()

            # pearson_corr_df.at['App CPU utilization', 'Wall time'] = stats.pearsonr(wall_time_series, scores_df['App CPU utilization'])[0]
            # spearman_corr_df.at['App CPU utilization', 'Wall time'] = stats.spearmanr(wall_time_series, scores_df['App CPU utilization'])[0]
            pearson_corr_df.at['Idle CPU', 'Wall time'] = stats.pearsonr(wall_time_series, scores_df['Idle CPU'])[0]
            spearman_corr_df.at['Idle CPU', 'Wall time'] = stats.spearmanr(wall_time_series, scores_df['Idle CPU'])[0]
            
            pearson_corr_df.at['Idle CPU', 'Stall time'] = stats.pearsonr(stall_time_series, scores_df['Idle CPU'])[0]
            spearman_corr_df.at['Idle CPU', 'Stall time'] = stats.spearmanr(stall_time_series, scores_df['Idle CPU'])[0]
            
            pearson_corr_df.at['Idle CPU', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, scores_df['Idle CPU'])[0]
            spearman_corr_df.at['Idle CPU', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, scores_df['Idle CPU'])[0]

            rows.append(["App CPU util", scores_df['App CPU utilization'].mean(), scores_df['App CPU utilization'].min(), scores_df['App CPU utilization'].max(), scores_df['App CPU utilization'].std(), scores_df.loc[scores_df['App CPU utilization'] == scores_df['App CPU utilization'].min(), 'Run'].iloc[0], scores_df.loc[scores_df['App CPU utilization'] == scores_df['App CPU utilization'].max(), 'Run'].iloc[0]])
            rows.append(["Idle CPU util", scores_df['Idle CPU'].mean(), scores_df['Idle CPU'].min(), scores_df['Idle CPU'].max(), scores_df['Idle CPU'].std(), scores_df.loc[scores_df['Idle CPU'] == scores_df['Idle CPU'].max(), 'Run'].iloc[0], scores_df.loc[scores_df['Idle CPU'] == scores_df['Idle CPU'].min(), 'Run'].iloc[0]])
        
        if (os.path.isfile(f'{path}/misses_percent.csv')):
            # print("\n----------------------- MISS % -----------------------")
            misses_percent_headers = ['Run', 'Cache misses %', 'Branch misses %']
            misses_percent_df = pd.read_csv(f'{path}/misses_percent.csv', names=misses_percent_headers)
            # print(misses_percent_df[['Cache misses %', 'Branch misses %']].describe().applymap('{:,.2f}'.format))
            # print()
            # print(f"Run iteration with the highest cache miss %:    {misses_percent_df.loc[misses_percent_df['Cache misses %'] == misses_percent_df['Cache misses %'].max(), 'Run'].iloc[0]}")
            # print(f"Run iteration with the highest branch miss %:   {misses_percent_df.loc[misses_percent_df['Branch misses %'] == misses_percent_df['Branch misses %'].max(), 'Run'].iloc[0]}")
            # print()

            pearson_corr_df.at['Cache misses %', 'Wall time'] = stats.pearsonr(wall_time_series, misses_percent_df['Cache misses %'])[0]
            pearson_corr_df.at['Branch misses %', 'Wall time'] = stats.pearsonr(wall_time_series, misses_percent_df['Branch misses %'])[0]
            spearman_corr_df.at['Cache misses %', 'Wall time'] = stats.spearmanr(wall_time_series, misses_percent_df['Cache misses %'])[0]
            spearman_corr_df.at['Branch misses %', 'Wall time'] = stats.spearmanr(wall_time_series, misses_percent_df['Branch misses %'])[0]
            
            pearson_corr_df.at['Cache misses %', 'Stall time'] = stats.pearsonr(stall_time_series, misses_percent_df['Cache misses %'])[0]
            pearson_corr_df.at['Branch misses %', 'Stall time'] = stats.pearsonr(stall_time_series, misses_percent_df['Branch misses %'])[0]
            spearman_corr_df.at['Cache misses %', 'Stall time'] = stats.spearmanr(stall_time_series, misses_percent_df['Cache misses %'])[0]
            spearman_corr_df.at['Branch misses %', 'Stall time'] = stats.spearmanr(stall_time_series, misses_percent_df['Branch misses %'])[0]
            
            pearson_corr_df.at['Cache misses %', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, misses_percent_df['Cache misses %'])[0]
            pearson_corr_df.at['Branch misses %', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, misses_percent_df['Branch misses %'])[0]
            spearman_corr_df.at['Cache misses %', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, misses_percent_df['Cache misses %'])[0]
            spearman_corr_df.at['Branch misses %', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, misses_percent_df['Branch misses %'])[0]
            
            rows.append(["Cache miss \%", misses_percent_df['Cache misses %'].mean(), misses_percent_df['Cache misses %'].min(), misses_percent_df['Cache misses %'].max(), misses_percent_df['Cache misses %'].std(), misses_percent_df.loc[misses_percent_df['Cache misses %'] == misses_percent_df['Cache misses %'].max(), 'Run'].iloc[0], misses_percent_df.loc[misses_percent_df['Cache misses %'] == misses_percent_df['Cache misses %'].min(), 'Run'].iloc[0]])
            rows.append(["Branch miss \%", misses_percent_df['Branch misses %'].mean(), misses_percent_df['Branch misses %'].min(), misses_percent_df['Branch misses %'].max(), misses_percent_df['Branch misses %'].std(), misses_percent_df.loc[misses_percent_df['Branch misses %'] == misses_percent_df['Branch misses %'].max(), 'Run'].iloc[0], misses_percent_df.loc[misses_percent_df['Branch misses %'] == misses_percent_df['Branch misses %'].min(), 'Run'].iloc[0]])
        
        if (os.path.isfile(f'{path}/hw_interrupts.csv')):
            # print("\n----------------------- HARDWARE INTERRUPTS -----------------------")
            hw_interrupts_headers = ['Run', 'HW interrupts']
            hw_interrupts_df = pd.read_csv(f'{path}/hw_interrupts.csv', names=hw_interrupts_headers)
            # print(hw_interrupts_df[['HW interrupts']].describe().applymap('{:,.2f}'.format))
            # print()
            # print(f"Run iteration with the highest hardware interrupts: {hw_interrupts_df.loc[hw_interrupts_df['HW interrupts'] == hw_interrupts_df['HW interrupts'].max(), 'Run'].iloc[0]}")
            # print()

            pearson_corr_df.at['HW interrupts', 'Wall time'] = stats.pearsonr(wall_time_series, hw_interrupts_df['HW interrupts'])[0]
            spearman_corr_df.at['HW interrupts', 'Wall time'] = stats.spearmanr(wall_time_series, hw_interrupts_df['HW interrupts'])[0]
            
            pearson_corr_df.at['HW interrupts', 'Stall time'] = stats.pearsonr(stall_time_series, hw_interrupts_df['HW interrupts'])[0]
            spearman_corr_df.at['HW interrupts', 'Stall time'] = stats.spearmanr(stall_time_series, hw_interrupts_df['HW interrupts'])[0]
            
            pearson_corr_df.at['HW interrupts', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, hw_interrupts_df['HW interrupts'])[0]
            spearman_corr_df.at['HW interrupts', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, hw_interrupts_df['HW interrupts'])[0]

            rows.append(['HW interrupts', hw_interrupts_df['HW interrupts'].mean(), hw_interrupts_df['HW interrupts'].min(), hw_interrupts_df['HW interrupts'].max(), hw_interrupts_df['HW interrupts'].std(), hw_interrupts_df.loc[hw_interrupts_df['HW interrupts'] == hw_interrupts_df['HW interrupts'].max(), 'Run'].iloc[0], hw_interrupts_df.loc[hw_interrupts_df['HW interrupts'] == hw_interrupts_df['HW interrupts'].min(), 'Run'].iloc[0]])
        
        if (os.path.isfile(f'{path}/ipc.csv')):
            # print("\n----------------------- INSTRUCTIONS PER CYCLE -----------------------")
            ipc_headers = ['Run', 'IPC']
            ipc_df = pd.read_csv(f'{path}/ipc.csv', names=ipc_headers)
            # print(ipc_df[['IPC']].describe().applymap('{:,.2f}'.format))
            # print()
            # print(f"Run iteration with the lowest IPC: {ipc_df.loc[ipc_df['IPC'] == ipc_df['IPC'].min(), 'Run'].iloc[0]}")
            # print()

            pearson_corr_df.at['IPC', 'Wall time'] = stats.pearsonr(wall_time_series, ipc_df['IPC'])[0]            
            spearman_corr_df.at['IPC', 'Wall time'] = stats.spearmanr(wall_time_series, ipc_df['IPC'])[0]            

            pearson_corr_df.at['IPC', 'Stall time'] = stats.pearsonr(stall_time_series, ipc_df['IPC'])[0]            
            spearman_corr_df.at['IPC', 'Stall time'] = stats.spearmanr(stall_time_series, ipc_df['IPC'])[0]            

            pearson_corr_df.at['IPC', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, ipc_df['IPC'])[0]            
            spearman_corr_df.at['IPC', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, ipc_df['IPC'])[0]            

            rows.append(['IPC', ipc_df['IPC'].mean(), ipc_df['IPC'].min(), ipc_df['IPC'].max(), ipc_df['IPC'].std(), ipc_df.loc[ipc_df['IPC'] == ipc_df['IPC'].min(), 'Run'].iloc[0], ipc_df.loc[ipc_df['IPC'] == ipc_df['IPC'].max(), 'Run'].iloc[0]])
        
        if (os.path.isfile(f'{path}/page_faults.csv')):
            page_faults_headers = ['Run', 'Page faults']
            page_faults_df = pd.read_csv(f'{path}/page_faults.csv', names=page_faults_headers)

            pearson_corr_df.at['Page faults', 'Wall time'] = stats.pearsonr(wall_time_series, page_faults_df['Page faults'])[0]            
            spearman_corr_df.at['Page faults', 'Wall time'] = stats.spearmanr(wall_time_series, page_faults_df['Page faults'])[0]            

            pearson_corr_df.at['Page faults', 'Stall time'] = stats.pearsonr(stall_time_series, page_faults_df['Page faults'])[0]            
            spearman_corr_df.at['Page faults', 'Stall time'] = stats.spearmanr(stall_time_series, page_faults_df['Page faults'])[0]            

            pearson_corr_df.at['Page faults', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, page_faults_df['Page faults'])[0]            
            spearman_corr_df.at['Page faults', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, page_faults_df['Page faults'])[0]            

            rows.append(['Page faults', page_faults_df['Page faults'].mean(), page_faults_df['Page faults'].min(), page_faults_df['Page faults'].max(), page_faults_df['Page faults'].std(), ipc_df.loc[page_faults_df['Page faults'] == page_faults_df['Page faults'].min(), 'Run'].iloc[0], ipc_df.loc[page_faults_df['Page faults'] == page_faults_df['Page faults'].max(), 'Run'].iloc[0]])
        
        if (os.path.isfile(f'{path}/mem_loads_stores.csv')):
            mem_loads_stores_headers = ['Run', 'Mem loads', 'Mem stores']
            mem_loads_stores_df = pd.read_csv(f'{path}/mem_loads_stores.csv', names=mem_loads_stores_headers)

            pearson_corr_df.at['Mem loads', 'Wall time'] = stats.pearsonr(wall_time_series, mem_loads_stores_df['Mem loads'])[0]            
            spearman_corr_df.at['Mem loads', 'Wall time'] = stats.spearmanr(wall_time_series, mem_loads_stores_df['Mem loads'])[0]            
            pearson_corr_df.at['Mem stores', 'Wall time'] = stats.pearsonr(wall_time_series, mem_loads_stores_df['Mem stores'])[0]            
            spearman_corr_df.at['Mem stores', 'Wall time'] = stats.spearmanr(wall_time_series, mem_loads_stores_df['Mem stores'])[0]            

            pearson_corr_df.at['Mem loads', 'Stall time'] = stats.pearsonr(stall_time_series, mem_loads_stores_df['Mem loads'])[0]            
            spearman_corr_df.at['Mem loads', 'Stall time'] = stats.spearmanr(stall_time_series, mem_loads_stores_df['Mem loads'])[0]            
            pearson_corr_df.at['Mem stores', 'Stall time'] = stats.pearsonr(stall_time_series, mem_loads_stores_df['Mem stores'])[0]            
            spearman_corr_df.at['Mem stores', 'Stall time'] = stats.spearmanr(stall_time_series, mem_loads_stores_df['Mem stores'])[0]            

            pearson_corr_df.at['Mem loads', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, mem_loads_stores_df['Mem loads'])[0]            
            spearman_corr_df.at['Mem loads', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, mem_loads_stores_df['Mem loads'])[0]            
            pearson_corr_df.at['Mem stores', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, mem_loads_stores_df['Mem stores'])[0]            
            spearman_corr_df.at['Mem stores', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, mem_loads_stores_df['Mem stores'])[0]            

            rows.append(['Mem loads', mem_loads_stores_df['Mem loads'].mean(), mem_loads_stores_df['Mem loads'].min(),\
                          mem_loads_stores_df['Mem loads'].max(), mem_loads_stores_df['Mem loads'].std(), \
                            ipc_df.loc[mem_loads_stores_df['Mem loads'] == mem_loads_stores_df['Mem loads'].min(), 'Run'].iloc[0],\
                                  ipc_df.loc[mem_loads_stores_df['Mem loads'] == mem_loads_stores_df['Mem loads'].max(), 'Run'].iloc[0]])
            rows.append(['Mem stores', mem_loads_stores_df['Mem stores'].mean(), mem_loads_stores_df['Mem stores'].min(),\
                          mem_loads_stores_df['Mem stores'].max(), mem_loads_stores_df['Mem stores'].std(), \
                            ipc_df.loc[mem_loads_stores_df['Mem stores'] == mem_loads_stores_df['Mem stores'].min(), 'Run'].iloc[0],\
                                  ipc_df.loc[mem_loads_stores_df['Mem stores'] == mem_loads_stores_df['Mem stores'].max(), 'Run'].iloc[0]])
        
        if (os.path.isfile(f'{path}/pidstat_average.csv')):
            pidstat_average_headers = ['Run', 'Average', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
            pidstat_average_df = pd.read_csv(f'{path}/pidstat_average.csv', verbose=True, names=pidstat_average_headers)
            pidstat_average_df['Run'] = pidstat_average_df['Run'].astype("string") if pidstat_average_df['Run'].nunique() < 6 else pidstat_average_df['Run']
            pidstat_average_df = pidstat_average_df.groupby(['Run', 'Command']).agg({'UID': 'first', 'PID': 'first', '"%"usr': 'sum', '"%"system': 'sum', '"%"guest': 'sum', '"%"wait': 'sum', '"%"CPU': 'sum'}).reset_index()
            pidstat_average_df = pidstat_average_df.pivot(index='Run', columns='Command', values='"%"CPU')
            pidstat_average_df = pidstat_average_df.fillna(0)

            # Compute the mean of each column
            column_means = pidstat_average_df.mean()

            # Sort the column names based on their mean values
            column_names = column_means.sort_values(ascending=False).index.tolist()

            # Reorder the columns based on the sorted names
            pidstat_average_df = pidstat_average_df[column_names]

            # Keep only the 10 first columns
            pidstat_average_df = pidstat_average_df.iloc[:, : 10]

            pearson_corr_df.at['App CPU %', 'Wall time'] = stats.pearsonr(wall_time_series, pidstat_average_df[process_name])[0]            
            spearman_corr_df.at['App CPU %', 'Wall time'] = stats.spearmanr(wall_time_series, pidstat_average_df[process_name])[0]

            pearson_corr_df.at['App CPU %', 'Stall time'] = stats.pearsonr(stall_time_series, pidstat_average_df[process_name])[0]            
            spearman_corr_df.at['App CPU %', 'Stall time'] = stats.spearmanr(stall_time_series, pidstat_average_df[process_name])[0]

            pearson_corr_df.at['App CPU %', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, pidstat_average_df[process_name])[0]            
            spearman_corr_df.at['App CPU %', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, pidstat_average_df[process_name])[0]

        if (os.path.isfile(f'{path}/pidstat_mem_average.csv')):
            pidstat_mem_average_headers = ['Run', 'Average', 'UID', 'PID', 'minflt/s', 'majflt/s', 'VSZ (kB)', 'RSS (kB)', '"%"MEM', 'Command']

            # %MEM
            pidstat_mem_average_df = pd.read_csv(f'{path}/pidstat_mem_average.csv', verbose=True, names=pidstat_mem_average_headers)
            pidstat_mem_average_df['Run'] = pidstat_mem_average_df['Run'].astype("string") if pidstat_mem_average_df['Run'].nunique() < 6 else pidstat_mem_average_df['Run']
            pidstat_mem_average_df = pidstat_mem_average_df.groupby(['Run', 'Command']).agg({'UID': 'first', 'PID': 'first', 'minflt/s': 'mean', 'majflt/s': 'mean', 'VSZ (kB)': 'sum', 'RSS (kB)': 'sum', '"%"MEM': 'sum'}).reset_index()
            pidstat_mem_average_df = pidstat_mem_average_df.pivot(index='Run', columns='Command', values='"%"MEM')
            pidstat_mem_average_df = pidstat_mem_average_df.fillna(0)

            # Compute the mean of each column
            column_means = pidstat_mem_average_df.mean()

            # Sort the column names based on their mean values
            column_names = column_means.sort_values(ascending=False).index.tolist()

            # Reorder the columns based on the sorted names
            pidstat_mem_average_df = pidstat_mem_average_df[column_names]

            # Keep only the 10 first columns
            pidstat_mem_average_df = pidstat_mem_average_df.iloc[:, : 10]

            pearson_corr_df.at['App mem %', 'Wall time'] = stats.pearsonr(wall_time_series, pidstat_mem_average_df[process_name])[0]            
            spearman_corr_df.at['App mem %', 'Wall time'] = stats.spearmanr(wall_time_series, pidstat_mem_average_df[process_name])[0]

            pearson_corr_df.at['App mem %', 'Stall time'] = stats.pearsonr(stall_time_series, pidstat_mem_average_df[process_name])[0]            
            spearman_corr_df.at['App mem %', 'Stall time'] = stats.spearmanr(stall_time_series, pidstat_mem_average_df[process_name])[0]

            pearson_corr_df.at['App mem %', 'Ideal CPU time'] = stats.pearsonr(ideal_time_series, pidstat_mem_average_df[process_name])[0]            
            spearman_corr_df.at['App mem %', 'Ideal CPU time'] = stats.spearmanr(ideal_time_series, pidstat_mem_average_df[process_name])[0]

        if (os.path.isfile(f'{path}/sar_r_average.csv')):
            sar_r_average_headers = ['Run', 'Time', 'kbmemfree', 'kbavail', 'kbmemused', '"%"memused', 'kbbuffers', 'kbcached', 'kbcommit', '"%"commit', 'kbactive', 'kbinact', 'kbdirty', 'kbanonpg', 'kbslab', 'kbkstack', 'kbpgtbl', 'kbvmused']
            sar_r_average_df = pd.read_csv(f'{path}/sar_r_average.csv', verbose=True, names=sar_r_average_headers)
            sar_r_average_df.set_index('Run')
            params = sar_r_average_headers.copy()
            params.remove('Run')
            params.remove('Time')
            pearson_corr_df, spearman_corr_df = corr(wall_time_series, stall_time_series, ideal_time_series, pearson_corr_df, spearman_corr_df, params, sar_r_average_df)
        
        pearson_corr_df = pearson_corr_df.sort_values(by=['Wall time'], ascending=False)
        for row in pearson_corr_df.iterrows():
            arr = [row[0]]
            for val in row[1]:
                arr.append(val)
            rows_pearson.append(arr)

        spearman_corr_df = spearman_corr_df.sort_values(by=['Wall time'], ascending=False)
        for row in spearman_corr_df.iterrows():
            arr = [row[0]]
            for val in row[1]:
                arr.append(val)
            rows_spearman.append(arr)

        summary_table.add_rows(rows)
        pearson_table.add_rows(rows_pearson)
        spearman_table.add_rows(rows_spearman)
        
        print("\nSummary")
        print(summary_table.draw())
        
        print("\nPearson")
        print(pearson_table.draw())

        print("\nSpearman")
        print(spearman_table.draw())

        # print(latextable.draw_latex(summary_table, caption="Summary table.", label="table:summary_table"))
        # print(latextable.draw_latex(pearson_table, caption="Pearson correlation table.", label="table:pearson_table"))
        # print(latextable.draw_latex(spearman_table, caption="Spearman correlation table.", label="table:spearman_table"))
        
    else:
        sys.stdout = old_stdout
        summary = open(f"{path}/summary.txt", "r")
        print(summary.read())
        old_stdout = sys.stdout


    ################# PLOTS #################

    if (not plot_graphs):
        exit()

    if (save_graphs):
        os.makedirs(f'{path}/figures/', exist_ok=True)
    
    old_stdout = sys.stdout
    sys.stdout = f

    style_options = ['+-','o-','.--','s:']
    
    if (all_iterations):

        if (os.path.isfile(f'{path}/times.csv')):
            times_headers = ['Run', 'Ideal CPU time', 'Stall time', 'Ideal CPU time with stall cycles', 'Actual CPU time', 'Wall time']
            times_df = pd.read_csv(f'{path}/times.csv', names=times_headers)
            times_df['Run'] = times_df['Run'].astype("string") if times_df.shape[0] < 6 else times_df['Run']
            times_df.set_index('Run')
            fig = times_df.plot(kind='line', x='Run', y=['Wall time'], ylim=[0, 140])
            plt.xlabel('Run iteration')
            plt.ylabel('Time (s)')
            plt.title(f'Wall time per run iteration')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/wall_time.png', format="png")
            fig = times_df.plot(kind='line', x='Run', y=['Ideal CPU time'], ylim=[0, 140])
            plt.xlabel('Run iteration')
            plt.ylabel('Time (s)')
            plt.title(f'Ideal CPU time per run iteration')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/ideal_time.png', format="png")
            fig = times_df.plot(kind='line', x='Run', y=['Stall time'], ylim=[0, 140])
            plt.xlabel('Run iteration')
            plt.ylabel('Time (s)')
            plt.title(f'Stall time per run iteration')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/stall_time.png', format="png")
            fig = times_df.plot(kind='line', x='Run', y=['Ideal CPU time', 'Stall time', 'Actual CPU time'], ylim=[0, 140])
            plt.xlabel('Run iteration')
            plt.ylabel('Time (s)')
            plt.title(f'Estimated and measured times per run iteration')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/times.png', format="png")
        
        # if (os.path.isfile(f'{path}/scores.csv')):
        #     scores_headers = ['Run', 'Score', 'CPU utilization score', 'CPU idle score']
        #     scores_df = pd.read_csv(f'{path}/scores.csv', names=scores_headers)
        #     scores_df['Run'] = scores_df['Run'].astype("string") if scores_df.shape[0] < 6 else scores_df['Run']
        #     scores_df.set_index('Run')
        #     fig = scores_df.plot(kind='line', x='Run', y=['Score'], ylim=[0, 110])
        #     plt.xlabel('Run iteration')
        #     plt.ylabel('Score')
        #     plt.title(f'Score per run iteration')
        #     if (save_graphs):
        #         fig.figure.savefig(f'{path}/figures/score.png', format="png")
        
        if (os.path.isfile(f'{path}/scores.csv')):
            scores_headers = ['Run', 'CPU time score', 'App CPU utilization', 'Idle CPU']
            scores_df = pd.read_csv(f'{path}/scores.csv', names=scores_headers)
            scores_df['Run'] = scores_df['Run'].astype("string") if scores_df.shape[0] < 6 else scores_df['Run']
            scores_df.set_index('Run')
            fig = scores_df.plot(kind='line', x='Run', y=['App CPU utilization', 'Idle CPU'], ylim=[0, 110])
            plt.xlabel('Run iteration')
            plt.ylabel('CPU utilization (%)')
            plt.title(f'App CPU utilization per run iteration')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/cpu_utilization.png', format="png")
        
        if (os.path.isfile(f'{path}/misses_percent.csv') and verbose):
            misses_percent_headers = ['Run', 'Cache misses percentage', 'Branch misses percentage']
            misses_percent_df = pd.read_csv(f'{path}/misses_percent.csv', names=misses_percent_headers)
            misses_percent_df['Run'] = misses_percent_df['Run'].astype("string") if misses_percent_df.shape[1] < 6 else misses_percent_df['Run']
            misses_percent_df.set_index('Run')
            fig = misses_percent_df.plot(kind='line', x='Run', y=['Cache misses percentage', 'Branch misses percentage'], ylim=[0, 50])
            plt.xlabel('Run iteration')
            plt.ylabel('Miss %')
            plt.title(f'Cache and branch misses %')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/misses_percent.png', format="png")
        
        if (os.path.isfile(f'{path}/hw_interrupts.csv') and verbose):
            hw_interrupts_headers = ['Run', 'HW interrupts']
            hw_interrupts_df = pd.read_csv(f'{path}/hw_interrupts.csv', names=hw_interrupts_headers)
            hw_interrupts_df['Run'] = hw_interrupts_df['Run'].astype("string") if hw_interrupts_df.shape[0] < 6 else hw_interrupts_df['Run']
            hw_interrupts_df.set_index('Run')
            fig = hw_interrupts_df.plot(kind='line', x='Run', y=['HW interrupts'], ylim=[0, 260000])
            plt.xlabel('Run iteration')
            plt.ylabel('HW interrupt counts')
            plt.title(f'Hardware interrupts')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/hw_interrupts.png', format="png")
        
        if (os.path.isfile(f'{path}/ipc.csv') and verbose):
            ipc_headers = ['Run', 'IPC']
            ipc_df = pd.read_csv(f'{path}/ipc.csv', names=ipc_headers)
            ipc_df['Run'] = ipc_df['Run'].astype("string") if ipc_df.shape[0] < 6 else ipc_df['Run']
            ipc_df.set_index('Run')
            fig = ipc_df.plot(kind='line', x='Run', y=['IPC'], ylim=[0.5, 1.5])
            plt.xlabel('Run iteration')
            plt.ylabel('IPC')
            plt.title(f'Instructions per cycle')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/ipc.png', format="png")
        
        for i in range(n_cpus):
            if (os.path.isfile(f'{path}/top_five_processes_cpu{i}.csv') and verbose):
                top_five_processes_headers = ['Run', 'cpu', 'process', 'run-time (ms)']
                top_five_processes_df = pd.read_csv(f'{path}/top_five_processes_cpu{i}.csv', names=top_five_processes_headers)
                top_five_processes_df['Run'] = top_five_processes_df['Run'].astype("string") if top_five_processes_df.shape[0] < 6 else top_five_processes_df['Run']
                top_five_processes_df = top_five_processes_df.groupby(['Run', 'process']).agg({'cpu': 'first', 'run-time (ms)': 'sum'}).reset_index()
                top_five_processes_df = top_five_processes_df.pivot(index='Run', columns='process', values='run-time (ms)')
                style_list = []
                for n in range(top_five_processes_df.shape[1]):
                    style_list.append(style_options[n % len(style_options)])
                markevery = 2
                if (top_five_processes_df.shape[0] > 50):
                    markevery=(top_five_processes_df.shape[0] // 10)
                if (top_five_processes_df.shape[0] < 10):
                    markevery=1
                fig = top_five_processes_df.plot(kind='line', style=style_list, markevery=markevery, ylim=[0, 100000])
                plt.xlabel('Run iteration')
                plt.ylabel('Runtime (ms)')
                plt.title(f'Top 3 process runtimes for each iteration in CPU {i}')
                if (save_graphs):
                    fig.figure.savefig(f'{path}/figures/top_five_processes_cpu{i}.png', format="png")


        if (os.path.isfile(f'{path}/pidstat_average.csv')):
            pidstat_average_headers = ['Run', 'Average', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
            pidstat_average_df = pd.read_csv(f'{path}/pidstat_average.csv', verbose=True, names=pidstat_average_headers)
            pidstat_average_df['Run'] = pidstat_average_df['Run'].astype("string") if pidstat_average_df['Run'].nunique() < 6 else pidstat_average_df['Run']
            pidstat_average_df = pidstat_average_df.groupby(['Run', 'Command']).agg({'UID': 'first', 'PID': 'first', '"%"usr': 'sum', '"%"system': 'sum', '"%"guest': 'sum', '"%"wait': 'sum', '"%"CPU': 'sum'}).reset_index()
            pidstat_average_df = pidstat_average_df.pivot(index='Run', columns='Command', values='"%"CPU')
            pidstat_average_df = pidstat_average_df.fillna(0)

            # Compute the mean of each column
            column_means = pidstat_average_df.mean()

            # Sort the column names based on their mean values
            column_names = column_means.sort_values(ascending=False).index.tolist()

            # Reorder the columns based on the sorted names
            pidstat_average_df = pidstat_average_df[column_names]

            # Keep only the 10 first columns
            pidstat_average_df = pidstat_average_df.iloc[:, : 10]

            style_list = []
            for n in range(pidstat_average_df.shape[1]):
                style_list.append(style_options[n % len(style_options)])
            markevery = 2
            if (pidstat_average_df.shape[0] > 50):
                markevery = (pidstat_average_df.shape[0] // 10)
            if (pidstat_average_df.shape[0] < 10):
                markevery = 1
            fig = pidstat_average_df.plot(kind='line', style=style_list, markevery=markevery, ylim=[0, 110])
            plt.xlabel('Run iteration')
            plt.ylabel('Relative CPU usage (%) (ms)')
            plt.title(f'CPU usage of top 10 running processes for each iteration across all CPUs')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/top_10_all_cpus.png', format="png")


        if (os.path.isfile(f'{path}/pidstat_mem_average.csv')):
            pidstat_mem_average_headers = ['Run', 'Average', 'UID', 'PID', 'minflt/s', 'majflt/s', 'VSZ (kB)', 'RSS (kB)', '"%"MEM', 'Command']

            # %MEM
            pidstat_mem_average_df = pd.read_csv(f'{path}/pidstat_mem_average.csv', verbose=True, names=pidstat_mem_average_headers)
            pidstat_mem_average_df['Run'] = pidstat_mem_average_df['Run'].astype("string") if pidstat_mem_average_df['Run'].nunique() < 6 else pidstat_mem_average_df['Run']
            pidstat_mem_average_df = pidstat_mem_average_df.groupby(['Run', 'Command']).agg({'UID': 'first', 'PID': 'first', 'minflt/s': 'mean', 'majflt/s': 'mean', 'VSZ (kB)': 'sum', 'RSS (kB)': 'sum', '"%"MEM': 'sum'}).reset_index()
            pidstat_mem_average_df = pidstat_mem_average_df.pivot(index='Run', columns='Command', values='"%"MEM')
            pidstat_mem_average_df = pidstat_mem_average_df.fillna(0)

            # Compute the mean of each column
            column_means = pidstat_mem_average_df.mean()

            # Sort the column names based on their mean values
            column_names = column_means.sort_values(ascending=False).index.tolist()

            # Reorder the columns based on the sorted names
            pidstat_mem_average_df = pidstat_mem_average_df[column_names]

            # Keep only the 10 first columns
            pidstat_mem_average_df = pidstat_mem_average_df.iloc[:, : 10]

            style_list = []
            for n in range(pidstat_mem_average_df.shape[1]):
                style_list.append(style_options[n % len(style_options)])
            markevery = 2
            if (pidstat_mem_average_df.shape[0] > 50):
                markevery = (pidstat_mem_average_df.shape[0] // 10)
            if (pidstat_mem_average_df.shape[0] < 10):
                markevery = 1
            fig = pidstat_mem_average_df.plot(kind='line', style=style_list, markevery=markevery, ylim=[0, 10])
            plt.xlabel('Run iteration')
            plt.ylabel('Relative memory usage (%)')
            plt.title(f'Relative memory usage of top 10 running processes for each iteration across all CPUs')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/top_10_mem.png', format="png")

        if (process_name == "thesis_app"):
            app_output_df['Run'] = app_output_df['Run'].astype("string") if app_output_df.shape[0] < 6 else app_output_df['Run']
            app_output_df.set_index('Run')
            app_output_df.plot(kind='line', x='Run', y=['Memory time', 'Disk time', 'Calc time', 'App time src'], xticks=app_output_df['Run'])
            plt.xlabel('run iteration')
            plt.ylabel('runtime')
            plt.title('thesis_app runtimes')
        
    else:
        if (verbose):
            webbrowser.open(f"{path}/perf.svg")

        if (os.path.isfile(f'{path}/pidstat_all.csv')):
            pidstat_all_headers = ['Time', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
            pidstat_all_df = pd.read_csv(f'{path}/pidstat_all.csv', verbose=True, names=pidstat_all_headers)
            pidstat_all_df['Time'] = pd.to_datetime(pidstat_all_df['Time'])
            pidstat_all_df['seconds'] = pidstat_all_df['Time'].dt.strftime("%H:%M:%S")
            pidstat_all_df = pidstat_all_df.groupby(['seconds', 'Command']).agg({'UID': 'first', 'PID': 'first', '"%"usr': 'sum', '"%"system': 'sum', '"%"guest': 'sum', '"%"wait': 'sum', '"%"CPU': 'sum'}).reset_index()
            pidstat_all_df = pidstat_all_df.pivot(index='seconds', columns='Command', values='"%"CPU')
            pidstat_all_df = pidstat_all_df.fillna(0)

            # Compute the mean of each column
            column_means = pidstat_all_df.mean()

            # Sort the column names based on their mean values
            column_names = column_means.sort_values(ascending=False).index.tolist()

            # Reorder the columns based on the sorted names
            pidstat_all_df = pidstat_all_df[column_names]

            # Keep only the 10 first columns
            pidstat_all_df = pidstat_all_df.iloc[:, : 10]

            style_list = []
            for n in range(pidstat_all_df.shape[1]):
                style_list.append(style_options[n % len(style_options)])
            markevery = 2
            if (pidstat_all_df.shape[0] > 50):
                markevery = (pidstat_all_df.shape[0] // 10)
            if (pidstat_all_df.shape[0] < 10):
                markevery = 1
            fig = pidstat_all_df.plot(kind='line', style=style_list, markevery=markevery)
            plt.xlabel('Time (hour:minute:second)')
            plt.ylabel('Relative CPU usage (%) (ms)')
            plt.title(f'CPU usage of top 10 running processes across all CPUs')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/top_10_all_cpus.png', format="png")


        if (os.path.isfile(f'{path}/pidstat_mem_all.csv')):
            pidstat_mem_all_headers = ['Time', 'UID', 'PID', 'minflt/s', 'majflt/s', 'VSZ (kB)', 'RSS (kB)', '"%"MEM', 'Command']
            
            # %MEM
            pidstat_mem_all_df = pd.read_csv(f'{path}/pidstat_mem_all.csv', verbose=True, names=pidstat_mem_all_headers)
            pidstat_mem_all_df['Time'] = pd.to_datetime(pidstat_mem_all_df['Time'])
            pidstat_mem_all_df['seconds'] = pidstat_mem_all_df['Time'].dt.strftime("%H:%M:%S")
            pidstat_mem_all_df = pidstat_mem_all_df.groupby(['seconds', 'Command']).agg({'UID': 'first', 'PID': 'first', 'minflt/s': 'mean', 'majflt/s': 'mean', 'VSZ (kB)': 'sum', 'RSS (kB)': 'sum', '"%"MEM': 'sum'}).reset_index()
            pidstat_mem_all_df = pidstat_mem_all_df.pivot(index='seconds', columns='Command', values='"%"MEM')
            pidstat_mem_all_df = pidstat_mem_all_df.fillna(0)

            # Compute the mean of each column
            column_means = pidstat_mem_all_df.mean()

            # Sort the column names based on their mean values
            column_names = column_means.sort_values(ascending=False).index.tolist()

            # Reorder the columns based on the sorted names
            pidstat_mem_all_df = pidstat_mem_all_df[column_names]

            # Keep only the 10 first columns
            pidstat_mem_all_df = pidstat_mem_all_df.iloc[:, : 10]

            style_list = []
            for n in range(pidstat_mem_all_df.shape[1]):
                style_list.append(style_options[n % len(style_options)])
            markevery = 2
            if (pidstat_mem_all_df.shape[0] > 50):
                markevery = (pidstat_mem_all_df.shape[0] // 10)
            if (pidstat_mem_all_df.shape[0] < 10):
                markevery = 1
            fig = pidstat_mem_all_df.plot(kind='line', style=style_list, markevery=markevery, ylim=[0, 10])
            plt.xlabel('Time (hour:minute:second)')
            plt.ylabel('Relative memory usage (%)')
            plt.title(f'Memory usage of top 10 running processes across all CPUs')
            if (save_graphs):
                fig.figure.savefig(f'{path}/figures/top_10_mem.png', format="png")

    if (os.path.isfile(f'{path}/vmstat.csv') and verbose):
        vmstat_headers = ['Run', 'runnable processes', 'ps blckd wait for I/O', 'tot swpd used', 'free (kB)', 'buff (kB)', 'cache (kB)', 'mem swapped in/s', 'mem swapped out/s', 'from block device (KiB/s)', 'to block device (KiB/s)', 'interrupts/s', 'cxt switch/s', 'user time', 'system time', 'idle time', 'wait io time', 'stolen time', 'Date', 'Time']
        vmstat_df = pd.read_csv(f'{path}/vmstat.csv', verbose=True, names=vmstat_headers)
        vmstat_df['Time'] = pd.to_datetime(vmstat_df['Time'])
        vmstat_df['seconds'] = vmstat_df['Time'].dt.strftime("%H:%M:%S")
        vmstat_df.set_index('seconds')
        fig = vmstat_df.plot(kind='line', x='seconds', y=['runnable processes', 'ps blckd wait for I/O'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Count')
        plt.title('vmstat -t -w 1 Processes')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/vmstat_processes.png', format="png")
        fig = vmstat_df.plot(kind='line', x='seconds', y=['tot swpd used', 'mem swapped in/s', 'mem swapped out/s'], ylim=[0, 50000])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Size (KiB)')
        plt.title('vmstat -t -w 1 Swap')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/vmstat_swap.png', format="png")
        fig = vmstat_df.plot(kind='line', x='seconds', y=['from block device (KiB/s)', 'to block device (KiB/s)'], ylim=[0, 170000])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Size per second (KiB/s)')
        plt.title('vmstat -t -w 1 I/O')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/vmstat_block_device.png', format="png")
        fig = vmstat_df.plot(kind='line', x='seconds', y=['cxt switch/s'], ylim=[0, 30000])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Count per second')
        plt.title('vmstat -t -w 1 System')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/vmstat_cxt_switches.png', format="png")
        fig = vmstat_df.plot(kind='line', x='seconds', y=['user time', 'system time', 'idle time', 'wait io time', 'stolen time'], ylim=[0, 110])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Relative time spent (%)')
        plt.title('vmstat -t -w 1 CPU')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/vmstat_cpu_rel_time.png', format="png")

    if (os.path.isfile(f'{path}/pidstat.csv') and verbose):
        pidstat_headers = ['Run', 'Time', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
        pidstat_df = pd.read_csv(f'{path}/pidstat.csv', verbose=True, names=pidstat_headers)
        pidstat_df['Time'] = pd.to_datetime(pidstat_df['Time'])
        pidstat_df['seconds'] = pidstat_df['Time'].dt.strftime("%H:%M:%S")
        pidstat_df.set_index('seconds')
        fig = pidstat_df.plot(kind='line', x='seconds', y=['"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Relative CPU usage (%)')
        plt.title(f'pidstat 1 | grep {process_name} (and subthreads)')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/pidstat_cpu.png', format="png")

    if (os.path.isfile(f'{path}/pidstat_mem.csv') and verbose):
        pidstat_mem_headers = ['Run', 'Time', 'UID', 'PID', 'minflt/s', 'majflt/s', 'VSZ (kB)', 'RSS (kB)', '"%"MEM', 'Command']
        pidstat_mem_df = pd.read_csv(f'{path}/pidstat_mem.csv', verbose=True, names=pidstat_mem_headers)
        pidstat_mem_df['Time'] = pd.to_datetime(pidstat_mem_df['Time'])
        pidstat_mem_df['seconds'] = pidstat_mem_df['Time'].dt.strftime("%H:%M:%S")
        pidstat_mem_df.set_index('seconds')
        fig = pidstat_mem_df.plot(kind='line', x='seconds', y=['minflt/s', 'majflt/s', 'VSZ (kB)', 'RSS (kB)'])
        plt.xlabel('time (hour:minute:second)')
        plt.ylabel('Size (kB)')
        plt.title(f'pidstat 1 -r | grep {process_name} (and subthreads)')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/pidstat_mem.png', format="png")

    if (os.path.isfile(f'{path}/sar_r.csv') and verbose):
        sar_r_headers = ['Run', 'Time', 'kbmemfree', 'kbavail', 'kbmemused', '"%"memused', 'kbbuffers', 'kbcached', 'kbcommit', '"%"commit', 'kbactive', 'kbinact', 'kbdirty', 'kbanonpg', 'kbslab', 'kbkstack', 'kbpgtbl', 'kbvmused']
        sar_r_df = pd.read_csv(f'{path}/sar_r.csv', verbose=True, names=sar_r_headers)
        sar_r_df['Time'] = pd.to_datetime(sar_r_df['Time'])
        sar_r_df['seconds'] = sar_r_df['Time'].dt.strftime("%H:%M:%S")
        sar_r_df.set_index('Time')
        style_list = []
        for n in range(len(sar_r_df.columns) - 2):
            style_list.append(style_options[n % len(style_options)])
        markevery = 2
        if (sar_r_df.shape[0] > 50):
            markevery = (sar_r_df.shape[0] // 10)
        if (sar_r_df.shape[0] > 500):
            markevery = (sar_r_df.shape[0] // 100)
        if (sar_r_df.shape[0] < 10):
            markevery = 1
        fig = sar_r_df.plot(kind='line', style=style_list, markevery=markevery, x='seconds', y=['kbmemfree', 'kbavail', 'kbmemused', 'kbbuffers', 'kbcached', 'kbcommit', 'kbactive', 'kbinact', 'kbdirty', 'kbanonpg', 'kbslab', 'kbkstack', 'kbpgtbl', 'kbvmused'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Size (kB)')
        plt.title('sar -r ALL 1')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/sar_mem.png', format="png")
        fig = sar_r_df.plot(kind='line', x='seconds', y=['"%"memused', '"%"commit'], ylim=[0, 110])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Percentage (%)')
        plt.title('sar -r ALL 1')
        if (save_graphs):
            fig.figure.savefig(f'{path}/figures/sar_rel_mem.png', format="png")
    
    sys.stdout = old_stdout

    print("Plotting graphs, press Ctrl+C and Alt+Tab to clear...")
    plt.show()

if __name__ == "__main__":
   main(sys.argv[1:])