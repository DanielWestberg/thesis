#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

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
  t = clock();
  matrix_mult(800);
  t = clock() - t;
  double time_taken_tot = ((double)t) / CLOCKS_PER_SEC;      // in seconds
  printf("%f", time_taken_tot);
  return 0;
}