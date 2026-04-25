import logging
import os
import re
import pandas as pd
from functools import lru_cache
from contextlib import contextmanager

logger = logging.getLogger('pythia.browser')

from app import USE_CONNECTION_POOL, PERFORMANCE_PROFILE, POOL_SIZE, TRANSCRIPT_DB_DIR
from connection_helper import get_optimized_connection
from connection_pool import ConnectionPool

# Initialize connection pool if enabled
_connection_pools = {}


def get_transcript_db_path(species):
    """
    Get the path to the transcript sequences database for a given species.

    Args:
        species (str): Species name (e.g., "Homo sapiens" or "Xenopus tropicalis")

    Returns:
        str: Full path to the species-specific transcript database
    """
    species_formatted = species.replace(' ', '_')
    db_filename = f"{species_formatted}_transcript_sequences.db"
    return os.path.join(TRANSCRIPT_DB_DIR, db_filename)


def resolve_db_path(path):
    """Return path if the full DB exists, otherwise fall back to the _sample.db version."""
    if os.path.exists(path):
        return path
    return path.replace(".db", "_sample.db")


def get_db_connection(db_path):
    """
    Get a database connection (pooled or direct based on USE_CONNECTION_POOL).

    Returns a context manager that yields a connection.
    """
    if USE_CONNECTION_POOL:
        # Use connection pool (production mode)
        if db_path not in _connection_pools:
            _connection_pools[db_path] = ConnectionPool(
                db_path,
                pool_size=POOL_SIZE,
                profile=PERFORMANCE_PROFILE
            )
        return _connection_pools[db_path].get_connection()
    else:
        # Direct connection (development mode)
        @contextmanager
        def direct_connection():
            conn = get_optimized_connection(db_path, profile=PERFORMANCE_PROFILE)
            try:
                yield conn
            finally:
                conn.close()
        return direct_connection()


@lru_cache(maxsize=32)
def get_last_exon_length_cached(gene_name, species):
    """Cached query for last exon length in Intron mode - eliminates repeated queries"""
    try:
        transcript_db_path = get_transcript_db_path(species)
        with get_db_connection(transcript_db_path) as conn:
            query = "SELECT last_exon_sequence FROM transcript_data WHERE gene_id = ?"
            result = pd.read_sql_query(query, conn, params=(gene_name,))
            if not result.empty and result['last_exon_sequence'].iloc[0]:
                last_exon_length = len(result['last_exon_sequence'].iloc[0])
                return last_exon_length
    except Exception as e:
        logger.warning("Error fetching last_exon_sequence: %s", e)
    return None


@lru_cache(maxsize=32)
def get_zoom_data_cached(gene, species, mode, cell_type, tag_length='3bp', gene_symbol=None):
    """Cached database query for zoom data - eliminates repeated queries

    Args:
        gene: Transcript ID (e.g., "ENSMUST00000161498" for mouse, "KDM1A-237" for human)
        species: Species name
        mode: Mode (Exon/Intron)
        cell_type: Cell type
        tag_length: Tag length (3bp/6bp)
        gene_symbol: Gene symbol (e.g., "Kdm1a" for mouse) - used for indexed lookup
    """
    # Construct database file path based on selections
    species_formatted = species.replace(' ', '_')
    if mode == 'Exon':
        mode_formatted = '6BP' if tag_length == '6bp' else '3BP'
    else:
        mode_formatted = 'Intron'
    db_path = resolve_db_path(f"db/{species_formatted}_{mode_formatted}_{cell_type}.db")

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_rows = cursor.fetchall()
        table_candidates = [
            row[0]
            for row in table_rows
            if row and row[0] not in ("sqlite_sequence", "gene_index")
        ]
        if not table_candidates:
            return pd.DataFrame().to_json(orient='records')
        table_name = table_candidates[0]

        # Check if this is mouse - different query logic
        is_mouse = 'Mus' in species or 'mus' in species

        if is_mouse:
            q = f"""
                SELECT DISTINCT m.*
                FROM '{table_name}' m
                INNER JOIN gene_index gi ON m.rowid = gi.main_id
                WHERE gi.gene_id = ?
                AND m.transcript_ids LIKE ? AND m.CRISPRScan_score > 0
                ORDER BY m.integration_score DESC
            """
            df_zoom = pd.read_sql_query(q, conn, params=(
                gene_symbol,
                f'%{gene}%',
            ))
        else:
            q = f"""
                SELECT DISTINCT m.*
                FROM '{table_name}' m
                INNER JOIN gene_index gi ON m.rowid = gi.main_id
                WHERE gi.gene_id = ? AND m.CRISPRScan_score > 0
                ORDER BY m.integration_score DESC
            """
            df_zoom = pd.read_sql_query(q, conn, params=(gene,))
    logger.info("Gene lookup: %s (%s, %s) → %d guides retrieved", gene, species, mode, len(df_zoom))
    return df_zoom.to_json(orient='records')


