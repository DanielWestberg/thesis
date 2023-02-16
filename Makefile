C_COMPILER		= gcc
C_OPTIONS		= -g -c -Wall
GPROF			= -pg
VAL				= valgrind --leak-check=full -v
SHELL			:=/bin/bash

all:
	sudo ./script.sh

compile: thesis_app mem_app cpu_app disk_app


run_thesis_app: thesis_app
	./thesis_app

thesis_app: thesis_app.o
	$(C_COMPILER) $(GPROF) thesis_app.o -o thesis_app

thesis_app.o: thesis_app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) thesis_app.c -o thesis_app.o

gprof_thesis_app: thesis_app
	gprof -b ./thesis_app gmon.out


run_mem_app: mem_app
	./mem_app

mem_app: mem_app.o
	$(C_COMPILER) $(GPROF) mem_app.o -o mem_app

mem_app.o: mem_app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) mem_app.c -o mem_app.o

gprof_mem: mem_app
	gprof -b ./mem_app gmon.out


run_cpu_app: cpu_app
	./cpu_app

cpu_app: cpu_app.o
	$(C_COMPILER) $(GPROF) cpu_app.o -o cpu_app

cpu_app.o: cpu_app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) cpu_app.c -o cpu_app.o

gprof_cpu: cpu_app
	gprof -b ./cpu_app gmon.out


run_disk_app: disk_app
	./disk_app

disk_app: disk_app.o
	$(C_COMPILER) $(GPROF) disk_app.o -o disk_app

disk_app.o: disk_app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) disk_app.c -o disk_app.o

gprof_disk: disk_app
	gprof -b ./disk_app gmon.out


visuals:
	./visuals.sh

clean:
	sudo rm *.o *.txt *.pdf *.svg *.bin *.data *.data.old gmon.out thesis_app mem_app cpu_app disk_app

clean_output:
	sudo rm -rf output/*

clean_all: clean_output clean