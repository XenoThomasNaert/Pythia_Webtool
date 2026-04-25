"""
Standalone helper to recompute integration scores for a single gRNA/tag pair.
The logic here mirrors the Pythia integration routines but is fully contained
in this file to avoid importing Pythia_ExonTagger.
"""
import inspect
import argparse
import importlib
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger('pythia.browser')

import pandas as pd

# Default GFP tag (plus orientation).
GFP_SEQUENCE = ("GGATCAGGAGGATCAGGAATGGTCTCAAAGGGAGAGGAGGAAAACATGGCTAGTACACCATTTAAATTTCAACTTAAAGGAACCATCAATGGCAAATCGTTTACCGTTGAAGGCGAAGGTGAAGGGAAcTCACATGAAGGTTCTCATAAAGGAAAATATGTTTGTACAAGTGGAAAACTACCGATGTCATGGGCAGCACTTGGGACAACCTTTGGTTATGGAATGAAATATTATACCAAATATCCTAGTGGACTGAAGAACTGGTTTCGTGAAGTAATGCCCGGAGGCTTTACCTACGATCGTCATATTCAATATAAAGGCGATGGGAGTATCCATGCAAAACACCAACACTTTATGAAAAATGGGACTTATCACAACATTGTAGAATTTACCGGTCAGGATTTTAAAGAAAATAGTCCAGTCTTAACTGGAGATATGAATGTCTCATTACCGAATGAAGTCCCACAAATACCCAGAGATGATGGAGTAGAATGCCCAGTGACCTTGCTTTATCCTTTATTATCGGATAAATCAAAATACGTCGAGGCTCACCAATATACAATCTGCAAGCCTCTTCATAATCAACCAGCACCTGATGTCCCATATCACTGGATTCGTAAACAATACACACAAAGCAAAGATGATGCCGAGGAACGCGATCATATCTGTCAATCAGAGACTCTCGAAGCACACTTAAAGGGCATGGACGAGCTGTATAAGTGA")

REVCOMP_CACHE: Dict[str, str] = {}
LAST_CELLTYPE: Optional[str] = None

# Make sure inDelphi is importable relative to this file.
sys.path.insert(0, '/home/lienkamplab/Pythia/Indelphi_installation/inDelphi-model-master')  # inDelphi install path on system
import inDelphi

def _default_transcript_db() -> Path:
    """
    Return the default path to transcript_sequences.db (as a Path).

    For backward compatibility, checks multiple locations:
    1. New location: transcript_sequences/Homo_sapiens_transcript_sequences.db
    2. Legacy location: transcript_sequences.db (alongside this script)
    """
    # Try new location first (species-specific databases)
    new_location = Path(__file__).parent / "transcript_sequences" / "Homo_sapiens_transcript_sequences.db"
    if new_location.exists():
        return new_location

    # Fall back to legacy location for backward compatibility
    legacy_location = Path(__file__).with_name("transcript_sequences.db")
    return legacy_location


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


def get_context(sequence: str, grna_seq: str, offset_left: int = 23, offset_right: int = 37) -> Optional[str]:
    start_index = sequence.find(grna_seq)
    if start_index == -1:
        return None
    start = start_index - offset_left
    end = start_index + len(grna_seq) + offset_right
    if start < 0 or end > len(sequence):
        return None
    return sequence[start:end]


def get_dynamic_cassette(last_exon_seq: str, cleavage_index: int) -> str:
    """
    Given the last_exon_sequence and a cleavage index,
    remove the terminal stop codon (if present) and return the substring starting at cleavage_index.
    """
    if last_exon_seq[-3:] in ['TAA', 'TAG', 'TGA']:
        trimmed_seq = last_exon_seq[:-3]
    else:
        trimmed_seq = last_exon_seq

    if cleavage_index < 0 or cleavage_index > len(trimmed_seq):
        return ""

    return trimmed_seq[cleavage_index:]


