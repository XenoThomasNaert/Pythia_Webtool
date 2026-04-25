#!/usr/bin/env python
# coding: utf-8
"""
Optimized integration analysis script.
Key improvements:
1. Eliminated redundant genotype calculations (stored from pythia)
2. Reduced duplicate reverse complement operations
3. Optimized DataFrame operations (vectorized where possible)
4. Cached commonly used values
5. Streamlined context extraction
6. Reduced string operations in loops
"""

import os
import time
import tempfile
import subprocess
import sys
import importlib
from datetime import datetime
import pandas as pd
from Bio import SeqUtils
from Bio.Seq import Seq
import pyfastx
import numpy as np
import warnings
import sqlite3
import argparse

warnings.simplefilter("ignore")
warnings.showwarning = lambda *args, **kwargs: None

# Global variable for GFP sequence (assumed to be in plus orientation).
GFP_SEQUENCE = ("GGATCAGGAGGATCAGGAATGGTCTCAAAGGGAGAGGAGGAAAACATGGCTAGTACACCATTTAAATTTCAACTTAAAGGAACCATCAATGGCAAATCGTTTACCGTTGAAGGCGAAGGTGAAGGGAAcTCACATGAAGGTTCTCATAAAGGAAAATATGTTTGTACAAGTGGAAAACTACCGATGTCATGGGCAGCACTTGGGACAACCTTTGGTTATGGAATGAAATATTATACCAAATATCCTAGTGGACTGAAGAACTGGTTTCGTGAAGTAATGCCCGGAGGCTTTACCTACGATCGTCATATTCAATATAAAGGCGATGGGAGTATCCATGCAAAACACCAACACTTTATGAAAAATGGGACTTATCACAACATTGTAGAATTTACCGGTCAGGATTTTAAAGAAAATAGTCCAGTCTTAACTGGAGATATGAATGTCTCATTACCGAATGAAGTCCCACAAATACCCAGAGATGATGGAGTAGAATGCCCAGTGACCTTGCTTTATCCTTTATTATCGGATAAATCAAAATACGTCGAGGCTCACCAATATACAATCTGCAAGCCTCTTCATAATCAACCAGCACCTGATGTCCCATATCACTGGATTCGTAAACAATACACACAAAGCAAAGATGATGCCGAGGAACGCGATCATATCTGTCAATCAGAGACTCTCGAAGCACACTTAAAGGGCATGGACGAGCTGTATAAGTGA")

# Cache for reverse complements
_revcomp_cache = {}

# --- Off-Target Calculator Constants ---
DEFAULT_CAS_BIN         = r"C:\KVr_Process_on_SSD\251111_ExonTaggingNPTCalculators\ExonTagger\cas-offinder.exe"
DEFAULT_OFFTARGET_GENOME_PATH = r"C:\KVr_Process_on_SSD\251111_ExonTaggingNPTCalculators\ExonTagger\HumanGenome\Homo_sapiens.GRCh38.dna.primary_assembly.fa"
OFFTARGET_PATTERN = "NNNNNNNNNNNNNNNNNNNNNRG"
OFFTARGET_SUFFIX = "NNN 0"

def log(msg):
    print(msg)

log(f"Starting integration analysis with gRNA finder at {datetime.now()}")
start = time.time()

# ------------------------------
# CRISPRScan parameter list: each tuple is (modelSequence, position, weight)
paramsCRISPRscan = [
    ('AA',19,-0.097377097),
    ('TT',18,-0.094424075), ('TT',13,-0.08618771), ('CT',26,-0.084264893), ('GC',25,-0.073453609),
    ('T',21,-0.068730497), ('TG',23,-0.066388075), ('AG',23,-0.054338456), ('G',30,-0.046315914),
    ('A',4,-0.042153521), ('AG',34,-0.041935908), ('GA',34,-0.037797707), ('A',18,-0.033820432),
    ('C',25,-0.031648353), ('C',31,-0.030715556), ('G',1,-0.029693709), ('C',16,-0.021638609),
    ('A',14,-0.018487229), ('A',11,-0.018287292), ('T',34,-0.017647692), ('AA',10,-0.016905415),
    ('A',19,-0.015576499), ('G',34,-0.014167123), ('C',30,-0.013182733), ('GA',31,-0.01227989),
    ('T',24,-0.011996172), ('A',15,-0.010595296), ('G',4,-0.005448869), ('GG',9,-0.00157799),
    ('T',23,-0.001422243), ('C',15,-0.000477727), ('C',26,-0.000368973), ('T',27,-0.000280845),
    ('A',31,0.00158975), ('GT',18,0.002391744), ('C',9,0.002449224), ('GA',20,0.009740799),
    ('A',25,0.010506405), ('A',12,0.011633235), ('A',32,0.012435231), ('T',22,0.013224035),
    ('C',20,0.015089514), ('G',17,0.01549378), ('G',18,0.016457816), ('T',30,0.017263162),
    ('A',13,0.017628924), ('G',19,0.017916844), ('A',27,0.019126815), ('G',11,0.020929039),
    ('TG',3,0.022949996), ('GC',3,0.024681785), ('G',14,0.025116714), ('GG',10,0.026802158),
    ('G',12,0.027591138), ('G',32,0.03071249), ('A',22,0.031930909), ('G',20,0.033957008),
    ('C',21,0.034262921), ('TT',17,0.03492881), ('T',13,0.035445171), ('G',26,0.036146649),
    ('A',24,0.037466478), ('C',22,0.03763162), ('G',16,0.037970942), ('GG',12,0.041883009),
    ('TG',18,0.045908991), ('TG',31,0.048136812), ('A',35,0.048596259), ('G',15,0.051129717),
    ('C',24,0.052972314), ('TG',15,0.053372822), ('GT',11,0.053678436), ('GC',9,0.054171402),
    ('CA',30,0.057759851), ('GT',24,0.060952114), ('G',13,0.061360905), ('CA',24,0.06221937),
    ('AG',10,0.063717093), ('G',10,0.067739182), ('C',13,0.069495944), ('GT',31,0.07342535),
    ('GG',13,0.074355848), ('C',27,0.079933922), ('G',27,0.085151052), ('CC',21,0.088919601),
    ('CC',23,0.095072286), ('G',22,0.10114438), ('G',24,0.105488325), ('GT',23,0.106718563),
    ('GG',25,0.111559441), ('G',9,0.114600681)
]

def open_cache_connection(cache_db_path, timeout=30):
    conn = sqlite3.connect(cache_db_path, timeout=timeout, check_same_thread=False)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    return conn

