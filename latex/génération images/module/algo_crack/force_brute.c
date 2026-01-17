#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <sys/types.h>
#include "include/CE.h"

int main(int argc, char** argv) { // P.x P.y B.x B.y CE.a CE.p
    if (argc != 7) {
        fprintf(stderr, "Usage: %s Px Py Bx By a p\n", argv[0]);
        return 1;
    }
    
    CE CEstand = {0};
    Point P = {0}, B = {0};
    char *endptr;
    
    P.CE = B.CE = &CEstand;
    P.x = strtoull(argv[1], &endptr, 10); P.y = strtoull(argv[2], &endptr, 10);
    B.x = strtoull(argv[3], &endptr, 10); B.y = strtoull(argv[4], &endptr, 10);
    CEstand.a = strtoull(argv[5], &endptr, 10); CEstand.p = strtoull(argv[6], &endptr, 10);
    P.infini = 0;   
    B.infini = 0;
    Point R = P;
    uint64_t s = 1;

    while ((R.x != B.x) && (R.y != B.y))  {
        R = plus(R,P);
        s++;
    }
    printf("%lu",s);
    return 0;
}
