#!/usr/bin/env python3

from assignment5_problem1b import murmur3_32
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate the murmur3_32 hash function on a dataset of words')
    parser.add_argument('-s', '--dataset', type=str, required=True, help='Path to the dataset of words (one word per line)')
    parser.add_argument('-m', '--lsb', type=int, default=7, help='Number of least significant bits to evaluate (default: 7)')
    args = parser.parse_args()
    
    with open(args.dataset, 'r') as f:
        words = f.read().splitlines()
    
    B = 2 ** args.lsb
    counts = [0] * B
    seed = 0xee418b6c
    
    hash_mean = 0.0
    m2 = 0.0
    n = 0
    
    key_pairs = len(words) * (len(words) - 1) // 2
    collision_count = 0
    
    unique_hashes = set()
    
    for word in words:
        hash_value = murmur3_32(word, seed) & (B - 1)  # Get the least significant bits
        counts[hash_value] += 1
        unique_hashes.add(hash_value)
        
        n += 1
        delta = hash_value - hash_mean
        hash_mean += delta / n
        m2 += delta * (hash_value - hash_mean)
        
        
        collision_count += counts[hash_value] - 1
        
    collision_probability = collision_count / key_pairs if key_pairs > 0 else 0
    hash_stdev = (m2 / n) ** 0.5
    
    counts_mean = sum(counts) / B
    counts_var = sum((x - counts_mean) ** 2 for x in counts) / B
    counts_stdev = counts_var ** 0.5
    # print hash value, count, expected count.
    print('Hash value<tab>Count<tab>Expected Count')
    for hash_value in unique_hashes:
        print(f'{hash_value}\t{counts[hash_value]}\t{len(words)/B:.0f}')
    
    print(f'Hash value mean: {hash_mean:.4f}')
    print(f'Hash value standard deviation: {hash_stdev:.4f}')
    print(f'Counts mean: {counts_mean:.4f}')
    print(f'Counts standard deviation: {counts_stdev:.4f}')
    print(f'Collision probability: {collision_probability:.4f}')
    