def load_transcript_context(gene_id: str, transcript_db_path: Optional[str] = None) -> Tuple[str, str, str, str]:
    """
    Load last exon, context sequence, transcript_id, and full CDS for a given
    gene_id from the transcript DB.

    Returns: (last_exon_seq, context_seq, transcript_id, full_cds)

    NOTE: sqlite3.connect in Python 3.6 does not accept Path objects, so we
    always convert the path to str before connecting.
    """
    db_path = Path(transcript_db_path) if transcript_db_path else _default_transcript_db()
    db_path_str = str(db_path)

    conn = sqlite3.connect(db_path_str)
    df = pd.read_sql_query(
        """
        SELECT gene_id, transcript_id, last_exon_sequence,
               last_exon_sequence_with_context, nucleotide_sequence
        FROM transcript_data
        WHERE gene_id = ?
        LIMIT 1
        """,
        conn,
        params=(gene_id,),
    )
    if df.empty:
        # Caller may have passed a transcript ID (ENSMUST…) instead of a gene ID
        df = pd.read_sql_query(
            """
            SELECT gene_id, transcript_id, last_exon_sequence,
                   last_exon_sequence_with_context, nucleotide_sequence
            FROM transcript_data
            WHERE transcript_id = ?
            LIMIT 1
            """,
            conn,
            params=(gene_id,),
        )
    conn.close()

    if df.empty:
        raise ValueError("No transcript entry found for gene_id '{}' in {}".format(gene_id, db_path_str))

    row = df.iloc[0]
    last_exon_seq = str(row["last_exon_sequence"]).upper()
    context_seq = row.get("last_exon_sequence_with_context")
    if isinstance(context_seq, str):
        context_seq = context_seq.upper()
    else:
        context_seq = last_exon_seq

    full_cds = row.get("nucleotide_sequence")
    full_cds = str(full_cds).upper() if isinstance(full_cds, str) else ""

    return last_exon_seq, context_seq, str(row.get("transcript_id", "")), full_cds


# ---------------------------------------------------------------------------
# Standalone protein translation (no biopython dependency)
# ---------------------------------------------------------------------------
_CODON_TABLE: Dict[str, str] = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}


def _translate_dna(dna: str) -> str:
    """Translate a DNA string to a protein string using the standard genetic code."""
    out = []
    dna = dna.upper()
    for i in range(0, len(dna) - 2, 3):
        out.append(_CODON_TABLE.get(dna[i:i + 3], 'X'))
    return ''.join(out)


def _translate_genotype(genotype: str, full_cds: str, last_exon_seq: str, location: int) -> Tuple[str, int]:
    """
    Translate an inDelphi genotype (80-bp context window) back to a full
    protein, using the same logic as Pythia_ExonTagger.translate_genotype_to_protein.

    Returns (protein_string, cut_position_in_protein).
    Returns ("", 0) on any failure.
    """
    try:
        last_exon_start = full_cds.find(last_exon_seq)
        if last_exon_start == -1:
            return "", 0

        cut_pos_in_cds = last_exon_start + location
        cut_pos_in_protein = cut_pos_in_cds // 3

        if location >= 40:
            modified_last_exon = last_exon_seq[:location - 40] + genotype
        else:
            modified_last_exon = genotype[40 - location:]

        modified_cds = full_cds[:last_exon_start] + modified_last_exon
        return _translate_dna(modified_cds), cut_pos_in_protein

    except Exception:
        return "", 0


def add_protein_columns(
    max_integration_scores: pd.DataFrame,
    full_cds: str,
    last_exon_seq: str,
) -> pd.DataFrame:
    """
    Translate every x0–x5 genotype to a protein sequence and add
    x{i}_protein + protein_cut_position columns to the DataFrame.
    """
    if not full_cds or not last_exon_seq:
        for x in range(6):
            max_integration_scores[f"x{x}_protein"] = ""
        max_integration_scores["protein_cut_position"] = 0
        return max_integration_scores

    for x in range(6):
        max_integration_scores[f"x{x}_protein"] = ""
    max_integration_scores["protein_cut_position"] = 0

    for idx, row in max_integration_scores.iterrows():
        location = int(row["location"])
        cut_pos_set = False
        for x in range(6):
            genotype = row.get(f"x{x}_genotype", "")
            if not genotype:
                continue
            protein, cut_pos = _translate_genotype(genotype, full_cds, last_exon_seq, location)
            max_integration_scores.at[idx, f"x{x}_protein"] = protein
            if not cut_pos_set and cut_pos:
                max_integration_scores.at[idx, "protein_cut_position"] = cut_pos
                cut_pos_set = True

    return max_integration_scores


