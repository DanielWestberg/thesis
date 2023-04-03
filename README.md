# Performance evaluation tool

1. Run `git clone https://github.com/DanielWestberg/thesis.git`
2. Run `cd thesis`
3. Run `sudo apt install -y linux-tools-common linux-tools-generic sysstat stress`
4. Run `pip install -r requirements.txt`
5. Run `git clone https://github.com/brendangregg/FlameGraph.git`
6. Edit `config.json` to run the script with your preferable configuration.
7. Run `make`

You might need to install more tools in order for the script to work.

## config.json explanation
* "process_name": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; The process to be observed
* "app_path": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Absolute path to the application. Necessary if run command is an executable
* "pre_run_command": &nbsp; Optional command to be run before the run command. Leave blank if none
* "run_command": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; The command to be run when starting the observability tools
* "is_executable": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "yes" if run_command is an executable (ex: "./app"), "no" if not
* "noise": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "cpu", "memory", "disk", "io" or "none". Multiple can be chosen (except "none") by adding comma (ex: "cpu, io")
* "cpu_isolation": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Number/index of the CPU you want to isolate the process on. Groups/sets of CPUs are not supported
* "all_cpus": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "yes" or "no". If "yes", the process will run on all CPUs and ignore the CPU isolation
* "plot_graphs": &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "yes" or "no". If "yes", graphs containing data over the application's runtime will be displayed

Run `python3 score.py 'run_path' 'process_name' 'n_cpus' 'plot_graphs'` to see the data for a specific run, where
* `'run_path'` is the path to the outputs of the specific run, e.g. `/home/user/thesis/output/20230101_010101`
* `'process_name'` is the name of the process to be observed, same as in config.json
* `'n_cpus'` is the number of CPUs used (not just by the app) by the computer during the application's runtime
* `'plot_graphs'` is wheter or not the python program should plot graphs or not, specified by either `yes` or `no`