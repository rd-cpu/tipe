#ifndef CE_H
#define CE_H
#include <stdio.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdlib.h>
static inline uint64_t modmul(uint64_t a, uint64_t b, uint64_t mod);
uint64_t modpow(uint64_t base, uint64_t exp, uint64_t mod);


#endif