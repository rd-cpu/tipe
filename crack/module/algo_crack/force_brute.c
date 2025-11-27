#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

static inline uint64_t modmul(uint64_t a, uint64_t b, uint64_t mod) {
    return (uint64_t)(((__uint128_t)a * (__uint128_t)b) % mod);
}

uint64_t modpow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp) { 
        if (exp & 1) res = modmul(res, base, mod);
        base = modmul(base, base, mod);
        exp >>= 1;
    }
    return res;
}

typedef struct {
    uint64_t a, b, p;  // TOUS uint64_t
} CE;

typedef struct {
    uint64_t x, y, fp;
    int infini;
    CE* CE;
} Point;

uint64_t fp(Point P) {
    uint64_t p = P.CE->p;
    return (3 * modmul(P.x, P.x, p) + P.CE->a) % p;  // Modularité !
}

uint64_t inv_mod(uint64_t e, uint64_t p) {
    int64_t a = (int64_t)p, b = (int64_t)(e % p);
    int64_t x0 = 1, x1 = 0;
    int64_t y0 = 0, y1 = 1;
    int64_t q, r, tmp;

    while (b != 0) {
        q = a / b; r = a % b;
        tmp = x1; x1 = x0 - q * x1; x0 = tmp;
        tmp = y1; y1 = y0 - q * y1; y0 = tmp;
        a = b; b = r;
    }
    if (a != 1) return 0;
    if (x0 < 0) x0 += p;
    return (uint64_t)x0;
}

Point etoile(Point P1, Point P2) {
    Point P3 = {0};  // Initialisation !
    uint64_t p = P1.CE->p, a = P1.CE->a;
    P3.CE = P1.CE;

    if (P1.infini) return P2;
    if (P2.infini) return P1;
    
    if (P1.x == P2.x) {
        if (P1.y != P2.y || P1.y == 0) {
            P3.infini = 1;
            return P3;
        }
        uint64_t lambda_num = (modmul(3, modmul(P1.x, P1.x, p), p) + a) % p;
        uint64_t lambda_den = (2 * P1.y) % p;
        uint64_t inv_den = inv_mod(lambda_den, p);
        if (!inv_den) { P3.infini = 1; return P3; }
        P3.x = (modmul(inv_den, lambda_num, p) * inv_den % p * inv_den % p + p - 2 * P1.x + p) % p; // CORRIGÉ
        P3.y = (modmul(inv_den, lambda_num, p) * (P1.x + p - P3.x) % p + p - P1.y) % p; // CORRIGÉ
    } else {
        uint64_t lambda_num = ((P2.y + p - P1.y) % p);
        uint64_t lambda_den = ((P2.x + p - P1.x) % p);
        uint64_t inv_den = inv_mod(lambda_den, p);
        if (!inv_den) { P3.infini = 1; return P3; }
        uint64_t lambda = modmul(lambda_num, inv_den, p);
        P3.x = (modmul(lambda, lambda, p) + p - P1.x + p - P2.x) % p;
        P3.y = (modmul(lambda, (P1.x + p - P3.x) % p, p) + p - P1.y) % p; // CORRIGÉ
    }
    P3.infini = 0;
    return P3;
}

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
