#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define SIZE 6

void memory_load()
{
  int *ptr;
  for (int i = 0; i < 1000000; i++)
  {
    ptr = (int *)malloc(sizeof(int));
    free(ptr);
  }
}

int disk_load()
{
  FILE *file;
  int numbers[SIZE] = {20, 20, 20, 20, 20, 20};
  char file_name[] = "numbers.bin";
  // This variable will store the result of writing/reading
  size_t result;

  /* Opening the file for writing*/
  file = fopen(file_name, "w");
  if (file == NULL)
  {
    printf("Error when opening file for writing.\n");
    return -1;
  }
  // Writing a block of data
  result = fwrite(numbers, sizeof(int), SIZE, file);
  if (result != SIZE)
  {
    printf("The %d numbers have not been written.\n", SIZE);
  }

  if (fclose(file) != 0)
  {
    printf("Error when closing file.\n");
    return -1;
  }

  /* Open for reading */
  int sum = 0;
  file = fopen(file_name, "r");
  if (file == NULL)
  {
    printf("Error when opening file for reading.\n");
    return -1;
  }
  // Reading number by number, not in block.
  int num;
  while (!feof(file))
  {
    result = fread(&num, sizeof(int), 1, file);
    if (result != 1)
    {
      break;
    }
    sum = sum + num;
  }

  if (ferror(file) != 0)
  {
    printf("An error has occurred while reading.\n");
  }
  else
  {
    printf("The sum of numbers is: %d\n", sum);
  }

  if (fclose(file) != 0)
  {
    printf("Error when closing file.\n");
    return -1;
  }
  return 0;
}

void calculation()
{
  int n = 10;
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

  printf("multiply of the matrix=\n");
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
  // for printing result
  for (i = 0; i < r; i++)
  {
    for (j = 0; j < c; j++)
    {
      printf("%d\t", mul[i][j]);
    }
    printf("\n");
  }
}

int main(void)
{
  clock_t t;
  clock_t memt;
  clock_t diskt;
  clock_t calct;
  t = clock();
  memory_load();
  memt = clock() - t;
  disk_load();
  diskt = clock() - t - memt;
  calculation();
  calct = clock() - t - memt - diskt;
  t = clock() - t;
  double time_taken_mem = ((double)memt) / CLOCKS_PER_SEC;   // in seconds
  double time_taken_disk = ((double)diskt) / CLOCKS_PER_SEC; // in seconds
  double time_taken_calc = ((double)calct) / CLOCKS_PER_SEC; // in seconds
  double time_taken_tot = ((double)t) / CLOCKS_PER_SEC;      // in seconds

  printf("mem took        %f seconds to execute \n", time_taken_mem);
  printf("disk took       %f seconds to execute \n", time_taken_disk);
  printf("calc took       %f seconds to execute \n", time_taken_calc);
  printf("everything took %f seconds to execute \n", time_taken_tot);
  return 0;
}