def reload_indelphi_if_needed(celltype: str) -> None:
    global LAST_CELLTYPE, inDelphi
    if celltype != LAST_CELLTYPE:
        inDelphi = importlib.reload(inDelphi)
        inDelphi.init_model(celltype=celltype)
        LAST_CELLTYPE = celltype


def add_genotype_columns_from_cache(max_integration_scores: pd.DataFrame, tag_sequence: str) -> pd.DataFrame:
    tag_seq = tag_sequence.upper()
    tag_revcomp = reverse_complement(tag_seq)

    for x in range(6):
        max_integration_scores["x{}_genotype".format(x)] = ""
        max_integration_scores["x{}_frequency".format(x)] = 0.0

    for idx, row in max_integration_scores.iterrows():
        strand = row.get("strand", "plus")
        if strand == "plus":
            cache_key = ("left", int(row["Homol_length_left"]), int(row["Amount_of_trimologies_left"]))
            genotype_cache = row.get("genotype_cache_left", {})
            left = row["context"][:40]
            ology = left[-int(row["Homol_length_left"]) :]
            donor_component = row["dynamic_cassette"] + tag_seq
            cached_genotypes = genotype_cache.get(cache_key, [])

            for x in range(6):
                repair_string = left + ology * x + donor_component
                repair_check = repair_string.upper()
                for genotype, freq in cached_genotypes:
                    if repair_check in genotype.upper():
                        max_integration_scores.at[idx, "x{}_genotype".format(x)] = genotype
                        max_integration_scores.at[idx, "x{}_frequency".format(x)] = freq
                        break
        else:
            cache_key = ("right", int(row["Homol_length_right"]), int(row["Amount_of_trimologies_right"]))
            genotype_cache = row.get("genotype_cache_right", {})
            right = row["context"][40:]
            ology = right[: int(row["Homol_length_right"])]
            donor_component = tag_revcomp + row["dynamic_cassette"]
            cached_genotypes = genotype_cache.get(cache_key, [])

            for x in range(5):
                repair_string = donor_component + ology * x + right
                repair_check = reverse_complement(repair_string).upper() if strand == "min" else repair_string.upper()
                for genotype, freq in cached_genotypes:
                    if repair_check in genotype.upper():
                        max_integration_scores.at[idx, "x{}_genotype".format(x)] = genotype
                        max_integration_scores.at[idx, "x{}_frequency".format(x)] = freq
                        break

    return max_integration_scores


