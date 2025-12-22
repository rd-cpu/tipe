#include "include/CE.h"

uint64_t modmul(uint64_t a, uint64_t b, uint64_t mod) {
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

uint64_t fp(Point P) {
    uint64_t p = P.CE->p;
    return (3 * modmul(P.x, P.x, p) + P.CE->a) % p;  // Modularité !
}
uint64_t inv_mod(uint64_t a, uint64_t b)
{
	int64_t b0 = b, t, q;
	int64_t x0 = 0, x1 = 1;
	if (b == 1) return 1;
	while (a > 1) {
		q = a / b;
		t = b, b = a % b, a = t;
		t = x0, x0 = x1 - q * x0, x1 = t;
	}
	if (x1 < 0) x1 += b0;
	return x1;
}

Point moins(Point P) {
    P.y = (P.CE->p -P.y) % P.CE->p;
    return P;
}

Point etoile(Point P1, Point P2) {
    Point P3 = {0};  // Initialisation !
    uint64_t p = P1.CE->p;
    P3.CE = P1.CE;

    if (P1.infini) return moins(P2);
    if (P2.infini) return moins(P1);

    uint64_t lambda;

    if (P1.x == P2.x) {
        if (P1.y != P2.y || P1.y == 0) {
            P3.infini = 1;
            return P3;
        }
        uint64_t num = (3 * modmul(P1.x, P1.x, p) + P1.CE->a) % p;
        uint64_t den = (2 * P1.y) % p;
        lambda = modmul(num, inv_mod(den, p), p);
    } else {
        uint64_t num = (P2.y - P1.y) % p;
        uint64_t den = (P2.x - P1.x) % p;
        lambda = modmul(num, inv_mod(den, p), p);
    }

    P3.x = (modmul(lambda, lambda, p) + p - P1.x + p - P2.x) % p;
    // P3.y = (modmul(lambda, (P1.x + p - P3.x) % p, p) + p - P1.y) % p;
    P3.y = (modmul(lambda, P3.x, p) + p - modmul(lambda, P1.x, p) + P1.y) % p;

    P3.infini = 0;
    return P3;
}

Point plus(Point P,Point Q) {
    Point R = etoile(P,Q);
    R.y = R.CE->p - R.y;
    return R;
}
/*
static inline uint64_t add_mod(uint64_t a, uint64_t b, uint64_t p) {
    a += b;
    return (a >= p) ? a - p : a;
}

static inline uint64_t sub_mod(uint64_t a, uint64_t b, uint64_t p) {
    return (a >= b) ? (a - b) : (a + p - b);
}


Point plus(Point P, Point Q) {
    Point R = {0};
    uint64_t p = P.CE->p;
    R.CE = P.CE;

    //  Cas du point à l'infini 
    if (P.infini) return Q;
    if (Q.infini) return P;

    // P + (-P) = O 
    if (P.x == Q.x && P.y == sub_mod(0, Q.y, p)) {
        R.infini = 1;
        return R;
    }

    uint64_t lambda;

    // Doublement 
    if (P.x == Q.x && P.y == Q.y) {
        if (P.y == 0) {
            R.infini = 1;
            return R;
        }
        uint64_t num = add_mod(modmul(3, modmul(P.x, P.x, p), p), P.CE->a, p);
        uint64_t den = modmul(2, P.y, p);
        lambda = modmul(num, inv_mod(den, p), p);
    }
    // Addition générale 
    else {
        uint64_t num = sub_mod(Q.y, P.y, p);
        uint64_t den = sub_mod(Q.x, P.x, p);
        lambda = modmul(num, inv_mod(den, p), p);
    }

    R.x = sub_mod(modmul(lambda, lambda, p), add_mod(P.x, Q.x, p), p);

    uint64_t dx = sub_mod(P.x, R.x, p);
    R.y = sub_mod(modmul(lambda, dx, p), P.y, p);

    R.infini = 0;
    return R;
}
*/
