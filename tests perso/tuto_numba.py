#conda activate cuda_env

import numpy as np
from numba import cuda

@cuda.jit
def add(r,x,y):
    i = cuda.grid(1)
    if i<len(r):
        r[i] = x[i] + y[i]

'''x = np.arange(10)
y = x * 2
r = np.zeros_like(x)
print("r = ",r)
config = (1, 32)
add[config](r,x,y)
print("r = ",r)'''

def add_main(r,x,y):
  for i in range(len(x)):
    r[i]= x[i]+y[i]

'''x = np.arange(10)
y = x * 2
r = np.zeros_like(x)

print("r = ",r)
add_main(r,x,y)
print("r = ",r)
'''

def prodmat(m1,m2):
  n = len(m1)
  m3 = [[0]*n for i in range(n)]
  for i in range(n):
    for j in range(n):
      for k in range(n):
          m3[i][j] += m1[i][k]*m2[k][j]
  return m3

'''
m1 = [[1,2,3],[1,2,3],[1,2,3]]
m2 = [[1,2,3],[1,2,3],[1,2,3]]
id = [[1,0,0],[0,1,0],[0,0,1]]
'''


def printmat(m):
  for e in m:
    print(e)

'''printmat(prodmat(m1,m2))
printmat(prodmat(m1,id))'''

@cuda.jit
def prodmat_cuda(m,m1,m2):
    n = m.shape[0]
    p = cuda.grid(1)
    i = p//n
    j = p%n
    if p<n**2:
        for k in range(n):
            m[i,j] += m1[i,k]*m2[k,j]

#m1 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.float32)
#m2 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.float32)
#id = np.array([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float32)
#m3 = np.array([[0,0,0],[0,0,0],[0,0,0]],dtype=np.float32)
#
#printmat(m1)
#d_m1 = cuda.to_device(m1)
#d_m2 = cuda.to_device(m2)
#d_m3 = cuda.to_device(m3)
#
#config = (3,3)
#prodmat_cuda[config](d_m3,d_m1,d_m2)
#
#m3 = d_m3.copy_to_host()
#print("m3 = ",m3)

def max(v):
  m = v[0]
  for e in v:
    if e>m:
      m = e
  return m

@cuda.jit
def normal(vr,v,m):
  n = vr.shape[0]
  i = cuda.grid(1)
  if i<n:
    vr[i]=v[i]/m

'''v = np.array([1,2,3,4,5,6,7],dtype=np.float32)
vr = np.array([0,0,0,0,0,0,0],dtype=np.float32)



print("v = ",v)
config = (1, 9)
m = max(v)
normal[config](vr,v,m)
print("vr= ",vr)
'''


@cuda.jit
def prodhad(m,m1,m2):
  n = m.shape[1]
  i,j = cuda.grid(2)
  if i<n and j<n :
    m[i,j] =m1[i,j]*m2[i,j]

'''m1 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.float32)
m2 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.float32)
id = np.array([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float32)
m3 = np.array([[0,0,0],[0,0,0],[0,0,0]],dtype=np.float32)
'''

'''print("m3 = ",m)
config = (1, (3,3))
prodhad[config](m3,m1,m2)
print("m3 = ",m3)
'''