def run_single_grna_integration(
    *,
    grna_seq: str,
    strand: str,
    location: int,
    last_exon_seq: str,
    full_context_seq: str,
    tag_sequence: str,
    crispr_scan_score: Optional[float],
    celltype: str,
    microhomology_length: int,
    collect_all_pairs: bool = False,
) -> pd.DataFrame:
    reload_indelphi_if_needed(celltype)

    strand_norm = normalize_strand(strand)
    tag_seq = tag_sequence.upper()
    tag_revcomp = reverse_complement(tag_seq)
    grna_seq = grna_seq.upper()
    last_exon_seq = last_exon_seq.upper()
    full_context_seq = full_context_seq.upper()

    context_source = full_context_seq if strand_norm == "plus" else reverse_complement(full_context_seq)
    context = get_context(context_source, grna_seq)
    if not context or len(context) != 80:
        return pd.DataFrame()

    dynamic_cassette = get_dynamic_cassette(last_exon_seq, int(location))
    if strand_norm == "min":
        dynamic_cassette = reverse_complement(dynamic_cassette)
        donor_component = tag_revcomp + dynamic_cassette
    else:
        donor_component = dynamic_cassette + tag_seq

    left = context[:40]
    right = context[40:]

    if strand_norm == "plus":
        left_homol_lengths = [microhomology_length]
        left_repeat_range = range(2, 6)
        right_homol_lengths = [3, 4, 5, 6]
        right_repeat_range = [5]
    else:
        left_homol_lengths = [3, 4, 5, 6]
        left_repeat_range = [5]
        right_homol_lengths = [microhomology_length]
        right_repeat_range = range(2, 6)

    genotype_cache: Dict[Tuple[str, int, int], List[List]] = {}
    results_list: List[Dict] = []

    # Left boundary predictions
    for homol_len in left_homol_lengths:
        ology = left[-homol_len:]
        for repeats in left_repeat_range:
            left_donor = ology * repeats + donor_component
            if strand_norm == "min":
                seq_for_indelphi = reverse_complement(left + left_donor)
                cutsite = len(seq_for_indelphi) - len(left)
            else:
                seq_for_indelphi = left + left_donor
                cutsite = len(left)

            try:
                pred_df, stats = inDelphi.predict(seq_for_indelphi, cutsite)
                pred_df = inDelphi.add_genotype_column(pred_df, stats)
                pred_df = pred_df.dropna(subset=["Genotype"])
            except Exception:
                continue

            cache_key = ("left", homol_len, repeats)
            genotype_cache[cache_key] = pred_df[["Genotype", "Predicted frequency"]].values.tolist()

            for _, pred_row in pred_df.iterrows():
                genotype_upper = pred_row["Genotype"].upper()
                for x in range(6):
                    repair_string = left + ology * x + donor_component
                    repair_check = reverse_complement(repair_string) if strand_norm == "min" else repair_string
                    if repair_check.upper() in genotype_upper:
                        results_list.append(
                            {
                                "side": "left",
                                "Homol_length": homol_len,
                                "Amount_of_trimologies": repeats,
                                "Predicted_frequency": pred_row["Predicted frequency"],
                                "Perfect_repair_at": x,
                                "context": context,
                                "genotype": pred_row["Genotype"],
                                "cache_key": cache_key,
                            }
                        )

    # Right boundary predictions
    for homol_len in right_homol_lengths:
        ology = right[:homol_len]
        for repeats in right_repeat_range:
            right_donor = donor_component + (ology * repeats)
            if strand_norm == "min":
                seq_for_indelphi = reverse_complement(right_donor + right)
                cutsite = len(seq_for_indelphi) - len(right_donor)
            else:
                seq_for_indelphi = right_donor + right
                cutsite = len(right_donor)

            try:
                pred_df, stats = inDelphi.predict(seq_for_indelphi, cutsite)
                pred_df = inDelphi.add_genotype_column(pred_df, stats)
                pred_df = pred_df.dropna(subset=["Genotype"])
            except Exception:
                continue

            cache_key = ("right", homol_len, repeats)
            genotype_cache[cache_key] = pred_df[["Genotype", "Predicted frequency"]].values.tolist()

            for _, pred_row in pred_df.iterrows():
                genotype_upper = pred_row["Genotype"].upper()
                for x in range(6):
                    repair_string = donor_component + ology * x + right
                    repair_check = reverse_complement(repair_string) if strand_norm == "min" else repair_string
                    if repair_check.upper() in genotype_upper:
                        results_list.append(
                            {
                                "side": "right",
                                "Homol_length": homol_len,
                                "Amount_of_trimologies": repeats,
                                "Predicted_frequency": pred_row["Predicted frequency"],
                                "Perfect_repair_at": x,
                                "context": context,
                                "genotype": pred_row["Genotype"],
                                "cache_key": cache_key,
                            }
                        )

    if not results_list:
        return pd.DataFrame()

    results_df = pd.DataFrame(results_list)
    agg_df = (
        results_df.groupby(["Amount_of_trimologies", "Homol_length", "side", "context"])["Predicted_frequency"]
        .sum()
        .reset_index()
    )
    agg_df["gRNA"] = grna_seq
    agg_df["CRISPRScan_score"] = crispr_scan_score
    agg_df["strand"] = strand_norm
    agg_df["location"] = int(location)
    agg_df["dynamic_cassette"] = dynamic_cassette
    agg_df["genotype_cache"] = [genotype_cache] * len(agg_df)

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
        merged_df["Predicted_frequency_left"] * merged_df["Predicted_frequency_right"]
    ) / 100

    def _add_seq_metadata(row: pd.Series) -> pd.Series:
        strand_here = row["strand"]
        donor_component_here = (
            tag_revcomp + row["dynamic_cassette"] if strand_here == "min" else row["dynamic_cassette"] + tag_seq
        )

        left_ctx = row["context"][:40]
        right_ctx = row["context"][40:]

        ology_left = left_ctx[-int(row["Homol_length_left"]) :]
        left_donor = ology_left * int(row["Amount_of_trimologies_left"]) + donor_component_here
        if strand_here == "min":
            seq_left = reverse_complement(left_ctx + left_donor)
            cut_left = len(seq_left) - len(left_ctx)
        else:
            seq_left = left_ctx + left_donor
            cut_left = len(left_ctx)

        ology_right = right_ctx[: int(row["Homol_length_right"])]
        right_donor = donor_component_here + (ology_right * int(row["Amount_of_trimologies_right"]))
        if strand_here == "min":
            seq_right = reverse_complement(right_donor + right_ctx)
            cut_right = len(seq_right) - len(right_donor)
        else:
            seq_right = right_donor + right_ctx
            cut_right = len(right_donor)

        return pd.Series(
            {
                "donor_component": donor_component_here,
                "left_inDelphi_seq": seq_left,
                "left_cutsite": cut_left,
                "right_inDelphi_seq": seq_right,
                "right_cutsite": cut_right,
            }
        )

    seq_meta_df = merged_df.apply(_add_seq_metadata, axis=1)
    merged_df_full = pd.concat([merged_df, seq_meta_df], axis=1)

    max_scores = merged_df.groupby("gRNA")["integration_score"].max().reset_index()
    max_scores.rename(columns={"integration_score": "max_integration_score"}, inplace=True)
    merged_df = pd.merge(merged_df, max_scores, on="gRNA", how="left")
    merged_df["threshold"] = merged_df["max_integration_score"] - 1
    filtered_df = merged_df[merged_df["integration_score"] >= merged_df["threshold"]].copy()
    filtered_df["solution_complexity"] = (
        filtered_df["Amount_of_trimologies_left"] * filtered_df["Homol_length_left"]
        + filtered_df["Amount_of_trimologies_right"] * filtered_df["Homol_length_right"]
    )
    complexity_idx = filtered_df.groupby("gRNA")["solution_complexity"].idxmin().tolist()
    max_integration_scores = (
        filtered_df.loc[complexity_idx].sort_values(by="integration_score", ascending=False).reset_index(drop=True)
    )

    def extract_left_repair_arm(row: pd.Series) -> str:
        hl = int(row["Homol_length_left"])
        mid = 40
        start = max(0, mid - hl)
        return row["context"][start:mid] * int(row["Amount_of_trimologies_left"])

    def extract_right_repair_arm(row: pd.Series) -> str:
        hr = int(row["Homol_length_right"])
        mid = 40
        end = min(80, mid + hr)
        return row["context"][mid:end] * int(row["Amount_of_trimologies_right"])

    max_integration_scores["left_repair_arm"] = max_integration_scores.apply(extract_left_repair_arm, axis=1)
    max_integration_scores["right_repair_arm"] = max_integration_scores.apply(extract_right_repair_arm, axis=1)

    def compute_full_repair_cassette(row: pd.Series) -> str:
        if row["strand"] == "min":
            return (
                row["left_repair_arm"]
                + tag_revcomp
                + row["dynamic_cassette"]
                + row["right_repair_arm"]
            )
        return row["left_repair_arm"] + row["dynamic_cassette"] + tag_seq + row["right_repair_arm"]

    def compute_core_cassette(row: pd.Series) -> str:
        if row["strand"] == "min":
            return tag_revcomp + row["dynamic_cassette"]
        return row["dynamic_cassette"] + tag_seq

    max_integration_scores["Repair_Cassette"] = max_integration_scores.apply(compute_full_repair_cassette, axis=1)
    max_integration_scores["Core_Cassette"] = max_integration_scores.apply(compute_core_cassette, axis=1)

    max_integration_scores = add_genotype_columns_from_cache(max_integration_scores, tag_seq)
    max_integration_scores = max_integration_scores.drop(
        columns=["side_left", "side_right", "genotype_cache_left", "genotype_cache_right"],
        errors="ignore",
    )
    if collect_all_pairs:
        return max_integration_scores, merged_df_full
    return max_integration_scores


