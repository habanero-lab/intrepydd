#!/usr/bin/env python

"""
    lgc/main.py
    
    Note to program performers:
        - parallel_pr_nibble produces the same results as ligra's `apps/localAlg/ACL-Sync-Local-Opt.C`
        - ista produces the same results as LocalGraphClustering's `ista_dinput_dense` method
"""

import os
import sys
import argparse
import numpy as np
from time import time
from tqdm import tqdm
from scipy import sparse
from scipy.io import mmread
from scipy.stats import spearmanr

from logs.loggers import log_array, log_sparse_vector, log_header, log_sparse_matrix

# --
# Parallel PR-Nibble

def parallel_pr_nibble(seeds, adj, alpha, epsilon):
    out = []
    for seed in seeds:
        print('INIT parallel_pr_nibble')
        print('seed:', seed)
        
        degrees = np.asarray(adj.sum(axis=-1)).squeeze().astype(int)
        log_array('INIT degrees:', degrees)
        
        num_nodes = adj.shape[0]
        
        p = np.zeros(num_nodes)
        log_sparse_vector('INIT p:', p)
        
        r = np.zeros(num_nodes)
        r[seed] = 1
        log_sparse_vector('INIT r:', r)
        
        frontier = np.array([seed])
        log_array('INIT frontier:', frontier)
        
        it = 0
        while True:
            log_header('START ITERATION:', it, n=10)
            
            if len(frontier) == 0:
                print('frontier is empty -- breaking')
                break
            
            r_prime = r.copy()
            print('(Line 13) copy r_prime to r')
            
            print('(Line 14) running vertexMap')
            for node_idx in frontier:
                p[node_idx] += (2 * alpha) / (1 + alpha) * r[node_idx]
                r_prime[node_idx] = 0
            
            log_sparse_vector('p:', p)
            log_sparse_vector('r_prime:', r_prime)
            
            print('(Line 15) running edgeMap')
            for src_idx in frontier:
                neighbors = adj.indices[adj.indptr[src_idx]:adj.indptr[src_idx + 1]]
                for dst_idx in neighbors:
                    update = ((1 - alpha) / (1 + alpha)) * r[src_idx] / degrees[src_idx]
                    r_prime[dst_idx] += update
            
            log_sparse_vector('r_prime:', r_prime)
            
            r = r_prime
            print('(Line 16) copy r to r_prime')
            
            print('(Line 17) create next frontier')
            frontier = np.where((r >= degrees * epsilon) & (degrees > 0))[0]
            log_array('frontier:', frontier)
            
            it += 1
        
        log_sparse_vector('RETURN p:', p)
        
        out.append(p)
        return # Early exit
    
    return np.column_stack(out)


# --
# ISTA algorithm

def ista(seeds, adj, alpha, rho, iters):
    out = []
    for seed in tqdm(seeds):
        print('INIT ista')
        print('seed: ', seed)
        
        # Make personalized distribution
        s = np.zeros(adj.shape[0])
        s[seed] = 1
        log_sparse_vector('INIT s:', s)
        
        # Compute degree vectors/matrices
        d       = np.asarray(adj.sum(axis=-1)).squeeze()
        log_array('INIT d: ', d)
        d_sqrt  = np.sqrt(d)
        dn_sqrt = 1 / d_sqrt
        
        D       = sparse.diags(d)
        log_sparse_matrix('INIT D: ', D.astype(np.int))
        Dn_sqrt = sparse.diags(dn_sqrt)
        log_sparse_matrix('INIT (D ** -1/2):', Dn_sqrt)
        
        # Normalized adjacency matrix
        Q = D - ((1 - alpha) / 2) * (D + adj)
        Q = Dn_sqrt @ Q @ Dn_sqrt
        
        # Initialize
        q = np.zeros(adj.shape[0], dtype=np.float64)
        log_sparse_vector('INIT q:', q)
        
        rad   = rho * alpha * d_sqrt
        grad0 = -alpha * dn_sqrt * s
        grad  = grad0
        log_sparse_vector('INIT grad0:', grad0)
        
        # Run
        for it in range(iters):
            log_header('START ITERATION:', it, n=10)
            q    = np.maximum(q - grad - rad, 0)
            log_sparse_vector('(Line 3) q:', q)
            grad = grad0 + Q @ q
            log_sparse_vector('(Line 4) grad:', grad)
        
        log_header('ITERATIONS COMPLETE', n=10)
        
        p = q * d_sqrt
        log_sparse_vector('RETURN p:', p)
        out.append(p)
        return # Early exit
    
    return np.column_stack(out)

# --
# Run

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-seeds', type=int, default=50)
    parser.add_argument('--alpha', type=float, default=0.15)
    parser.add_argument('--pnib-epsilon', type=float, default=1e-6)
    parser.add_argument('--ista-rho', type=float, default=1e-5)
    parser.add_argument('--ista-iters', type=int, default=50)
    args = parser.parse_args()
    
    # !! In order to check accuracy, you _must_ use these parameters !!
    assert args.num_seeds == 50
    assert args.alpha == 0.15
    assert args.pnib_epsilon == 1e-6
    assert args.ista_rho == 1e-5
    assert args.ista_iters == 50
    
    return args


if __name__ == "__main__":
    args = parse_args()
    
    # --
    # IO
    
    adj = mmread('data/jhu.mtx').tocsr()
    
    # PNIB: Use first `num_seeds` nodes as seeds
    # ISTA: Faster algorithm, so use more seeds to get roughly comparable total runtime
    pnib_seeds = list(range(args.num_seeds))
    ista_seeds = list(range(10 * args.num_seeds))
    
    # --
    # Run Parallel PR-Nibble
    
    # t = time()
    pnib_scores = parallel_pr_nibble(pnib_seeds, adj, alpha=args.alpha, epsilon=args.pnib_epsilon)
    # assert pnib_scores.shape[0] == adj.shape[0]
    # assert pnib_scores.shape[1] == len(pnib_seeds)
    # pnib_elapsed = time() - t
    # print('parallel_pr_nibble: elapsed = %f' % pnib_elapsed, file=sys.stderr)
    
    # --
    # Run ISTA
    
    # t = time()
    ista_scores = ista(ista_seeds, adj, alpha=args.alpha, rho=args.ista_rho, iters=args.ista_iters)
    # assert ista_scores.shape[0] == adj.shape[0]
    # assert ista_scores.shape[1] == len(ista_seeds)
    # ista_elapsed = time() - t
    # print('ista: elapsed = %f' % ista_elapsed, file=sys.stderr)
    
    # --
    # Write output
    
    # os.makedirs('results', exist_ok=True)
    
    # np.savetxt('results/pnib_score.txt', pnib_scores)
    # np.savetxt('results/ista_score.txt', ista_scores)
    
    # open('results/pnib_elapsed', 'w').write(str(pnib_elapsed))
    # open('results/ista_elapsed', 'w').write(str(ista_elapsed))

