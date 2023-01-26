C_COMPILER     = gcc
C_OPTIONS      = -g -c -Wall
CUNIT_LINK     = -lcunit -pg
TEST           = valgrind --leak-check=full -v

run: app
	./app

app: app.o
	$(C_COMPILER) app.o -o app

app.o: app.c
	$(C_COMPILER) $(C_OPTIONS) app.c -o app.o

clean:
	rm *.o
# gmon.out a.out