#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

int disk_load(int n)
{
  FILE *file;
  int size = 5;
  int numbers[size];
  char file_name[] = "numbers.bin";
  size_t result;

  for (int i = 0; i < size; i++)
  {
    numbers[i] = 10;
  }
  for (int i = 0; i < n; i++)
  {
    file = fopen(file_name, "w");
    result = fwrite(numbers, sizeof(int), size, file);
    if (fclose(file) != 0) {return -1;}

    file = fopen(file_name, "r");
    if (fclose(file) != 0) {return -1;}
  }

  return 0;
}

int main(void)
{
  clock_t t;
  t = clock();
  disk_load(100000);
  t = clock() - t;
  double time_taken_tot = ((double)t) / CLOCKS_PER_SEC;      // in seconds
  printf("%f", time_taken_tot);
  return 0;
}