from numba import cuda, int64, njit
import numpy as np
from module.courbe_el_final import *
from module.el_gamal import *
import math
from math import gcd
from random import randint
# ── Couche 0 : CPU ────────────────────────────────────────────────────────────

def flatten_point(P, courbe=None):
    c = courbe or P.courbe_el
    inf = (P == Infini(c))
    return (P.x if not inf else 0,
            P.y if not inf else 0,
            int(inf))

def point_to_array(P, courbe=None):
    x, y, inf = flatten_point(P, courbe)
    return np.array([x, y, inf], dtype=np.int64)


# ── Couche 1 : device functions ───────────────────────────────────────────────

@cuda.jit(device=True)
def modinv_gpu(a, p):
    old_r = a % p
    r     = p
    old_s = int64(1)
    s     = int64(0)
    while r != int64(0):
        q     = old_r // r
        old_r, r   = r, old_r - q * r
        old_s, s   = s, old_s - q * s
    result = old_s % p
    if result < int64(0):
        result += p
    return result

@cuda.jit(device=True)
def neg_gpu(x, y, inf):
    return (x, -y, inf)

@cuda.jit(device=True)
def etoile_gpu(x1, y1, inf1, x2, y2, inf2, a, p):
    if inf1 == 1:
        return neg_gpu(x2, y2, inf2)
    if inf2 == 1:
        return neg_gpu(x1, y1, inf1)

    if x1 == x2:
        if y1 != y2 or y1 == 0:
            return (int64(0), int64(0), int64(1))  
        lamb = (3 * x1 * x1 + a) % p * modinv_gpu(2 * y1 % p, p) % p
    else:
        lamb = (y1 - y2) % p * modinv_gpu((x1 - x2) % p, p) % p

    x3 = (lamb * lamb - x1 - x2) % p
    y3 = (lamb * (x3 - x1) + y1) % p
    return (x3, y3, int64(0))

@cuda.jit(device=True)
def ec_add_gpu(x1, y1, inf1, x2, y2, inf2, a, p):
    return neg_gpu(*etoile_gpu(x1, y1, inf1, x2, y2, inf2, a, p))

@cuda.jit(device=True)
def ec_double_gpu(x, y, inf, a, p):
    return neg_gpu(*etoile_gpu(x, y, inf, x, y, inf, a, p))

@cuda.jit(device=True)
def mult_by_int_gpu(k, x, y, inf, a, p):
    neg_result = False
    if k < 0:
        k = -k
        neg_result = True
    if k == 0:
        return (int64(0), int64(0), int64(1))

    rx, ry, rinf = int64(0), int64(0), int64(1)
    qx, qy, qinf = x, y, inf

    while k > 0:
        if k & 1:
            rx, ry, rinf = ec_add_gpu(rx, ry, rinf, qx, qy, qinf, a, p)
        qx, qy, qinf = ec_double_gpu(qx, qy, qinf, a, p)
        k >>= 1

    if neg_result:
        return neg_gpu(rx, ry, rinf)
    return (rx, ry, rinf)


# ── Couche 1b : host functions ───────────────────────────────────────────────

@njit
def modinv_cpu(a, p):
    old_r = a % p
    r     = p
    old_s = int64(1)
    s     = int64(0)
    while r != int64(0):
        q     = old_r // r
        old_r, r   = r, old_r - q * r
        old_s, s   = s, old_s - q * s
    result = old_s % p
    if result < int64(0):
        result += p
    return result

@njit
def neg_cpu(x, y, inf):
    return (x, -y, inf)

@njit
def etoile_cpu(x1, y1, inf1, x2, y2, inf2, a, p):
    if inf1 == 1:
        return neg_cpu(x2, y2, inf2)
    if inf2 == 1:
        return neg_cpu(x1, y1, inf1)

    if x1 == x2:
        if y1 != y2 or y1 == np.int64(0):
            return (int64(0), int64(0), int64(1))  
        lamb = (3 * x1 * x1 + a) % p * modinv_cpu(2 * y1 % p, p) % p
    else:
        lamb = (y1 - y2) % p * modinv_cpu((x1 - x2) % p, p) % p

    x3 = (lamb * lamb - x1 - x2) % p
    y3 = (lamb * (x3 - x1) + y1) % p
    return (x3, y3, int64(0))

@njit
def ec_add_cpu(x1, y1, inf1, x2, y2, inf2, a, p):
    return neg_cpu(*etoile_cpu(x1, y1, inf1, x2, y2, inf2, a, p))

@njit
def ec_double_cpu(x, y, inf, a, p):
    return neg_cpu(*etoile_cpu  (x, y, inf, x, y, inf, a, p))

@njit
def mult_by_int_cpu(k, x, y, inf, a, p):
    neg_result = False
    if k < 0:
        k = -k
        neg_result = True
    if k == 0:
        return (int64(0), int64(0), int64(1))

    rx, ry, rinf = int64(0), int64(0), int64(1)
    qx, qy, qinf = x, y, inf

    while k > 0:
        if k & 1:
            rx, ry, rinf = ec_add_cpu(rx, ry, rinf, qx, qy, qinf, a, p)
        qx, qy, qinf = ec_double_cpu(qx, qy, qinf, a, p)
        k >>= 1

    if neg_result:
        return neg_cpu(rx, ry, rinf)
    return (rx, ry, rinf)

# ── Couche 2 : Infrastructure kangourou sur GPU ───────────────────────────────────────────────

@njit
def hash_to_jump_index(x,r):
    return x % r

@njit
def is_distinguished(x, f):
    return (x & ((int64(1) << f) - int64(1))) == int64(0)


@njit
def precompute_jumps_cpu(x, y, jump_distances, p, a):
    n = jump_distances.shape[0]
    jumps = np.zeros((n, 3), dtype=np.int64)
    for i in range(n):
        ji = mult_by_int_cpu(jump_distances[i], x, y, np.int64(0), a, p)
        jumps[i][0] = ji[0]
        jumps[i][1] = ji[1]
        jumps[i][2] = ji[2]
    return jumps