def recalculate_grna(
    gene_id: str,
    grna_seq: str,
    strand: str,
    location: int,
    tag_sequence: str,
    *,
    crispr_scan_score: Optional[float] = None,
    celltype: str = "HEK293",
    microhomology_length: int = 3,
    transcript_db_path: Optional[str] = None,
    last_exon_seq: Optional[str] = None,
    full_context_seq: Optional[str] = None,
    debug: bool = True,
    debug_csv_path: Optional[str] = None,
) -> pd.DataFrame:
    primary_gene = gene_id.split(",")[0].strip()
    logger.info("Recalculating with custom repair template — gene: %s, gRNA: %s (cell type: %s)",
                primary_gene, grna_seq, celltype)

    full_cds = ""
    if last_exon_seq is None or full_context_seq is None:
        last_exon_seq_db, context_seq_db, _, full_cds = load_transcript_context(primary_gene, transcript_db_path)
        last_exon_seq = last_exon_seq or last_exon_seq_db
        full_context_seq = full_context_seq or context_seq_db

    results = run_single_grna_integration(
        grna_seq=grna_seq,
        strand=strand,
        location=location,
        last_exon_seq=last_exon_seq,
        full_context_seq=full_context_seq,
        tag_sequence=tag_sequence,
        crispr_scan_score=crispr_scan_score,
        celltype=celltype,
        microhomology_length=microhomology_length,
        collect_all_pairs=debug or bool(debug_csv_path),
    )

    all_pairs_df = None
    if isinstance(results, tuple):
        results, all_pairs_df = results

    if debug_csv_path and all_pairs_df is not None and not all_pairs_df.empty:
        try:
            all_pairs_df.to_csv(debug_csv_path, index=False)
        except Exception:
            pass

    if not results.empty:
        results = add_protein_columns(results, full_cds, last_exon_seq)

    logger.info("Recalculation complete — %d results passed to frontend", len(results))
    return results


