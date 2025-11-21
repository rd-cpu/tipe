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
    return 3*P.x + Courbe.a;
}

u_int64_t inv_mod(u_int64_t e, u_int64_t p) {
    u_int64_t unm1= 1;
    u_int64_t un = 0;
    u_int64_t vnm1= 0;
    u_int64_t vn = 1;
    u_int64_t a = p;
    u_int64_t b = e % p;
    while (b != 0) {
        u_int64_t q = a / b;
        u_int64_t r =  a % b;
        u_int64_t temp1 = unm1;
        u_int64_t temp2 = vnm1;
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
    u_int64_t lambda;
    P3.CE = P1.CE;
    if (P1.x == P2.x) {
        if (P1.y != P2.y || P1.y == 0) {
            P3.infini = 1;
        } else {
            P3.infini = 0;
            lambda = P1.fp * inv_mod(2*P1.y, P1.CE->p);
        }
    } else {
        P3.infini = 0;
        lambda = (P2.x - P1.x) * inv_mod(P2.y - P1.y, P1.CE->p);
    }
    P3.x = (lambda*lambda - P1.CE->a - P1.x - P2.x)%P3.CE->p;
    P3.y = (lambda * P3.x - lambda * P1.x + P1.y)%P3.CE->p;
    return P3;
}

Point plus(Point P, Point Q) {
    Point P3 = etoile(P,Q);
    P3.y = -P3.y;
}

u_int64_t log_discret_force_brute(Point P,Point Q) {
    Point R = P;
    u_int64_t x = 1;
    while (R.x != Q.x && R.y != Q.y) {
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