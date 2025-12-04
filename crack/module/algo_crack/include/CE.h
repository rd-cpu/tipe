#ifndef CE_H
#define CE_H
#include <stdio.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdlib.h>
uint64_t modmul(uint64_t a, uint64_t b, uint64_t mod);
uint64_t modpow(uint64_t base, uint64_t exp, uint64_t mod);

typedef struct{
    uint64_t a, b, p;
} CE;

typedef struct {
    uint64_t x, y, fp;
    int infini;
    CE* CE;
} Point;

uint64_t fp(Point P);

uint64_t inv_mod(uint64_t e, uint64_t p);

Point etoile(Point P1, Point P2);

Point plus(Point P, Point Q);
#endif