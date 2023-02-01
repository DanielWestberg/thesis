C_COMPILER		= gcc
C_OPTIONS		= -g -c -Wall
GPROF			= -pg
VAL				= valgrind --leak-check=full -v
SHELL			:=/bin/bash

all: thesis_app
	sudo ./script.sh
	./thesis_app

run: thesis_app
	./thesis_app

thesis_app: thesis_app.o
	$(C_COMPILER) thesis_app.o -o thesis_app

thesis_app.o: thesis_app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) thesis_app.c -o thesis_app.o

gprof: thesis_app
	gprof ./thesis_app | less

clean:
	sudo rm *.o *.txt thesis_app numbers.bin perf.data perf.data.old

clean_output:
	sudo rm -rf output/*

tabs:
	sudo ./script.sh