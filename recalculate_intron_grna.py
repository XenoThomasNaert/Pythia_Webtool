"""
Standalone helper to recompute intron-tagging integration scores for a single gRNA/tag pair.
This file is self-contained and does NOT import Pythia_IntronTagger.
"""
import argparse
import importlib
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger('pythia.browser')

import pandas as pd

# Default GFP tag (plus orientation).
GFP_SEQUENCE = ("GGATCAGGAGGATCAGGAATGGTCTCAAAGGGAGAGGAGGAAAACATGGCTAGTACACCATTTAAATTTCAACTTAAAGGAACCATCAATGGCAAATCGTTTACCGTTGAAGGCGAAGGTGAAGGGAAcTCACATGAAGGTTCTCATAAAGGAAAATATGTTTGTACAAGTGGAAAACTACCGATGTCATGGGCAGCACTTGGGACAACCTTTGGTTATGGAATGAAATATTATACCAAATATCCTAGTGGACTGAAGAACTGGTTTCGTGAAGTAATGCCCGGAGGCTTTACCTACGATCGTCATATTCAATATAAAGGCGATGGGAGTATCCATGCAAAACACCAACACTTTATGAAAAATGGGACTTATCACAACATTGTAGAATTTACCGGTCAGGATTTTAAAGAAAATAGTCCAGTCTTAACTGGAGATATGAATGTCTCATTACCGAATGAAGTCCCACAAATACCCAGAGATGATGGAGTAGAATGCCCAGTGACCTTGCTTTATCCTTTATTATCGGATAAATCAAAATACGTCGAGGCTCACCAATATACAATCTGCAAGCCTCTTCATAATCAACCAGCACCTGATGTCCCATATCACTGGATTCGTAAACAATACACACAAAGCAAAGATGATGCCGAGGAACGCGATCATATCTGTCAATCAGAGACTCTCGAAGCACACTTAAAGGGCATGGACGAGCTGTATAAGTGA")

REVCOMP_CACHE: Dict[str, str] = {}
LAST_CELLTYPE: Optional[str] = None

# Make sure inDelphi is importable relative to this file.
sys.path.insert(0, '/home/lienkamplab/Pythia/Indelphi_installation/inDelphi-model-master')  # adjust to your inDelphi install path
import inDelphi


def normalize_strand(raw: str) -> str:
    s = str(raw).strip().lower()
    return "plus" if s in {"+", "plus", "forward", "pos"} else "min"


def reverse_complement(seq: str) -> str:
    if seq in REVCOMP_CACHE:
        return REVCOMP_CACHE[seq]
    complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
    rc = "".join(complement.get(base, base) for base in reversed(seq.upper()))
    REVCOMP_CACHE[seq] = rc
    return rc


def get_context(sequence: str, grna_seq: str, offset_left: int = 23, offset_right: int = 37,
                debug: bool = False) -> Optional[str]:
    seq_upper = sequence.upper()
    grna_upper = grna_seq.upper()
    start_index = seq_upper.find(grna_upper)
    if start_index == -1:
        if debug:
            print(f"[INTRON RECALC] gRNA not found in context (len={len(sequence)}). "
                  f"gRNA={grna_upper[:10]}... loc_index={start_index}")
        return None
    start = start_index - offset_left
    end = start_index + len(grna_upper) + offset_right
    if start < 0 or end > len(sequence):
        if debug:
            print(f"[INTRON RECALC] context window out of bounds: start={start}, end={end}, seq_len={len(sequence)}")
        return None
    ctx = sequence[start:end]
    if debug:
        print(f"[INTRON RECALC] context window located at {start}-{end} (len={len(ctx)})")
    return ctx


def get_dynamic_cassette(last_intron_seq: str, last_exon_seq: str) -> str:
    """
    Intron cassette: last 25bp of intron (splice acceptor) + exon without stop.
    """
    splice_acceptor = last_intron_seq[-25:] if len(last_intron_seq) >= 25 else last_intron_seq
    exon_upper = last_exon_seq.upper()
    if exon_upper[-3:] in ["TAA", "TAG", "TGA"]:
        exon_no_stop = last_exon_seq[:-3]
    else:
        exon_no_stop = last_exon_seq
    return splice_acceptor + exon_no_stop