@lru_cache(maxsize=1)
def _build_mouse_symbol_map():
    """Build a gene_symbol → [versioned ENSMUST IDs] mapping for mouse.

    The mouse transcript DB stores Ensembl IDs only (ENSMUSG / ENSMUST), so we
    join it with the ensembl_mouse_transcripts.tsv (ENSMUST-no-version → gene
    symbol) to produce a user-friendly lookup.  The result is cached for the
    lifetime of the process so it's only computed once.

    Returns:
        dict mapping gene_symbol (str) → sorted list of versioned ENSMUST IDs
    """
    tsv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'db', 'ensembl_mouse_transcripts.tsv'
    )

    # Phase 1: load TSV → base transcript ID → gene symbol
    base_to_symbol = {}
    try:
        with open(tsv_path, 'r') as fh:
            next(fh)  # skip header
            for line in fh:
                parts = line.strip().split('\t')
                if len(parts) >= 2 and parts[0] and parts[1]:
                    base_to_symbol[parts[0]] = parts[1]
    except Exception as e:
        logger.warning("_build_mouse_symbol_map: could not load TSV: %s", e)
        return {}

    # Phase 2: read all transcript IDs from the DB and join with the TSV
    db_path = get_transcript_db_path('Mus musculus')
    symbol_to_tids = {}
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT transcript_id FROM transcript_data")
            for (tid,) in cursor.fetchall():
                base = tid.split('.')[0]
                symbol = base_to_symbol.get(base)
                if symbol:
                    symbol_to_tids.setdefault(symbol, []).append(tid)
    except Exception as e:
        logger.warning("_build_mouse_symbol_map: could not query DB: %s", e)
        return {}

    for tids in symbol_to_tids.values():
        tids.sort()

    logger.info("Mouse symbol map: %d gene symbols, %d transcripts",
                len(symbol_to_tids), sum(len(v) for v in symbol_to_tids.values()))
    return symbol_to_tids


def search_genes_in_transcript_db(search_term, species, limit=100):
    """Search genes directly in the transcript sequences DB (not the gRNA DB).

    Used by Custom Tagging so every gene with transcript data is available,
    not just genes that have pre-calculated gRNA databases.

    Returns unique gene NAMES:
      - Human:   'KDM1A'   (gene_id stripped of transcript number)
      - Xenopus: 'dok1'    (gene_id is the gene name directly)
      - Mouse:   'Kdm1a'   (gene symbol via ensembl_mouse_transcripts.tsv)
    """
    if search_term:
        sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '', search_term)[:100]
        if sanitized != search_term:
            print(f"Warning: Search term sanitized: '{search_term}' → '{sanitized}'")
        search_term = sanitized

    is_mouse = 'Mus' in species or 'mus' in species
    is_xenopus = 'Xenopus' in species or 'xenopus' in species

    # --- Mouse: use in-memory symbol map built from TSV + DB ---
    if is_mouse:
        symbol_to_tids = _build_mouse_symbol_map()
        if not symbol_to_tids:
            return []
        if search_term:
            st_lower = search_term.lower()
            gene_names = sorted(
                s for s in symbol_to_tids if s.lower().startswith(st_lower)
            )[:limit]
        else:
            gene_names = sorted(symbol_to_tids.keys())[:limit]
        return gene_names

    # --- Human / Xenopus: query the transcript DB directly ---
    db_path = get_transcript_db_path(species)
    if not os.path.exists(db_path):
        logger.warning("Transcript DB not found: %s", db_path)
        return []

    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            if not search_term:
                cursor.execute(
                    "SELECT DISTINCT gene_id FROM transcript_data ORDER BY gene_id LIMIT ?",
                    (limit * 10,)
                )
            else:
                cursor.execute(
                    "SELECT DISTINCT gene_id FROM transcript_data WHERE gene_id LIKE ? ORDER BY gene_id LIMIT ?",
                    (f"{search_term}%", limit * 10)
                )
            gene_ids = [row[0] for row in cursor.fetchall()]

        if is_xenopus:
            gene_names = sorted(set(gene_ids))[:limit]
        else:
            # Human: strip the "-201" transcript suffix to get the gene symbol
            gene_names_set = set()
            for gid in gene_ids:
                gene_names_set.add(gid.rsplit('-', 1)[0] if '-' in gid else gid)
            gene_names = sorted(gene_names_set)[:limit]

        return gene_names
    except Exception as e:
        logger.warning("Error searching transcript DB: %s", e)
        return []


