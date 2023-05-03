# Performance evaluation tool

## Setup

1. Run `git clone https://github.com/DanielWestberg/thesis.git`
2. Run `cd thesis`
3. Run `sudo apt install -y linux-tools-common linux-tools-generic sysstat stress`
4. Run `pip install -r requirements.txt`
5. Run `git clone https://github.com/brendangregg/FlameGraph.git`
6. Edit `config.json` to run the script with your preferable configuration.
7. Run `make` to run the script

You might need to install more tools in order for the script to work.

## config.json explanation

<pre>
"process_name":     The process to be observed
"app_path":         Absolute path to the application. Necessary if run command is an executable
"pre_run_command":  Optional command to be run before the run command. Leave blank if none
"run_command":      The command to be run when starting the observability tools
"is_executable":    "yes" if run_command is an executable (ex: "./app"), "no" if not
"noise_type":       "cpu", "memory", "disk", "io" or "none". Multiple can be chosen (except "none") by adding comma (ex: "cpu, io")
"noise_workers":    Number of workers you want to use for the noise
"cpu_isolation":    Number/index of the CPU you want to isolate the process on. Groups/sets of CPUs are not supported
"all_cpus":         "yes" or "no". If "yes", the process will run on all CPUs and ignore the CPU isolation
"plot_graphs":      "yes" or "no". If "yes", graphs containing data over the application's runtime will be displayed
"n_iterations":     Number of iterations to perform the run command
</pre>

## Only display data

Run `python3 score.py 'run_path' 'process_name' 'n_cpus' 'plot_graphs'` to see the data for a specific run, either all iterations or a single one, where

- `'run_path'` is the path to the outputs of the specific run, e.g. `/home/user/thesis/output/20230101_010101` or `/home/user/thesis/output/20230101_010101/2`
- `'process_name'` is the name of the process to be observed, same as in config.json
- `'n_cpus'` is the number of CPUs used (not just by the app) by the computer during the application's runtime
- `'plot_graphs'` is wheter or not the python program should plot graphs or not, specified by either `yes` or `no`
