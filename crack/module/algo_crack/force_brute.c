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

typedef struct {
    uint64_t a;
    uint64_t b;
    u_int64_t p;
} CE;

typedef struct {
    u_int64_t x;
    u_int64_t y;
    int infini;
    u_int64_t fp;
    CE* CE;
} Point;

u_int64_t fp(CE Courbe,Point P) {
    return 3*P.x*P.x+ Courbe.a;
}

u_int64_t inv_mod(u_int64_t e, u_int64_t p) {
    int64_t unm1= 1;
    int64_t un = 0;
    int64_t vnm1= 0;
    int64_t vn = 1;
    int64_t a = (int64_t) p;
    int64_t b = ((int64_t) e) % ((int64_t) p);
    while (b != 0) {
        int64_t q = a / b;
        int64_t r =  a % b;
        int64_t temp1 = unm1;
        int64_t temp2 = vnm1;
        unm1 = un;
        vnm1 = vn;
        un = -q*un + temp1;
        vn =  -q*vn + temp2;
        a = b;
        b = r;
    }
    if (unm1 < 0) unm1 += p;
    return (u_int64_t)unm1;
}

Point etoile(Point P1, Point P2) {
    Point P3;
    u_int64_t lambda_num, lambda_den, lambda;
    u_int64_t p = P1.CE->p;
    u_int64_t a = P1.CE->a;

    P3.CE = P1.CE;
    P3.infini = 0;

    if (P1.infini) return P2;
    if (P2.infini) return P1;

    if (P1.x == P2.x) {
        if (P1.y != P2.y || P1.y == 0) {
            P3.infini = 1;
            return P3;
        }
        lambda_num = (3 * modmul(P1.x, P1.x, p) + a) % p;
        lambda_den = (2 * P1.y) % p;
    } else {
        lambda_num = (P2.y + p - P1.y) % p;
        lambda_den = (P2.x + p - P1.x) % p;
    }

    u_int64_t inv_lambda_den = inv_mod(lambda_den, p);
    lambda = modmul(lambda_num, inv_lambda_den, p);

    P3.x = (modmul(lambda, lambda, p) + p - P1.x + p - P2.x) % p;
    P3.y = (modmul(lambda, (P1.x + p - P3.x) % p, p) + p - P1.y) % p;

    return P3;
}

Point plus(Point P, Point Q) {
    Point P3 = etoile(P,Q);
    P3.y = -P3.y;
    return P3;
}

u_int64_t log_discret_force_brute(Point P,Point Q) {
    Point R = P;
    u_int64_t x = 1;
    while (R.x != Q.x || R.y != Q.y) {
        R = plus(R,P);
        x++;
    }
    return x;
}

int main(int argc, char** argv) {
    Point P;
    Point B;
    CE CEstand;
    char *endptr;
    P.CE = &CEstand;
    B.CE = &CEstand;
    P.x = strtoul(argv[1],&endptr,10);
    P.y = strtoul(argv[2],&endptr,10);
    B.x = strtoul(argv[3],&endptr,10);
    B.y = strtoul(argv[4],&endptr,10);
    CEstand.a = strtoul(argv[5],&endptr,10);
    CEstand.p = strtoul(argv[6],&endptr,10);
    /*u_int64_t s = log_discret_force_brute(P,B);
    printf("%lu",s);*/
    Point P2 = etoile(P,B);
    printf("%lu,%lu\n",P2.x,P2.y);
    return 0;
}