def get_assemblies_for_gene_in_transcript_db(gene_name, species):
    """Get transcript IDs for a gene from the transcript sequences DB.

    Used by Custom Tagging for all species so every transcript is available
    regardless of gRNA pre-calculation status.

    Return values are used directly as the dropdown `value` fed to
    autofill_from_transcript, which queries:
      - Mouse:          WHERE transcript_id = ?   (versioned ENSMUST IDs)
      - Human/Xenopus:  WHERE gene_id = ?         (gene_id strings)
    """
    if gene_name:
        sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '', gene_name)[:100]
        gene_name = sanitized

    is_mouse = 'Mus' in species or 'mus' in species
    is_xenopus = 'Xenopus' in species or 'xenopus' in species

    # --- Mouse: look up versioned ENSMUST IDs from the cached symbol map ---
    if is_mouse:
        symbol_to_tids = _build_mouse_symbol_map()
        return list(symbol_to_tids.get(gene_name, []))

    # --- Human / Xenopus: query the transcript DB ---
    db_path = get_transcript_db_path(species)
    if not os.path.exists(db_path):
        return []

    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            if is_xenopus:
                cursor.execute(
                    "SELECT DISTINCT gene_id FROM transcript_data WHERE gene_id = ?",
                    (gene_name,)
                )
                result = cursor.fetchone()
                return [result[0]] if result else []
            else:
                # Human: gene_id is like "KDM1A-201"
                cursor.execute(
                    "SELECT DISTINCT gene_id FROM transcript_data WHERE gene_id LIKE ? ORDER BY gene_id",
                    (f"{gene_name}-%",)
                )
                gene_ids = [row[0] for row in cursor.fetchall()]

                def get_num(gid):
                    try:
                        return int(gid.rsplit('-', 1)[1])
                    except (ValueError, IndexError):
                        return 999999

                gene_ids.sort(key=get_num)
                return gene_ids
    except Exception as e:
        logger.warning("Error getting assemblies from transcript DB: %s", e)
        return []


def search_genes_in_db(search_term, species, mode, cell_type, limit=100, tag_length='3bp'):
    """Search for genes matching the search term - returns limited results for speed

    With 1.6M rows, we can't load all genes. Instead, search on-demand with LIMIT.
    If no search term, return first N genes alphabetically for initial display.

    Returns unique GENE NAMES (e.g., 'A1CF') not transcript IDs (e.g., 'A1CF-201').
    """
    species_formatted = species.replace(' ', '_')
    if mode == 'Exon':
        mode_formatted = '6BP' if tag_length == '6bp' else '3BP'
    else:
        mode_formatted = 'Intron'
    db_path = resolve_db_path(f"db/{species_formatted}_{mode_formatted}_{cell_type}.db")

    if not os.path.exists(db_path):
        logger.warning("DB not found: %s", db_path)
        return []

    # Sanitize search term
    if search_term:
        sanitized_search = re.sub(r'[^a-zA-Z0-9\-_.]', '', search_term)
        sanitized_search = sanitized_search[:100]
        if sanitized_search != search_term:
            logger.warning("Search term sanitized: '%s' → '%s'", search_term, sanitized_search)
        search_term = sanitized_search

    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            if not search_term or len(search_term) < 1:
                query = "SELECT DISTINCT gene_id FROM gene_index ORDER BY gene_id LIMIT ?"
                cursor.execute(query, (limit * 10,))
                transcript_ids = [row[0] for row in cursor.fetchall()]
            else:
                query = "SELECT DISTINCT gene_id FROM gene_index WHERE gene_id LIKE ? ORDER BY gene_id LIMIT ?"
                cursor.execute(query, (f"{search_term}%", limit * 10))
                transcript_ids = [row[0] for row in cursor.fetchall()]

            gene_names = set()
            is_xenopus = 'Xenopus' in species or 'xenopus' in species

            for transcript_id in transcript_ids:
                if is_xenopus:
                    gene_name = transcript_id
                else:
                    if '-' in transcript_id:
                        gene_name = transcript_id.rsplit('-', 1)[0]
                    else:
                        gene_name = transcript_id
                gene_names.add(gene_name)

            gene_names = sorted(list(gene_names))[:limit]

            return gene_names
    except Exception as e:
        logger.warning("Error searching genes: %s", e)
        return []


