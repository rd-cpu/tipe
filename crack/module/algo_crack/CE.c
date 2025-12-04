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
    P.y = -P.y % P.CE->p;
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
        uint64_t lambda_num = P1.fp;
        uint64_t lambda_den = (2 * P1.y);
        uint64_t inv_den = inv_mod(lambda_den, p);
        /*P3.x = (modmul(inv_den, lambda_num, p) * inv_den % p * inv_den % p + p - 2 * P1.x + p) % p; // CORRIGÉ
        P3.y = (modmul(inv_den, lambda_num, p) * (P1.x + p - P3.x) % p + p - P1.y) % p; // CORRIGÉ*/
        lambda = modmul(lambda_num, inv_den, p);  // lambda = num/den
    } else {
        uint64_t lambda_num = ((P2.y - P1.y) % p);
        uint64_t lambda_den = ((P2.x - P1.x) % p);
        uint64_t inv_den = inv_mod(lambda_den, p);
        lambda = modmul(lambda_num, inv_den, p);
    }
    P3.x = (modmul(lambda, lambda, p) - P1.x - P2.x) % p;
    P3.y = (modmul(lambda, P3.x, p) - modmul(lambda, P1.x,p)+P1.y);
    
    P3.fp = fp(P3);
    P3.infini = 0;
    return P3;
}

Point plus(Point P, Point Q) {
    Point R = etoile(P,Q);
    R.y = (-R.y) % P.CE->p;
    return R;
}