def recalculate_grna_to_json(**kwargs) -> str:
    df = recalculate_grna(**kwargs)
    if df.empty:
        return "[]"
    return df.to_json(orient="records")


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Standalone re-run of integration scoring for a single gRNA with a custom tag."
    )
    parser.add_argument("--gene-id", required=True)
    parser.add_argument("--gRNA", required=True, help="20bp guide sequence (plus orientation)")
    parser.add_argument("--strand", required=True, help="+/- or plus/min")
    parser.add_argument("--location", required=True, type=int, help="Cut position used in DB row")
    parser.add_argument("--tag-sequence", required=True, help="Replacement for GFP sequence")
    parser.add_argument("--celltype", default="HEK293")
    parser.add_argument("--microhomology-length", type=int, default=3)
    parser.add_argument("--crispr-score", type=float)
    parser.add_argument(
        "--transcript-db",
        help="Override path to transcript_sequences.db (defaults to alongside this script)",
    )
    parser.add_argument(
        "--context",
        help="Optional full context sequence; skips DB lookup when provided",
    )
    parser.add_argument(
        "--last-exon",
        help="Optional last exon sequence; skips DB lookup when provided",
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output for inspection"
    )
    parser.add_argument(
        "--debug-csv",
        help="Optional path to save all boundary configurations (with inDelphi input sequences) as CSV",
    )

    args = parser.parse_args()
    df = recalculate_grna(
        gene_id=args.gene_id,
        grna_seq=args.gRNA,
        strand=args.strand,
        location=args.location,
        tag_sequence=args.tag_sequence,
        crispr_scan_score=args.crispr_score,
        celltype=args.celltype,
        microhomology_length=args.microhomology_length,
        transcript_db_path=args.transcript_db,
        last_exon_seq=args.last_exon,
        full_context_seq=args.context,
        debug_csv_path=args.debug_csv,
    )

    if df.empty:
        print("[]")
        return

    records = df.to_dict(orient="records")
    if args.pretty:
        print(json.dumps(records, indent=2))
    else:
        print(json.dumps(records))


if __name__ == "__main__":
    _cli()
