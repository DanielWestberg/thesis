# Performance evaluation tool

1. Run `sudo apt install -y linux-tools-common cpupower sysstat stress`
2. Run `pip install -r requirements.txt`
3. Edit `config.json` to run the script with your preferable configuration.
4. Run `make`

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