@cuda.jit
def sommevect(ls,v):
  n = ls.shape[0]
  m = v.shape[0]
  i = cuda.grid(1)
  if i<n:
    k = (m//n)*i
    for j in range(m//n):
      ls[i] += v[k+j]

def somme_cpu(ls):
  s = 0
  for e in ls:
    s+=e
  return s

'''v = np.linspace(0,11,12,dtype=np.float32)
ls = np.zeros(3,dtype=np.float32)
config = (1,4)
print("ls = ",ls)
print("v = ",v)
sommevect[config](ls,v)
print("ls = ",ls)
s = somme_cpu(ls)
print(s)
'''

def somme(v):
  k = 0
  for e in v:
   k+=e
  return k

'''print(somme(v))
'''



@cuda.jit
def max_cuda(lm,v):
  n = lm.shape[0]
  m = v.shape[0]
  i = cuda.grid(1)
  if i<n:
    k = (m//n)*i
    lm[i] = v[k]
    for j in range(m//n):
      if v[k+j]>lm[i] :
        lm[i] = v[k+j]

def max(v):
  m = v[0]
  for e in v:
    if e>m:
      m = e
  return m

'''
v = np.linspace(0,11,12,dtype=np.float32)
lm = np.zeros(3,dtype=np.float32)
config = (1,4)
print("lm = ",lm)
print("v = ",v)
max_cuda[config](lm,v)
print("lm = ",lm)
s = max(lm)
print(s)
'''

@cuda.jit
def prodmat_cuda_2d(m,m1,m2):
  i,j = cuda.grid(2)
  n = m.shape[0]
  if i<n and j<n:
    s = 0
    for k in range(n):
      s+=m1[i,k]*m2[k,j]
    m[i,j] = s


#m1 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.float32)
#m2 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.float32)
#id = np.array([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float32)
#m3 = np.array([[0,0,0],[0,0,0],[0,0,0]],dtype=np.float32)
#
#printmat(m1)
#d_m1 = cuda.to_device(m1)
#d_m2 = cuda.to_device(m2)
#d_m3 = cuda.to_device(m3)
#
#config = [(1,1), (3,3)]
#prodmat_cuda_2d[config](d_m3,d_m1,d_m2)
#
#m3 = d_m3.copy_to_host()
#print("m3 = ",m3)


@cuda.jit
def somme(r,v):
  n = v.shape[0]
  i = cuda.grid(1)
  nb = cuda.gridDim.x 
  k = n//nb
  s = 0
  shared_array = cuda.shared.array(nb, dtype = np.int)


import numba as nb
import numpy as np

BLOCK_SIZE = 128

@cuda.jit
def sum_kernel(arr, partial_sums):
    shared = cuda.shared.array(BLOCK_SIZE, dtype=nb.float32)
    
    idx = cuda.grid(1)
    tid = cuda.threadIdx.x
    bid = cuda.blockIdx.x

    # Chaque thread charge son élément en shared memory
    if idx < arr.shape[0]:
        shared[tid] = arr[idx]
    else:
        shared[tid] = 0.0          # thread hors tableau → contribue 0

    cuda.syncthreads()             # attendre que tous les threads aient chargé

    # Réduction en arbre dans la shared memory
    stride = BLOCK_SIZE // 2
    while stride > 0:
        if tid < stride:
            shared[tid] += shared[tid + stride]
        cuda.syncthreads()         # synchroniser à chaque étape
        stride //= 2

    # Thread 0 de chaque block écrit la somme partielle en global memory
    if tid == 0:
        partial_sums[bid] = shared[0]


def sum_gpu(arr):
    threads = BLOCK_SIZE
    blocks  = (arr.shape[0] + threads - 1) // threads

    partial_sums = np.zeros(blocks, dtype=np.float32)

    d_arr          = cuda.to_device(arr)
    d_partial_sums = cuda.to_device(partial_sums)

    sum_kernel[blocks, threads](d_arr, d_partial_sums)

    # Rapatrier les sommes partielles et finir sur le CPU
    partial_sums = d_partial_sums.copy_to_host()
    return partial_sums.sum()


# Test
#v = np.linspace(0, 99, 100, dtype=np.float32)
#print("Résultat GPU :", sum_gpu(v))
#print("Résultat CPU :", v.sum())

@cuda.jit
def histo(res, m):
  i,j = cuda.grid(2)
  n = m.shape[0]
  if j<n and i < n :
     cuda.atomic.add(res,m[i,j],1)
#
#m1 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.int32)
#m2 = np.array([[1,2,3],[1,2,3],[1,2,3]],dtype=np.int32)
#res = np.zeros(255,dtype=np.int32)
#
#printmat(m1)
#d_m1 = cuda.to_device(m1)
#d_m2 = cuda.to_device(m2)
#d_res = cuda.to_device(res)
#
#config = [(1,1), (3,3)]
#histo[config](d_res,d_m1)
#
#res = d_res.copy_to_host()

@cuda.jit 
def detcol(tame, wild, b):
    i = cuda.grid(1)
    if i >= wild.shape[0]:
        return
    
    for k in range(tame.shape[0]):
        if tame[k] == wild[i]:
            cuda.atomic.exch(b, 0, i)  
            break

tame = np.random.randint(0,5,10,dtype = np.int32)
wild = np.random.randint(0,5,10,dtype = np.int32)
b = np.array([0],dtype=np.int32)

print("tame = ",tame)
print("wild = ",wild)
d_tame = cuda.to_device(tame)
d_wild = cuda.to_device(wild)
d_b = cuda.to_device(b)

config = (1, 10)
detcol[config](d_tame,d_wild,d_b)
b = d_b.copy_to_host()
print("b = ",b)