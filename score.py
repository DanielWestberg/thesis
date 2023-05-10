#!/usr/bin/python3
import pandas as pd
import matplotlib.pyplot as plt
import webbrowser
import os
import sys

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
    f = open(os.devnull, 'w')

    print("Loading stats, please wait...")
    old_stdout = sys.stdout

    if (all_iterations):
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
            print(f"CPU time score (ideal/wall):            {((t_ideal/wall_time)*100):.2f}   (0 = bad, lots of stalls and noise. 100 = good, no stall cycles or noise)", file = summary_file)
            # print(f"CPU time score (ideal/actual):          {((t_ideal/tot_runtime_all_cpus)*100):.2f}   (0 = bad, lots of stall cycles. 100 = good, no stall cycles)", file = summary_file)
            # print(f"CPU time score (incl. stalls/wall):     {((t_with_stalls/wall_time)*100):.2f}   (0 = bad, lots of noise. 100 = good, no noise)", file = summary_file)
            # print(f"CPU time score (incl. stalls/actual):   {((t_with_stalls/tot_runtime_all_cpus)*100):.2f}   (0 = bad, lots of noise. 100 = good, no noise)", file = summary_file)
            # print(f"CPU time score (actual/wall):           {((tot_runtime_all_cpus/wall_time)*100):.2f}   (0 = bad, lots of noise. 100 = good, no noise)", file = summary_file)
            print(f"CPU utilization score:                  {(cpu_util_score):.2f}   (0 = bad, CPU idle or used for other processes. 100 = good, CPU only used for app)", file = summary_file)
            print(f"CPU idle score:                         {(idle_score):.2f}   (0 = good, CPU not idle. 100 = bad, CPU idle)", file = summary_file)
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

            for i in range(n_cpus):
                top_five_processes_file = open(f"{path}/top_five_processes_cpu{i}.csv", "a")
                for j in range(5):
                    top_five_processes_file.write(f"{run_iter},{i},{perf_sched_summary_cpu_dfs_new[i].iloc[j]['process'].split('[')[0]},{perf_sched_summary_cpu_dfs_new[i].iloc[j]['run-time (ms)']}\n")
                top_five_processes_file.close()


        ################# SUMMARY ALL ITERATIONS #################
        print(f"\n###################### SUMMARY ######################\n")

        if (os.path.isfile(f'{path}/times.csv')):
            print("\n----------------------- TIMES -----------------------")
            times_headers = ['Run', 'Ideal CPU time', 'Stall time', 'Ideal CPU time with stall cycles', 'Actual CPU time', 'Wall time']
            times_df = pd.read_csv(f'{path}/times.csv', names=times_headers)
            print(times_df[['Ideal CPU time', 'Stall time', 'Ideal CPU time with stall cycles', 'Actual CPU time', 'Wall time']].describe().applymap('{:,.2f}'.format))
            print()
            print(f"Run iteration with highest ideal CPU time:  {times_df.loc[times_df['Ideal CPU time'] == times_df['Ideal CPU time'].max(), 'Run'].iloc[0]}")
            print(f"Run iteration with highest stall time:      {times_df.loc[times_df['Stall time'] == times_df['Stall time'].max(), 'Run'].iloc[0]}")
            print(f"Run iteration with highest actual CPU time: {times_df.loc[times_df['Actual CPU time'] == times_df['Actual CPU time'].max(), 'Run'].iloc[0]}")
            print(f"Run iteration with highest wall time:       {times_df.loc[times_df['Wall time'] == times_df['Wall time'].max(), 'Run'].iloc[0]}")
            print()
        
        if (os.path.isfile(f'{path}/scores.csv')):
            print("\n----------------------- SCORES -----------------------")
            scores_headers = ['Run', 'CPU time score', 'CPU utilization score', 'CPU idle score']
            scores_df = pd.read_csv(f'{path}/scores.csv', names=scores_headers)
            print(scores_df[['CPU time score', 'CPU utilization score', 'CPU idle score']].describe().applymap('{:,.2f}'.format))
            print()
            print(f"Run iteration with the lowest CPU time score:          {scores_df.loc[scores_df['CPU time score'] == scores_df['CPU time score'].min(), 'Run'].iloc[0]}")
            print(f"Run iteration with the lowest CPU utilization score:    {scores_df.loc[scores_df['CPU utilization score'] == scores_df['CPU utilization score'].min(), 'Run'].iloc[0]}")
            print(f"Run iteration with the highest CPU idle score:          {scores_df.loc[scores_df['CPU idle score'] == scores_df['CPU idle score'].max(), 'Run'].iloc[0]}")
            print()
        
        if (os.path.isfile(f'{path}/misses_percent.csv')):
            print("\n----------------------- MISS % -----------------------")
            misses_percent_headers = ['Run', 'Cache misses %', 'Branch misses %']
            misses_percent_df = pd.read_csv(f'{path}/misses_percent.csv', names=misses_percent_headers)
            print(misses_percent_df[['Cache misses %', 'Branch misses %']].describe().applymap('{:,.2f}'.format))
            print()
            print(f"Run iteration with the highest cache miss %:    {misses_percent_df.loc[misses_percent_df['Cache misses %'] == misses_percent_df['Cache misses %'].max(), 'Run'].iloc[0]}")
            print(f"Run iteration with the highest branch miss %:   {misses_percent_df.loc[misses_percent_df['Branch misses %'] == misses_percent_df['Branch misses %'].max(), 'Run'].iloc[0]}")
            print()
        
        if (os.path.isfile(f'{path}/hw_interrupts.csv')):
            print("\n----------------------- HARDWARE INTERRUPTS -----------------------")
            hw_interrupts_headers = ['Run', 'HW interrupts']
            hw_interrupts_df = pd.read_csv(f'{path}/hw_interrupts.csv', names=hw_interrupts_headers)
            print(hw_interrupts_df[['HW interrupts']].describe().applymap('{:,.2f}'.format))
            print()
            print(f"Run iteration with the highest hardware interrupts: {hw_interrupts_df.loc[hw_interrupts_df['HW interrupts'] == hw_interrupts_df['HW interrupts'].max(), 'Run'].iloc[0]}")
            print()
        
        if (os.path.isfile(f'{path}/ipc.csv')):
            print("\n----------------------- INSTRUCTIONS PER CYCLE -----------------------")
            ipc_headers = ['Run', 'IPC']
            ipc_df = pd.read_csv(f'{path}/ipc.csv', names=ipc_headers)
            print(ipc_df[['IPC']].describe().applymap('{:,.2f}'.format))
            print()
            print(f"Run iteration with the lowest IPC: {ipc_df.loc[ipc_df['IPC'] == ipc_df['IPC'].min(), 'Run'].iloc[0]}")
            print()
    else:
        sys.stdout = old_stdout
        summary = open(f"{path}/summary.txt", "r")
        print(summary.read())
        old_stdout = sys.stdout


    ################# PLOTS #################

    if (not plot_graphs):
        exit()

    old_stdout = sys.stdout
    sys.stdout = f

    style_options = ['+-','o-','.--','s:']
    
    if (all_iterations):

        if (os.path.isfile(f'{path}/times.csv')):
            times_headers = ['Run', 'Ideal CPU time', 'Stall time', 'Ideal CPU time with stall cycles', 'Actual CPU time', 'Wall time']
            times_df = pd.read_csv(f'{path}/times.csv', names=times_headers)
            times_df.set_index('Run')
            times_df.plot(kind='line', x='Run', y=['Wall time'], ylim=[0, times_df['Wall time'].max()*1.1])
            plt.xlabel('Run iteration')
            plt.ylabel('Time (s)')
            plt.title(f'Wall time per run iteration')
            times_df.plot(kind='line', x='Run', y=['Ideal CPU time', 'Stall time', 'Ideal CPU time with stall cycles', 'Actual CPU time'], ylim=[0, times_df['Wall time'].max()*1.1])
            plt.xlabel('Run iteration')
            plt.ylabel('Time (s)')
            plt.title(f'Estimated and measured times per run iteration')
        
        if (os.path.isfile(f'{path}/scores.csv')):
            # scores_headers = ['Run', 'ideal/wall', 'CPU stall score', 'incl. stalls/wall', 'incl. stalls/actual', 'CPU noise score', 'CPU utilization score', 'CPU idle score']
            # scores_headers = ['Run', 'CPU stall score', 'CPU noise score', 'CPU utilization score', 'CPU idle score']
            scores_headers = ['Run', 'CPU time score', 'CPU utilization score', 'CPU idle score']
            scores_df = pd.read_csv(f'{path}/scores.csv', names=scores_headers)
            scores_df.set_index('Run')
            scores_df.plot(kind='line', x='Run', y=['CPU time score', 'CPU utilization score', 'CPU idle score'], ylim=[0, 110])
            plt.xlabel('Run iteration')
            plt.ylabel('Score')
            plt.title(f'Scores per run iteration')
        
        if (os.path.isfile(f'{path}/misses_percent.csv')):
            misses_percent_headers = ['Run', 'Cache misses percentage', 'Branch misses percentage']
            misses_percent_df = pd.read_csv(f'{path}/misses_percent.csv', names=misses_percent_headers)
            misses_percent_df.set_index('Run')
            misses_percent_df.plot(kind='line', x='Run', y=['Cache misses percentage', 'Branch misses percentage'], ylim=[0, 110])
            plt.xlabel('Run iteration')
            plt.ylabel('Miss %')
            plt.title(f'Cache and branch misses %')
        
        if (os.path.isfile(f'{path}/hw_interrupts.csv')):
            hw_interrupts_headers = ['Run', 'HW interrupts']
            hw_interrupts_df = pd.read_csv(f'{path}/hw_interrupts.csv', names=hw_interrupts_headers)
            hw_interrupts_df.set_index('Run')
            hw_interrupts_df.plot(kind='line', x='Run', y=['HW interrupts'], ylim=[0, hw_interrupts_df['HW interrupts'].max()*1.1])
            plt.xlabel('Run iteration')
            plt.ylabel('HW interrupt counts')
            plt.title(f'Hardware interrupts')
        
        if (os.path.isfile(f'{path}/ipc.csv')):
            ipc_headers = ['Run', 'IPC']
            ipc_df = pd.read_csv(f'{path}/ipc.csv', names=ipc_headers)
            ipc_df.set_index('Run')
            ipc_df.plot(kind='line', x='Run', y=['IPC'], ylim=[0, ipc_df['IPC'].max()*1.1])
            plt.xlabel('Run iteration')
            plt.ylabel('IPC')
            plt.title(f'Instructions per cycle')
        
        for i in range(n_cpus):
            if (os.path.isfile(f'{path}/top_five_processes_cpu{i}.csv')):
                top_five_processes_headers = ['Run', 'cpu', 'process', 'run-time (ms)']
                top_five_processes_df = pd.read_csv(f'{path}/top_five_processes_cpu{i}.csv', names=top_five_processes_headers)
                top_five_processes_df = top_five_processes_df.groupby(['Run', 'process']).agg({'cpu': 'first', 'run-time (ms)': 'sum'}).reset_index()
                top_five_processes_df = top_five_processes_df.pivot(index='Run', columns='process', values='run-time (ms)')
                style_list = []
                for n in range(len(top_five_processes_df.columns)):
                    style_list.append(style_options[n % len(style_options)])
                markevery = 2
                if (len(top_five_processes_df.columns) > 50):
                    markevery=(len(top_five_processes_df.columns) // 10)
                if (len(top_five_processes_df.columns) < 10):
                    markevery=1
                top_five_processes_df.plot(kind='line', style=style_list, markevery=markevery)
                plt.xlabel('Run iteration')
                plt.ylabel('Runtime (ms)')
                plt.title(f'Top <=5 process runtimes for each iteration in CPU {i}')

        if (process_name == "thesis_app"):
            app_output_df.set_index('Run')
            app_output_df.plot(kind='line', x='Run', y=['Memory time', 'Disk time', 'Calc time', 'App time src'], xticks=app_output_df['Run'])
            plt.xlabel('run iteration')
            plt.ylabel('runtime')
            plt.title('thesis_app runtimes')
        
    else:
        webbrowser.open(f"{path}/perf.svg")
    
    if (os.path.isfile(f'{path}/vmstat.csv')):
        vmstat_headers = ['Run', 'runnable processes', 'ps blckd wait for I/O', 'tot swpd used', 'free (kB)', 'buff (kB)', 'cache (kB)', 'mem swapped in/s', 'mem swapped out/s', 'from block device (KiB/s)', 'to block device (KiB/s)', 'interrupts/s', 'cxt switch/s', 'user time', 'system time', 'idle time', 'wait io time', 'stolen time', 'Date', 'Time']
        vmstat_df = pd.read_csv(f'{path}/vmstat.csv', verbose=True, names=vmstat_headers)
        vmstat_df['Time'] = pd.to_datetime(vmstat_df['Time'])
        vmstat_df['seconds'] = vmstat_df['Time'].dt.strftime("%H:%M:%S")
        vmstat_df.set_index('seconds')
        vmstat_ax1 = vmstat_df.plot(kind='line', x='seconds', y=['free (kB)', 'buff (kB)', 'cache (kB)'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Memory size (kB)')
        plt.title('vmstat -t -w 1 Memory')
        vmstat_ax2 = vmstat_df.plot(kind='line', x='seconds', y=['runnable processes', 'ps blckd wait for I/O'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Count')
        plt.title('vmstat -t -w 1 Processes')
        vmstat_ax3 = vmstat_df.plot(kind='line', x='seconds', y=['tot swpd used', 'mem swapped in/s', 'mem swapped out/s'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Size (KiB)')
        plt.title('vmstat -t -w 1 Swap')
        vmstat_ax4 = vmstat_df.plot(kind='line', x='seconds', y=['from block device (KiB/s)', 'to block device (KiB/s)'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Size per second (KiB/s)')
        plt.title('vmstat -t -w 1 I/O')
        vmstat_ax5 = vmstat_df.plot(kind='line', x='seconds', y=['interrupts/s', 'cxt switch/s'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Count')
        plt.title('vmstat -t -w 1 System')
        vmstat_ax6 = vmstat_df.plot(kind='line', x='seconds', y=['user time', 'system time', 'idle time', 'wait io time', 'stolen time'], ylim=[0, 110])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Relative time spent (%)')
        plt.title('vmstat -t -w 1 CPU')
        # vmstat_ax7 = vmstat_df.plot(kind='line', x='seconds', y=['Run'])
        # plt.xlabel('Time (hour:minute:second)')
        # plt.ylabel('Run iteration')
        # plt.title('Run iteration time')

    # mpstat_df = [0 for i in range(n_cpus)]
    # for i in range(n_cpus):
    #     if (os.path.isfile(f'{path}/mpstat{i}.csv')):
    #         mpstat_headers = ['Run', 'Time', 'CPU', '"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle']
    #         mpstat_df[i] = pd.read_csv(f'{path}/mpstat{i}.csv', verbose=True, names=mpstat_headers)
    #         mpstat_df[i]['Time'] = pd.to_datetime(mpstat_df[i]['Time'])
    #         mpstat_df[i]['seconds'] = mpstat_df[i]['Time'].dt.strftime("%H:%M:%S")
    #         mpstat_df[i].set_index('seconds')
    #         mpstat_ax = mpstat_df[i].plot(kind='line', x='seconds', y=['"%"usr', '"%"nice', '"%"sys', '"%"iowait', '"%"irq', '"%"soft', '"%"steal', '"%"guest', '"%"gnice', '"%"idle'], ylim=[0, 110])
    #         plt.xlabel('Time (hour:minute:second)')
    #         plt.ylabel('%')
    #         plt.title(f'mpstat -P {i} 1')

    if (os.path.isfile(f'{path}/pidstat.csv')):
        pidstat_headers = ['Run', 'Time', 'UID', 'PID', '"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU', 'CPU', 'Command']
        pidstat_df = pd.read_csv(f'{path}/pidstat.csv', verbose=True, names=pidstat_headers)
        pidstat_df['Time'] = pd.to_datetime(pidstat_df['Time'])
        pidstat_df['seconds'] = pidstat_df['Time'].dt.strftime("%H:%M:%S")
        pidstat_df.set_index('seconds')
        pidstat_ax = pidstat_df.plot(kind='line', x='seconds', y=['"%"usr', '"%"system', '"%"guest', '"%"wait', '"%"CPU'], ylim=[0, 110])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Relative CPU usage (%)')
        plt.title(f'pidstat 1 | grep {process_name} (and subthreads)')

    if (os.path.isfile(f'{path}/pidstat_mem.csv')):
        pidstat_mem_headers = ['Run', 'Time', 'UID', 'PID', 'minflt/s', 'majflt/s', 'VSZ (kB)', 'RSS (kB)', '"%"MEM', 'Command']
        pidstat_mem_df = pd.read_csv(f'{path}/pidstat_mem.csv', verbose=True, names=pidstat_mem_headers)
        pidstat_mem_df['Time'] = pd.to_datetime(pidstat_mem_df['Time'])
        pidstat_mem_df['seconds'] = pidstat_mem_df['Time'].dt.strftime("%H:%M:%S")
        pidstat_mem_df.set_index('seconds')
        pidstat_mem_ax = pidstat_mem_df.plot(kind='line', x='seconds', y=['minflt/s', 'majflt/s', 'VSZ (kB)', 'RSS (kB)'])
        plt.xlabel('time (hour:minute:second)')
        plt.ylabel('Size (kB)')
        plt.title(f'pidstat 1 -r | grep {process_name} (and subthreads)')
        pidstat_mem_ax2 = pidstat_mem_df.plot(kind='line', x='seconds', y=['"%"MEM'], ylim=[0, 110])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Relative memory usage (%)')
        plt.title(f'pidstat 1 -r | grep {process_name} (and subthreads)')        

    sys.stdout = old_stdout

    if (os.path.isfile(f'{path}/sar_r.csv')):
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
        sar_r_df.plot(kind='line', style=style_list, markevery=markevery, x='seconds', y=['kbmemfree', 'kbavail', 'kbmemused', 'kbbuffers', 'kbcached', 'kbcommit', 'kbactive', 'kbinact', 'kbdirty', 'kbanonpg', 'kbslab', 'kbkstack', 'kbpgtbl', 'kbvmused'])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Size (kB)')
        plt.title('sar -r ALL 1')
        sar_r_df.plot(kind='line', x='seconds', y=['"%"memused', '"%"commit'], ylim=[0, 110])
        plt.xlabel('Time (hour:minute:second)')
        plt.ylabel('Percentage (%)')
        plt.title('sar -r ALL 1')

    # if (os.path.isfile(f'{path}/iostat_d.csv')):
    #     iostat_d_headers = ['Run', 'Date', 'Time', 'Device', 'tps', 'kB_read/s', 'kB_wrtn/s', 'kB_dscrded/s', 'kB_read', 'kB_wrtn', 'kB_dscrded']
    #     iostat_d_df = pd.read_csv(f'{path}/iostat_d.csv', verbose=True, names=iostat_d_headers)
    #     iostat_d_df['Time'] = pd.to_datetime(iostat_d_df['Time'])
    #     iostat_d_df['seconds'] = iostat_d_df['Time'].dt.strftime("%H:%M:%S")
    #     iostat_d_df.set_index('Time')
    #     iostat_d_ax = iostat_d_df.plot(kind='line', x='seconds', y=['tps', 'kB_read/s', 'kB_wrtn/s', 'kB_dscrded/s', 'kB_read', 'kB_wrtn', 'kB_dscrded'])
    #     plt.xlabel('Time (hour:minute:second)')
    #     plt.ylabel('Size (kB)')
    #     plt.title('iostat -td -p sda 1')

    # if (os.path.isfile(f'{path}/iostat_xd.csv')):
    #     iostat_xd_headers = ['Run', 'Date', 'Time', 'Device', 'read reqs per s', 'rkB/s', 'rrqm/s', '"%"rrqm', 'r_await', 'rareq-sz', 'write reqs per s', 'wkB/s', 'wrqm/s', '"%"wrqm',\
    #                         'w_await', 'wareq-sz', 'd/s', 'dkB/s', 'drqm/s', '"%"drqm', 'd_await', 'dareq-sz', 'f/s', 'f_await', 'aqu-sz', '"%"util']
    #     iostat_xd_df = pd.read_csv(f'{path}/iostat_xd.csv', verbose=True, names=iostat_xd_headers)
    #     iostat_xd_df['Time'] = pd.to_datetime(iostat_xd_df['Time'])
    #     iostat_xd_df['seconds'] = iostat_xd_df['Time'].dt.strftime("%H:%M:%S")
    #     iostat_xd_df.set_index('seconds')
    #     iostat_xd_ax = iostat_xd_df.plot(kind='line', x='seconds', y=['read reqs per s', 'rkB/s', 'rrqm/s', '"%"rrqm', 'r_await', 'rareq-sz', 'write reqs per s'])
    #     plt.xlabel('Time (hour:minute:second)')
    #     plt.ylabel('Count')
    #     plt.title('iostat -txd -p sda 1')
    
    sys.stdout = old_stdout

    print("Plotting graphs, press Ctrl+C and Alt+Tab to clear...")
    plt.show()

if __name__ == "__main__":
   main(sys.argv[1:])