def load_transcript_context(gene_id: str, transcript_db: Path) -> Tuple[str, str, str]:
    conn = sqlite3.connect(str(transcript_db))
    # Prefer rows with non-NULL intron context; also fall back to transcript_id lookup
    df = pd.read_sql_query(
        """
        SELECT last_intron_sequence, last_intron_sequence_with_context, last_exon_sequence
        FROM transcript_data
        WHERE gene_id = ?
        ORDER BY (last_intron_sequence_with_context IS NOT NULL) DESC,
                 (last_intron_sequence IS NOT NULL) DESC
        LIMIT 1
        """,
        conn,
        params=(gene_id,),
    )
    if df.empty:
        # Try matching on transcript_id (e.g. mouse ENSMUST IDs used as assembly key)
        df = pd.read_sql_query(
            """
            SELECT last_intron_sequence, last_intron_sequence_with_context, last_exon_sequence
            FROM transcript_data
            WHERE transcript_id = ?
            ORDER BY (last_intron_sequence_with_context IS NOT NULL) DESC,
                     (last_intron_sequence IS NOT NULL) DESC
            LIMIT 1
            """,
            conn,
            params=(gene_id,),
        )
    conn.close()
    if df.empty:
        raise ValueError(f"No transcript entry found for gene_id '{gene_id}' in {transcript_db}")
    row = df.iloc[0]
    last_intron_raw = row["last_intron_sequence"]
    ctx_raw = row["last_intron_sequence_with_context"]
    if not isinstance(last_intron_raw, str) or not last_intron_raw:
        raise ValueError(f"No intron sequence data for gene_id '{gene_id}' in {transcript_db}")
    last_intron = last_intron_raw.upper()
    context = ctx_raw.upper() if isinstance(ctx_raw, str) and ctx_raw else last_intron
    last_exon = str(row["last_exon_sequence"]).upper()
    return last_intron, context, last_exon


