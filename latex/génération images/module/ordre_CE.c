#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <inttypes.h>  // ← indispensable pour PRIu64

uint64_t f(int a, int b, int c, uint64_t x) {
    return (uint64_t)x*x*x + (uint64_t)a*x*x + (uint64_t)b*x + (uint64_t)c;
}


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


/* Legendre symbol (a|p) via Euler's criterion:
   returns 1 if a is quadratic residue mod p (and a != 0),
           0 if a % p == 0,
          -1 if a is non-residue.
   p must be odd prime.
   legendre(a,p) -> (x^((p-1)/2)) mod p
*/
int legendre(uint64_t a, uint64_t p) {
    if (a % p == 0) return 0;
    uint64_t ls = modpow(a, (p - 1) >> 1, p);
    if (ls == 1) return 1;
    if (ls == p - 1) return -1;
    return 0; /* should not happen for prime p */
}

/*
/* Tonelli-Shanks:
   Solve x^2 ≡ n (mod p). p odd prime.
   On success: store one root in *root (the other is p - *root) and return 0.
   If no root exists, return -1.

int tonelli_shanks(uint64_t n, uint64_t p, uint64_t *root) {
    n %= p;
    if (p == 2) {
		*root = n;
		return 0;
	}
    if (n == 0) {
		*root = 0;
		return 0;
	}

    int leg = legendre(n, p);
    if (leg == -1) 
		return -1; // no solution

    //  If p % 4 == 3, use simple formula: r = n^{(p+1)/4} (mod p) 
    if ((p & 3) == 3) {
        *root = modpow(n, (p + 1) >> 2, p);
        return 0;
    }

    // Factor p-1 as q * 2^s with q odd 
    uint64_t q = p - 1;
    uint64_t s = 0;
    while ((q & 1) == 0) {
        q >>= 1;
        s += 1;
    }

    // Find a quadratic non-residue z (Legendre(z,p) == -1) 
    uint64_t z = 2;
    while (legendre(z, p) != -1) {
        z++;
        // In practice z will be found quickly; for safety we do not bound it here. 
    }

    uint64_t c = modpow(z, q, p);
    uint64_t r = modpow(n, (q + 1) >> 1, p);
    uint64_t t = modpow(n, q, p);
    uint64_t m = s;

    while (t != 1) {
        // find smallest i (0 < i < m) such that t^{2^i} == 1
        uint64_t tt = t;
        uint64_t i = 0;
        for (i = 1; i < m; ++i) {
            tt = modmul(tt, tt, p);
            if (tt == 1) break;
        }
        // b = c^{2^{m-i-1}} 
        uint64_t pow2 = 1ULL << (m - i - 1); // safe because m-i-1 < 64 for reasonable primes
        uint64_t b = modpow(c, pow2, p);
        r = modmul(r, b, p);
        c = modmul(b, b, p);
        t = modmul(t, c, p);
        m = i;
    }

    *root = r % p;
    return 0;
}
*/


int main(int argc, char* argv[]){
    if (argc != 5) {
        printf("Usage: %s a b c p\n", argv[0]);
        return 1;
    }
	int a = atoi(argv[1]);
	int b = atoi(argv[2]);
	int c = atoi(argv[3]);
    uint64_t o = strtoull(argv[4], NULL, 10);
    uint64_t i = 0;
    uint64_t x;
    for (uint64_t x = 0; x < o; x++) {
        uint64_t fx_mod = f(a,b,c,x) % o;
        int ls = legendre(fx_mod, o);
        if (ls == 1)
            i += 2;
        else if (ls == 0)
            i += 1;
    }
    i++;
    printf("%" PRIu64 "\n", i);
    return 0;
}
