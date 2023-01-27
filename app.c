#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void memory_load(int n)
{
  int *ptr;
  for (int i = 0; i < n; i++)
  {
    ptr = (int *)malloc(sizeof(int));
    free(ptr);
  }
  printf("Allocated and free'd %d times\n", n);
}

int disk_load(int n)
{
  int size = 5;
  int sum = 0;
  FILE *file;
  int numbers[size];
  char file_name[] = "numbers.bin";
  // This variable will store the result of writing/reading
  size_t result;

  for (int i = 0; i < size; i++)
  {
    numbers[i] = 10;
  }
  for (int i = 0; i < n; i++)
  {
    sum = 0;
    /* Opening the file for writing*/
    file = fopen(file_name, "w");
    if (file == NULL)
    {
      printf("Error when opening file for writing.\n");
      return -1;
    }
    // Writing a block of data
    result = fwrite(numbers, sizeof(int), size, file);
    if (result != size)
    {
      printf("The %d numbers have not been written.\n", size);
    }

    if (fclose(file) != 0)
    {
      printf("Error when closing file.\n");
      return -1;
    }

    /* Open for reading */
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

    if (fclose(file) != 0)
    {
      printf("Error when closing file.\n");
      return -1;
    }
  }
  printf("The sum of numbers is: %d\n", sum);
  printf("Opened, wrote to disk (file) and closed %d times\n", n);

  return 0;
}

void calculation(int n)
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

  printf("dim of matrix a: %d\n", n);
  printf("dim of matrix b: %d\n", n);
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
  printf("\n");
}

int main(void)
{
  // int i = 0;
  // while (i < 3000000)
  // {
  //   i++;
  //   printf("%d\n", i);
  // }
  clock_t t;
  clock_t memt;
  clock_t diskt;
  clock_t calct;

  t = clock();
  printf("\n===== Memory allocation =====\n");
  memory_load(1000000000);
  memt = clock() - t;
  printf("\n===== Write to disk =====\n");
  disk_load(100000);
  diskt = clock() - t - memt;
  printf("\n===== Matrix multiplication =====\n");
  calculation(800);
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