def get_assemblies_for_gene(gene_name, species, mode, cell_type, tag_length='3bp'):
    """Get all assembly/transcript IDs for a specific gene name.

    For Homo sapiens: if gene_name is 'A1CF', returns ['A1CF-201', 'A1CF-202', 'A1CF-203', ...]
    For Xenopus: gene_name is already the full transcript_id, so just return it as a single-item list
    """
    species_formatted = species.replace(' ', '_')
    if mode == 'Exon':
        mode_formatted = '6BP' if tag_length == '6bp' else '3BP'
    else:
        mode_formatted = 'Intron'
    db_path = resolve_db_path(f"db/{species_formatted}_{mode_formatted}_{cell_type}.db")

    if not os.path.exists(db_path):
        logger.warning("DB not found: %s", db_path)
        return []

    # Sanitize gene_name
    if gene_name:
        sanitized_gene = re.sub(r'[^a-zA-Z0-9\-_.]', '', gene_name)
        sanitized_gene = sanitized_gene[:100]
        if sanitized_gene != gene_name:
            logger.warning("Gene name sanitized: '%s' → '%s'", gene_name, sanitized_gene)
        gene_name = sanitized_gene

    is_xenopus = 'Xenopus' in species or 'xenopus' in species
    is_mouse = 'Mus' in species or 'mus' in species

    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            if is_xenopus:
                query = "SELECT DISTINCT gene_id FROM gene_index WHERE gene_id = ?"
                cursor.execute(query, (gene_name,))
                result = cursor.fetchone()
                transcript_ids = [result[0]] if result else []
            elif is_mouse:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('sqlite_sequence', 'gene_index')")
                table_result = cursor.fetchone()
                if table_result:
                    table_name = table_result[0]
                    query = f"""
                        SELECT DISTINCT m.transcript_ids
                        FROM '{table_name}' m
                        INNER JOIN gene_index gi ON m.rowid = gi.main_id
                        WHERE gi.gene_id = ?
                        AND m.transcript_ids IS NOT NULL AND m.transcript_ids != ''
                    """
                    cursor.execute(query, (gene_name,))
                    rows = cursor.fetchall()
                    all_tids = set()
                    for row in rows:
                        for tid in row[0].split(','):
                            tid = tid.strip()
                            if tid:
                                all_tids.add(tid)
                    transcript_ids = sorted(all_tids)
                else:
                    logger.warning("Mouse: no valid table found in database for gene '%s'", gene_name)
                    transcript_ids = []
            else:
                query = "SELECT DISTINCT gene_id FROM gene_index WHERE gene_id LIKE ? ORDER BY gene_id"
                cursor.execute(query, (f"{gene_name}-%",))
                transcript_ids = [row[0] for row in cursor.fetchall()]

                def get_assembly_number(transcript_id):
                    try:
                        return int(transcript_id.rsplit('-', 1)[1])
                    except (ValueError, IndexError):
                        return 999999

                transcript_ids.sort(key=get_assembly_number)

            logger.info("Gene '%s' → %d assemblies found", gene_name, len(transcript_ids))
            return transcript_ids
    except Exception as e:
        logger.warning("Error getting assemblies: %s", e)
        return []
