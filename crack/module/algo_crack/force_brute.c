#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <sys/types.h>


/* modular multiplication a * b % mod using 128-bit intermediate */
static inline uint64_t modmul(uint64_t a, uint64_t b, uint64_t mod) {
    return (uint64_t)(((__uint128_t)a * (__uint128_t)b) % mod);
}

/* modular exponentiation base^exp % mod */
uint64_t modpow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp) { 
        if (exp & 1) // <=> (exp % 2) = 1
			res = modmul(res, base, mod);
        base = modmul(base, base, mod);
        exp >>= 1; // <=> exp = exp/2 entière juste on décale les bits vers la droite
    }
    return res;
}

struct Point {
    u_int64_t x;
    u_int64_t y;
    u_int64_t p;  
};


int main(int argc, char** argv) {
    
    return 0;
}