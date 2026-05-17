#!/usr/bin/env python3

import argparse
import sys
import os
from pyspark import SparkContext, SparkConf
import math
import time

def rol32(x,k):
    """Auxiliary function (left rotation for 32-bit words)"""
    return ((x << k) | (x >> (32-k))) & 0xffffffff

def murmur3_32(key, seed):
    """Computes the 32-bit murmur3 hash"""
    # use the implementation from Problem 1
    byte8_key = key.encode('utf-8')
    
    c1 = 0xcc9e2d51
    c2 = 0x1b873593
    r1 = 15
    r2 = 13
    m = 5
    n = 0xe6546b64
    
    hash = seed
    
    len_key = len(byte8_key)
    nblocks = len_key // 4
    
    for i in range(nblocks):
        block = byte8_key[i*4:(i+1)*4]
        k = int.from_bytes(block, byteorder='little')
        k = k * c1 & 0xffffffff
        k = rol32(k, r1)
        k = k * c2 & 0xffffffff
        
        hash = hash ^ k & 0xffffffff
        hash = rol32(hash, r2)
        hash = ((hash * m) + n) & 0xffffffff
        
        
    remainder = byte8_key[nblocks*4:]
    if len(remainder) > 0:
        k1 = int.from_bytes(remainder, byteorder='little')
        k1 = (k1 * c1) & 0xffffffff
        k1 = rol32(k1, r1)
        k1 = (k1 * c2) & 0xffffffff
        hash = (hash ^ k1) & 0xffffffff
    
    hash = hash ^ len_key & 0xffffffff
    hash = hash ^ (hash >> 16)
    hash = (hash * 0x85ebca6b) & 0xffffffff
    hash = hash ^ (hash >> 13)
    hash = (hash * 0xc2b2ae35) & 0xffffffff
    hash = hash ^ (hash >> 16)
    
    return hash

def auto_int(x):
    """Auxiliary function to help convert e.g. hex integers"""
    return int(x,0)

def dlog2(n):
    return n.bit_length() - 1

def rho(n):
    """Given a 32-bit number n, return the 1-based position of the first
    1-bit from the left"""
    if n == 0:
        return 0
    return 32 - n.bit_length() + 1

def compute_jr(key,seed,log2m):
    """hash the string key with murmur3_32, using the given seed
    then take the **least significant** log2(m) bits as j
    then compute the rho value **from the left**

    E.g., if m = 1024 and we compute hash value 0x70ffec73
    or 0b01110000111111111110110001110011
    then j = 0b0001110011 = 115
         r = 2
         since the 2nd digit of 0111000011111111111011 is the first 1

    Return a tuple (j,r) of integers
    """
    h = murmur3_32(key,seed)
    j = ~(0xffffffff << log2m) & h
    r = rho(h)
    return j, r


def get_files(path):
    """
    A generator function: Iterates through all .txt files in the path and
    returns the content of the files

    Parameters:
    - path : string, path to walk through

    Yields:
    The content of the files as strings
    """
    for (root, dirs, files) in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                path = f'{root}/{file}'
                with open(path,'r') as f:
                    yield f.read()

def alpha(m):
    """Auxiliary function: bias correction"""
    match m:
        case 16:
            return 0.673
        case 32:
            return 0.697
        case 64:
            return 0.709
        case _ if m >= 128:
            return 0.7213/(1+1.079/m)
    raise ValueError('m must be a power of 2 greater than or equal to 16')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Using HyperLogLog, computes the approximate number of '
            'distinct words in all .txt files under the given path.'
    )
    parser.add_argument('path',help='path to walk',type=str)
    parser.add_argument('-s','--seed',type=auto_int,default=0,help='seed value')
    parser.add_argument('-m','--num-registers',type=int,required=True,
                            help=('number of registers (must be a power of two)'))
    parser.add_argument('-w','--num-workers',type=int,default=1,
                        help='number of Spark workers')
    args = parser.parse_args()

    seed = args.seed
    m = args.num_registers
    if m <= 0 or (m&(m-1)) != 0:
        sys.stderr.write(f'{sys.argv[0]}: m must be a positive power of 2\n')
        quit(1)
    log2m = dlog2(m)

    num_workers = args.num_workers
    if num_workers < 1:
        sys.stderr.write(f'{sys.argv[0]}: must have a positive number of '
                         'workers\n')
        quit(1)

    path = args.path
    if not os.path.isdir(path):
        sys.stderr.write(f"{sys.argv[0]}: `{path}' is not a valid directory\n")
        quit(1)

    start = time.time()
    conf = SparkConf()
    conf.setMaster(f'local[{num_workers}]')
    conf.set('spark.driver.memory', '64g')
    sc = SparkContext(conf=conf)

    data = sc.parallelize(get_files(path))

    # Implement HyperLogLog here
    
    
    jr_pairs = data.flatMap(lambda text: text.split()) \
                    .map(lambda word: compute_jr(word, seed, log2m)) \
                    .reduceByKey(lambda x,y: max(x,y)) \
                    .cache()
    
    V = m - jr_pairs.count()
    zero_padded_sum = jr_pairs.map(lambda x: 2**(-x[1])).sum() + V
    harmonic_mean = alpha(m) * m**2 * (1 / zero_padded_sum)
    E = harmonic_mean
    
    if E <= (5 / 2) * m:
        E = -m * math.log(V/m)
    elif E <= ((1/30)*(2**32)):
        E = -2**32 * math.log(1 - harmonic_mean/2**32)
    
    end = time.time()

    n_actual = len(set(data.flatMap(lambda text: text.split()).collect()))
    
    print(f'Actual cardinality: {n_actual}')
    #print(f'Seed: 0x{seed:0x}', f'm: {m}')
    print(f'Cardinality estimate: {E}')
    print(f'Number of workers: {num_workers}')
    print(f'Took {end-start} s')

    

    