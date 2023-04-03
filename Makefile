C_COMPILER		= gcc
C_OPTIONS		= -g -c -Wall
GPROF			= -pg
VAL				= valgrind --leak-check=full -v
SHELL			:=/bin/bash

all:
	sudo ./script.sh

run_thesis_app: thesis_app
	./thesis_app

thesis_app: thesis_app.o
	$(C_COMPILER) $(GPROF) thesis_app.o -o thesis_app

thesis_app.o: thesis_app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) thesis_app.c -o thesis_app.o

gprof_thesis_app: thesis_app
	gprof -b ./thesis_app gmon.out

clean:
	sudo rm *.o *.txt *.pdf *.svg *.bin *.data *.data.old gmon.out thesis_app

clean_output:
	sudo rm -rf output/*

clean_all: clean_output clean