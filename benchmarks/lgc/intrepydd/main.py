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
import kernel as kernel

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

    out = kernel.func0_unopt(np_seeds, degrees, np_alpha, np_epsilon, num_nodes, adj_indices, adj_indptr)
    return out


# --
# ISTA algorithm

def ista(seeds, adj, alpha, rho, iters):

    np_alpha = np.float64(alpha)
    np_rho = np.float64(rho)
    np_iters = np.int32(iters)
    np_seeds = np.array(seeds).astype(np.int32)
    d = np.asarray(adj.sum(axis=-1)).squeeze().astype(np.int32)
    adj_vals = adj.data.astype(np.float64)
    adj_cols = adj.indices
    adj_idxs = adj.indptr
    nrows = adj.shape[0]
    ncols = adj.shape[1]

    out = kernel.func1_unopt(np_seeds, d, np_alpha, np_rho, np_iters, adj_vals, adj_cols, adj_idxs, nrows, ncols)
    return out


# --
# Run

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-seeds', type=int, default=1000)  # was 50
    parser.add_argument('--alpha', type=float, default=0.15)
    parser.add_argument('--pnib-epsilon', type=float, default=1e-6)
    parser.add_argument('--ista-rho', type=float, default=1e-5)
    parser.add_argument('--ista-iters', type=int, default=50)
    args = parser.parse_args()
    
    # !! In order to check accuracy, you _must_ use these parameters !!
    assert args.num_seeds == 1000
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
    # pnib_seeds = list(range(50))
    # ista_seeds = list(range(10 * 50))
    pnib_seeds = list(range(args.num_seeds))
    ista_seeds = list(range(10 * args.num_seeds))
    
    # --
    # Run Parallel PR-Nibble
    
    t = time()
    pnib_scores = parallel_pr_nibble(pnib_seeds, adj, alpha=args.alpha, epsilon=args.pnib_epsilon)
    t2 = time()
    assert pnib_scores.shape[0] == adj.shape[0]
    assert pnib_scores.shape[1] == len(pnib_seeds)
    pnib_elapsed = time() - t
    # print('parallel_pr_nibble: elapsed = %f' % pnib_elapsed, file=sys.stderr)
    
    print("[Nibble Elapsed Time]: ", (t2 - t))
    # sys.exit(0)
    # --
    # Run ISTA
    
    t = time()
    ista_scores = ista(ista_seeds, adj, alpha=args.alpha, rho=args.ista_rho, iters=args.ista_iters)
    t2 = time()
    assert ista_scores.shape[0] == adj.shape[0]
    assert ista_scores.shape[1] == len(ista_seeds)
    ista_elapsed = time() - t
    # print('ista: elapsed = %f' % ista_elapsed, file=sys.stderr)
    
    print("[ISTA Elapsed Time]: ", (t2 - t))

    # --
    # Write output
    
    os.makedirs('results', exist_ok=True)
    
    np.savetxt('results/pnib_score.txt', pnib_scores)
    np.savetxt('results/ista_score.txt', ista_scores)
    
    open('results/pnib_elapsed', 'w').write(str(pnib_elapsed))
    open('results/ista_elapsed', 'w').write(str(ista_elapsed))

