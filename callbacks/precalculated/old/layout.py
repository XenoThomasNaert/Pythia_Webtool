import json

from dash import dcc, html
import dash_bootstrap_components as dbc
from .panels import build_readme_panel


page_tagging_precalculated_layout = html.Div([
    html.H1('Pythia Tagging', style={"marginTop": "0.5em", "marginBottom": "1.2em", "paddingBottom": "0.2em", "textAlign": "center"}),



    # Parameter bar (not sticky anymore)
    html.Div([
        # Left side - Tag type and length buttons
        html.Div([
            dbc.Button("Intron", id="tag-intron", n_clicks=0, color="primary", outline=True, size="sm"),
            dbc.Button("Exon 3bp", id="tag-exon-3bp", n_clicks=0, color="primary", outline=False, size="sm"),
            dbc.Button("Exon 6bp", id="tag-exon-6bp", n_clicks=0, color="primary", outline=True, size="sm"),
        ], className='mode-selection-panel'),

        # Separator
        html.Div(className='param-separator'),

        # Species Dropdown

            dcc.Dropdown(
                id='species-dropdown',
                className='gene-dropdown-custom',
                options=[
                    {'label': 'Homo sapiens', 'value': 'Homo sapiens'},
                    {'label': 'Xenopus tropicalis', 'value': 'Xenopus tropicalis'},
                    {'label': 'Mus musculus', 'value': 'Mus musculus'}
                ],
                value='Homo sapiens',
                clearable=False,
            )
        ,

        # Cell Type Dropdown
        html.Div([
            html.Span([
                html.Span('ⓘ', style={'color': '#3B82F6', 'cursor': 'help', 'fontSize': '0.95rem', 'fontWeight': 'bold', 'marginRight': '6px'}),
                html.Span([
                    html.Div("Choosing an inDelphi model", style={'fontWeight': '700', 'marginBottom': '8px', 'fontSize': '0.85rem', 'color': '#93C5FD'}),
                    html.Div("inDelphi was trained on five cell types: mESC, HEK293, U2OS, HCT116, and K562. Repair outcome preferences are cell-type-specific, and predictive performance can vary when the model is applied outside its training distribution.", style={'fontSize': '0.75rem', 'color': '#D1D5DB', 'marginBottom': '10px', 'lineHeight': '1.5'}),
                    html.Div([html.Span("✓ ", style={'color': '#6EE7B7'}), "If your cell type is in the training panel, select the matching model."], style={'marginBottom': '5px', 'fontSize': '0.75rem', 'lineHeight': '1.4'}),
                    html.Div([html.Span("✓ ", style={'color': '#6EE7B7'}), ["If your cell type is independently validated for a specific model, use that combination. The mESC model has been validated for early Xenopus and zebrafish embryos in our hands (Naert et al., ", html.Em("Sci Rep"), " 2020). For zebrafish specifically, Lin et al. (", html.Em("NAR"), " 2025) benchmarked inDelphi alongside Lindel and FORECasT in a large-scale F0 crispant screen and found all three useful, with some variation between tools. Note that these benchmarks address indel-outcome prediction at the DSB, whereas Pythia extends such predictions to the full genome\u2013transgene junction to guide integration design \u2014 a related but distinct task, and currently supported only by inDelphi within Pythia."]], style={'marginBottom': '8px', 'fontSize': '0.75rem', 'lineHeight': '1.4'}),
                    html.Div([html.Span("→ ", style={'color': '#FCD34D'}), "For other contexts (primary cells, iPSCs, patient-derived lines, other cancer lines, non-mammalian systems): MMEJ is broadly conserved, and Pythia-guided designs generally transfer reasonably well across mammalian cell types. Pick the model from the training panel that most plausibly resembles your system — if unsure, mESC and HEK293 are sensible defaults given their broad use in benchmarking. Predictions should be treated as strong guides rather than exact forecasts, and confirming performance at a small number of loci is good practice before scaling up. Comparing outputs across models can also help identify robust designs."], style={'marginBottom': '8px', 'fontSize': '0.75rem', 'lineHeight': '1.4'}),
                    html.Div([html.Span("✗ Not recommended: ", style={'color': '#FCA5A5', 'fontWeight': '600'}), "cells with compromised MMEJ machinery (e.g., POLQ-knockout or Pol θ–deficient backgrounds). The microhomology-driven repair outcomes Pythia exploits are substantially reduced in these contexts, and predictions are unlikely to be informative."], style={'fontSize': '0.75rem', 'color': '#D1D5DB', 'marginBottom': '6px', 'lineHeight': '1.4', 'borderTop': '1px solid #374151', 'paddingTop': '8px'}),
                    html.Div([html.Span("Note on iPSCs: ", style={'fontWeight': '600', 'color': '#FCD34D'}), ["hiPSCs have been reported to show higher MMEJ usage than inDelphi predicts (Grajcarek et al., ", html.Em("Nat Commun"), " 2019). Empirical validation is especially advisable here."]], style={'fontSize': '0.75rem', 'color': '#D1D5DB', 'lineHeight': '1.4'}),
                ], className='tooltip-text',
                   style={'visibility': 'hidden', 'width': '380px', 'backgroundColor': '#1F2937', 'color': '#fff',
                          'textAlign': 'left', 'borderRadius': '6px', 'padding': '12px', 'position': 'absolute',
                          'zIndex': '1000', 'bottom': '125%', 'left': '0', 'fontSize': '0.82rem', 'lineHeight': '1.4',
                          'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'})
            ], className='tooltip-container', style={'position': 'relative', 'display': 'inline-block', 'verticalAlign': 'middle'}),
            dcc.Dropdown(
                id='cell-type-dropdown',
                className='gene-dropdown-custom',
                options=[
                    {'label': 'HEK293', 'value': 'HEK293'},
                    {'label': 'mESC', 'value': 'mESC'}
                ],
                value='HEK293',
                clearable=False,
                style={'display': 'inline-block', 'verticalAlign': 'middle', 'minWidth': '120px'}
            ),
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '4px'}),

        dcc.Store(id="repair-cassette-store"),
        dcc.Store(id="repair-left-arm-store"),
        dcc.Store(id="repair-right-arm-store"),
        dcc.Store(id="repair-strand-store"),
        dcc.Store(id="custom-sequence-data-store"),

        dcc.Download(id="download-cassette-fasta"),
        dcc.Download(id="download-cassette-txt"),

        # Download confirmation modal
        dbc.Modal([
            dbc.ModalHeader("Important Warning: Off-Target Considerations"),
            dbc.ModalBody([
                html.H5("Important: Off-Target Analysis Required", style={'marginBottom': '15px'}),
                html.P([
                    "Each gRNA shown here has passed an initial screening – we've confirmed there's only one perfect match in the genome followed by an NGG PAM site."
                ], style={'marginBottom': '15px'}),
                html.H6("What you need to know:", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.P([
                    "CRISPR can sometimes bind to similar (but not perfect) sequences in the genome. Checking for these potential off-target sites across all possible mismatches is extremely computation-heavy, so we haven't pre-calculated this for every gRNA in our database."
                ], style={'marginBottom': '15px'}),
                html.H6("Quick next step (takes ~1 minute):", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.P([
                    "Before using your chosen gRNA, please run it through ",
                    html.A("Cas-OFFinder", href="http://www.rgenome.net/cas-offinder/", target="_blank", style={'textDecoration': 'underline'}),
                    " or equivalent tool:"
                ], style={'marginBottom': '10px'}),
                html.Ul([
                    html.Li("Visit the website and follow their simple instructions"),
                    html.Li("Confirm your gRNA has minimal off-target matches"),
                    html.Li("Results typically appear in under a minute")
                ], style={'marginBottom': '15px'}),
                html.H6("Why this approach works better:", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.P([
                    "Rather than us spending months computing off-target profiles for millions of gRNAs (most of which you won't use), you can get comprehensive results for your chosen gRNA in seconds externally. This gives you the thorough analysis you need, exactly when you need it."
                ])
            ]),
            dbc.ModalFooter([
                dcc.Checklist(
                    id="dont-show-again-checkbox",
                    options=[{"label": " Don't show this warning again for this session", "value": "hide"}],
                    value=[],
                    style={'marginRight': 'auto', 'fontSize': '14px'}
                ),
                dbc.Button("I Understand", id="download-confirm-btn", n_clicks=0)
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], id="download-modal", is_open=False, size="lg"),

        # Store to track which download/copy was requested
        dcc.Store(id="pending-download-type"),

        # Store to track if user has acknowledged the warning
        dcc.Store(id="warning-acknowledged", storage_type='memory', data=False),

        # Hidden clipboard for confirmed copies
        dcc.Clipboard(id="confirmed-clipboard", style={'display': 'none'}),

        # Dummy store used as output for the clientside clipboard callback
        dcc.Store(id="copy-dummy-store"),

        # Gene name dropdown (first search bar)
        dcc.Loading(
            type='circle',
            color='#2E5BFF',
            parent_style={'minHeight': '38px'},
            children=dcc.Dropdown(
                id='gene-dropdown-tagging',
                placeholder='Type to search genes...',
                className='gene-dropdown-custom',
                options=[],  # Will be populated by callback
                searchable=True,
                clearable=False,  # Disable clear button to prevent bugs
                optionHeight=35,
                maxHeight=400,
            ),
        ),

        # Assembly/transcript dropdown (second search bar)
        dcc.Loading(
            type='circle',
            color='#2E5BFF',
            parent_style={'minHeight': '38px'},
            children=dcc.Dropdown(
                id='assembly-dropdown-tagging',
                placeholder='Select assembly...',
                className='transcript-dropdown-custom',
                options=[],  # Will be populated when gene is selected
                searchable=True,
                clearable=False,
                optionHeight=35,
                maxHeight=400,
            ),
        ),

    ], className='custom-parameter-bar'),

    # Sticky bar host + all scrollable content in one wrapper so sticky holds through the table
    html.Div([
        html.Div(
            id='tagging-bar-host',
            children=[
                html.Div(
                    html.P(
                        "Select a gRNA from the table below to view its tagging design",
                        style={'margin': '0', 'color': '#6B7280', 'fontSize': '0.9em',
                               'textAlign': 'center', 'padding': '12px 0'}
                    ),
                    className="tagging-bar-sticky"
                )
            ]
        ),

        dcc.Loading(
            id='mutation-detail-loading',
            type='circle',
            parent_style={'minHeight': '0'},
            children=html.Div(
                id='mutation-detail-container',
                style={'marginBottom': '0.5em'}
            )
        ),

        # Hidden trigger div — keeps existing callback outputs working
        html.Div(id='mutation-loading-trigger', style={'display': 'none'}),

        # Container for temporary auto-tooltip
        html.Div(id="auto-tooltip-container"),

        # Results table container wrapped in dcc.Loading — only fires on
        # gene-table-container updates (assembly dropdown change), which has
        # no fast-callback descendants that would cause over-triggering.
        dcc.Loading(
            id='gene-table-loading',
            type='circle',
            parent_style={'minHeight': '200px'},
            children=html.Div(
                [
                    html.Div(
                        id='gene-table-container',
                        style={
                            'padding': '0',
                            'flex': '1 1 100%',
                            'backgroundColor': 'transparent',
                            'border': 'none',
                            'boxShadow': 'none'
                        },
                        children=[
                            # Ensure full-grna-data exists in the layout at all times
                            html.Div(
                                id='full-grna-data',
                                style={'display': 'none'},
                                children=json.dumps({
                                    'data': [],
                                    'sequence_length': 0,
                                    'selected_gene': '',
                                    'species': ''
                                })
                            ),
                            build_readme_panel()
                        ]
                    )
                ],
                style={
                    'display': 'flex',
                    'gap': '20px',
                    'alignItems': 'stretch',
                    'marginTop': '5px',
                    'marginBottom': '2em',
                    'width': '100%'
                }
            )
        ),

    ]),  # end of sticky-bar outer wrapper

    # Hidden divs to store selected values
    html.Div(id='selected-mode', style={'display': 'none'}, children='Exon'),
    html.Div(id='selected-tag-length', style={'display': 'none'}, children='3bp'),
    html.Div(id='selected-cell-type', style={'display': 'none'}, children='HEK293'),
    html.Div(id='selected-grna-index', style={'display': 'none'}, children=None),

    # Hidden div to store recent gene search history (JSON list)
    html.Div(id='recent-genes-store', style={'display': 'none'}, children=json.dumps([])),

], className="tagging-page",
style={"minHeight": "100vh"})
