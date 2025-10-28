#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdlib.h>

int f(int a,int b,int c,int x) {
	return x*x*x + a*x*x + b*x + c;
}


/* modular multiplication a * b % mod using 128-bit intermediate to avoid overflow */
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


/* Tonelli-Shanks:
   Solve x^2 ≡ n (mod p). p odd prime.
   On success: store one root in *root (the other is p - *root) and return 0.
   If no root exists, return -1.
*/
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
		return -1; /* no solution */

    /* If p % 4 == 3, use simple formula: r = n^{(p+1)/4} (mod p) */
    if ((p & 3) == 3) {
        *root = modpow(n, (p + 1) >> 2, p);
        return 0;
    }

    /* Factor p-1 as q * 2^s with q odd */
    uint64_t q = p - 1;
    uint64_t s = 0;
    while ((q & 1) == 0) {
        q >>= 1;
        s += 1;
    }

    /* Find a quadratic non-residue z (Legendre(z,p) == -1) */
    uint64_t z = 2;
    while (legendre(z, p) != -1) {
        z++;
        /* In practice z will be found quickly; for safety we do not bound it here. */
    }

    uint64_t c = modpow(z, q, p);
    uint64_t r = modpow(n, (q + 1) >> 1, p);
    uint64_t t = modpow(n, q, p);
    uint64_t m = s;

    while (t != 1) {
        /* find smallest i (0 < i < m) such that t^{2^i} == 1 */
        uint64_t tt = t;
        uint64_t i = 0;
        for (i = 1; i < m; ++i) {
            tt = modmul(tt, tt, p);
            if (tt == 1) break;
        }
        /* b = c^{2^{m-i-1}} */
        uint64_t pow2 = 1ULL << (m - i - 1); /* safe because m-i-1 < 64 for reasonable primes */
        uint64_t b = modpow(c, pow2, p);
        r = modmul(r, b, p);
        c = modmul(b, b, p);
        t = modmul(t, c, p);
        m = i;
    }

    *root = r % p;
    return 0;
}


int main(){
	int a;
	int b;
	int c;
	int o;
	printf("Rentrez a : ");
	scanf("%d",&a);
	printf("Rentrez b : ");
	scanf("%d",&b);
	printf("Rentrez c : ");
	scanf("%d",&c);
	printf("Rentrez o : ");
	scanf("%d",&o);

	char filename[255];
	sprintf(filename,"pointsCEs/points_%d_%d_%d_%d.txt",a,b,c,o);

	FILE *file = fopen(filename, "w");
    	if (file == NULL) {
        	printf("Erreur d'ouverture du fichier.\n");
        return 1;
    	}

	for (int x = 0; x < o; x++) {
    	int fx_mod = f(a,b,c,x) % o;
    	if (fx_mod < 0) fx_mod += o;  // modulo positif

    	uint64_t y1, y2;
    	int has_root = tonelli_shanks(fx_mod, o, &y1);
    	if (has_root == 0) {
			y2 = o - y1; // l'autre racine

			// Écriture dans le fichier
			if (b == 0) {
				fprintf(file, "(%llu, %llu) from Courbe elliptique  y² = x³ + %dx² + %d mod %d\n",
						(unsigned long long)x, (unsigned long long)y1, a, c, o);
				if (y1 != y2) {
					fprintf(file, "(%llu, %llu) from Courbe elliptique  y² = x³ + %dx² + %d mod %d\n",
							(unsigned long long)x, (unsigned long long)y2, a, c, o);
				}
			} else {
				fprintf(file, "(%llu, %llu) from Courbe elliptique  y² = x³ + %dx² + %dx + %d mod %d\n",
						(unsigned long long)x, (unsigned long long)y1, a, b, c, o);
				if (y1 != y2) {
					fprintf(file, "(%llu, %llu) from Courbe elliptique  y² = x³ + %dx² + %dx + %d mod %d\n",
							(unsigned long long)x, (unsigned long long)y2, a, b, c, o);
				}
			}
    	}
	}

	printf("l'ensemble des points a été retranscrit dans le fichier %s\n",filename);

	return 0;
}
