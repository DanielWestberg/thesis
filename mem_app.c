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
}

int main(void)
{
  clock_t t;
  t = clock();
  memory_load(100000000);
  t = clock() - t;
  double time_taken_tot = ((double)t) / CLOCKS_PER_SEC;
  printf("%f", time_taken_tot);
  return 0;
}