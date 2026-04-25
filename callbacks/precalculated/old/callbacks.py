import dash
from dash import html, dcc, dash_table, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash.dependencies import Input, Output, State, ALL, MATCH
import pandas as pd
import json
import os
import re
import plotly.graph_objects as go

from utils.db import (
    get_db_connection,
    get_transcript_db_path,
    get_zoom_data_cached,
    get_last_exon_length_cached,
    search_genes_in_db,
    get_assemblies_for_gene,
    resolve_db_path,
)
from utils.tag_presets import TAG_PRESETS
from .gene_bar import build_gene_bar
from .panels import (
    build_readme_panel,
    build_grna_scatter_plot,
    build_allele_panel,
    build_info_panel,
    build_custom_sequence_panel,
)
from recalculate_grna import recalculate_grna
from recalculate_intron_grna import recalculate_intron
from Pythia_ExonTagger import reverse_complement


def register_callbacks(app):

    # =========================================================
    # Tagging page callbacks
    # =========================================================

    # Callback to toggle collapse
    @app.callback(
        [Output("collapse", "is_open"),
         Output("chevron-icon", "className"),
         Output("collapse-tab", "style")],
        [Input("collapse-tab", "n_clicks")],
        [State("collapse", "is_open")]
    )
    def toggle_collapse(n, is_open):
        base_style = {
            'cursor': 'pointer',
            'padding': '0.5em 1em',
            'backgroundColor': 'var(--primary-color)',
            'color': 'white',
            'borderRadius': '0 0 8px 8px',
            'display': 'inline-flex',
            'alignItems': 'center',
            'fontSize': '0.9em',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'pointerEvents': 'auto'
        }

        if n:
            if is_open:
                return False, "bi bi-chevron-right", base_style
            else:
                return True, "bi bi-chevron-down", base_style
        return True, "bi bi-chevron-down", base_style

    # === MODE SELECTION (Intron/Exon 3bp/Exon 6bp) ==========
    @app.callback(
        [Output('selected-mode', 'children'),
         Output('selected-tag-length', 'children'),
         Output('tag-intron', 'outline'),
         Output('tag-exon-3bp', 'outline'),
         Output('tag-exon-6bp', 'outline')],
        [Input('tag-intron', 'n_clicks'),
         Input('tag-exon-3bp', 'n_clicks'),
         Input('tag-exon-6bp', 'n_clicks')]
    )
    def update_mode_and_tag_length(n_clicks_intron, n_clicks_3bp, n_clicks_6bp):
        ctx = dash.callback_context
        if not ctx.triggered:
            return 'Exon', '3bp', True, False, True

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'tag-intron':
            return 'Intron', '3bp', False, True, True
        elif button_id == 'tag-exon-3bp':
            return 'Exon', '3bp', True, False, True
        elif button_id == 'tag-exon-6bp':
            return 'Exon', '6bp', True, True, False

        return 'Exon', '3bp', True, False, True

    # === SELECT CELLTYPE =====================================
    @app.callback(
        Output('selected-cell-type', 'children'),
        Input('cell-type-dropdown', 'value')
    )
    def update_cell_type(selected_value):
        if not selected_value:
            return dash.no_update
        return selected_value

    # === TRACK RECENT GENE SELECTIONS =============
    @app.callback(
        Output('recent-genes-store', 'children'),
        Input('gene-dropdown-tagging', 'value'),
        State('recent-genes-store', 'children'),
        prevent_initial_call=True
    )
    def update_recent_genes(selected_gene, recent_genes_json):
        """Track up to 5 most recent gene selections"""
        if not selected_gene:
            return dash.no_update

        import json
        recent_genes = json.loads(recent_genes_json) if recent_genes_json else []

        # Remove gene if already in list
        if selected_gene in recent_genes:
            recent_genes.remove(selected_gene)

        # Add to front of list
        recent_genes.insert(0, selected_gene)

        # Keep only last 5 genes
        recent_genes = recent_genes[:5]

        return json.dumps(recent_genes)

    # === SEARCH GENES AS USER TYPES (ON-DEMAND) =============
    # Update cell type dropdown based on species selection
    @app.callback(
        [Output('cell-type-dropdown', 'options'),
         Output('cell-type-dropdown', 'value')],
        Input('species-dropdown', 'value'),
        prevent_initial_call=False
    )
    def update_cell_type_options(species):
        """Update cell type dropdown options based on selected species"""
        if species == 'Homo sapiens':
            options = [
                {'label': 'HEK293', 'value': 'HEK293'},
                {'label': 'mESC', 'value': 'mESC'}
            ]
            default_value = 'HEK293'
        elif species == 'Xenopus tropicalis':
            options = [
                {'label': 'mESC', 'value': 'mESC'}
            ]
            default_value = 'mESC'
        elif species == 'Mus musculus':
            options = [
                {'label': 'mESC', 'value': 'mESC'}
            ]
            default_value = 'mESC'
        else:
            # Default fallback
            options = [
                {'label': 'HEK293', 'value': 'HEK293'},
                {'label': 'mESC', 'value': 'mESC'}
            ]
            default_value = 'HEK293'

        return options, default_value


    @app.callback(
        [Output('gene-dropdown-tagging', 'options'),
         Output('gene-dropdown-tagging', 'placeholder'),
         Output('gene-dropdown-tagging', 'value'),
         Output('gene-dropdown-tagging', 'search_value')],
        [Input('gene-dropdown-tagging', 'search_value'),
         Input('selected-mode', 'children'),
         Input('species-dropdown', 'value'),
         Input('selected-cell-type', 'children'),
         Input('selected-tag-length', 'children')],
        [State('gene-dropdown-tagging', 'value'),
         State('recent-genes-store', 'children')]
    )
    def update_gene_options(search_value, mode, species, cell_type, tag_length, current_value, recent_genes_json):
        """Search genes on-demand as user types - handles 1.6M rows!"""
        print("=" * 80)
        print("SEARCHING GENES")
        print(f"Search: '{search_value}'")
        print(f"Mode: {mode}")
        print(f"Species: {species}")
        print(f"Cell type: {cell_type}")
        print(f"Current selected value: {current_value}")

        if not mode or not species or not cell_type:
            print("Missing parameters")
            print("=" * 80)
            return [], 'Select mode, species and cell type first', dash.no_update, dash.no_update

        # Parse recent genes
        import json
        recent_genes = json.loads(recent_genes_json) if recent_genes_json else []
        print(f"Recent genes: {recent_genes}")

        # Search database with LIMIT - fast even with huge tables!
        # If empty/short search, shows first 100 genes. If searching, shows matching genes.
        gene_ids = search_genes_in_db(search_value, species, mode, cell_type, limit=95, tag_length=tag_length)  # Leave room for recent genes

        # Determine what triggered this callback
        ctx = dash.callback_context
        trigger_id = None
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            print(f"Triggered by: {trigger_id}")

        if not gene_ids:
            print("No genes found")
            print("=" * 80)
            # Check if database doesn't exist
            import os
            species_formatted = species.replace(' ', '_')
            mode_formatted = '6BP' if (mode == 'Exon' and tag_length == '6bp') else ('3BP' if mode == 'Exon' else 'Intron')
            db_path = resolve_db_path(f"db/{species_formatted}_{mode_formatted}_{cell_type}.db")

            if not os.path.exists(db_path):
                # Database doesn't exist - show custom message
                print(f"Database doesn't exist: {db_path}")
                return [], 'Our glass ball is cloudy. Please wait for these guides to be predicted.', None, '' if trigger_id == 'species-dropdown' else dash.no_update

            # Database exists but no genes match search
            if search_value and len(search_value) >= 1:
                return [], f'No genes matching "{search_value}"', dash.no_update, dash.no_update
            else:
                return [], 'No genes available', dash.no_update, dash.no_update

        # Build the final gene list in order: current selection, recent genes, search results
        final_gene_list = []

        # Clear recent genes only when species changes (not mode or cell type)
        if trigger_id == 'species-dropdown':
            print(f"Species changed ({trigger_id}), clearing recent genes")
            recent_genes = []

        # Step 1: Add current selection at the very top (if not changing species)
        if trigger_id != 'species-dropdown':
            if current_value:
                final_gene_list.append(current_value)
                print(f"Adding current selection at top: {current_value}")

        # Step 2: Add recent genes (excluding current selection and genes already in gene_ids)
        for gene in recent_genes:
            if gene != current_value and gene not in final_gene_list:
                final_gene_list.append(gene)
                print(f"Adding recent gene: {gene}")

        # Step 3: Add search results (excluding current selection and recent genes)
        for gene in gene_ids:
            if gene not in final_gene_list:
                final_gene_list.append(gene)

        # Limit to 100 total items
        if len(final_gene_list) > 100:
            final_gene_list = final_gene_list[:100]
            print(f"Trimmed list to 100 items")

        # Create options list
        options = [{'label': gene_id, 'value': gene_id} for gene_id in final_gene_list]

        print(f"Returning {len(options)} options")

        # Hard reset when species changes: clear selection entirely
        # Preserve selection when mode, cell type, or tag length changes
        if trigger_id == 'species-dropdown':
            print(f"Species changed ({trigger_id}), hard-resetting gene selection and search")
            # Clear gene selection and search box on organism switch
            preserved_value = None
            clear_search = ''
        else:
            # User is searching or mode/cell type changed - preserve current selection
            preserved_value = dash.no_update
            clear_search = dash.no_update
            print(f"Preserving current value using dash.no_update")

        print("=" * 80)

        if not search_value or len(search_value) < 1:
            placeholder = f'Type to search genes (showing first {len(options)})...'
        else:
            placeholder = f'Found {len(options)} genes' + (' (showing first 100)' if len(options) == 100 else '')

        return options, placeholder, preserved_value, clear_search


    # === UPDATE ASSEMBLY DROPDOWN ============================
    @app.callback(
        [Output('assembly-dropdown-tagging', 'options'),
         Output('assembly-dropdown-tagging', 'value'),
         Output('assembly-dropdown-tagging', 'placeholder')],
        [Input('gene-dropdown-tagging', 'value'),
         Input('selected-mode', 'children'),
         Input('species-dropdown', 'value'),
         Input('selected-cell-type', 'children'),
         Input('selected-tag-length', 'children')],
        [State('assembly-dropdown-tagging', 'value')]
    )
    def update_assembly_options(selected_gene, mode, species, cell_type, tag_length, current_assembly):
        """Populate assembly dropdown when a gene is selected"""
        print("=" * 80)
        print("UPDATE ASSEMBLY OPTIONS")
        print(f"Selected gene: {selected_gene}")
        print(f"Mode: {mode}, Species: {species}, Cell type: {cell_type}")
        print(f"Current assembly: {current_assembly}")

        if not selected_gene or not mode or not species or not cell_type:
            print("Missing parameters - clearing assembly dropdown")
            print("=" * 80)
            return [], None, 'Select a transcript first'

        # Get all assemblies for this gene
        assemblies = get_assemblies_for_gene(selected_gene, species, mode, cell_type, tag_length)

        if not assemblies:
            print(f"No assemblies found for gene '{selected_gene}'")
            print("=" * 80)
            return [], None, f'No assemblies found for {selected_gene}'

        # Create options list
        # For Mus musculus, transcript_ids are raw Ensembl IDs (ENSMUST...) which are
        # not user-friendly. Display them as GeneName-1, GeneName-2, etc. instead,
        # while keeping the Ensembl ID as the value for DB lookups.
        is_mouse = 'Mus' in (species or '') or 'mus' in (species or '')
        if is_mouse:
            options = [{'label': f'{selected_gene}-{i+1}', 'value': assembly}
                       for i, assembly in enumerate(assemblies)]
        else:
            options = [{'label': assembly, 'value': assembly} for assembly in assemblies]

        # Preserve the current selection if it's still valid, otherwise clear it
        if current_assembly and current_assembly in assemblies:
            default_assembly = current_assembly
            print(f"Preserving current assembly: {current_assembly}")
        else:
            default_assembly = None
            print("Current assembly not in new list - clearing selection")

        print(f"Found {len(assemblies)} assemblies available")
        print("=" * 80)

        placeholder = 'Select a transcript'
        return options, default_assembly, placeholder


    # === CLEAR VISUALIZATION WHEN DB CHANGES =================
    @app.callback(
        [Output('selected-grna-index', 'children', allow_duplicate=True),
         Output('tagging-bar-host', 'children', allow_duplicate=True),
         Output('mutation-detail-container', 'children', allow_duplicate=True)],
        [Input('selected-mode', 'children'),
         Input('selected-cell-type', 'children'),
         Input('species-dropdown', 'value'),
         Input('selected-tag-length', 'children'),
         Input('gene-dropdown-tagging', 'value')],
        prevent_initial_call=True
    )
    def clear_visualization_on_db_change(mode, cell_type, species, tag_length, selected_gene):
        """Clear tagging bar and detail panels when database parameters change

        Also show message if database doesn't exist.
        """
        import os

        # Check if we have all parameters
        if not mode or not species or not cell_type:
            return None, html.Div(), html.Div()

        # Construct database path to check if it exists
        species_formatted = species.replace(' ', '_')
        if mode == 'Exon':
            mode_formatted = '6BP' if tag_length == '6bp' else '3BP'
        else:
            mode_formatted = 'Intron'
        db_path = f"db/{species_formatted}_{mode_formatted}_{cell_type}.db"

        # If database doesn't exist, show the message in the bar area
        if not os.path.exists(db_path):
            message_div = html.Div(
                "Our glass ball is cloudy. Please wait for these guides to be predicted.",
                style={
                    'textAlign': 'center',
                    'color': 'var(--text-secondary)',
                    'padding': '3em 2em',
                    'fontSize': '1.2em',
                    'fontWeight': '500',
                    'backgroundColor': 'var(--bg-primary)',
                    'borderRadius': '10px',
                    'margin': '2em 0'
                }
            )
            return None, message_div, html.Div()

        # Database exists, just clear the visualization
        return None, html.Div(), html.Div()

    # === CLEAR VISUALIZATION WHEN DATA STORE IS EMPTY ===========
    @app.callback(
        [Output('tagging-bar-host', 'children', allow_duplicate=True),
         Output('mutation-detail-container', 'children', allow_duplicate=True)],
        [Input('full-grna-data', 'children')],
        prevent_initial_call=True
    )
    def clear_visualization_on_empty_store(full_data_json):
        import json
        if not full_data_json:
            return build_readme_panel(), html.Div()
        try:
            full = json.loads(full_data_json)
            if not full.get('data') or full.get('sequence_length', 0) <= 0:
                return build_readme_panel(), html.Div()
        except Exception:
            return build_readme_panel(), html.Div()
        return dash.no_update, dash.no_update

    # === HARD RESET WHEN SPECIES CHANGES ======================
    @app.callback(
        [
            Output('gene-table-container', 'children', allow_duplicate=True),
            Output('recent-genes-store', 'children', allow_duplicate=True),
            Output('assembly-dropdown-tagging', 'value', allow_duplicate=True)
        ],
        Input('species-dropdown', 'value'),
        prevent_initial_call=True
    )
    def reset_on_species_change(species):
        """When organism changes, clear gene table, recent genes, and assembly selection."""
        import json
        empty_grid = dag.AgGrid(
            id="gene-grid",
            columnDefs=[],
            rowData=[],
            style={"display": "none"}
        )
        empty_store = html.Div(
            id='full-grna-data',
            style={'display': 'none'},
            children=json.dumps({
                'data': [],
                'sequence_length': 0,
                'selected_gene': '',
                'species': species or ''
            })
        )
        return html.Div([empty_grid, empty_store]), json.dumps([]), None

    # === DISPLAY GENE TABLE ==================================
    @app.callback(
        Output('gene-table-container', 'children'),
        [Input('assembly-dropdown-tagging', 'value')],
        [State('selected-mode', 'children'),
         State('selected-tag-length', 'children'),
         State('species-dropdown', 'value'),
         State('selected-cell-type', 'children'),
         State('gene-dropdown-tagging', 'value')],
        prevent_initial_call=True,
    )
    def display_gene_table(selected_assembly, mode, tag_length, species, cell_type, selected_gene):
        import time, json
        start_time = time.time()

        print("=" * 80)
        print("DISPLAY GENE TABLE DEBUG")
        print(f"Selected assembly: {selected_assembly}")
        print(f"Mode: {mode}")
        print(f"Tag length: {tag_length}")
        print(f"Species: {species}")
        print(f"Cell type: {cell_type}")

        if not selected_assembly or not mode or not tag_length or not species or not cell_type:
            print("Missing required parameters, returning empty grid")
            print("=" * 80)
            # Return empty grid + empty store to keep dependent callbacks happy
            return html.Div([
                dag.AgGrid(
                    id="gene-grid",
                    columnDefs=[],
                    rowData=[],
                    style={"display": "none"}
                ),
                html.Div(
                    id='full-grna-data',
                    style={'display': 'none'},
                    children=json.dumps({
                        'data': [],
                        'sequence_length': 0,
                        'selected_gene': '',
                        'species': species
                    })
                )
            ])

        try:
            import os

            # Get the last_exon_sequence or last_intron_sequence length from transcript_sequences.db
            try:
                t1 = time.time()
                transcript_db_path = get_transcript_db_path(species)

                # Choose column based on mode
                sequence_column = "last_intron_sequence" if mode == "Intron" else "last_exon_sequence"
                print(f"Fetching {sequence_column} length from {transcript_db_path}...")

                # Determine which column to query based on species
                is_mouse = 'Mus' in species or 'mus' in species

                with get_db_connection(transcript_db_path) as conn_first3:
                    if is_mouse:
                        # For mouse, use transcript_id column (contains Ensembl IDs like ENSMUST...)
                        query_seq = f"SELECT {sequence_column} FROM transcript_data WHERE transcript_id = ?"
                    else:
                        # For human/xenopus, use gene_id column
                        query_seq = f"SELECT {sequence_column} FROM transcript_data WHERE gene_id = ?"
                    result_seq = pd.read_sql_query(query_seq, conn_first3, params=(selected_assembly,))
                print(f"Sequence query took: {time.time() - t1:.2f}s")

                if not result_seq.empty and result_seq[sequence_column].iloc[0]:
                    sequence_length = len(result_seq[sequence_column].iloc[0])
                    print(f"Sequence length: {sequence_length}")
                else:
                    sequence_length = 2000
                    print(f"No sequence found, using default: {sequence_length}")
            except Exception as e:
                print(f"Error fetching sequence length: {e}")
                sequence_length = 2000

            # Connect to database and get gRNA data
            # Construct database file path based on selections
            species_formatted = species.replace(' ', '_')
            if mode == 'Exon':
                mode_formatted = '6BP' if tag_length == '6bp' else '3BP'
            else:
                mode_formatted = 'Intron'
            db_path = resolve_db_path(f"db/{species_formatted}_{mode_formatted}_{cell_type}.db")

            print(f"Constructed DB path: {db_path}")
            print(f"DB file exists: {os.path.exists(db_path)}")

            # Check if database exists
            if not os.path.exists(db_path):
                print(f"Database doesn't exist: {db_path}")
                print("=" * 80)
                return html.Div([
                    dag.AgGrid(
                        id="gene-grid",
                        columnDefs=[],
                        rowData=[],
                        style={"display": "none"}
                    ),
                    html.Div(
                        "Our glass ball is cloudy. Please wait for these guides to be predicted.",
                        style={
                            'textAlign': 'center',
                            'color': 'var(--text-secondary)',
                            'padding': '2em',
                            'fontSize': '1.1em',
                            'fontWeight': '500'
                        }
                    ),
                    html.Div(
                        id='full-grna-data',
                        style={'display': 'none'},
                        children=json.dumps({
                            'data': [],
                            'sequence_length': 0,
                            'selected_gene': '',
                            'species': species
                        })
                    )
                ])

            t2 = time.time()
            print(f"Connecting to database...")
            with get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                print("Fetching table name...")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                table_name = cursor.fetchone()[0]
                print(f"Table name: {table_name}")

                # Check if this is mouse - different query logic
                is_mouse = 'Mus' in species or 'mus' in species

                if is_mouse:
                    query = f"""
                        SELECT m.gRNA, m.CRISPRScan_score, m.integration_score, m.location, m.strand,
                               m.x0_frequency, m.x1_frequency, m.x2_frequency, m.x3_frequency, m.x4_frequency
                        FROM '{table_name}' m
                        INNER JOIN gene_index gi ON m.rowid = gi.main_id
                        WHERE gi.gene_id = ?
                        AND m.transcript_ids LIKE ? AND m.CRISPRScan_score > 0
                        ORDER BY m.integration_score DESC
                    """
                    print(f"Executing mouse query for gene: {selected_gene}, transcript: {selected_assembly}")
                    t3 = time.time()
                    df = pd.read_sql_query(query, conn, params=(
                        selected_gene,
                        f'%{selected_assembly}%',
                    ))
                    print(f"Query took: {time.time() - t3:.2f}s")
                    print(f"Query returned {len(df)} rows")
                else:
                    # Use gene_index table for fast lookup of individual transcript IDs
                    # This allows searching for 'KDM1A-237' even when gene_id contains 'KDM1A-237,KDM1A-210,...'
                    query = f"""
                        SELECT m.gRNA, m.CRISPRScan_score, m.integration_score, m.location, m.strand,
                               m.x0_frequency, m.x1_frequency, m.x2_frequency, m.x3_frequency, m.x4_frequency
                        FROM '{table_name}' m
                        INNER JOIN gene_index gi ON m.rowid = gi.main_id
                        WHERE gi.gene_id = ? AND m.CRISPRScan_score > 0
                        ORDER BY m.integration_score DESC
                    """
                    print(f"Executing query for assembly: {selected_assembly}")
                    t3 = time.time()
                    df = pd.read_sql_query(query, conn, params=(selected_assembly,))
                    print(f"Query took: {time.time() - t3:.2f}s")
                    print(f"Query returned {len(df)} rows")
            print(f"Total database time: {time.time() - t2:.2f}s")

            if df.empty:
                import json
                return html.Div([
                    dag.AgGrid(
                        id="gene-grid",
                        columnDefs=[],
                        rowData=[],
                        style={"display": "none"}
                    ),
                    html.P(
                        f"No results found for {selected_assembly}",
                        style={
                            'textAlign': 'center',
                            'color': 'var(--text-secondary)',
                            'padding': '2em'
                        }
                    ),
                    html.Div(
                        id='full-grna-data',
                        style={'display': 'none'},
                        children=json.dumps({
                            'data': [],
                            'sequence_length': sequence_length,
                            'selected_gene': selected_assembly,
                            'species': species
                        })
                    )
                ])

            # ===== FORMAT NEW TABLE COLUMNS =====
            df['CRISPRScan_score'] = df['CRISPRScan_score'].round(2)
            df['integration_score'] = df['integration_score'].round(2)

            # Calculate in-frame chance (sum of all x_frequency values)
            freq_cols = [f'x{i}_frequency' for i in range(5)]
            df['inframe_pct'] = df[freq_cols].fillna(0).sum(axis=1).round(2)

            # Calculate efficiency based on Pythia score and CRISPRScan score
            import numpy as np
            conditions = [
                (df['integration_score'] >= 75) & (df['CRISPRScan_score'] >= 50),
                (df['integration_score'] >= 60) & (df['CRISPRScan_score'] >= 40),
            ]
            df['efficiency'] = np.select(conditions, ["Very Good", "Good"], default="Low")

            # Sort by efficiency first (Very Good > Good > Low), then Pythia score DESC
            efficiency_order = {"Very Good": 0, "Good": 1, "Low": 2}
            df['_efficiency_rank'] = df['efficiency'].map(efficiency_order)
            df = df.sort_values(
                ['_efficiency_rank', 'integration_score'],
                ascending=[True, False]
            ).reset_index(drop=True)
            df = df.drop(columns=['_efficiency_rank'])
            df['global_idx'] = df.index  # index into this df (used for zoom)

            # Display-friendly frame (used for AG-Grid rowData)
            df_display = pd.DataFrame({
                "Location": df["location"],
                "Strand": df["strand"].replace({"plus": "+", "min": "-"}).fillna(""),
                "gRNA": df["gRNA"],
                "Inframe %": df["inframe_pct"],
                "CRISPRScan": df["CRISPRScan_score"],
                "Pythia": df["integration_score"],
                "Efficiency": df["efficiency"],
                "global_idx": df["global_idx"]
            })

            # ===== AG-GRID TABLE =====
            grid = dag.AgGrid(
                id="gene-grid",
                columnDefs=[
                    {"headerName": "Location", "field": "Location", "flex": 0.8,
                     "cellStyle": {"textAlign": "left"}},
                    {"headerName": "Strand", "field": "Strand", "flex": 0.8,
                     "cellStyle": {"textAlign": "left"}},
                    {"headerName": "gRNA", "field": "gRNA", "flex": 2,
                     "cellStyle": {"textAlign": "left"}},
                    {"headerName": "Inframe %", "field": "Inframe %", "flex": 1,
                     "cellStyle": {"textAlign": "left"}},
                    {"headerName": "CRISPRScan", "field": "CRISPRScan", "flex": 1,
                     "cellStyle": {"textAlign": "left"}},
                    {"headerName": "Pythia", "field": "Pythia", "flex": 1,
                     "cellStyle": {"fontWeight": "bold", "textAlign": "left"}},
                    {"headerName": "Efficiency", "field": "Efficiency", "flex": 1,
                     "cellStyle": {"fontWeight": "bold", "textAlign": "left"}},
                    # global_idx is used only internally; we don't define a column for it
                ],
                rowData=df_display.to_dict('records'),
                defaultColDef={
                    "resizable": True,
                    "sortable": True,
                    "filter": False,
                    "wrapHeaderText": True,
                    "autoHeaderHeight": True
                },
                dashGridOptions={
                    "rowSelection": "single",
                    "suppressRowClickSelection": False,
                    "domLayout": "autoHeight"
                },
                style={"width": "100%", "marginTop": "0.5rem"},
            )

            # ===== STORE RAW DATA FOR ZOOM MODE ======
            import json
            full_data_store = html.Div(
                id='full-grna-data',
                style={'display': 'none'},
                children=json.dumps({
                    'data': df.to_dict('records'),   # raw original df with global_idx
                    'sequence_length': sequence_length,
                    'selected_gene': selected_assembly,
                    'selected_gene_symbol': selected_gene,  # Gene symbol (e.g., "Kdm1a" for mouse)
                    'species': species
                })
            )

            return html.Div([grid, full_data_store])

        except Exception as e:
            print(f"Error loading gene data: {e}")
            import json
            return html.Div([
                dag.AgGrid(
                    id="gene-grid",
                    columnDefs=[],
                    rowData=[],
                    style={"display": "none"}
                ),
                html.P(
                    f"Error loading data: {str(e)}",
                    style={'textAlign': 'center', 'color': 'red', 'padding': '2em'}
                ),
                html.Div(
                    id='full-grna-data',
                    style={'display': 'none'},
                    children=json.dumps({
                        'data': [],
                        'sequence_length': 0,
                        'selected_gene': '',
                        'species': species
                    })
                )
            ])

    # === STORE SELECTED GRNA INDEX ===========================
    @app.callback(
        Output('selected-grna-index', 'children'),
        [
            Input({'type': 'grna-arrow', 'index': ALL}, 'n_clicks'),
            Input('gene-grid', 'selectedRows'),
        ],
        prevent_initial_call=True
    )
    def update_selected_grna(arrow_clicks, selected_rows):
        import json
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        trig = ctx.triggered[0]['prop_id']

        # === ROW CLICK ===
        if 'gene-grid' in trig:
            if selected_rows:
                row = selected_rows[0]
                if 'global_idx' in row:
                    return int(row['global_idx'])
            return dash.no_update

        # === ARROW CLICK ===
        if "grna-arrow" in trig and arrow_clicks and any(n and n > 0 for n in arrow_clicks):
            idx_local = json.loads(trig.split('.')[0])["index"]  # ALWAYS matches df_all
            return int(idx_local)

        return dash.no_update

    # === SCATTER PLOT CLICK HANDLER ===========================
    @app.callback(
        Output('selected-grna-index', 'children', allow_duplicate=True),
        Input('grna-scatter-plot', 'clickData'),
        prevent_initial_call=True
    )
    def update_selected_grna_from_scatter(click_data):
        if click_data:
            point_data = click_data['points'][0]
            if 'customdata' in point_data:
                return int(point_data['customdata'])
        return dash.no_update

    # === UNIFIED DISPLAY CALLBACK ============================
    @app.callback(
        [
            Output('tagging-bar-host', 'children'),
            Output('mutation-detail-container', 'children'),
            Output('mutation-loading-trigger', 'children'),
            Output("repair-cassette-store", "data"),
            Output("repair-left-arm-store", "data"),
            Output("repair-right-arm-store", "data"),
            Output("repair-strand-store", "data"),
        ],
        [
            Input('selected-grna-index', 'children'),
            Input('custom-sequence-data-store', 'data'),
            Input('full-grna-data', 'children'),
        ],
        [
            State('selected-mode', 'children'),
            State('selected-tag-length', 'children'),
            State('species-dropdown', 'value'),
            State('selected-cell-type', 'children'),
            State('assembly-dropdown-tagging', 'value'),
            State('assembly-dropdown-tagging', 'options'),
        ],
        prevent_initial_call=True
    )
    def update_mutation_detail(
        selected_idx, custom_data, full_data_json,
        mode, tag_length, species, cell_type, gene_name, assembly_options):
        import json

        if not full_data_json:
            # database not loaded: show README instead of bar/detail
            return build_readme_panel(), html.Div(), None, "", "", "", ""

        # Load everything
        full = json.loads(full_data_json)

        # Guard: if database not loaded / no rows, show nothing
        if not full.get('data') or full.get('sequence_length', 0) <= 0:
            # database empty/unloaded: show README instead of bar/detail
            return build_readme_panel(), html.Div(), None, "", "", "", ""

        df_all = pd.DataFrame(full['data'])
        L = full['sequence_length']
        gene = full['selected_gene']
        gene_symbol = full.get('selected_gene_symbol', gene)  # For mouse, this is the gene symbol

        # For mouse, use the human-readable label (e.g. "Kdm1a-1") from the assembly dropdown
        is_mouse = 'Mus' in (species or '') or 'mus' in (species or '')
        if is_mouse and assembly_options and gene_name:
            display_gene = next(
                (opt['label'] for opt in assembly_options if opt['value'] == gene_name),
                gene_symbol
            )
        else:
            display_gene = gene

        if 'global_idx' in df_all.columns:
            df_all = df_all.sort_values('global_idx').reset_index(drop=True)

        # Fetch last_exon_sequence length for Intron mode (cached for performance)
        last_exon_length = None
        if mode == 'Intron' and gene_name and species:
            last_exon_length = get_last_exon_length_cached(gene_name, species)

        # Helper: build bar (and allele panel if zoomed) with a *stable* wrapper
        def build_bar_and_alleles(df_view, sel_idx, custom_insert_len=None, linker_color=None, tag_color=None,
                                  linker_name=None, tag_name=None, linker_len=None, tag_len=None, extra_components=None):
            bar, allele_panel = build_gene_bar(df_view, L, display_gene, sel_idx, tag_length,
                                               custom_insert_length=custom_insert_len,
                                               linker_color=linker_color, tag_color=tag_color,
                                               linker_name=linker_name, tag_name=tag_name,
                                               linker_len=linker_len, tag_len=tag_len, mode=mode,
                                               last_exon_length=last_exon_length,
                                               extra_components=extra_components)
            bar_block = html.Div(
                bar,
                className="tagging-bar-sticky",
                style={'margin': '15px 0'}
            )
            return bar_block, allele_panel

        # ---------- PURE OVERVIEW (no selected gRNA) ----------
        if selected_idx is None:
            df_view = df_all.copy()
            bar_block, _ = build_bar_and_alleles(df_view, None)

            instruction_message = html.Div(
                "\U0001f446 Click on a gRNA in the visualization above or on a row in the table below to view detailed repair template information",
                style={
                    'backgroundColor': '#FFF3E0',
                    'border': '2px solid #FF9800',
                    'borderRadius': '8px',
                    'padding': '12px 20px',
                    'margin': '6px 0 4px 0',
                    'textAlign': 'center',
                    'fontSize': '15px',
                    'fontWeight': '600',
                    'color': '#E65100',
                    'boxShadow': '0 2px 4px rgba(255, 152, 0, 0.1)'
                }
            )
            return bar_block, instruction_message, None, "", "", "", ""

        # ---------- ZOOM MODE ----------
        try:
            # Use cached database query - much faster on subsequent calls!
            # For mouse, we need both gene symbol and transcript ID for efficient querying
            zoom_json = get_zoom_data_cached(gene, species, mode, cell_type, tag_length, gene_symbol)
            df_zoom = pd.read_json(zoom_json, orient='records')
            df_zoom = df_zoom.sort_values('integration_score', ascending=False).reset_index(drop=True)
        except Exception:
            df_zoom = df_all.copy()

        # Guard against bad indices -> fall back to overview
        if selected_idx is None or selected_idx < 0 or selected_idx >= len(df_zoom):
            df_view = df_all.copy()
            bar_block, _ = build_bar_and_alleles(df_view, None)
            return bar_block, html.Div(), None, "", "", "", ""

        # Valid zoomed selection
        row = df_zoom.iloc[selected_idx]

        # Check if we have custom sequence data for this gRNA
        custom_insert_len = None
        linker_color = None
        tag_color = None
        linker_name = None
        tag_name = None
        linker_len = None
        tag_len = None
        extra_components = []

        if custom_data and custom_data.get('selected_idx') == selected_idx:
            # Merge custom recalculated data into the row
            custom_result = custom_data.get('result', {})
            # Create a copy of the row as a dict and update with custom data
            row_dict = row.to_dict()
            row_dict.update(custom_result)
            # Convert back to Series to maintain compatibility
            row = pd.Series(row_dict)

            # Update df_zoom with the custom data so allele panel gets updated values
            df_zoom_updated = df_zoom.copy()
            for col in custom_result.keys():
                if col in df_zoom_updated.columns or col not in df_zoom_updated.columns:
                    df_zoom_updated.at[selected_idx, col] = custom_result[col]

            # Extract preset colors if this was a preset-based recalculation
            preset_info = custom_data.get('preset_info')
            if preset_info:
                # For presets, don't set custom_insert_len - we want the split view with colors
                linker_name = preset_info.get('linker')
                tag_name = preset_info.get('tag')
                custom_insert_len = None

                # Look up colors from presets
                for linker in TAG_PRESETS.get('linkers', []):
                    if linker['name'] == linker_name:
                        linker_color = linker.get('color')
                        linker_len = len(linker.get('sequence', '') or '')
                        break

                for tag in TAG_PRESETS.get('tags', []):
                    if tag['name'] == tag_name:
                        tag_color = tag.get('color')
                        tag_len = len(tag.get('sequence', '') or '')
                        break

                # Look up extra components (all beyond the primary linker + tag)
                all_component_names = preset_info.get('all_components', [])
                all_presets = TAG_PRESETS.get('linkers', []) + TAG_PRESETS.get('tags', [])
                for comp_name in all_component_names[2:]:
                    for item in all_presets:
                        if item['name'] == comp_name:
                            extra_components.append({
                                'name': comp_name,
                                'color': item.get('color', '#888888'),
                                'length': len(item.get('sequence', '') or '')
                            })
                            break
            else:
                # Only set custom_insert_len for non-preset custom sequences
                custom_sequence = custom_data.get('custom_sequence', '')
                if custom_sequence:
                    # Get dynamic cassette length from the row
                    dynamic_cassette = row.get('dynamic_cassette', '')
                    if isinstance(dynamic_cassette, str):
                        if mode == "Intron":
                            # In intron mode, custom insert should replace only linker+tag.
                            custom_insert_len = len(custom_sequence)
                        else:
                            # Exon mode keeps dynamic cassette + custom tag together
                            custom_insert_len = len(dynamic_cassette) + len(custom_sequence)
        else:
            df_zoom_updated = df_zoom

        info_panel = build_info_panel(row, gene, tag_length)
        bar_block, allele_panel = build_bar_and_alleles(
            df_zoom_updated,
            selected_idx,
            custom_insert_len,
            linker_color,
            tag_color,
            linker_name,
            tag_name,
            linker_len,
            tag_len,
            extra_components
        )

        # Build scatter plot for all gRNAs
        scatter_plot = build_grna_scatter_plot(df_zoom, selected_idx, row, mode=mode)

        # Build custom sequence panel, restoring any sequence the user already entered
        current_seq = (custom_data or {}).get('custom_sequence', '') or ''
        custom_seq_panel = build_custom_sequence_panel(current_sequence=current_seq)

        zoom_layout = html.Div([
            html.Div(
                "Click on the bar to return to overview",
                style={
                    'textAlign': 'center',
                    'margin': '0 0 10px 0',
                    'color': '#6B7280',
                    'fontStyle': 'italic',
                    'fontSize': '0.9rem'
                }
            ),
            # Wrap heavy content in delayed div - appears after bar animation
            html.Div(
                id='zoom-content-delayed',
                children=[
                    html.Div(
                        [info_panel, allele_panel],
                        style={
                            'display': 'flex',
                            'gap': '20px',
                            'alignItems': 'stretch',
                            'marginTop': '5px'
                        }
                    ),
                    html.Div(
                        [scatter_plot, custom_seq_panel],
                        style={
                            'display': 'flex',
                            'gap': '20px',
                            'alignItems': 'stretch',
                            'marginTop': '5px'
                        }
                    )
                ],
                style={
                    'opacity': '0',
                    'transition': 'opacity 0.3s ease-in',
                    'animation': 'fade-in-delayed 0.3s ease-in 0.5s forwards'  # Delay 500ms
                }
            )
        ])

        return (
            bar_block,
            zoom_layout,
            None,
            row.get("Repair_Cassette", ""),
            row.get("left_repair_arm", ""),
            row.get("right_repair_arm", ""),
            row.get("strand", "")
        )

    # =========================================================
    # === DOWNLOAD / COPY CALLBACKS ===========================
    # =========================================================

    @app.callback(
        Output("warning-acknowledged", "data"),
        Input("download-confirm-btn", "n_clicks"),
        State("dont-show-again-checkbox", "value"),
        prevent_initial_call=True
    )
    def update_warning_acknowledged(confirm_clicks, checkbox_value):
        """Save user's preference to not show warning again"""
        if checkbox_value and "hide" in checkbox_value:
            return True
        return dash.no_update

    # === DOWNLOAD/COPY CONFIRMATION MODAL ========================
    @app.callback(
        [Output("download-modal", "is_open"),
         Output("pending-download-type", "data")],
        [Input({'type': 'download-cassette', 'gRNA': ALL}, 'n_clicks'),
         Input({'type': 'download-cassette-txt', 'gRNA': ALL}, 'n_clicks'),
         Input({'type': 'copy-grna-btn', 'gRNA': ALL}, 'n_clicks'),
         Input({'type': 'copy-cassette-btn', 'gRNA': ALL}, 'n_clicks'),
         Input("download-confirm-btn", "n_clicks")],
        [State("download-modal", "is_open"),
         State("pending-download-type", "data"),
         State("repair-cassette-store", "data"),
         State("warning-acknowledged", "data")],
        prevent_initial_call=True
    )
    def toggle_download_modal(fasta_clicks, txt_clicks, copy_grna_clicks, copy_cassette_clicks, confirm_clicks, is_open, pending_type, cassette, warning_acknowledged):
        """Show confirmation modal when download/copy buttons are clicked (unless user has opted out)"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        trigger_id = ctx.triggered[0]['prop_id']

        # If confirm button was clicked, close modal
        if 'download-confirm-btn' in trigger_id:
            return False, pending_type  # Keep pending_type so download/copy can proceed

        # If user has acknowledged warning, skip modal and proceed directly
        if warning_acknowledged:
            # Don't show modal, but still set pending_type for the action to proceed
            if 'download-cassette' in trigger_id and 'txt' not in trigger_id and 'copy' not in trigger_id:
                if fasta_clicks and any(fasta_clicks):
                    return False, {'type': 'fasta', 'trigger': trigger_id}

            if 'download-cassette-txt' in trigger_id:
                if txt_clicks and any(txt_clicks):
                    return False, {'type': 'txt', 'trigger': trigger_id}

            if 'copy-grna-btn' in trigger_id:
                if copy_grna_clicks and any(copy_grna_clicks):
                    gRNA = json.loads(trigger_id.split('.')[0])['gRNA']
                    return False, {'type': 'copy-grna', 'trigger': trigger_id, 'content': gRNA}

            if 'copy-cassette-btn' in trigger_id:
                if copy_cassette_clicks and any(copy_cassette_clicks):
                    return False, {'type': 'copy-cassette', 'trigger': trigger_id, 'content': cassette}

        # User hasn't acknowledged - show modal
        # If FASTA download button clicked
        if 'download-cassette' in trigger_id and 'txt' not in trigger_id and 'copy' not in trigger_id:
            if fasta_clicks and any(fasta_clicks):
                return True, {'type': 'fasta', 'trigger': trigger_id}

        # If txt download button clicked
        if 'download-cassette-txt' in trigger_id:
            if txt_clicks and any(txt_clicks):
                return True, {'type': 'txt', 'trigger': trigger_id}

        # If copy gRNA button clicked
        if 'copy-grna-btn' in trigger_id:
            if copy_grna_clicks and any(copy_grna_clicks):
                gRNA = json.loads(trigger_id.split('.')[0])['gRNA']
                return True, {'type': 'copy-grna', 'trigger': trigger_id, 'content': gRNA}

        # If copy cassette button clicked
        if 'copy-cassette-btn' in trigger_id:
            if copy_cassette_clicks and any(copy_cassette_clicks):
                return True, {'type': 'copy-cassette', 'trigger': trigger_id, 'content': cassette}

        return dash.no_update, dash.no_update

    @app.callback(
        Output("download-cassette-fasta", "data"),
        [Input("download-confirm-btn", "n_clicks"),
         Input("pending-download-type", "data")],
        [State("repair-cassette-store", "data"),
         State("repair-strand-store", "data"),
         State('assembly-dropdown-tagging', 'value'),
         State("warning-acknowledged", "data")],
        prevent_initial_call=True
    )
    def download_repair_cassette(confirm_clicks, pending_type, cassette, strand, assembly, warning_acknowledged):
        """Download FASTA after confirmation"""
        if not pending_type or pending_type.get('type') != 'fasta':
            return dash.no_update

        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else ''

        # Only proceed if: confirm button clicked OR (pending type changed AND warning acknowledged)
        if not ('download-confirm-btn' in trigger_id or ('pending-download-type' in trigger_id and warning_acknowledged)):
            return dash.no_update

        # Extract gRNA from the stored trigger
        gRNA = json.loads(pending_type['trigger'].split('.')[0])['gRNA']

        # Apply reverse complement if strand is minus
        cassette_output = cassette
        if strand == 'min' or strand == 'minus':
            cassette_output = reverse_complement(cassette)

        fasta_text = f">{assembly}_{gRNA}\n{cassette_output}\n"

        return dict(
            content=fasta_text,
            filename=f"{assembly}_{gRNA}.fa",
            type="text/plain"
        )

    @app.callback(
        Output("download-cassette-txt", "data"),
        [Input("download-confirm-btn", "n_clicks"),
         Input("pending-download-type", "data")],
        [State("repair-cassette-store", "data"),
         State("repair-strand-store", "data"),
         State('assembly-dropdown-tagging', 'value'),
         State("warning-acknowledged", "data")],
        prevent_initial_call=True
    )
    def download_repair_cassette_txt(confirm_clicks, pending_type, cassette, strand, assembly, warning_acknowledged):
        """Download TXT after confirmation"""
        if not pending_type or pending_type.get('type') != 'txt':
            return dash.no_update

        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else ''

        # Only proceed if: confirm button clicked OR (pending type changed AND warning acknowledged)
        if not ('download-confirm-btn' in trigger_id or ('pending-download-type' in trigger_id and warning_acknowledged)):
            return dash.no_update

        # Extract gRNA from the stored trigger
        gRNA = json.loads(pending_type['trigger'].split('.')[0])['gRNA']

        # Apply reverse complement if strand is minus
        cassette_output = cassette
        if strand == 'min' or strand == 'minus':
            cassette_output = reverse_complement(cassette)

        return dict(
            content=cassette_output,
            filename=f"{assembly}_{gRNA}.txt",
            type="text/plain"
        )

    @app.callback(
        Output("confirmed-clipboard", "content"),
        [Input("download-confirm-btn", "n_clicks"),
         Input("pending-download-type", "data")],
        State("warning-acknowledged", "data"),
        prevent_initial_call=True
    )
    def copy_after_confirmation(confirm_clicks, pending_type, warning_acknowledged):
        """Copy to clipboard after confirmation for copy actions"""
        if not pending_type:
            return dash.no_update

        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else ''

        action_type = pending_type.get('type')

        # Only handle copy actions (not downloads)
        if action_type in ['copy-grna', 'copy-cassette']:
            # If triggered by pending_type change AND warning was already acknowledged, copy immediately
            # OR if triggered by confirm button click
            if 'pending-download-type' in trigger_id and warning_acknowledged:
                return pending_type.get('content', '')
            elif 'download-confirm-btn' in trigger_id:
                return pending_type.get('content', '')

        return dash.no_update

    # === CLIENTSIDE CLIPBOARD WRITE ==========================
    # dcc.Clipboard won't auto-copy when `content` is set server-side, so we
    # use a clientside callback with a textarea fallback that works without
    # requiring a fresh user gesture.
    app.clientside_callback(
        """
        function(content) {
            if (!content || content === '') {
                return window.dash_clientside.no_update;
            }
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(content).catch(function() {
                    var ta = document.createElement('textarea');
                    ta.value = content;
                    ta.style.position = 'fixed';
                    ta.style.opacity = '0';
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    document.body.removeChild(ta);
                });
            } else {
                var ta = document.createElement('textarea');
                ta.value = content;
                ta.style.position = 'fixed';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('copy-dummy-store', 'data'),
        Input('confirmed-clipboard', 'content'),
        prevent_initial_call=True
    )

    # === CLEAR TABLE SELECTION ===============================
    @app.callback(
        Output('gene-grid', 'selectedRows'),
        Input('back-to-full-bar', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_table_selection(n):
        # AG-Grid clears selection when selectedRows = []
        return []

    # === CLICK BLUE SEGMENTS TO GO BACK ======================
    @app.callback(
        Output('selected-grna-index', 'children', allow_duplicate=True),
        Input({'type': 'blue-seg-back', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def blue_segment_back(n_clicks_list):
        if n_clicks_list and any(n and n > 0 for n in n_clicks_list):
            return None
        return dash.no_update

    # =========================================================
    # === CUSTOM SEQUENCE RECALCULATION =======================
    # =========================================================

    @app.callback(
        Output('custom-sequence-validation', 'children'),
        Input('custom-sequence-input', 'value')
    )
    def validate_custom_sequence(sequence):
        """Validate that the input sequence contains only ATCG characters"""
        if not sequence or sequence.strip() == '':
            return ""

        sequence_upper = sequence.upper().strip()
        # Check if sequence contains only ATCG
        if re.match(r'^[ATCG]+$', sequence_upper):
            return html.Div(
                f"\u2713 Valid sequence ({len(sequence_upper)} bp)",
                style={'color': '#10B981', 'fontWeight': '600', 'fontSize': '14px'}
            )
        else:
            invalid_chars = set(re.findall(r'[^ATCG\s]', sequence_upper))
            return html.Div(
                f"\u2717 Invalid characters found: {', '.join(sorted(invalid_chars))}",
                style={'color': '#EF4444', 'fontWeight': '600', 'fontSize': '14px'}
            )

    @app.callback(
        [
            Output('custom-sequence-data-store', 'data'),
            Output('custom-sequence-input', 'value', allow_duplicate=True),
            Output('mutation-loading-trigger', 'children', allow_duplicate=True)
        ],
        [
            Input('recalculate-button', 'n_clicks'),
            Input('reset-sequence-button', 'n_clicks')
        ],
        [
            State('custom-sequence-input', 'value'),
            State('selected-grna-index', 'children'),
            State('full-grna-data', 'children'),
            State('assembly-dropdown-tagging', 'value'),
            State('selected-mode', 'children'),
            State('selected-cell-type', 'children'),
            State('selected-tag-length', 'children')
        ],
        prevent_initial_call=True
    )
    def handle_custom_sequence_calculation(
        recalc_clicks, reset_clicks, sequence, selected_idx,
        full_data_json, assembly, mode, cell_type, tag_length
    ):
        """Handle recalculation with custom sequence or reset to original"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Handle reset
        if button_id == 'reset-sequence-button':
            return None, '', dash.no_update

        # Handle recalculation
        if button_id == 'recalculate-button':
            # Validate inputs
            if not sequence or not sequence.strip():
                return dash.no_update, dash.no_update, dash.no_update

            sequence_upper = sequence.upper().strip()
            if not re.match(r'^[ATCG]+$', sequence_upper):
                return dash.no_update, dash.no_update, dash.no_update

            if not full_data_json or selected_idx is None:
                return dash.no_update, dash.no_update, dash.no_update

            try:
                # Load current data
                full = json.loads(full_data_json)
                df_all = pd.DataFrame(full['data'])

                if 'global_idx' in df_all.columns:
                    df_all = df_all.sort_values('global_idx').reset_index(drop=True)

                # Get zoom data using same logic as main callback
                species = full.get('species', 'Homo sapiens')
                gene_symbol = full.get('selected_gene_symbol', assembly)
                zoom_json = get_zoom_data_cached(assembly, species, mode, cell_type, tag_length, gene_symbol)
                df_zoom = pd.read_json(zoom_json, orient='records')
                if df_zoom.empty or 'integration_score' not in df_zoom.columns:
                    print(f"[CUSTOM RECALC] zoom empty or missing integration_score "
                          f"(len={len(df_zoom)}) for assembly={assembly}, species={species}, mode={mode}")
                    return dash.no_update, dash.no_update, dash.no_update
                df_zoom = df_zoom.sort_values('integration_score', ascending=False).reset_index(drop=True)

                if selected_idx < 0 or selected_idx >= len(df_zoom):
                    print(f"[CUSTOM RECALC] selected_idx {selected_idx} out of range for zoom size {len(df_zoom)}")
                    return dash.no_update, dash.no_update, dash.no_update

                row = df_zoom.iloc[selected_idx]

                # Extract required parameters
                grna_seq = row['gRNA']
                strand = row.get('strand', 'plus')
                location = int(row['location'])
                crispr_score = row.get('CRISPRScan_score')

                # Determine microhomology length from tag_length
                microhomology_length = 3 if tag_length == '3bp' else 6

                # Recalculate using the custom sequence
                print(f"\n{'='*80}")
                print(f"RECALCULATING for assembly {assembly}, gRNA {grna_seq}")
                print(f"{'='*80}")
                if mode == "Intron":
                    result_df = recalculate_intron(
                        gene_id=assembly,
                        grna_seq=grna_seq,
                        strand=strand,
                        location=location,
                        tag_sequence=sequence_upper,
                        crispr_scan_score=crispr_score,
                        celltype=cell_type,
                        microhomology_length=microhomology_length,
                        transcript_db_path=get_transcript_db_path(species),
                        debug=True
                    )
                else:
                    result_df = recalculate_grna(
                        gene_id=assembly,
                        grna_seq=grna_seq,
                        strand=strand,
                        location=location,
                        tag_sequence=sequence_upper,
                        crispr_scan_score=crispr_score,
                        celltype=cell_type,
                        microhomology_length=microhomology_length,
                        transcript_db_path=get_transcript_db_path(species),
                        debug=True  # Enable debug output
                    )
                print(f"{'='*80}\n")

                if result_df.empty:
                    print(f"[CUSTOM RECALC] result_df empty for assembly={assembly}, gRNA={grna_seq}")
                    return dash.no_update, dash.no_update, dash.no_update

                # Store the recalculated data
                custom_data = {
                    'selected_idx': selected_idx,
                    'custom_sequence': sequence_upper,
                    'result': result_df.to_dict('records')[0],
                    'gene': assembly,
                    'mode': mode,
                    'cell_type': cell_type
                }

                return custom_data, sequence, None

            except Exception as e:
                print(f"Error recalculating with custom sequence: {e}")
                import traceback
                traceback.print_exc()
                return dash.no_update, dash.no_update, dash.no_update

        return dash.no_update, dash.no_update, dash.no_update

    # =========================================================
    # === PRESET AUTO-FILL CALLBACKS ==========================
    # =========================================================

    @app.callback(
        Output('preset-sequence-info', 'children'),
        [
            Input('linker-dropdown', 'value'),
            Input('tag-dropdown', 'value'),
            Input({'type': 'component-value', 'index': ALL, 'subtype': ALL}, 'value')
        ],
        [
            State({'type': 'component-type', 'index': ALL}, 'value')
        ]
    )
    def display_preset_sequence_info(linker_name, tag_name, additional_values, additional_types):
        """Display information about the combined sequence"""
        if not linker_name or not tag_name:
            return ""

        # Find linker and tag sequences
        linker_seq = None
        tag_seq = None
        linker_color = "#8B4513"
        tag_color = "#10B981"

        for linker in TAG_PRESETS.get('linkers', []):
            if linker['name'] == linker_name:
                linker_seq = linker['sequence']
                linker_color = linker.get('color', linker_color)
                break

        for tag in TAG_PRESETS.get('tags', []):
            if tag['name'] == tag_name:
                tag_seq = tag['sequence']
                tag_color = tag.get('color', tag_color)
                break

        if not linker_seq or not tag_seq:
            return ""

        # Build list of all components in order
        components = []
        components.append({
            'name': linker_name,
            'sequence': linker_seq,
            'color': linker_color,
            'type': 'Linker'
        })
        components.append({
            'name': tag_name,
            'sequence': tag_seq,
            'color': tag_color,
            'type': 'Tag'
        })

        # Add additional components
        for i, value in enumerate(additional_values):
            if value and i < len(additional_types) and additional_types[i]:
                comp_type = additional_types[i]
                comp_seq = None
                comp_color = "#8B4513" if comp_type == "linker" else "#10B981"

                # Find the sequence
                search_list = TAG_PRESETS.get('linkers', []) if comp_type == "linker" else TAG_PRESETS.get('tags', [])
                for item in search_list:
                    if item['name'] == value:
                        comp_seq = item['sequence']
                        comp_color = item.get('color', comp_color)
                        break

                if comp_seq:
                    components.append({
                        'name': value,
                        'sequence': comp_seq,
                        'color': comp_color,
                        'type': comp_type
                    })

        # Calculate combined sequence
        combined_seq = ''.join([c['sequence'] for c in components])
        combined_length = len(combined_seq)

        # Build component badges
        component_badges = []
        for comp in components:
            component_badges.append(
                html.Span(
                    f"{comp['type']}: {len(comp['sequence'])} bp",
                    style={
                        'backgroundColor': comp['color'],
                        'color': 'white',
                        'padding': '4px 8px',
                        'borderRadius': '4px',
                        'marginRight': '10px',
                        'marginBottom': '6px',
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'display': 'inline-block'
                    }
                )
            )

        return html.Div([
            html.Div(
                f"Combined Sequence Length: {combined_length} bp",
                style={
                    'fontWeight': '600',
                    'marginBottom': '8px',
                    'color': 'var(--text-primary)'
                }
            ),
            html.Div(
                component_badges,
                style={'display': 'flex', 'flexWrap': 'wrap'}
            )
        ], style={
            'padding': '12px',
            'backgroundColor': '#F3F4F6',
            'borderRadius': '6px',
            'border': '1px solid #E5E7EB'
        })

    # Callback to add additional components
    @app.callback(
        [Output('additional-components-container', 'children'),
         Output('component-counter', 'data')],
        [Input('add-component-button', 'n_clicks'),
         Input({'type': 'remove-component', 'index': ALL}, 'n_clicks')],
        [State('additional-components-container', 'children'),
         State('component-counter', 'data')],
        prevent_initial_call=True
    )
    def manage_components(add_clicks, remove_clicks, current_children, counter):
        """Add or remove additional linker/tag components"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_children, counter

        trigger_id = ctx.triggered[0]['prop_id']

        # Handle remove button clicks
        if 'remove-component' in trigger_id:
            # Find which component to remove
            import json
            trigger_dict = json.loads(trigger_id.split('.')[0])
            remove_idx = trigger_dict['index']

            # Remove the component with matching index
            updated_children = [
                child for child in current_children
                if child['props']['id'] != f'component-{remove_idx}'
            ]
            return updated_children, counter

        # Handle add button click
        if 'add-component-button' in trigger_id and add_clicks:
            new_component = html.Div(
                id=f'component-{counter}',
                style={'marginBottom': '20px', 'padding': '15px', 'backgroundColor': '#F9FAFB', 'borderRadius': '6px', 'border': '1px solid #E5E7EB'},
                children=[
                    html.Div([
                        html.Label(
                            f"Additional Element {counter + 1}:",
                            style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block', 'color': 'var(--text-primary)'}
                        ),
                        dcc.Dropdown(
                            id={'type': 'component-type', 'index': counter},
                            options=[
                                {'label': 'Linker', 'value': 'linker'},
                                {'label': 'Tag', 'value': 'tag'}
                            ],
                            placeholder='Select type...',
                            searchable=False,
                            style={'marginBottom': '12px'}
                        ),
                    ]),
                    html.Div(id={'type': 'component-dropdown-container', 'index': counter}),
                    html.Button(
                        '\u00d7 Remove',
                        id={'type': 'remove-component', 'index': counter},
                        n_clicks=0,
                        style={
                            'padding': '6px 12px',
                            'backgroundColor': '#EF4444',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'marginTop': '8px'
                        }
                    )
                ]
            )

            updated_children = current_children + [new_component]
            return updated_children, counter + 1

        return current_children, counter

    # Callback to populate component dropdown based on type selection
    @app.callback(
        Output({'type': 'component-dropdown-container', 'index': MATCH}, 'children'),
        Input({'type': 'component-type', 'index': MATCH}, 'value'),
        State({'type': 'component-type', 'index': MATCH}, 'id'),
        prevent_initial_call=True
    )
    def populate_component_dropdown(component_type, triggered_id):
        """Show appropriate dropdown based on component type selection"""
        if not component_type:
            return None

        # Extract the actual index from the triggered id
        index = triggered_id['index']

        if component_type == 'linker':
            return dcc.Dropdown(
                id={'type': 'component-value', 'index': index, 'subtype': 'linker'},
                options=[
                    {'label': f"{l['name']} ({l['description']})", 'value': l['name']}
                    for l in TAG_PRESETS.get('linkers', [])
                ],
                placeholder='Select a linker...',
                searchable=False
            )
        elif component_type == 'tag':
            return dcc.Dropdown(
                id={'type': 'component-value', 'index': index, 'subtype': 'tag'},
                options=[
                    {'label': f"{t['name']} ({t['description']})", 'value': t['name']}
                    for t in TAG_PRESETS.get('tags', [])
                ],
                placeholder='Select a tag...',
                searchable=False
            )

        return None

    # Callback to handle custom tab switching
    @app.callback(
        [
            Output('custom-tab-content', 'style'),
            Output('presets-tab-content', 'style'),
            Output('tab-custom-button', 'style'),
            Output('tab-presets-button', 'style'),
            Output('active-tab-store', 'data')
        ],
        [
            Input('tab-custom-button', 'n_clicks'),
            Input('tab-presets-button', 'n_clicks')
        ],
        State('active-tab-store', 'data'),
        prevent_initial_call=True
    )
    def switch_custom_tabs(custom_clicks, presets_clicks, current_tab):
        """Handle switching between custom and presets tabs"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'tab-custom-button':
            return (
                {'display': 'block'},  # custom content visible
                {'display': 'none'},   # presets content hidden
                {'flex': '1', 'padding': '10px', 'backgroundColor': '#3B82F6', 'color': 'white',
                 'border': 'none', 'borderRadius': '4px 0 0 0', 'fontWeight': '600',
                 'cursor': 'pointer', 'fontSize': '14px'},  # custom button active
                {'flex': '1', 'padding': '10px', 'backgroundColor': '#9CA3AF', 'color': 'white',
                 'border': 'none', 'borderRadius': '0 4px 0 0', 'fontWeight': '600',
                 'cursor': 'pointer', 'fontSize': '14px'},  # presets button inactive
                'custom'
            )
        else:  # presets button clicked
            return (
                {'display': 'none'},   # custom content hidden
                {'display': 'block'},  # presets content visible
                {'flex': '1', 'padding': '10px', 'backgroundColor': '#9CA3AF', 'color': 'white',
                 'border': 'none', 'borderRadius': '4px 0 0 0', 'fontWeight': '600',
                 'cursor': 'pointer', 'fontSize': '14px'},  # custom button inactive
                {'flex': '1', 'padding': '10px', 'backgroundColor': '#3B82F6', 'color': 'white',
                 'border': 'none', 'borderRadius': '0 4px 0 0', 'fontWeight': '600',
                 'cursor': 'pointer', 'fontSize': '14px'},  # presets button active
                'presets'
            )

    @app.callback(
        [
            Output('custom-sequence-data-store', 'data', allow_duplicate=True),
            Output('mutation-loading-trigger', 'children', allow_duplicate=True),
            Output('preset-loading-output', 'children', allow_duplicate=True)
        ],
        Input('recalculate-preset-button', 'n_clicks'),
        [
            State('linker-dropdown', 'value'),
            State('tag-dropdown', 'value'),
            State({'type': 'component-value', 'index': ALL, 'subtype': ALL}, 'value'),
            State({'type': 'component-type', 'index': ALL}, 'value'),
            State('selected-grna-index', 'children'),
            State('full-grna-data', 'children'),
            State('assembly-dropdown-tagging', 'value'),
            State('selected-mode', 'children'),
            State('selected-cell-type', 'children'),
            State('selected-tag-length', 'children')
        ],
        prevent_initial_call=True
    )
    def handle_preset_recalculation(
        n_clicks, linker_name, tag_name, additional_values, additional_types,
        selected_idx, full_data_json, assembly, mode, cell_type, tag_length
    ):
        """Handle recalculation with preset linker + tag combination"""
        if not n_clicks or n_clicks == 0:
            return dash.no_update, dash.no_update, dash.no_update

        # Validate inputs
        if not linker_name or not tag_name:
            return dash.no_update, dash.no_update, dash.no_update

        if not full_data_json or selected_idx is None:
            return dash.no_update, dash.no_update, dash.no_update

        # Find linker and tag sequences
        linker_seq = None
        tag_seq = None

        for linker in TAG_PRESETS.get('linkers', []):
            if linker['name'] == linker_name:
                linker_seq = linker['sequence']
                break

        for tag in TAG_PRESETS.get('tags', []):
            if tag['name'] == tag_name:
                tag_seq = tag['sequence']
                break

        if not linker_seq or not tag_seq:
            return dash.no_update, dash.no_update, dash.no_update

        # Combine sequences - start with linker + tag
        combined_sequence = linker_seq + tag_seq

        # Add additional component sequences
        component_names = [linker_name, tag_name]
        for i, value in enumerate(additional_values):
            if value and i < len(additional_types) and additional_types[i]:
                comp_type = additional_types[i]
                comp_seq = None

                # Find the sequence
                search_list = TAG_PRESETS.get('linkers', []) if comp_type == "linker" else TAG_PRESETS.get('tags', [])
                for item in search_list:
                    if item['name'] == value:
                        comp_seq = item['sequence']
                        break

                if comp_seq:
                    combined_sequence += comp_seq
                    component_names.append(value)

        try:
            # Load current data - same logic as custom sequence callback
            full = json.loads(full_data_json)
            df_all = pd.DataFrame(full['data'])

            if 'global_idx' in df_all.columns:
                df_all = df_all.sort_values('global_idx').reset_index(drop=True)

            # Get zoom data using same logic as main callback
            species = full.get('species', 'Homo sapiens')
            gene_symbol = full.get('selected_gene_symbol', assembly)
            zoom_json = get_zoom_data_cached(assembly, species, mode, cell_type, tag_length, gene_symbol)
            df_zoom = pd.read_json(zoom_json, orient='records')
            df_zoom = df_zoom.sort_values('integration_score', ascending=False).reset_index(drop=True)

            if selected_idx < 0 or selected_idx >= len(df_zoom):
                return dash.no_update, dash.no_update, dash.no_update

            row = df_zoom.iloc[selected_idx]

            # Extract required parameters
            grna_seq = row['gRNA']
            strand = row.get('strand', 'plus')
            location = int(row['location'])
            crispr_score = row.get('CRISPRScan_score')

            # Determine microhomology length from tag_length
            microhomology_length = 3 if tag_length == '3bp' else 6

            # Recalculate using the preset sequence
            print(f"\n{'='*80}")
            print(f"RECALCULATING WITH PRESET: {linker_name} + {tag_name}")
            print(f"Combined sequence length: {len(combined_sequence)} bp")
            print(f"Assembly: {assembly}, gRNA: {grna_seq}")
            print(f"{'='*80}")

            if mode == "Intron":
                result_df = recalculate_intron(
                    gene_id=assembly,
                    grna_seq=grna_seq,
                    strand=strand,
                    location=location,
                    tag_sequence=combined_sequence,
                    crispr_scan_score=crispr_score,
                    celltype=cell_type,
                    microhomology_length=microhomology_length,
                    transcript_db_path=get_transcript_db_path(species),
                    debug=True
                )
            else:
                result_df = recalculate_grna(
                    gene_id=assembly,
                    grna_seq=grna_seq,
                    strand=strand,
                    location=location,
                    tag_sequence=combined_sequence,
                    crispr_scan_score=crispr_score,
                    celltype=cell_type,
                    microhomology_length=microhomology_length,
                    transcript_db_path=get_transcript_db_path(species),
                    debug=True
                )
            print(f"{'='*80}\n")

            if result_df.empty:
                return dash.no_update, dash.no_update, dash.no_update

            # Store the recalculated data
            custom_data = {
                'selected_idx': selected_idx,
                'custom_sequence': combined_sequence,
                'result': result_df.to_dict('records')[0],
                'gene': assembly,
                'mode': mode,
                'cell_type': cell_type,
                'preset_info': {
                    'linker': linker_name,
                    'tag': tag_name,
                    'all_components': component_names
                }
            }

            return custom_data, None, None

        except Exception as e:
            print(f"Error recalculating with preset: {e}")
            import traceback
            traceback.print_exc()
            return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output('custom-sequence-data-store', 'data', allow_duplicate=True),
        [
            Input('assembly-dropdown-tagging', 'value'),
            Input('selected-mode', 'children'),
            Input('selected-cell-type', 'children')
        ],
        prevent_initial_call=True
    )
    def clear_custom_sequence_on_change(assembly, mode, cell_type):
        """Clear custom sequence data when assembly or database settings change"""
        return None
