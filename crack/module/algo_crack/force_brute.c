#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include "CE.h"

int main(int argc, char** argv) {
    if (argc != 7) {
        fprintf(stderr, "Usage: %s Px Py Bx By a p\n", argv[0]);
        return 1;
    }
    
    CE CEstand = {0};
    Point P = {0}, B = {0};
    char *endptr;
    
    P.CE = B.CE = &CEstand;
    P.x = strtoul(argv[1], &endptr, 10); P.y = strtoul(argv[2], &endptr, 10);
    B.x = strtoul(argv[3], &endptr, 10); B.y = strtoul(argv[4], &endptr, 10);
    CEstand.a = strtoul(argv[5], &endptr, 10); CEstand.p = strtoul(argv[6], &endptr, 10);
    
    Point P2 = etoile(P, B);
    printf("%lu,%lu\n", P2.x, P2.y);
    return 0;
}
