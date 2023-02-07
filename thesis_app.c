#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

void memory_load(int n)
{
  int *ptr;
  for (int i = 0; i < n; i++)
  {
    ptr = (int *)malloc(sizeof(int));
    free(ptr);
  }
  // printf("Allocated and free'd %d times\n", n);
}

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
    /* Opening the file for writing*/
    file = fopen(file_name, "w");

    result = fwrite(numbers, sizeof(int), size, file);
    if (fclose(file) != 0)
    {
      // printf("Error when closing file.\n");
      return -1;
    }

    file = fopen(file_name, "r");
    if (fclose(file) != 0)
    {
      // printf("Error when closing file.\n");
      return -1;
    }
  }
  // printf("The sum of numbers is: %d\n", sum);
  // printf("Opened file, wrote to it, and closed it %d times\n", n);

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

  // printf("dim of matrix a: %d\n", n);
  // printf("dim of matrix b: %d\n", n);
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
  // printf("\n");
}

int main(void)
{
  clock_t t;
  clock_t memt;
  clock_t diskt;
  clock_t calct;

  t = clock();
  // printf("\n===== Memory allocation =====\n");
  // memory_load(1000000000);
  memory_load(100000000);
  // memory_load(1);
  memt = clock() - t;
  // printf("\n===== Write to disk =====\n");
  // disk_load(100000);
  disk_load(100000);
  // disk_load(1);
  diskt = clock() - t - memt;
  // printf("\n===== Matrix multiplication =====\n");
  // matrix_mult(800);
  matrix_mult(800);
  // matrix_mult(8);
  calct = clock() - t - memt - diskt;
  t = clock() - t;
  double time_taken_mem = ((double)memt) / CLOCKS_PER_SEC;   // in seconds
  double time_taken_disk = ((double)diskt) / CLOCKS_PER_SEC; // in seconds
  double time_taken_calc = ((double)calct) / CLOCKS_PER_SEC; // in seconds
  double time_taken_tot = ((double)t) / CLOCKS_PER_SEC;      // in seconds

  printf("%f,%f,%f,%f", time_taken_mem, time_taken_disk, time_taken_calc, time_taken_tot);
  // printf("mem took        %f seconds to execute \n", time_taken_mem);
  // printf("disk took       %f seconds to execute \n", time_taken_disk);
  // printf("calc took       %f seconds to execute \n", time_taken_calc);
  // printf("everything took %f seconds to execute \n", time_taken_tot);

  return 0;

  // // ============ GNUPLOT ============

  // FILE *file;
  // char file_name[] = "data.txt";

  // file = fopen(file_name, "w");
  // // char *commandsForGnuplot[] = {"set title \"TITLEEEEE\"", "set xrange [-1:4]", "plot 'data.txt'"};
  // // FILE *gnuplotPipe = popen("gnuplot -persistent", "w");

  // fprintf(file, "%d\t%f\n", 1, time_taken_mem);
  // fprintf(file, "%d\t%f\n", 2, time_taken_disk);
  // fprintf(file, "%d\t%f\n", 3, time_taken_calc);
  // fprintf(file, "%d\t%f\n", 4, time_taken_tot);

  // // for (int i = 0; i < 3; i++)
  // // {
  // //   fprintf(gnuplotPipe, "%s \n", commandsForGnuplot[i]); // Send commands to gnuplot one by one.
  // // }

  // if (fclose(file) != 0)
  // {
  //   printf("Error when closing file.\n");
  //   return -1;
  // }
}