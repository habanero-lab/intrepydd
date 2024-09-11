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
import numba
from numba import jit
from numba import prange

@jit(cache=True, nopython=True, parallel=True, nogil=True)
def func0(seeds, degrees, alpha, epsilon,
          num_nodes, adj_indices, adj_indptr):

    alpha_exp = (2 * alpha) / (1 + alpha)
    alpha_degree_exp = ((1 - alpha) / (1 + alpha)) / degrees
    epsilon_degree_exp = degrees * epsilon

    num_seeds = seeds.shape[0]
    
    out = np.empty((num_seeds, num_nodes), numba.float64) 
    for i in range(num_seeds):
        seed = seeds[i]
        p = np.zeros(num_nodes)
        r = np.zeros(num_nodes)
        r[seed] = 1.0

        frontier = np.empty(1, numba.int64)
        frontier[0] = seed
        while frontier.shape[0] > 0:
            r_prime = r + 0.0 # instead of r.copy()

            for node_idx in frontier:
                
                p[node_idx] = p[node_idx] + alpha_exp * r[node_idx]
                r_prime[node_idx] = 0.0

            for src_idx in frontier:
                update = alpha_degree_exp[src_idx] * r[src_idx]
                for j in range(adj_indptr[src_idx], adj_indptr[src_idx+1]):
                    dst_idx = adj_indices[j]
                    r_prime[dst_idx] = r_prime[dst_idx] + update

            r = r_prime

            # frontier = where(logical_and(ge(r, epsilon_degree_exp), gt(degrees, 0))) # expand & fuse
            num_elems = 0
            cond = np.zeros(num_nodes)
            for j in range(num_nodes):
                if (r[j] >= epsilon_degree_exp[j]) and (degrees[j] > 0):
                    cond[j] = 1
                    num_elems += 1
            idx = 0
            frontier = np.empty(num_elems, numba.int64)
            for j in range(num_nodes):
                if cond[j] == 1:
                    frontier[idx] = j
                    idx += 1

        # out.append(p)
        for j in range(num_nodes):
            out[i,j] = p[j]

    return out.T


# --
# ISTA algorithm
@jit(cache=True)
def ista(seeds, adj, alpha, rho, iters):
    out = []
    for seed in tqdm(seeds):
        
        # Make personalized distribution
        s = np.zeros(adj.shape[0])
        s[seed] = 1
        
        # Compute degree vectors/matrices
        d       = np.asarray(adj.sum(axis=-1)).squeeze()
        d_sqrt  = np.sqrt(d)
        dn_sqrt = 1 / d_sqrt
        
        D       = sparse.diags(d)
        Dn_sqrt = sparse.diags(dn_sqrt)
        
        # Normalized adjacency matrix
        Q = D - ((1 - alpha) / 2) * (D + adj)
        Q = Dn_sqrt @ Q @ Dn_sqrt
        
        # Initialize
        q = np.zeros(adj.shape[0], dtype=np.float64)
        
        rad   = rho * alpha * d_sqrt
        grad0 = -alpha * dn_sqrt * s
        grad  = grad0
        
        # Run
        for _ in range(iters):
            q    = np.maximum(q - grad - rad, 0)
            grad = grad0 + Q @ q
        
        out.append(q * d_sqrt)
    
    return np.column_stack(out)

# --
# Parallel PR-Nibble

def parallel_pr_nibble(seeds, adj, alpha, epsilon):

    np_alpha = np.float64(alpha)
    np_epsilon = np.float64(epsilon)
    np_seeds = np.array(seeds).astype(np.int32)
    degrees = np.asarray(adj.sum(axis=-1)).squeeze().astype(np.int32)
    num_nodes = np.int32(adj.shape[0])
    adj_indices = adj.indices
    adj_indptr = adj.indptr

    out = func0(np_seeds, degrees, np_alpha, np_epsilon, num_nodes, adj_indices, adj_indptr)
    return out



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
    
    t = time()
    pnib_scores = parallel_pr_nibble(pnib_seeds, adj, alpha=args.alpha, epsilon=args.pnib_epsilon)
    pnib_elapsed = time() - t
    print(pnib_scores)
    assert pnib_scores.shape[0] == adj.shape[0]
    assert pnib_scores.shape[1] == len(pnib_seeds)
    
    print('parallel_pr_nibble: elapsed = %f' % pnib_elapsed, file=sys.stderr)

    exit(0)
    # --
    # Run ISTA
    
    t = time()
    ista_scores = ista(ista_seeds, adj, alpha=args.alpha, rho=args.ista_rho, iters=args.ista_iters)
    assert ista_scores.shape[0] == adj.shape[0]
    assert ista_scores.shape[1] == len(ista_seeds)
    ista_elapsed = time() - t
    print('ista: elapsed = %f' % ista_elapsed, file=sys.stderr)
    
    # --
    # Write output
    
    os.makedirs('results', exist_ok=True)
    
    np.savetxt('results/pnib_score.txt', pnib_scores)
    np.savetxt('results/ista_score.txt', ista_scores)
    
    open('results/pnib_elapsed', 'w').write(str(pnib_elapsed))
    open('results/ista_elapsed', 'w').write(str(ista_elapsed))


    print('Note that pr_nibble is nopython mode and ista is object mode.')