def load_cached_grnas(cache_db_path):
    if not os.path.exists(cache_db_path):
        return pd.DataFrame()

    conn = open_cache_connection(cache_db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM filtered_gRNAs", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()

    return df


def save_cached_grnas(cache_db_path, cache_df):
    conn = open_cache_connection(cache_db_path)
    try:
        cache_df.to_sql("filtered_gRNAs", conn, if_exists="replace", index=False)
    finally:
        conn.close()

def find_cas_bin_and_genome():
    # prefer local files in worker folder
    local_bin = os.path.join(os.getcwd(), "cas-offinder.exe")
    local_genomes = os.path.join(os.getcwd(), "genomes")

    if os.path.exists(local_bin):
        # local copies exist → use them
        genome_path = (
            local_genomes
            if os.path.exists(local_genomes)
            else DEFAULT_OFFTARGET_GENOME_PATH
        )
        log(f"Using local cas-offinder: {local_bin}")
        return local_bin, genome_path

    # fallback to global paths
    return DEFAULT_CAS_BIN, DEFAULT_OFFTARGET_GENOME_PATH


def calcCrisprScanScores(seqs):
    scores = []
    for seq in seqs:
        assert len(seq) == 35, "Sequence must be 35 bases long."
        intercept = 0.183930943629
        score = intercept
        for modelSeq, pos, weight in paramsCRISPRscan:
            subSeq = seq[pos - 1: pos + len(modelSeq) - 1]
            if subSeq == modelSeq:
                score += weight
        scores.append(int(100 * score))
    return scores

# Global variable for tracking cell type initialization
last_celltype = None
sys.path.insert(0, '/home/lienkamplab/Pythia/Indelphi_installation/inDelphi-model-master')
import inDelphi

def reload_inDelphi_if_needed(celltype):
    global last_celltype, inDelphi
    if celltype != last_celltype:
        inDelphi = importlib.reload(inDelphi)
        inDelphi.init_model(celltype=celltype)
        last_celltype = celltype
        log(f"inDelphi reloaded and initialized with: {celltype}")

def reverse_complement(seq):
    """Cached reverse complement function"""
    if seq in _revcomp_cache:
        return _revcomp_cache[seq]
    
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    seq_upper = seq.upper()
    result = ''.join(complement.get(b, b) for b in reversed(seq_upper))
    _revcomp_cache[seq] = result
    return result

def get_context(sequence, gRNA_seq, offset_left=23, offset_right=37):
    start_index = sequence.find(gRNA_seq)
    if start_index == -1:
        return None
    start = start_index - offset_left
    end = start_index + len(gRNA_seq) + offset_right
    if start < 0 or end > len(sequence):
        return None
    return sequence[start:end]

def get_dynamic_cassette(last_exon_seq, cleavage_index):
    """
    Given the last_exon_sequence and a cleavage index,
    remove the terminal stop codon (if present) and return the substring starting at cleavage_index.
    """
    if last_exon_seq[-3:] in ['TAA', 'TAG', 'TGA']:
        trimmed_seq = last_exon_seq[:-3]
    else:
        trimmed_seq = last_exon_seq
    
    if cleavage_index < 0 or cleavage_index > len(trimmed_seq):
        log(f"WARNING: Cleavage index {cleavage_index} is out of bounds for last_exon_seq length {len(trimmed_seq)}")
        return ""
    
    return trimmed_seq[cleavage_index:]

def collect_all_candidate_gRNAs(input_seq, full_context_seq, gene_id):
    """
    Collect ALL possible gRNA candidates for a gene and filter by cut location.
    Only keeps gRNAs where the cut site is within the last exon (input_seq).
    Returns a list of dictionaries with gRNA information.
    """
    log(f"Collecting all candidate gRNAs for gene {gene_id}")
    
    # Determine offset: position where input_seq occurs in full_context_seq
    offset = full_context_seq.find(input_seq)
    if offset == -1:
        log("Warning: input_seq not found in full_context_seq. Using offset=0.")
        offset = 0

    # Storage for all candidates
    all_candidates = []
    
    # Length of the actual last exon (input_seq)
    last_exon_length = len(input_seq)

    # --- gRNA Search on plus strand ---
    query = Seq("NNNNNNNGG")
    found_locs = SeqUtils.nt_search(input_seq, query)
    plus_locs = [int(x) for x in found_locs[1:]]
    
    for pos in plus_locs:
        pos_context = pos + offset
        gRNA = full_context_seq[max(0, pos_context-14): pos_context+6]
        crispr_seq = full_context_seq[max(0, pos_context-20): pos_context+15]
        if len(crispr_seq) != 35:
            continue
        
        # Calculate cut location within the last exon
        corrected_loc = pos_context + 3 - 50
        
        # Filter: cut location must be within the last exon (positive and <= last_exon_length)
        if corrected_loc <= 0 or corrected_loc > last_exon_length:
            continue
        
        all_candidates.append({
            'gene_id': gene_id,
            'gRNA_seq': gRNA,
            'gRNA_20bp': gRNA,
            'crispr_seq': crispr_seq,
            'pos_context': pos_context,
            'strand': 'plus',
            'location': corrected_loc
        })
    
    # --- gRNA Search on minus strand ---
    full_context_seq_rev = reverse_complement(full_context_seq)
    found_locs_rev = SeqUtils.nt_search(full_context_seq_rev, query)
    rev_locs = [int(x) for x in found_locs_rev[1:]]
    
    for pos in rev_locs:
        gRNA = full_context_seq_rev[max(0, pos-14): pos+6]
        crispr_seq = full_context_seq_rev[max(0, pos-20): pos+15]
        if len(crispr_seq) != 35:
            continue
        
        # Calculate cut location within the last exon
        corrected_loc = (len(full_context_seq) - pos) - 3 - 50
        
        # Filter: cut location must be within the last exon (positive and <= last_exon_length)
        if corrected_loc <= 0 or corrected_loc > last_exon_length:
            continue
        
        all_candidates.append({
            'gene_id': gene_id,
            'gRNA_seq': gRNA,
            'gRNA_20bp': gRNA,
            'crispr_seq': crispr_seq,
            'pos': pos,
            'strand': 'min',
            'full_context_seq_len': len(full_context_seq),
            'location': corrected_loc
        })
    
    log(f"Collected {len(all_candidates)} valid gRNAs (cut sites within last exon)")
    return all_candidates

def check_off_target_batch(candidate_list, cas_bin=None, genome_path=None, backup_dir=None, chunk_id=None):
    """
    Run cas-offinder on a batch of candidates and save outputs to backup folder.
    
    Args:
        candidate_list: List of gRNA sequences to check
        cas_bin: Path to cas-offinder binary
        genome_path: Path to genome file
        backup_dir: Directory to save backup files
        chunk_id: Identifier for this chunk (e.g., "chunk_1")
    
    Returns:
        dict: {gRNA_20bp: pass_status} for all candidates
    """
    # if nothing was passed, pick up local copy OR default paths
    if not cas_bin or not genome_path:
        cas_bin, genome_path = find_cas_bin_and_genome()
    
    # Create backup directory if provided
    if backup_dir:
        os.makedirs(backup_dir, exist_ok=True)
    
    # Create input file in current directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chunk_suffix = f"_{chunk_id}" if chunk_id else ""
    input_file = os.path.join(os.getcwd(), f"offtarget_input_{timestamp}{chunk_suffix}.txt")
    
    with open(input_file, "w") as f:
        f.write(genome_path + "\n")
        f.write(OFFTARGET_PATTERN + "\n")
        for cand in candidate_list:
            f.write(cand.upper() + OFFTARGET_SUFFIX + "\n")
    
    # Output file goes to backup directory if specified, otherwise current directory
    if backup_dir:
        output_file = os.path.join(backup_dir, f"offtarget_output_{timestamp}{chunk_suffix}.out")
    else:
        output_file = input_file + ".out"
    # Windows vs Linux command
    if os.name == "nt":
        cmd = f'"{cas_bin}" "{input_file}" "{output_file}"'
        shell_flag = True
    else:
        cmd = [cas_bin, input_file, "G", output_file]
        shell_flag = False
    try:
        result = subprocess.run(
            cmd,
            shell=shell_flag,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=600,  # 10 minutes timeout for larger batches
        )
    except Exception as e:
        log(f"Batch off-target calculator error: {e}")
        return {}
    if result.returncode != 0:
        log(f"cas-offinder failed: {result.stderr}")
        return {}
    
    counts = {}
    try:
        with open(output_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 1:
                    continue
                candidate_field = parts[0]
                candidate = candidate_field[:20]
                counts[candidate] = counts.get(candidate, 0) + 1
    except Exception as e:
        log(f"Error reading batch off-target output: {e}")
    
    # Clean up input file
    try:
        if os.path.exists(input_file):
            os.remove(input_file)
            log(f"Cleaned up input file: {input_file}")
    except Exception as e:
        log(f"Warning: Could not delete input file {input_file}: {e}")
    
    # Output file remains in backup
    log(f"Output file saved to backup: {output_file}")
    
    # Return dict with pass/fail for ALL candidates
    results = {}
    for cand in candidate_list:
        # Pass if exactly 1 hit (itself), fail otherwise
        results[cand] = (counts.get(cand, 0) == 1)
    
    passed_count = sum(1 for v in results.values() if v)
    log(f"Off-target chunk {chunk_id}: {passed_count}/{len(candidate_list)} passed")
    
    return results

def initialize_chunk_tracking_table(cache_db_path):
    """Create table to track which gene chunks have been processed."""
    conn = open_cache_connection(cache_db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunk_tracking (
                chunk_id TEXT PRIMARY KEY,
                gene_ids TEXT,
                num_genes INTEGER,
                num_grnas_tested INTEGER,
                num_grnas_passed INTEGER,
                timestamp TEXT,
                status TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()

def get_processed_chunks(cache_db_path):
    """Get set of chunk IDs that have been successfully processed."""
    conn = open_cache_connection(cache_db_path)
    try:
        df = pd.read_sql_query(
            "SELECT chunk_id FROM chunk_tracking WHERE status = 'completed'", 
            conn
        )
        return set(df['chunk_id'].values) if not df.empty else set()
    except Exception:
        return set()
    finally:
        conn.close()

def save_chunk_completion(cache_db_path, chunk_id, gene_ids, num_tested, num_passed):
    """Record that a chunk has been completed."""
    conn = open_cache_connection(cache_db_path)
    try:
        timestamp = datetime.now().isoformat()
        gene_ids_str = ','.join(gene_ids)
        
        conn.execute("""
            INSERT OR REPLACE INTO chunk_tracking 
            (chunk_id, gene_ids, num_genes, num_grnas_tested, num_grnas_passed, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, 'completed')
        """, (chunk_id, gene_ids_str, len(gene_ids), num_tested, num_passed, timestamp))
        conn.commit()
    finally:
        conn.close()

def filter_offtarget_and_score_gRNAs(all_candidates, full_context_seqs, celltype, cache_db_path, chunk_size=1000):
    """
    Takes all candidates from multiple genes, runs batch off-target analysis in chunks,
    applies unified cache DB, then CRISPRScan, then inDelphi.
    
    Args:
        all_candidates: Dictionary of {gene_id: [candidates]}
        full_context_seqs: Dictionary of {gene_id: (input_seq, full_context_seq)}
        celltype: Cell type for inDelphi
        cache_db_path: Path to cache database
        chunk_size: Number of genes to process per chunk (default: 100)
    """
    log("Starting batch off-target analysis for all genes...")
    reload_inDelphi_if_needed(celltype)

    # Create backup directory
    backup_dir = os.path.join(os.getcwd(), "backup")
    os.makedirs(backup_dir, exist_ok=True)
    log(f"Backup directory created: {backup_dir}")

    # Initialize chunk tracking
    initialize_chunk_tracking_table(cache_db_path)
    processed_chunks = get_processed_chunks(cache_db_path)

    # ---------------------------------------------------------
    # 1. Collect all unique 20bp gRNAs per gene
    # ---------------------------------------------------------
    gene_to_gRNAs = {}
    for gene_id, candidates in all_candidates.items():
        gene_gRNAs = set()
        for cand in candidates:
            gene_gRNAs.add(cand['gRNA_20bp'])
        gene_to_gRNAs[gene_id] = gene_gRNAs

    # ---------------------------------------------------------
    # 2. Load off-target cache
    # ---------------------------------------------------------
    if os.path.exists(cache_db_path):
        conn = open_cache_connection(cache_db_path)
        try:
            cached_df = pd.read_sql_query("SELECT * FROM offtarget_cache", conn)
        except Exception:
            cached_df = pd.DataFrame()
        finally:
            conn.close()
    else:
        cached_df = pd.DataFrame()

    # Build cache lookup: gRNA -> passed status
    cache_lookup = {}
    if not cached_df.empty and 'gRNA_20bp' in cached_df.columns and 'passed' in cached_df.columns:
        for _, row in cached_df.iterrows():
            cache_lookup[row['gRNA_20bp']] = row['passed']

    # ---------------------------------------------------------
    # 3. Process genes in chunks
    # ---------------------------------------------------------
    gene_ids = list(all_candidates.keys())
    total_genes = len(gene_ids)
    num_chunks = (total_genes + chunk_size - 1) // chunk_size
    
    log(f"Processing {total_genes} genes in {num_chunks} chunks of up to {chunk_size} genes each")
    log(f"Already processed chunks: {len(processed_chunks)}")
    
    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * chunk_size
        end_idx = min((chunk_idx + 1) * chunk_size, total_genes)
        chunk_genes = gene_ids[start_idx:end_idx]
        
        chunk_id = f"chunk_{chunk_idx + 1}_of_{num_chunks}"
        
        # Skip if already processed
        if chunk_id in processed_chunks:
            log(f"\n{chunk_id}: Already processed, skipping...")
            continue
        
        log(f"\n{'='*60}")
        log(f"Processing {chunk_id}: genes {start_idx + 1}-{end_idx} of {total_genes}")
        log(f"Gene IDs: {', '.join(chunk_genes[:5])}{'...' if len(chunk_genes) > 5 else ''}")
        log(f"{'='*60}")
        
        # Collect unique gRNAs for this chunk
        chunk_gRNAs = set()
        for gene_id in chunk_genes:
            chunk_gRNAs.update(gene_to_gRNAs[gene_id])
        
        # Filter out already tested gRNAs (both passed and failed)
        to_check = list(chunk_gRNAs - set(cache_lookup.keys()))
        
        if not to_check:
            log(f"{chunk_id}: All {len(chunk_gRNAs)} gRNAs already in cache")
            # Still mark chunk as completed
            num_passed = sum(1 for g in chunk_gRNAs if cache_lookup.get(g, False))
            save_chunk_completion(cache_db_path, chunk_id, chunk_genes, len(chunk_gRNAs), num_passed)
            continue
        
        log(f"{chunk_id}: Testing {len(to_check)} new gRNAs (out of {len(chunk_gRNAs)} total)")
        
        # Run cas-offinder for this chunk
        chunk_results = check_off_target_batch(
            to_check,
            backup_dir=backup_dir,
            chunk_id=chunk_id
        )
        
        if not chunk_results:
            log(f"{chunk_id}: cas-offinder failed, skipping this chunk")
            continue
        
        # Update cache lookup with new results
        cache_lookup.update(chunk_results)
        
        # Build new rows for database
        new_rows = pd.DataFrame([
            {'gRNA_20bp': grna, 'passed': passed}
            for grna, passed in chunk_results.items()
        ])
        
        # Merge with existing cache
        if cached_df.empty:
            merged = new_rows
        else:
            merged = pd.concat([cached_df, new_rows], ignore_index=True)
            merged = merged.drop_duplicates(subset=['gRNA_20bp'], keep='last')
        
        # Save updated cache
        conn = open_cache_connection(cache_db_path)
        try:
            merged.to_sql("offtarget_cache", conn, if_exists="replace", index=False)
        finally:
            conn.close()
        
        # Update cached_df for next iteration
        cached_df = merged
        
        # Mark chunk as completed
        num_passed_in_chunk = sum(1 for g in chunk_gRNAs if cache_lookup.get(g, False))
        save_chunk_completion(cache_db_path, chunk_id, chunk_genes, len(chunk_gRNAs), num_passed_in_chunk)
        
        log(f"{chunk_id}: Complete. Passed: {num_passed_in_chunk}/{len(chunk_gRNAs)}")

    total_passed = sum(1 for v in cache_lookup.values() if v)
    total_tested = len(cache_lookup)
    
    log(f"\n{'='*60}")
    log(f"Off-target analysis complete.")
    log(f"Total gRNAs tested: {total_tested}")
    log(f"Total gRNAs passed: {total_passed} ({100*total_passed/total_tested:.1f}%)")
    log(f"{'='*60}\n")

    # ---------------------------------------------------------
    # 4. Score per gene - Filter by passed status and calculate scores
    # ---------------------------------------------------------
    results_per_gene = {}
    all_grnas_for_table = []

    for gene_id, candidates in all_candidates.items():
        log(f"Processing gene {gene_id}: filtering and scoring {len(candidates)} candidates...")

        input_seq, full_context_seq = full_context_seqs[gene_id]
        full_context_seq_rev = reverse_complement(full_context_seq)

        filtered_candidates = []

        for cand in candidates:
            # Skip if this gRNA hasn't been tested yet (not in cache)
            if cand['gRNA_20bp'] not in cache_lookup:
                continue
            
            # Determine if passed from cache
            passed_val = 1 if cache_lookup[cand['gRNA_20bp']] else 0
            
            corrected_loc = cand['location']

            # CRISPRScan (always calculate)
            score_val = calcCrisprScanScores([cand['crispr_seq']])[0]
            
            # Add to filtered list (only passed gRNAs go to results_per_gene)
            if passed_val == 1:
                filtered_candidates.append({
                    'gRNA_seq': cand['gRNA_seq'],
                    'CRISPR_Scan_Score': score_val,
                    'location': corrected_loc,
                    'strand': cand['strand']
                })
            
            # Store ALL candidates for the table (with passed column)
            all_grnas_for_table.append({
                'gene_id': gene_id,
                'gRNA_seq': cand['gRNA_seq'],
                'CRISPR_Scan_Score': score_val,
                'location': corrected_loc,
                'strand': cand['strand'],
                'passed': passed_val
            })

        # if nothing passed, skip
        if not filtered_candidates:
            log(f"Gene {gene_id}: No candidates passed off-target filtering.")
            results_per_gene[gene_id] = pd.DataFrame()
            continue

        df_all = pd.DataFrame(filtered_candidates)

        # keep all ≥45, top up to 15 from below-45 if needed
        passing = df_all[df_all['CRISPR_Scan_Score'] >= 0].copy()
        below_threshold = df_all[df_all['CRISPR_Scan_Score'] < 0].copy()

        if len(passing) < 15 and not below_threshold.empty:
            needed = 15 - len(passing)
            top_below = below_threshold.nlargest(needed, 'CRISPR_Scan_Score')
            df_all = pd.concat([passing, top_below], ignore_index=True)
        else:
            df_all = passing.reset_index(drop=True)

        # ensure formatting
        if not df_all.empty and 'CRISPR_Scan_Score' in df_all.columns:
            df_all['CRISPR_Scan_Score'] = df_all['CRISPR_Scan_Score'].astype(str).str.strip('[]')

        log(f"Gene {gene_id}: {len(df_all)} gRNAs selected after filtering.")
        results_per_gene[gene_id] = df_all

    # ---------------------------------------------------------
    # 5. Save ALL gRNAs to filtered_gRNAs table (with passed column)
    # ---------------------------------------------------------
    if all_grnas_for_table:
        all_df = pd.DataFrame(all_grnas_for_table)
        conn = open_cache_connection(cache_db_path)
        try:
            # CRITICAL: Use 'append' not 'replace' to avoid wiping existing cache!
            # We only want to add NEW gRNAs, not delete existing ones
            all_df.to_sql('filtered_gRNAs', conn, if_exists='append', index=False)
            log(f"Appended {len(all_df)} gRNAs to filtered_gRNAs table")
        finally:
            conn.close()

    log(f"\nSummary: Pythia will score gRNAs from {len([g for g in results_per_gene.values() if not g.empty])} genes")
    
    return results_per_gene

def process_pythia_integration_with_gRNA(input_seq, full_context_seq, celltype, integration_mode, gene_id, filtered_gRNAs_df, microhomology_length=3):
    """
    Process integration predictions for a gene using pre-filtered gRNAs.
    OPTIMIZED: Store genotypes during pythia prediction to avoid recalculation.

    NOTE: filtered_gRNAs_df contains ONLY gRNAs that passed off-target filtering.
    """
    log(f"Processing integration mode: {integration_mode} for gene {gene_id}")
    log(f"Input: {len(filtered_gRNAs_df)} gRNAs that passed off-target filtering")
    reload_inDelphi_if_needed(celltype)

    # Set MICROHOMOLOGY_LENGTH for use in homology calculations
    MICROHOMOLOGY_LENGTH = microhomology_length
    
    df_all = filtered_gRNAs_df.copy()
    
    # Return early if no candidates
    if df_all.empty:
        log(f"No gRNA candidates available for gene {gene_id}.")
        return pd.DataFrame()
    
    # --- Extract 80-base context for each gRNA (vectorized where possible) ---
    rev_context = reverse_complement(full_context_seq)
    
    # Vectorize context extraction
    contexts = []
    for idx, row in df_all.iterrows():
        if row['strand'] == 'plus':
            c = get_context(full_context_seq, row['gRNA_seq'])
        else:
            c = get_context(rev_context, row['gRNA_seq'])
        contexts.append(c if c and len(c)==80 else None)
    
    df_all['contexts'] = contexts
    df_all = df_all.dropna(subset=['contexts'])
    df_all = df_all[df_all['contexts'].apply(lambda x: isinstance(x, str) and len(x)==80)]
    
    # Pre-compute GFP reverse complement (used multiple times)
    GFP_REVCOMP = reverse_complement(GFP_SEQUENCE)
    
    # --- Integration Prediction for donor boundaries ---
    final_results = pd.DataFrame()
    total_gRNAs = len(df_all)

    df_all = df_all.reset_index(drop=True)
    
    for j, row in df_all.iterrows():
        log(f"Processing gRNA: {row['gRNA_seq']} ({j+1}/{total_gRNAs} for gene {gene_id})")
        gRNA_name = row['gRNA_seq']
        loc = int(row['location'])
        orig_strand = row['strand']
        score = row.get('CRISPR_Scan_Score', None)
        context_current = row['contexts']
        
        dynamic_cassette = get_dynamic_cassette(input_seq, loc)
        if orig_strand == 'min':
            dynamic_cassette = reverse_complement(dynamic_cassette)
            donor_component = GFP_REVCOMP + dynamic_cassette
        else:
            donor_component = dynamic_cassette + GFP_SEQUENCE
        
        # Pre-split context
        Left = context_current[:40]
        Right = context_current[40:]
        
        # Determine homology length ranges based on strand
        if orig_strand == 'plus':
            left_homol_lengths = [MICROHOMOLOGY_LENGTH]
            left_repeat_range = range(2, 6)
            right_homol_lengths = [3, 4, 5, 6]
            right_repeat_range = [5]
        else:
            left_homol_lengths = [3, 4, 5, 6]
            left_repeat_range = [5]
            right_homol_lengths = [MICROHOMOLOGY_LENGTH]
            right_repeat_range = range(2, 6)
        
        # Store genotypes during prediction to avoid recalculation
        genotype_cache = {}
        results_list = []  # Use list for faster appending
        
        # Left boundary predictions
        for i in left_homol_lengths:
            ology = Left[-i:]
            for j2 in left_repeat_range:
                Left_donor = ology * j2 + donor_component
                
                # For minus strand, reverse complement the sequence for inDelphi
                if orig_strand == 'min':
                    seq_for_indelphi = reverse_complement(Left + Left_donor)
                    cutsite_for_indelphi = len(seq_for_indelphi) - len(Left)
                else:
                    seq_for_indelphi = Left + Left_donor
                    cutsite_for_indelphi = len(Left)
                
                pred_df, stats = inDelphi.predict(seq_for_indelphi, cutsite_for_indelphi)
                pred_df = inDelphi.add_genotype_column(pred_df, stats)
                pred_df = pred_df.dropna(subset=['Genotype'])
                
                # Store genotypes in cache for this boundary configuration
                cache_key = ('left', i, j2)
                genotype_cache[cache_key] = pred_df[['Genotype', 'Predicted frequency']].values.tolist()
                
                for _, row_pred in pred_df.iterrows():
                    genotype_upper = row_pred['Genotype'].upper()
                    for x in range(6):
                        repair_string = Left + ology * x + donor_component
                        
                        if orig_strand == 'min':
                            repair_string_check = reverse_complement(repair_string)
                        else:
                            repair_string_check = repair_string
                        
                        if repair_string_check.upper() in genotype_upper:
                            results_list.append({
                                "side": "left",
                                "Homol_length": i,
                                "Amount_of_trimologies": j2,
                                "Predicted_frequency": row_pred['Predicted frequency'],
                                "Perfect_repair_at": x,
                                "context": context_current,
                                "genotype": row_pred['Genotype'],  # Store genotype
                                "cache_key": cache_key
                            })

        # Right boundary predictions
        for i in right_homol_lengths:
            ology = Right[:i]
            for j2 in right_repeat_range:
                Right_donor = donor_component + (ology * j2)
                
                if orig_strand == 'min':
                    seq_for_indelphi = reverse_complement(Right_donor + Right)
                    cutsite_for_indelphi = len(seq_for_indelphi) - len(Right_donor)
                else:
                    seq_for_indelphi = Right_donor + Right
                    cutsite_for_indelphi = len(Right_donor)
                
                pred_df, stats = inDelphi.predict(seq_for_indelphi, cutsite_for_indelphi)
                pred_df = inDelphi.add_genotype_column(pred_df, stats)
                pred_df = pred_df.dropna(subset=['Genotype'])
                
                # Store genotypes in cache
                cache_key = ('right', i, j2)
                genotype_cache[cache_key] = pred_df[['Genotype', 'Predicted frequency']].values.tolist()
                
                for _, row_pred in pred_df.iterrows():
                    genotype_upper = row_pred['Genotype'].upper()
                    for x in range(6):
                        repair_string = donor_component + ology * x + Right
                        
                        if orig_strand == 'min':
                            repair_string_check = reverse_complement(repair_string)
                        else:
                            repair_string_check = repair_string

                        if repair_string_check.upper() in genotype_upper:
                            results_list.append({
                                "side": "right",
                                "Homol_length": i,
                                "Amount_of_trimologies": j2,
                                "Predicted_frequency": row_pred['Predicted frequency'],
                                "Perfect_repair_at": x,
                                "context": context_current,
                                "genotype": row_pred['Genotype'],  # Store genotype
                                "cache_key": cache_key
                            })

        if not results_list:
            log("No integration predictions produced for this gRNA.")
            continue
        
        # Convert to DataFrame once
        results_df = pd.DataFrame(results_list)
        
        # Store genotype cache in the row data for later use
        agg_df = results_df.groupby(['Amount_of_trimologies', 'Homol_length', 'side', 'context'])['Predicted_frequency'].sum().reset_index()
        agg_df["gRNA"] = gRNA_name
        agg_df["CRISPRScan_score"] = score
        agg_df["strand"] = orig_strand
        agg_df["location"] = loc
        agg_df["dynamic_cassette"] = dynamic_cassette
        agg_df["genotype_cache"] = [genotype_cache] * len(agg_df)  # Store cache with each row
        
        final_results = pd.concat([final_results, agg_df], ignore_index=True)
    
    if final_results.empty:
        log("No integration predictions produced for this sequence.")
        return final_results
    if 'side' not in final_results.columns:
        log("Warning: 'side' column missing in final_results; cannot merge left/right predictions.")
        return final_results
    
    # --- Merge left and right predictions ---
    left_df = final_results[final_results['side'] == 'left'].copy().reset_index(drop=True)
    right_df = final_results[final_results['side'] == 'right'].copy().reset_index(drop=True)
    
    merged_df = pd.merge(
        left_df, 
        right_df, 
        on=['gRNA', 'CRISPRScan_score', 'strand', 'location', 'dynamic_cassette', 'context'],
        suffixes=('_left', '_right')
    )
    
    # Calculate integration score
    merged_df['integration_score'] = (merged_df['Predicted_frequency_left'] * merged_df['Predicted_frequency_right']) / 100

    # --- Complexity Tie-Breaker Integration ---
    max_scores = merged_df.groupby('gRNA')['integration_score'].max().reset_index()
    max_scores.rename(columns={'integration_score': 'max_integration_score'}, inplace=True)
    merged_df = pd.merge(merged_df, max_scores, on='gRNA', how='left')
    merged_df['threshold'] = merged_df['max_integration_score'] - 1
    filtered_df = merged_df[merged_df['integration_score'] >= merged_df['threshold']]
    filtered_df['solution_complexity'] = (
        filtered_df['Amount_of_trimologies_left'] * filtered_df['Homol_length_left'] +
        filtered_df['Amount_of_trimologies_right'] * filtered_df['Homol_length_right']
    )
    complexity_idx = filtered_df.groupby('gRNA')['solution_complexity'].idxmin().tolist()
    max_integration_scores = filtered_df.loc[complexity_idx]
    max_integration_scores = max_integration_scores.sort_values(by='integration_score', ascending=False).reset_index(drop=True)
    
    # --- Repair Arm Extraction (vectorized) ---
    def extract_left_repair_arm(row):
        hl = int(row["Homol_length_left"])
        context = row["context"]
        mid = 40  # Pre-computed len(context) // 2
        start = max(0, mid - hl)
        return context[start:mid] * int(row["Amount_of_trimologies_left"])
    
    def extract_right_repair_arm(row):
        hr = int(row["Homol_length_right"])
        context = row["context"]
        mid = 40
        end = min(80, mid + hr)
        return context[mid:end] * int(row["Amount_of_trimologies_right"])
    
    max_integration_scores["left_repair_arm"] = max_integration_scores.apply(extract_left_repair_arm, axis=1)
    max_integration_scores["right_repair_arm"] = max_integration_scores.apply(extract_right_repair_arm, axis=1)
    max_integration_scores["Revcomp_right_repair_arm"] = max_integration_scores["right_repair_arm"].apply(reverse_complement)
    
    # Compute the full repair cassette
    def compute_full_repair_cassette(row):
        if row["strand"] == "min":
            return row["left_repair_arm"] + GFP_REVCOMP + row["dynamic_cassette"] + row["right_repair_arm"]
        else:
            return row["left_repair_arm"] + row["dynamic_cassette"] + GFP_SEQUENCE + row["right_repair_arm"]
    
    max_integration_scores["Repair_Cassette"] = max_integration_scores.apply(compute_full_repair_cassette, axis=1)
    
    # Compute the Core Cassette (without repair arms)
    def compute_core_cassette(row):
        if row["strand"] == "min":
            return GFP_REVCOMP + row["dynamic_cassette"]
        else:
            return row["dynamic_cassette"] + GFP_SEQUENCE
    
    max_integration_scores["Core_Cassette"] = max_integration_scores.apply(compute_core_cassette, axis=1)
    
    # --- Add perfect repair genotypes using stored cache ---
    max_integration_scores = add_genotype_columns_from_cache(max_integration_scores)
    
    # Drop unnecessary columns
    max_integration_scores = max_integration_scores.drop(columns=['side_left', 'side_right', 'genotype_cache_left', 'genotype_cache_right'], errors='ignore')
    
    log("Integration analysis completed for this sequence.")
    return max_integration_scores

def add_genotype_columns_from_cache(max_integration_scores):
    """
    OPTIMIZED: Extract genotypes from cached predictions instead of recalculating.
    """
    # Initialize columns
    for x in range(6):
        max_integration_scores[f'x{x}_genotype'] = ''
        max_integration_scores[f'x{x}_frequency'] = 0.0
    
    for idx, row in max_integration_scores.iterrows():
        # Determine which boundary to use based on strand
        if row['strand'] == 'plus':
            # Use left boundary
            cache_key = ('left', int(row['Homol_length_left']), int(row['Amount_of_trimologies_left']))
            genotype_cache = row.get('genotype_cache_left', {})
            
            Left = row['context'][:40]
            ology = Left[-int(row['Homol_length_left']):]
            if row["strand"] == "min":
                GFP_used = reverse_complement(GFP_SEQUENCE)
                donor_component = GFP_used + row["dynamic_cassette"]
            else:
                donor_component = row["dynamic_cassette"] + GFP_SEQUENCE
            
            # Get genotypes from cache
            if cache_key in genotype_cache:
                cached_genotypes = genotype_cache[cache_key]
                for x in range(6):
                    repair_string = Left + ology * x + donor_component
                    if row["strand"] == "min":
                        repair_string_check = reverse_complement(repair_string).upper()
                    else:
                        repair_string_check = repair_string.upper()
                    
                    # Find matching genotype in cache
                    for genotype, freq in cached_genotypes:
                        if repair_string_check in genotype.upper():
                            max_integration_scores.at[idx, f'x{x}_genotype'] = genotype
                            max_integration_scores.at[idx, f'x{x}_frequency'] = freq
                            break
        else:
            # Use right boundary for minus strand
            cache_key = ('right', int(row['Homol_length_right']), int(row['Amount_of_trimologies_right']))
            genotype_cache = row.get('genotype_cache_right', {})
            
            Right = row['context'][40:]
            ology = Right[:int(row['Homol_length_right'])]
            if row["strand"] == "min":
                GFP_used = reverse_complement(GFP_SEQUENCE)
                donor_component = GFP_used + row["dynamic_cassette"]
            else:
                donor_component = row["dynamic_cassette"] + GFP_SEQUENCE
            
            # Get genotypes from cache
            if cache_key in genotype_cache:
                cached_genotypes = genotype_cache[cache_key]
                for x in range(5):
                    repair_string = donor_component + ology * x + Right
                    if row["strand"] == "min":
                        repair_string_check = reverse_complement(repair_string).upper()
                    else:
                        repair_string_check = repair_string.upper()
                    
                    # Find matching genotype in cache
                    for genotype, freq in cached_genotypes:
                        if repair_string_check in genotype.upper():
                            max_integration_scores.at[idx, f'x{x}_genotype'] = genotype
                            max_integration_scores.at[idx, f'x{x}_frequency'] = freq
                            break
    
    return max_integration_scores

def translate_genotype_to_protein(genotype, full_protein_data, gene_id, transcript_id, last_exon_seq, location):
    """
    Translate a genotype to its protein sequence.
    Translates the entire sequence and marks stop codons with *.
    """
    try:
        # Get the full CDS for this transcript
        protein_row = full_protein_data[
            (full_protein_data['gene_id'] == gene_id) & 
            (full_protein_data['transcript_id'] == transcript_id)
        ]
        
        if protein_row.empty:
            log(f"Warning: No protein data found for {gene_id}/{transcript_id}")
            return "", 0
        
        full_cds = protein_row.iloc[0]['nucleotide_sequence']
        
        # Find where the last exon starts in the full CDS
        last_exon_start_in_cds = full_cds.find(last_exon_seq)
        
        if last_exon_start_in_cds == -1:
            log(f"Warning: Last exon not found in CDS for {gene_id}/{transcript_id}")
            return "", 0
        
        # Calculate the cut position in the full CDS
        cut_position_in_cds = last_exon_start_in_cds + location
        
        # Calculate the cut position in the protein (amino acid position)
        cut_position_in_protein = cut_position_in_cds // 3
        
        # Build the modified sequence
        if location >= 40:
            keep_until = location - 40
            modified_last_exon = last_exon_seq[:keep_until] + genotype
        else:
            skip_bp = 40 - location
            modified_last_exon = genotype[skip_bp:]
        
        # Build the full modified CDS
        modified_cds = full_cds[:last_exon_start_in_cds] + modified_last_exon
        
        # Translate in chunks of 3, manually handling stop codons
        protein = ""
        for i in range(0, len(modified_cds) - 2, 3):
            codon = modified_cds[i:i+3]
            if len(codon) == 3:
                aa = str(Seq(codon).translate())
                protein += aa
        
        return protein, cut_position_in_protein
        
    except Exception as e:
        log(f"Warning: Error translating genotype for {gene_id}/{transcript_id}: {e}")
        return "", 0
    
def add_protein_translations_to_results(max_integration_scores, full_protein_data, gene_id, transcript_id, last_exon_seq):
    """
    Add protein translation columns for x0-x5 genotypes.
    """
    # Initialize protein columns
    for x in range(5):
        max_integration_scores[f'x{x}_protein'] = ''
    
    max_integration_scores['protein_cut_position'] = 0
    
    for idx, row in max_integration_scores.iterrows():
        location = int(row['location'])
        cut_position_set = False
        
        for x in range(6):
            genotype_col = f'x{x}_genotype'
            if genotype_col in row and row[genotype_col]:
                genotype = row[genotype_col]
                protein, cut_position = translate_genotype_to_protein(
                    genotype=genotype,
                    full_protein_data=full_protein_data,
                    gene_id=gene_id,
                    transcript_id=transcript_id,
                    last_exon_seq=last_exon_seq,
                    location=location
                )
                max_integration_scores.at[idx, f'x{x}_protein'] = protein
                
                if not cut_position_set:
                    max_integration_scores.at[idx, 'protein_cut_position'] = cut_position
                    cut_position_set = True
    
    return max_integration_scores

def process_db_file(input_db, output_db, cache_db_path, celltype="mESC", integration_mode="last_exon", microhomology_length=3, search_only=False, pythia_only=False):
    # Read from SQLite database
    conn = sqlite3.connect(input_db)
    df = pd.read_sql_query("SELECT * FROM transcript_data", conn)
    full_protein_data = df.copy()
    conn.close()
    
    final_df = pd.DataFrame()
    
    total_genes = len(df)
    log(f"Starting processing for {total_genes} genes...")
    
    # CHECK FOR EXISTING GRNA DATABASE
    grna_cache_db = cache_db_path
    filtered_gRNAs_per_gene = {}
    full_context_seqs = {}
    
    # ===== PHASE 1: gRNA Search + Cas-offinder =====
    if not pythia_only:
        log("\n=== PHASE 1: gRNA SEARCH + CAS-OFFINDER ===")
        
        # Load existing cache if available
        cached_gene_ids = set()
        if os.path.exists(grna_cache_db):
            log(f"Loading cached gRNAs from {grna_cache_db}")
            try:
                conn = sqlite3.connect(grna_cache_db)
                # ONLY load gRNAs that passed (passed = 1)
                cached_grnas_df = pd.read_sql_query("SELECT * FROM filtered_gRNAs WHERE passed = 1", conn)
                conn.close()
                # Store cached gRNAs by gene_id
                for gene_id in cached_grnas_df['gene_id'].unique():
                    cached_gene_ids.add(gene_id)
                    gene_grnas = cached_grnas_df[cached_grnas_df['gene_id'] == gene_id].copy()
                    gene_grnas = gene_grnas.drop(columns=['gene_id'])
                    filtered_gRNAs_per_gene[gene_id] = gene_grnas
                
                log(f"Successfully loaded cached gRNAs for {len(cached_gene_ids)} genes")
                
            except Exception as e:
                log(f"Error loading cached gRNAs: {e}. Will regenerate.")
        
        # Identify genes that need gRNA generation
        genes_needing_grnas = []
        for i, row in df.iterrows():
            gene_id = row['gene_id']
            last_exon_seq = row['last_exon_sequence']
            if 'last_exon_sequence_with_context' in df.columns:
                full_context_seq = row['last_exon_sequence_with_context']
            else:
                full_context_seq = last_exon_seq

            full_context_seqs[gene_id] = (last_exon_seq, full_context_seq)

            if gene_id not in cached_gene_ids:
                genes_needing_grnas.append((i, gene_id, last_exon_seq, full_context_seq))
        
        # Only run Steps 1 and 2 if we have uncached genes
        if genes_needing_grnas:
            log(f"\n=== PROCESSING {len(genes_needing_grnas)} UNCACHED GENES ===")
            
            # Step 1: Collect candidates for uncached genes
            log("\n=== STEP 1: Collecting gRNA candidates for uncached genes ===")
            all_candidates_dict = {}
            
            for i, gene_id, last_exon_seq, full_context_seq in genes_needing_grnas:
                log(f"Collecting candidates for gene: {gene_id}")
                candidates = collect_all_candidate_gRNAs(last_exon_seq, full_context_seq, gene_id)
                all_candidates_dict[gene_id] = candidates
            
            # Step 2: Run batch off-target analysis and filter
            log("\n=== STEP 2: Running batch off-target analysis for uncached genes ===")
            new_filtered_gRNAs = filter_offtarget_and_score_gRNAs(
                all_candidates_dict,
                full_context_seqs,
                celltype,
                cache_db_path
            )
            
            # Merge new results with cached results
            filtered_gRNAs_per_gene.update(new_filtered_gRNAs)
            
            # SAVE NEW GRNAS TO CACHE DATABASE
            log(f"\n=== UPDATING cache {grna_cache_db} with new gRNAs ===")
            cache_rows = []
            for gene_id, grnas_df in new_filtered_gRNAs.items():
                if not grnas_df.empty:
                    temp_df = grnas_df.copy()
                    temp_df['gene_id'] = gene_id
                    cache_rows.append(temp_df)
            
            if cache_rows:
                new_cache_df = pd.concat(cache_rows, ignore_index=True)
                cols = ['gene_id'] + [col for col in new_cache_df.columns if col != 'gene_id']
                new_cache_df = new_cache_df[cols]
                
                conn = sqlite3.connect(grna_cache_db)
                new_cache_df.to_sql('filtered_gRNAs', conn, if_exists='append', index=False)
                conn.close()
                log(f"Added {len(new_cache_df)} new gRNAs to cache database")
        else:
            log(f"\n=== ALL {total_genes} GENES FOUND IN CACHE ===")
        
        # If search-only mode, stop here
        if search_only:
            log("\n=== SEARCH-ONLY MODE: Exiting before Pythia scoring ===")
            return pd.DataFrame()
    
    # ===== PHASE 2: Pythia Scoring =====
    if not search_only:
        log("\n=== PHASE 2: PYTHIA SCORING ===")

        if pythia_only:
            log("Pythia-only mode: Loading gRNAs from cache...")

            if not os.path.exists(grna_cache_db):
                log(f"ERROR: Cache database not found at {grna_cache_db}")
                return pd.DataFrame()

            try:
                # Extract gene IDs from input database
                log("Extracting gene IDs from input database...")
                gene_ids_in_subset = df['gene_id'].unique().tolist()
                log(f"Input DB contains {len(gene_ids_in_subset)} genes")

                # MEMORY FIX: Process genes in chunks to avoid loading all data at once
                CHUNK_SIZE = 50  # Process 50 genes at a time (optimized for parallel workers)
                total_genes = len(gene_ids_in_subset)
                num_chunks = (total_genes + CHUNK_SIZE - 1) // CHUNK_SIZE

                log(f"Processing {total_genes} genes in {num_chunks} chunks of {CHUNK_SIZE} genes each")
                log("This approach keeps memory usage low by loading data incrementally")
                log(f"Per-worker memory optimization: Each worker processes ~{total_genes} genes in {num_chunks} chunks")

                conn = sqlite3.connect(grna_cache_db)

                # Create index on gene_id and passed columns for faster queries
                log("Ensuring database indexes exist for optimal performance...")
                try:
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_gene_id ON filtered_gRNAs(gene_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_passed ON filtered_gRNAs(passed)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_gene_passed ON filtered_gRNAs(gene_id, passed)")
                    conn.commit()
                    log("Database indexes verified/created")
                except Exception as e:
                    log(f"Warning: Could not create indexes (may already exist): {e}")

                for chunk_idx in range(num_chunks):
                    start_idx = chunk_idx * CHUNK_SIZE
                    end_idx = min((chunk_idx + 1) * CHUNK_SIZE, total_genes)
                    chunk_gene_ids = gene_ids_in_subset[start_idx:end_idx]

                    log(f"\n[Chunk {chunk_idx+1}/{num_chunks}] Processing genes {start_idx+1} to {end_idx}")

                    # Create temp table for this chunk only
                    cursor = conn.cursor()
                    cursor.execute("DROP TABLE IF EXISTS temp_gene_ids")
                    cursor.execute("CREATE TEMPORARY TABLE temp_gene_ids (gene_id TEXT)")

                    # Insert in smaller batches to avoid memory spike
                    batch_size = 1000
                    for i in range(0, len(chunk_gene_ids), batch_size):
                        batch = chunk_gene_ids[i:i+batch_size]
                        cursor.executemany("INSERT INTO temp_gene_ids VALUES (?)", [(gid,) for gid in batch])
                    conn.commit()

                    # Query only this chunk's gRNAs
                    query = """
                        SELECT f.* FROM filtered_gRNAs f
                        INNER JOIN temp_gene_ids t ON f.gene_id = t.gene_id
                        WHERE f.passed = 1
                    """

                    log(f"[Chunk {chunk_idx+1}/{num_chunks}] Loading gRNAs from database...")
                    chunk_df = pd.read_sql_query(query, conn)
                    log(f"[Chunk {chunk_idx+1}/{num_chunks}] Loaded {len(chunk_df)} gRNAs")

                    if chunk_df.empty:
                        log(f"[Chunk {chunk_idx+1}/{num_chunks}] No gRNAs found")
                        continue

                    # Group and store this chunk's data
                    log(f"[Chunk {chunk_idx+1}/{num_chunks}] Organizing gRNAs by gene_id...")
                    grouped = chunk_df.groupby('gene_id', sort=False)

                    for gene_id, group in grouped:
                        filtered_gRNAs_per_gene[gene_id] = group.drop(columns=['gene_id']).reset_index(drop=True)

                    log(f"[Chunk {chunk_idx+1}/{num_chunks}] Stored gRNAs for {len(grouped)} genes")

                    # Free memory immediately
                    del chunk_df
                    del grouped
                    import gc
                    gc.collect()

                conn.close()
                log(f"\nSuccessfully organized gRNAs for {len(filtered_gRNAs_per_gene)} genes total")

                # Populate full_context_seqs (use itertuples for speed)
                log("Populating sequence context data...")
                for row in df.itertuples():
                    gene_id = row.gene_id
                    last_exon_seq = row.last_exon_sequence
                    if 'last_exon_sequence_with_context' in df.columns:
                        full_context_seq = row.last_exon_sequence_with_context
                    else:
                        full_context_seq = last_exon_seq
                    full_context_seqs[gene_id] = (last_exon_seq, full_context_seq)

                log("Pythia-only mode data loading complete!")

            except Exception as e:
                log(f"ERROR loading gRNAs from cache: {e}")
                import traceback
                traceback.print_exc()
                return pd.DataFrame()

        # ===== PREPROCESSING: Build last_exon → all gene_ids mapping =====
        log("\n=== PREPROCESSING: Building last_exon to gene_ids mapping ===")
        last_exon_to_gene_ids = {}
        gene_id_to_transcript_id = {}

        for row in df.itertuples():
            gene_id = row.gene_id
            transcript_id = row.transcript_id if hasattr(row, 'transcript_id') else gene_id
            last_exon_seq = row.last_exon_sequence

            # Map each gene_id to its transcript_id
            gene_id_to_transcript_id[gene_id] = transcript_id

            # Map last_exon_seq to ALL gene_ids that share it
            if last_exon_seq not in last_exon_to_gene_ids:
                last_exon_to_gene_ids[last_exon_seq] = []
            last_exon_to_gene_ids[last_exon_seq].append(gene_id)

        # Log statistics
        total_gene_ids = len(df)
        unique_last_exons = len(last_exon_to_gene_ids)
        max_sharing = max(len(genes) for genes in last_exon_to_gene_ids.values())
        avg_sharing = sum(len(genes) for genes in last_exon_to_gene_ids.values()) / unique_last_exons

        log(f"Total gene_ids (transcript variants): {total_gene_ids}")
        log(f"Unique last exon sequences: {unique_last_exons}")
        log(f"Average gene_ids per last exon: {avg_sharing:.1f}")
        log(f"Max gene_ids sharing one last exon: {max_sharing}")

        # Step 3: Process integration predictions for each gene
        log("\n=== STEP 3: Processing integration predictions ===")
        computed_cache = {}
        processed_last_exons = set()  # Track which last_exon sequences we've already saved
        
        for i, row in df.iterrows():
            gene_id = row['gene_id']
            transcript_id = row['transcript_id']
            last_exon_seq = row['last_exon_sequence']
            if 'last_exon_sequence_with_context' in df.columns:
                full_context_seq = row['last_exon_sequence_with_context']
            else:
                full_context_seq = last_exon_seq

            # SKIP if we've already saved results for this last_exon sequence
            if last_exon_seq in processed_last_exons:
                log(f"⏭️  Gene {gene_id} shares last exon with already-processed gene - skipping save (avoiding duplicate)")
                continue

            log(f"\nProcessing integration for gene: {gene_id} ({i+1}/{total_genes})")

            # Check if this gene has filtered gRNAs
            if gene_id not in filtered_gRNAs_per_gene or filtered_gRNAs_per_gene[gene_id].empty:
                log(f"No filtered gRNAs available for gene {gene_id}. Skipping.")
                continue

            # Check cache for duplicate sequences (for computation reuse)
            if last_exon_seq in computed_cache:
                log(f"⚡ Reusing cached Pythia computation for gene {gene_id}")
                integration_results = computed_cache[last_exon_seq].copy()
            else:
                integration_results = process_pythia_integration_with_gRNA(
                    input_seq=last_exon_seq,
                    full_context_seq=full_context_seq,
                    celltype=celltype,
                    integration_mode=integration_mode,
                    gene_id=gene_id,
                    filtered_gRNAs_df=filtered_gRNAs_per_gene[gene_id],
                    microhomology_length=microhomology_length
                )
                computed_cache[last_exon_seq] = integration_results.copy()

            if integration_results.empty:
                log("No integration events found for this gene.")
                continue

            # COLLAPSE ALL GENE_IDs SHARING THIS LAST EXON
            # Get all gene_ids that share this last_exon_seq
            all_gene_ids_for_this_exon = last_exon_to_gene_ids.get(last_exon_seq, [gene_id])

            # Convert to transcript IDs (comma-separated)
            all_transcript_ids = [gene_id_to_transcript_id.get(gid, gid) for gid in all_gene_ids_for_this_exon]
            transcript_list_str = ','.join(all_transcript_ids)

            # Also store gene_ids as comma-separated
            gene_id_list_str = ','.join(all_gene_ids_for_this_exon)

            integration_results['gene_id'] = gene_id_list_str
            integration_results['transcript_ids'] = transcript_list_str

            log(f"📋 Last exon shared by {len(all_gene_ids_for_this_exon)} gene_id(s): {gene_id_list_str}")
            log(f"   Transcript IDs: {transcript_list_str}")

            # Add protein translations (use first gene_id/transcript for protein data)
            integration_results = add_protein_translations_to_results(
                integration_results,
                full_protein_data,
                all_gene_ids_for_this_exon[0],
                all_transcript_ids[0],
                last_exon_seq
            )

            columns_to_keep = [
                'gene_id',
                'transcript_ids',
                'gRNA',
                'CRISPRScan_score',
                'Predicted_frequency_left',
                'Predicted_frequency_right',
                'integration_score',
                'strand',
                'location',
                'Amount_of_trimologies_left',
                'Homol_length_left',
                'left_repair_arm',
                'Amount_of_trimologies_right',
                'Homol_length_right',
                'right_repair_arm',
                'Repair_Cassette',
                'protein_cut_position',
                'x0_genotype',
                'x0_frequency',
                'x0_protein',
                'x1_genotype',
                'x1_frequency',
                'x1_protein',
                'x2_genotype',
                'x2_frequency',
                'x2_protein',
                'x3_genotype',
                'x3_frequency',
                'x3_protein',
                'x4_genotype',
                'x4_frequency',
                'x4_protein'
            ]

            # Only keep columns that exist
            columns_available = [col for col in columns_to_keep if col in integration_results.columns]
            integration_results = integration_results[columns_available]

            # Save results and mark this last_exon as processed
            final_df = pd.concat([final_df, integration_results], ignore_index=True)
            processed_last_exons.add(last_exon_seq)

            log(f"✅ Saved results for gene {gene_id} (marked last_exon as processed)")

        # Log summary statistics
        log("\n" + "="*60)
        log("DEDUPLICATION SUMMARY")
        log("="*60)
        log(f"Total input gene_ids (transcript variants): {total_genes}")
        log(f"Unique last exon sequences saved: {len(processed_last_exons)}")
        log(f"Output reduction factor: {total_genes / len(processed_last_exons):.1f}x")
        log(f"Storage savings: {100 * (1 - len(processed_last_exons)/total_genes):.1f}%")
        log("="*60 + "\n")

        try:
            conn = sqlite3.connect(output_db)
            table_name = f"{microhomology_length}BP_{celltype}"
            final_df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            log(f"\n=== ALL PROCESSING COMPLETED ===")
            log(f"Results saved to database: {output_db}")
            log(f"Output schema:")
            log(f"  - gene_id: comma-separated list of all gene_ids sharing the same last exon")
            log(f"  - transcript_ids: comma-separated list of corresponding transcript IDs")
            log(f"  - One row per unique last exon sequence (deduplicated)")
            end = time.time()
        except Exception as e:
            log(f"Error saving to database: {e}")
    
    return final_df

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--cache-db", required=True)
    p.add_argument("--celltype", default="mESC", help="Cell type for inDelphi")
    p.add_argument("--microhomology", type=int, default=3, help="Microhomology length (3 or 6)")
    p.add_argument("--search-only", action="store_true", help="Only run gRNA search and cas-offinder, skip Pythia scoring")
    p.add_argument("--pythia-only", action="store_true",help="Only run Pythia scoring, skip gRNA search (assumes cache DB is populated)")
    p.add_argument('-CPU', type=int, default=1, help='Number of CPU cores to use')

    args = p.parse_args()

    process_db_file(args.input, args.output, args.cache_db, 
                    celltype=args.celltype, 
                    microhomology_length=args.microhomology,
                    search_only=args.search_only,
                    pythia_only=args.pythia_only)

if __name__ == "__main__":
    main()