C_COMPILER		= gcc
C_OPTIONS		= -g -c -Wall
GPROF			= -pg
VAL				= valgrind --leak-check=full -v
SHELL			:=/bin/bash

all:
	sudo ./script.sh
	
run: thesis_app
	./thesis_app

thesis_app: thesis_app.o
	$(C_COMPILER) $(GPROF) thesis_app.o -o thesis_app

thesis_app.o: thesis_app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) thesis_app.c -o thesis_app.o

gprof: thesis_app
	gprof -b ./thesis_app gmon.out

visuals:
	./visuals.sh

clean:
	sudo rm *.o *.txt *.pdf thesis_app numbers.bin perf.data perf.data.old gmon.out 

clean_output:
	sudo rm -rf output/*