def recalculate_intron(
    gene_id: str,
    grna_seq: str,
    strand: str,
    location: int,
    tag_sequence: str,
    crispr_scan_score: float,
    celltype: str,
    microhomology_length: int,
    transcript_db_path: str,
    debug: bool = False,
) -> pd.DataFrame:
    """
    Standalone intron-mode recalculation.
    """
    # Normalize inputs
    grna_upper = grna_seq.upper()
    tag_sequence = tag_sequence.upper()
    tag_revcomp = reverse_complement(tag_sequence)
    strand_norm = normalize_strand(strand)
    logger.info("Recalculating with custom repair template — gene: %s, gRNA: %s (cell type: %s)",
                gene_id, grna_upper, celltype)

    if debug:
        print("[INTRON RECALC] enter",
              f"gene={gene_id}",
              f"grna={grna_upper}",
              f"strand={strand_norm}",
              f"loc={location}",
              f"tag_len={len(tag_sequence)}",
              f"microhomology_len={microhomology_length}",
              f"celltype={celltype}",
              f"transcript_db={transcript_db_path}",
              sep=" | ")

    # Normalize inputs to uppercase for consistent matching
    grna_upper = grna_seq.upper()
    tag_sequence = tag_sequence.upper()

    # Reload inDelphi if needed
    global LAST_CELLTYPE, inDelphi
    if celltype != LAST_CELLTYPE:
        if debug:
            print("[INTRON RECALC] reloading inDelphi for celltype", celltype)
        inDelphi = importlib.reload(inDelphi)
        inDelphi.init_model(celltype=celltype)
        LAST_CELLTYPE = celltype

    last_intron, context_seq, last_exon_seq = load_transcript_context(gene_id, Path(transcript_db_path))
    if debug:
        print("[INTRON RECALC] seq lengths",
              f"last_intron={len(last_intron)}",
              f"context={len(context_seq)}",
              f"last_exon={len(last_exon_seq)}",
              sep=" | ")

    # Build dynamic cassette once per gene
    base_dynamic_cassette = get_dynamic_cassette(last_intron, last_exon_seq)
    dynamic_cassette = base_dynamic_cassette if strand_norm == "plus" else reverse_complement(base_dynamic_cassette)
    if debug:
        print("[INTRON RECALC] dynamic cassette len", len(dynamic_cassette))

    # Context for this gRNA (80bp)
    context_source = context_seq if strand_norm == "plus" else reverse_complement(context_seq)
    context = get_context(context_source, grna_upper, debug=debug)
    if not context or len(context) != 80:
        if debug:
            print("[INTRON RECALC] context missing or wrong length", len(context) if context else None)
        return pd.DataFrame()
    Left = context[:40]
    Right = context[40:]
    if debug:
        donor_len = len(dynamic_cassette) + len(tag_sequence)
        print("[INTRON RECALC] context ok",
              f"Left_len={len(Left)}",
              f"Right_len={len(Right)}",
              f"donor_len={donor_len}",
              sep=" | ")

    # Donor component depends on strand
    if strand_norm == "min":
        donor_component = tag_revcomp + dynamic_cassette
        orig_strand = "min"
    else:
        donor_component = dynamic_cassette + tag_sequence
        orig_strand = "plus"

    left_homol_lengths = [3, 4, 5]
    right_homol_lengths = [3, 4, 5]
    repeat_range = [3, 4, 5]

    genotype_cache = {}
    results_list = []

    # Left predictions
    for i in left_homol_lengths:
        ology = Left[-i:]
        for j2 in repeat_range:
            Left_donor = ology * j2 + donor_component
            if orig_strand == "min":
                seq_for_indelphi = reverse_complement(Left + Left_donor)
                cutsite_for_indelphi = len(seq_for_indelphi) - len(Left)
            else:
                seq_for_indelphi = Left + Left_donor
                cutsite_for_indelphi = len(Left)
            pred_df, stats = inDelphi.predict(seq_for_indelphi, cutsite_for_indelphi)
            pred_df = inDelphi.add_genotype_column(pred_df, stats).dropna(subset=["Genotype"])
            cache_key = ("left", i, j2)
            genotype_cache[cache_key] = pred_df[["Genotype", "Predicted frequency"]].values.tolist()
            for _, row_pred in pred_df.iterrows():
                genotype_upper = row_pred["Genotype"].upper()
                for x in range(6):
                    repair_string = Left + ology * x + donor_component
                    repair_check = reverse_complement(repair_string) if orig_strand == "min" else repair_string
                    if repair_check.upper() in genotype_upper:
                        results_list.append(
                            {
                                "side": "left",
                                "Homol_length": i,
                                "Amount_of_trimologies": j2,
                                "Predicted_frequency": row_pred["Predicted frequency"],
                                "Perfect_repair_at": x,
                            }
                        )

    # Right predictions
    for i in right_homol_lengths:
        ology = Right[:i]
        for j2 in repeat_range:
            Right_donor = donor_component + (ology * j2)
            if orig_strand == "min":
                seq_for_indelphi = reverse_complement(Right_donor + Right)
                cutsite_for_indelphi = len(seq_for_indelphi) - len(Right_donor)
            else:
                seq_for_indelphi = Right_donor + Right
                cutsite_for_indelphi = len(Right_donor)
            pred_df, stats = inDelphi.predict(seq_for_indelphi, cutsite_for_indelphi)
            pred_df = inDelphi.add_genotype_column(pred_df, stats).dropna(subset=["Genotype"])
            cache_key = ("right", i, j2)
            genotype_cache[cache_key] = pred_df[["Genotype", "Predicted frequency"]].values.tolist()
            for _, row_pred in pred_df.iterrows():
                genotype_upper = row_pred["Genotype"].upper()
                for x in range(6):
                    repair_string = donor_component + ology * x + Right
                    repair_check = reverse_complement(repair_string) if orig_strand == "min" else repair_string
                    if repair_check.upper() in genotype_upper:
                        results_list.append(
                            {
                                "side": "right",
                                "Homol_length": i,
                                "Amount_of_trimologies": j2,
                                "Predicted_frequency": row_pred["Predicted frequency"],
                                "Perfect_repair_at": x,
                            }
                        )

    if not results_list:
        return pd.DataFrame()

    results_df = pd.DataFrame(results_list)
    agg_df = (
        results_df.groupby(["Amount_of_trimologies", "Homol_length", "side"])["Predicted_frequency"]
        .sum()
        .reset_index()
    )
    agg_df["gRNA"] = grna_upper
    agg_df["CRISPRScan_score"] = crispr_scan_score
    agg_df["strand"] = orig_strand
    agg_df["location"] = location
    agg_df["context"] = context
    agg_df["dynamic_cassette"] = dynamic_cassette

    left_df = agg_df[agg_df["side"] == "left"].copy().reset_index(drop=True)
    right_df = agg_df[agg_df["side"] == "right"].copy().reset_index(drop=True)
    if left_df.empty or right_df.empty:
        return pd.DataFrame()
    merged_df = pd.merge(
        left_df,
        right_df,
        on=["gRNA", "CRISPRScan_score", "strand", "location", "dynamic_cassette", "context"],
        suffixes=("_left", "_right"),
    )
    merged_df["integration_score"] = (
        merged_df["Predicted_frequency_left"] * merged_df["Predicted_frequency_right"] / 100
    )

    # Compute repair arms and full/core cassette for downstream UI
    def _safe_int(val, default=0):
        try:
            return int(val)
        except Exception:
            return default

    merged_df["left_repair_arm"] = merged_df.apply(
        lambda r: Left[-_safe_int(r["Homol_length_left"]):] * _safe_int(r["Amount_of_trimologies_left"], 1),
        axis=1,
    )
    merged_df["right_repair_arm"] = merged_df.apply(
        lambda r: Right[:_safe_int(r["Homol_length_right"])] * _safe_int(r["Amount_of_trimologies_right"], 1),
        axis=1,
    )

    def compute_full_cassette(row: pd.Series) -> str:
        if row["strand"] == "min":
            return row["left_repair_arm"] + tag_revcomp + dynamic_cassette + row["right_repair_arm"]
        return row["left_repair_arm"] + dynamic_cassette + tag_sequence + row["right_repair_arm"]

    def compute_core_cassette(row: pd.Series) -> str:
        if row["strand"] == "min":
            return tag_revcomp + dynamic_cassette
        return dynamic_cassette + tag_sequence

    merged_df["Repair_Cassette"] = merged_df.apply(compute_full_cassette, axis=1)
    merged_df["Core_Cassette"] = merged_df.apply(compute_core_cassette, axis=1)

    # pick the top-scoring configuration
    merged_df = merged_df.sort_values("integration_score", ascending=False).reset_index(drop=True)
    logger.info("Recalculation complete — %d results passed to frontend", len(merged_df))
    return merged_df


def main():
    parser = argparse.ArgumentParser(description="Standalone intron recalculation helper")
    parser.add_argument("--gene-id", required=True)
    parser.add_argument("--grna", required=True)
    parser.add_argument("--strand", default="plus")
    parser.add_argument("--location", type=int, required=True)
    parser.add_argument("--tag-sequence", required=True)
    parser.add_argument("--crispr-score", type=float, default=0.0)
    parser.add_argument("--celltype", default="HEK293")
    parser.add_argument("--microhomology", type=int, default=3)
    parser.add_argument("--transcript-db", default=str(Path(__file__).with_name("transcript_sequences.db")))
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    df = recalculate_intron(
        gene_id=args.gene_id,
        grna_seq=args.grna,
        strand=args.strand,
        location=args.location,
        tag_sequence=args.tag_sequence,
        crispr_scan_score=args.crispr_score,
        celltype=args.celltype,
        microhomology_length=args.microhomology,
        transcript_db_path=args.transcript_db,
    )

    if df is None or df.empty:
        print("No results produced.")
        return

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.output, index=False)
        print(f"Saved results to {args.output}")
    else:
        print(df.to_csv(index=False))


if __name__ == "__main__":
    main()
