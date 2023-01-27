C_COMPILER		= gcc
C_OPTIONS		= -g -c -Wall
GPROF			= -pg
VAL				= valgrind --leak-check=full -v
SHELL			:=/bin/bash

all: thesis_app
	./script.sh
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
	rm *.o *.txt thesis_app numbers.bin perf.data

tabs:
	./script.sh