#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

void memory_load(int n)
{
  int *ptr;
  for (int i = 0; i < n; i++)
  {
    ptr = (int *)malloc(sizeof(int) * 10);
    free(ptr);
  }
}

int disk_load(int n)
{
  FILE *file;
  // int size = 5;
  // int numbers[] = {10, 10, 10, 10, 10};
  // char file_name[] = "numbers.bin";
  char file_name[] = "file.txt";
  size_t result;

  // for (int i = 0; i < size; i++)
  // {
  //   numbers[i] = 10;
  // }
  for (int i = 0; i < n; i++)
  {
    file = fopen(file_name, "w");
    fprintf(file, "Write to disk...\n");
    // result = fwrite(numbers, sizeof(int), size, file);
    if (fclose(file) != 0)
    {
      return -1;
    }

    // file = fopen(file_name, "r");
    // if (fclose(file) != 0) {return -1;}
  }

  return 0;
}

void matrix_mult(int n)
{
  int a[n][n], b[n][n], mul[n][n], r, c, i, j, k;
  r = c = n;
  for (i = 0; i < r; i++)
  {
    for (j = 0; j < c; j++)
    {
      a[i][j] = 10;
      b[i][j] = 10;
    }
  }

  for (i = 0; i < r; i++)
  {
    for (j = 0; j < c; j++)
    {
      mul[i][j] = 0;
      for (k = 0; k < c; k++)
      {
        mul[i][j] += a[i][k] * b[k][j];
      }
    }
  }
}

int main(void)
{
  clock_t t;
  clock_t memt;
  clock_t diskt;
  clock_t calct;

  t = clock();
  memory_load(400000000);
  memt = clock() - t;
  disk_load(10000);
  diskt = clock() - t - memt;
  matrix_mult(830);
  // matrix_mult(2);
  calct = clock() - t - memt - diskt;
  t = clock() - t;
  double time_taken_mem = ((double)memt) / CLOCKS_PER_SEC;
  double time_taken_disk = ((double)diskt) / CLOCKS_PER_SEC;
  double time_taken_calc = ((double)calct) / CLOCKS_PER_SEC;
  double time_taken_tot = ((double)t) / CLOCKS_PER_SEC;

  printf("%f,%f,%f,%f", time_taken_mem, time_taken_disk, time_taken_calc, time_taken_tot);

  return 0;
}