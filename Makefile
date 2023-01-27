C_COMPILER		= gcc
C_OPTIONS		= -g -c -Wall
GPROF			= -pg
VAL				= valgrind --leak-check=full -v
SHELL			:=/bin/bash

run: app
	./app

app: app.o
	$(C_COMPILER) app.o -o app

app.o: app.c
	$(C_COMPILER) $(C_OPTIONS) $(GPROF) app.c -o app.o

gprof: app
	gprof ./app | less

clean:
	rm *.o *.txt app
