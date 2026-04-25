import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from connection_helper import get_optimized_connection

from utils.validation import validate_sequence_chars
from pythia_integration_gRNA_finder import process_pythia_integration_with_gRNA
from utils.tooltips import indelphi_model_tooltip

# ===================================================================
# CUSTOM TAGGING PAGE LAYOUT
# ===================================================================

page_tagging_custom_layout = html.Div([
    html.H1('Pythia Custom Tagging', style={"marginTop": "0.5em", "marginBottom": "0.5em", "paddingBottom": "0.2em", "textAlign": "center"}),
    html.P('Create N-terminal or C-terminal fluorescent or epitope tags on endogenous proteins with optimized reading frame preservation.',
           style={"textAlign": "center", "color": "#6B7280", "fontSize": "1.1rem", "marginBottom": "2em", "maxWidth": "800px", "margin": "0 auto 2em auto"}),

    # Step 1: Model Selection Card
    html.Div([
        html.Div([
            html.Div([
                html.H3('Step 1: Select inDelphi Model', className='step-title',
                        style={'display': 'inline', 'margin': 0}),
                indelphi_model_tooltip(),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.P('Choose the appropriate cell type model for your experiment', className='step-description')
        ], className='step-header'),
        html.Div([
            dcc.Dropdown(
                id='dropdown-menu-tagging',
                options=[
                    {'label': 'mESC', 'value': 'mESC'},
                    {'label': 'HEK293', 'value': 'HEK293'},
                    {'label': 'U2OS', 'value': 'U2OS'},
                    {'label': 'HCT116', 'value': 'HCT116'},
                    {'label': 'K562', 'value': 'K562'}
                ],
                value='HEK293',
                searchable=False,
                clearable=False,
                style={'width': '100%'}
            )
        ], className='step-content')
    ], className='step-card'),

    # Step 2: Tagging Type Selection Card
    html.Div([
        html.Div([
            html.H3('Step 2: Choose Tagging Type', className='step-title'),
            html.P('Select whether you need 5\' or 3\' tagging', className='step-description')
        ], className='step-header'),
        html.Div([
            html.Div([
                html.Button('5\' Tagging (N-terminal)',
                           id='choice-5prime-tagging',
                           n_clicks=0,
                           className='workflow-button',
                           style={
                               'width': '48%',
                               'padding': '1.5rem 2rem',
                               'backgroundColor': '#FFFFFF',
                               'border': '3px solid #2E5BFF',
                               'borderRadius': '0.75rem',
                               'cursor': 'pointer',
                               'fontSize': '1rem',
                               'fontWeight': '600',
                               'color': '#2E5BFF',
                               'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                               'transition': 'all 250ms ease-in-out',
                               'textAlign': 'center',
                               'whiteSpace': 'normal',
                               'minHeight': '80px',
                               'display': 'flex',
                               'alignItems': 'center',
                               'justifyContent': 'center',
                               'position': 'relative'
                           }),
                html.Button('3\' Tagging (C-terminal)',
                           id='choice-3prime-tagging',
                           n_clicks=0,
                           className='workflow-button',
                           style={
                               'width': '48%',
                               'padding': '1.5rem 2rem',
                               'backgroundColor': '#FFFFFF',
                               'border': '3px solid #2E5BFF',
                               'borderRadius': '0.75rem',
                               'cursor': 'pointer',
                               'fontSize': '1rem',
                               'fontWeight': '600',
                               'color': '#2E5BFF',
                               'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                               'transition': 'all 250ms ease-in-out',
                               'textAlign': 'center',
                               'whiteSpace': 'normal',
                               'minHeight': '80px',
                               'display': 'flex',
                               'alignItems': 'center',
                               'justifyContent': 'center',
                               'position': 'relative'
                           })
            ], style={'display': 'flex', 'gap': '1rem', 'marginBottom': '2rem'}),

            # Tagging input section (initially hidden, shown when either button is clicked)
            html.Div(id='tagging-input-section', children=[

                # === Gene Lookup panel ===
                html.Div([
                    html.P([
                        '🔍 Auto-fill from database: select a species, gene, and transcript to automatically populate the target and context sequences below.',
                        html.Span(' ?', id='autofill-tooltip-anchor', style={
                            'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center',
                            'width': '16px', 'height': '16px',
                            'backgroundColor': '#92400E', 'color': '#FEF3C7',
                            'borderRadius': '50%', 'fontSize': '11px', 'fontWeight': '700',
                            'cursor': 'help', 'marginLeft': '6px',
                            'verticalAlign': 'middle', 'lineHeight': '1',
                            'flexShrink': '0',
                        }),
                        dbc.Tooltip(
                            'Note: the sequence extracted is not always the strict "first exon" — it is the exon that contains the first coding sequence (CDS). For some transcripts this may be a downstream exon if the initial exons are non-coding (5′ UTR only).',
                            target='autofill-tooltip-anchor',
                            placement='right',
                            style={'fontSize': '0.82rem', 'maxWidth': '320px'},
                        ),
                    ],
                        style={
                            'fontSize': '0.875rem', 'color': '#92400E', 'fontWeight': '600',
                            'margin': '0 0 0.75rem 0', 'padding': '10px 16px',
                            'backgroundColor': '#FEF3C7', 'border': '2px solid #F59E0B',
                            'borderRadius': '8px',
                        }
                    ),
                    html.Div([
                        html.Div([
                            html.Label('Database', style={'fontSize': '0.75rem', 'fontWeight': '600',
                                'color': '#6B7280', 'marginBottom': '3px', 'display': 'block'}),
                            dcc.Dropdown(
                                id='custom-tagging-species',
                                className='gene-dropdown-custom',
                                options=[
                                    {'label': 'Homo sapiens', 'value': 'Homo sapiens'},
                                    {'label': 'Xenopus tropicalis', 'value': 'Xenopus tropicalis'},
                                    {'label': 'Mus musculus', 'value': 'Mus musculus'},
                                ],
                                value='Homo sapiens',
                                clearable=False,
                            ),
                        ]),
                        html.Div([
                            html.Label('Gene', style={'fontSize': '0.75rem', 'fontWeight': '600',
                                'color': '#6B7280', 'marginBottom': '3px', 'display': 'block'}),
                            dcc.Loading(
                                type='circle',
                                color='#2E5BFF',
                                parent_style={'minHeight': '38px'},
                                children=dcc.Dropdown(
                                    id='custom-tagging-gene',
                                    placeholder='Type to search genes...',
                                    className='gene-dropdown-custom',
                                    options=[],
                                    searchable=True,
                                    clearable=False,
                                    optionHeight=35,
                                    maxHeight=400,
                                ),
                            ),
                        ]),
                        html.Div([
                            html.Label('Transcript', style={'fontSize': '0.75rem', 'fontWeight': '600',
                                'color': '#6B7280', 'marginBottom': '3px', 'display': 'block'}),
                            dcc.Loading(
                                type='circle',
                                color='#2E5BFF',
                                parent_style={'minHeight': '38px'},
                                children=dcc.Dropdown(
                                    id='custom-tagging-transcript',
                                    placeholder='Select a gene first...',
                                    className='transcript-dropdown-custom',
                                    options=[],
                                    searchable=True,
                                    clearable=False,
                                    optionHeight=35,
                                    maxHeight=400,
                                ),
                            ),
                        ]),
                    ], className='custom-parameter-bar', style={'marginBottom': '0', 'alignItems': 'flex-end'}),
                    dcc.Loading(
                        type='circle',
                        parent_style={'minHeight': '0'},
                        children=html.Div(id='custom-tagging-fill-indicator',
                                          style={'fontSize': '0.8rem', 'color': '#6B7280',
                                                 'marginTop': '0.4rem', 'minHeight': '1.2rem'}),
                    ),
                ], style={'marginBottom': '1.5rem'}),

                html.H4('Genomic Target', style={'marginBottom': '1rem', 'color': 'var(--primary-color)'}),
                html.Label(id='tagging-target-label', children='Genomic target site where you wish to tag:', style={'fontWeight': '600', 'marginBottom': '0.5em', 'display': 'block'}),
                html.Div(id='codon-warning-message', children=[], style={'marginBottom': '0.5rem'}),
                html.Div([
                    dcc.Input(
                        id='input-box-tagging-target',
                        type='text',
                        placeholder='Enter your genomic sequence for tagging',
                        className='sequence-input',
                        style={'width': '100%'}
                    )
                ], className='input-with-examples'),
                html.Label('Genomic context around the target site:', style={'fontWeight': '600', 'marginTop': '1.5rem', 'marginBottom': '0.5em', 'display': 'block'}),
                html.P([
                    'Provide 50 bp of flanking sequence on each side (100 bp total around your target) ',
                    html.Span('(Include 50 bp upstream + your target sequence + 50 bp downstream)',
                              style={'fontStyle': 'italic', 'color': '#6B7280'}),
                    ' ',
                    html.Span([
                        html.Span('ⓘ', style={'color': '#3B82F6', 'cursor': 'help', 'fontSize': '1rem', 'fontWeight': 'bold'}),
                        html.Span('Why? CRITICAL STEP: The extended flanking context is required for accurate InDelphi predictions and microhomology identification. The deep learning algorithm requires genomic sequence both upstream and downstream of the integration site to properly evaluate microhomology opportunities and predict repair outcomes. The complete sequence in this box should be structured as: [50 bp upstream genomic sequence] - [Your target site (from box above)] - [50 bp downstream genomic sequence]. Without sufficient flanking sequence, the algorithm cannot properly assess repair efficiency and may truncate predictions at the sequence boundaries.',
                                  style={
                                      'visibility': 'hidden',
                                      'width': '400px',
                                      'backgroundColor': '#1F2937',
                                      'color': '#fff',
                                      'textAlign': 'left',
                                      'borderRadius': '6px',
                                      'padding': '12px',
                                      'position': 'absolute',
                                      'zIndex': '1000',
                                      'marginLeft': '10px',
                                      'fontSize': '0.8rem',
                                      'lineHeight': '1.4',
                                      'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
                                  },
                                  className='tooltip-text')
                    ], style={'position': 'relative', 'display': 'inline-block'}, className='tooltip-container')
                ], style={'fontSize': '0.875rem', 'color': 'var(--text-secondary)', 'marginBottom': '0.5rem'}),
                html.Div([
                    dcc.Input(
                        id='input-box-tagging-context',
                        type='text',
                        placeholder='Enter the genomic context around the target site',
                        className='sequence-input',
                        style={'width': '100%'}
                    )
                ], className='input-with-examples'),
                # Example buttons in separate wrapper divs
                html.Div([
                    html.Button(
                        'Example: GPAT2-214 (human)',
                        id='example-gpat2-3prime-button',
                        n_clicks=0,
                        className='submit-button',
                        style={'marginTop': '1rem', 'width': 'auto', 'padding': '0.75rem 1.5rem', 'textTransform': 'none'}
                    )
                ], id='example-3prime-buttons', style={'display': 'none'}),
                html.Div([
                    html.Button(
                        'Example: GPAT2-214 (human)',
                        id='example-gpat2-5prime-button',
                        n_clicks=0,
                        className='submit-button',
                        style={'marginTop': '1rem', 'width': 'auto', 'padding': '0.75rem 1.5rem', 'textTransform': 'none'}
                    )
                ], id='example-5prime-buttons', style={'display': 'none'}),

                # Tag Cassette section (part of hidden section)
                html.H4('Tag Cassette', style={'marginBottom': '1rem', 'color': 'var(--primary-color)', 'marginTop': '2rem'}),
                html.Div(id='tag-cassette-warning-message', children=[], style={'marginBottom': '0.5rem'}),
                html.Label('Tag Sequence:', style={'fontWeight': '600', 'marginBottom': '0.5em', 'display': 'block'}),
                html.Div([
                    dcc.Textarea(
                        id='input-box-tagging-cassette',
                        placeholder='Enter the genetic sequence of your tag cassette',
                        className='sequence-input',
                        style={'width': '100%', 'minHeight': '100px', 'resize': 'vertical'}
                    )
                ], className='input-with-examples'),
                # Example buttons in separate wrapper divs
                html.Div([
                    html.Button(
                        'Example: SSGSSG-eGFP-STOP',
                        id='example-egfp-3prime-button',
                        n_clicks=0,
                        className='submit-button',
                        style={'marginTop': '1rem', 'width': 'auto', 'padding': '0.75rem 1.5rem', 'textTransform': 'none'}
                    )
                ], id='example-3prime-cassette-button', style={'display': 'none'}),
                html.Div([
                    html.Button(
                        'Example: START-eGFP-SSGSSG',
                        id='example-egfp-5prime-button',
                        n_clicks=0,
                        className='submit-button',
                        style={'marginTop': '1rem', 'width': 'auto', 'padding': '0.75rem 1.5rem', 'textTransform': 'none'}
                    )
                ], id='example-5prime-cassette-button', style={'display': 'none'}),
            ], style={'display': 'none'})
        ], className='step-content')
    ], className='step-card'),

    # Submit Section
    html.Div([
        html.Button(
            'Run Analysis',
            id='submit-button-tagging',
            className='submit-button',
            style={
                'width': '100%',
                'padding': '1rem 2rem',
                'backgroundColor': 'var(--primary-color)',
                'color': 'white',
                'border': 'none',
                'borderRadius': 'var(--border-radius-lg)',
                'cursor': 'pointer',
                'fontSize': 'var(--font-size-lg)',
                'fontWeight': '700',
                'boxShadow': 'var(--shadow-lg)',
                'transition': 'all 0.2s ease',
                'margin': '2rem 0 1rem 0'
            }
        ),
        html.P(
            'PROCESSING TIME: ~1-1.5 minutes for 10 gRNAs (scales linearly with number of gRNAs found)',
            className='processing-time'
        )
    ]),
    dcc.Store(id='tagging-table-data-store'),
    dcc.Store(id='tagging-metadata-store'),
    dcc.Store(id='tagging-mode-store'),  # Store whether 5' or 3' tagging
    dcc.Download(id='download-tagging-excel'),

    # Off-target warning modal for Custom Tagging downloads
    dbc.Modal([
        dbc.ModalHeader("Important Warning: Off-Target Considerations"),
        dbc.ModalBody([
            html.H5("Important: Off-Target Analysis Required", style={'marginBottom': '15px', 'color': '#DC2626', 'fontWeight': 'bold'}),
            html.P([
                html.Strong("Please note: "),
                "Off-target screening has not been performed on these gRNAs. Comprehensive off-target analysis requires substantial computational resources and is best performed externally from our site for your specific gRNA of interest."
            ], style={'marginBottom': '15px', 'fontSize': '1rem'}),
            html.H6("What you need to know:", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.P([
                "CRISPR can sometimes bind to similar (but not perfect) sequences in the genome. Checking for these potential off-target sites across all possible mismatches is extremely computation-intensive, so we recommend you perform this analysis yourself for your chosen gRNA."
            ], style={'marginBottom': '15px'}),
            html.H6("Quick next step (takes ~1 minute):", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
            html.P([
                "Before using your chosen gRNA, please run it through ",
                html.A("Cas-OFFinder", href="http://www.rgenome.net/cas-offinder/", target="_blank", style={'textDecoration': 'underline', 'color': '#2E5BFF', 'fontWeight': '600'}),
                " or an equivalent tool:"
            ], style={'marginBottom': '10px'}),
            html.Ul([
                html.Li("Visit the website and follow their simple instructions"),
                html.Li("Confirm your gRNA has minimal off-target matches"),
                html.Li("Results typically appear in under a minute")
            ], style={'marginBottom': '15px'}),
        ]),
        dbc.ModalFooter([
            dcc.Checklist(
                id="tagging-dont-show-again-checkbox",
                options=[{"label": " Don't show this warning again for this session", "value": "hide"}],
                value=[],
                style={'marginRight': 'auto', 'fontSize': '14px'}
            ),
            dbc.Button("I Understand - Proceed with Download", id="tagging-download-confirm-btn", n_clicks=0, style={'backgroundColor': '#10B981', 'borderColor': '#10B981'})
        ], style={'display': 'flex', 'alignItems': 'center'}),
    ], id="tagging-download-modal", is_open=False, size="lg"),

    # Store for download flow
    dcc.Store(id="tagging-warning-acknowledged", storage_type='memory', data=False),

    html.Div(id='error-message-tagging', children=''),
    dcc.Loading(
        id='loading-tagging',
        type='circle',
        children=html.Div(id='heatmap-tagging-container')
    )
], style={'padding': '2em', 'maxWidth': '1000px', 'margin': '0 auto'})


# ===================================================================
# CUSTOM TAGGING PAGE CALLBACKS
# ===================================================================

def register_callbacks(app):

    # Callback for tagging type choice buttons (5' vs 3')
    @app.callback(
        [Output('choice-5prime-tagging', 'style'),
         Output('choice-3prime-tagging', 'style'),
         Output('tagging-input-section', 'style'),
         Output('tagging-mode-store', 'data'),
         Output('codon-warning-message', 'children'),
         Output('tag-cassette-warning-message', 'children'),
         Output('example-5prime-buttons', 'style'),
         Output('example-3prime-buttons', 'style'),
         Output('example-5prime-cassette-button', 'style'),
         Output('example-3prime-cassette-button', 'style'),
         Output('tagging-target-label', 'children'),
         Output('input-box-tagging-target', 'value'),
         Output('input-box-tagging-context', 'value'),
         Output('input-box-tagging-cassette', 'value'),
         Output('custom-tagging-transcript', 'value', allow_duplicate=True),
         Output('custom-tagging-fill-indicator', 'children', allow_duplicate=True)],
        [Input('choice-5prime-tagging', 'n_clicks'),
         Input('choice-3prime-tagging', 'n_clicks')],
        prevent_initial_call=True
    )
    def toggle_tagging_choice(fiveprime_clicks, threeprime_clicks):
        ctx = dash.callback_context

        base_style = {
            'width': '48%',
            'padding': '1.5rem 2rem',
            'backgroundColor': '#FFFFFF',
            'border': '3px solid #2E5BFF',
            'borderRadius': '0.75rem',
            'cursor': 'pointer',
            'fontSize': '1rem',
            'fontWeight': '600',
            'color': '#2E5BFF',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'transition': 'all 250ms ease-in-out',
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'minHeight': '80px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'position': 'relative'
        }

        if not ctx.triggered:
            return (base_style, base_style, {'display': 'none'}, None, [], [],
                    {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'},
                    'Genomic target site where you wish to tag:', '', '', '', None, '')

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        active_style = base_style.copy()
        active_style.update({
            'backgroundColor': '#2E5BFF',
            'color': '#FFFFFF',
            'borderColor': '#2E5BFF',
            'boxShadow': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            'transform': 'translateY(-1px)'
        })

        if button_id == 'choice-5prime-tagging':
            target_warning = html.P(
                'IMPORTANT: Make sure the first three bases in this window are the start codon (ATG)',
                style={'fontSize': '0.875rem', 'color': '#D97706', 'fontWeight': '600', 'fontStyle': 'italic',
                       'padding': '0.75rem', 'backgroundColor': '#FEF3C7', 'borderRadius': '0.5rem',
                       'border': '1px solid #F59E0B', 'marginBottom': '0.5rem'}
            )
            cassette_warning = html.P(
                'IMPORTANT: Don\'t forget to include your start codon (ATG) at the beginning of your tag sequence',
                style={'fontSize': '0.875rem', 'color': '#D97706', 'fontWeight': '600', 'fontStyle': 'italic',
                       'padding': '0.75rem', 'backgroundColor': '#FEF3C7', 'borderRadius': '0.5rem',
                       'border': '1px solid #F59E0B', 'marginBottom': '0.5rem'}
            )
            # Show 5' example buttons, hide 3' example buttons
            return (active_style, base_style, {'display': 'block'}, 'first_exon', target_warning, cassette_warning,
                    {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'none'},
                    'The complete first exon of the gene you wish to tag:', '', '', '', None, '')
        elif button_id == 'choice-3prime-tagging':
            target_warning = html.P(
                'IMPORTANT: Make sure the last three bases in this window are a stop codon (TAA, TAG, or TGA)',
                style={'fontSize': '0.875rem', 'color': '#D97706', 'fontWeight': '600', 'fontStyle': 'italic',
                       'padding': '0.75rem', 'backgroundColor': '#FEF3C7', 'borderRadius': '0.5rem',
                       'border': '1px solid #F59E0B', 'marginBottom': '0.5rem'}
            )
            cassette_warning = html.P(
                'IMPORTANT: Don\'t forget to include your stop codon (TAA, TAG, or TGA) at the end of your tag sequence',
                style={'fontSize': '0.875rem', 'color': '#D97706', 'fontWeight': '600', 'fontStyle': 'italic',
                       'padding': '0.75rem', 'backgroundColor': '#FEF3C7', 'borderRadius': '0.5rem',
                       'border': '1px solid #F59E0B', 'marginBottom': '0.5rem'}
            )
            # Show 3' example buttons, hide 5' example buttons
            return (base_style, active_style, {'display': 'block'}, 'last_exon', target_warning, cassette_warning,
                    {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'block'},
                    'The complete last exon of the gene you wish to tag:', '', '', '', None, '')

        return (base_style, base_style, {'display': 'none'}, None, [], [],
                {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'},
                'Genomic target site where you wish to tag:', None, None, None, None, '')

    # Callback for 3' GPAT2-214 example button - populate target and context
    @app.callback(
        [Output('input-box-tagging-target', 'value', allow_duplicate=True),
         Output('input-box-tagging-context', 'value', allow_duplicate=True)],
        [Input('example-gpat2-3prime-button', 'n_clicks'),
         Input('example-gpat2-5prime-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def populate_gpat2_example(threeprime_clicks, fiveprime_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'example-gpat2-3prime-button' and threeprime_clicks and threeprime_clicks > 0:
            # GPAT2-214 last exon (with stop codon TAG at the end) - 3' tagging
            last_exon = "GTTCTGCAGCAGACGCCGAGCCCTGCAGGCCCCAGGCTCCACCTGTCCCCTACTTTTGCCAGCCTGGACAATCAGGAAAAACTAGAACAGTTCATCCGGCAGTTCATTTGTAGCTAG"
            # Last exon with 50bp context on each side
            last_exon_context = "TACACAGTCCCTGTGGTGAGCGCACTCACGGCTTATCTTCCATGGCCCAGGTTCTGCAGCAGACGCCGAGCCCTGCAGGCCCCAGGCTCCACCTGTCCCCTACTTTTGCCAGCCTGGACAATCAGGAAAAACTAGAACAGTTCATCCGGCAGTTCATTTGTAGCTAGAACTGTGAGGAGGAGCCTGTGCTGAGACTTCTCAGCCCCAGAACACAGCT"
            return last_exon, last_exon_context
        elif button_id == 'example-gpat2-5prime-button' and fiveprime_clicks and fiveprime_clicks > 0:
            # GPAT2-214 first exon (starts with ATG) - 5' tagging
            first_exon = "ATGGCCACCATGTTGGAAGGCAGATGCCAAACTCAGCCAAGGAGCAGCCCCAGTGGCCGAGAG"
            # First exon with 50bp context on each side
            first_exon_context = "GGAGAAGGAGAGTGCCAGAGGTGACTGGTTCATGGTTCTTCTAGGCTCTCATGGCCACCATGTTGGAAGGCAGATGCCAAACTCAGCCAAGGAGCAGCCCCAGTGGCCGAGAGGTAATGTGGCTCCTCCCATTCCTCAAATCCTCTCTGCCCTGCCACCCCTT"
            return first_exon, first_exon_context

        return dash.no_update, dash.no_update

    # === GENE LOOKUP: search genes as user types ===
    @app.callback(
        [Output('custom-tagging-gene', 'options'),
         Output('custom-tagging-gene', 'placeholder'),
         Output('custom-tagging-gene', 'value')],
        [Input('custom-tagging-gene', 'search_value'),
         Input('custom-tagging-species', 'value')],
        [State('custom-tagging-gene', 'value')],
        prevent_initial_call=False
    )
    def search_custom_genes(search_value, species, current_value):
        # Search the transcript sequences DB directly so every gene with
        # transcript data is available, not only genes with pre-calculated
        # gRNA databases.  Mouse gene symbols are resolved via the bundled
        # ensembl_mouse_transcripts.tsv mapping (cached at first call).
        #
        # current_value (State) is always injected at the top of the option
        # list so the dropdown never loses its displayed label after selection
        # (Dash clears search_value on select, which would otherwise cause the
        # freshly-returned options to not contain the selected value).
        from utils.db import search_genes_in_transcript_db

        if not species:
            return [], 'Select a species first', dash.no_update

        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        species_changed = (trigger_id == 'custom-tagging-species')

        gene_names = search_genes_in_transcript_db(search_value, species, limit=99)

        # Keep the current selection visible only when NOT switching species;
        # on organism switch we hard-reset so old-species genes don't appear at the top.
        if not species_changed and current_value and current_value not in gene_names:
            gene_names = [current_value] + gene_names

        options = [{'label': g, 'value': g} for g in gene_names]
        safe = (search_value or '').strip()
        placeholder = (f'Found {len(options)} genes' if safe
                       else f'Type to search genes (showing first {len(options)})...')
        new_value = None if species_changed else dash.no_update
        return options, placeholder, new_value

    # === GENE LOOKUP: populate transcript dropdown ===
    @app.callback(
        [Output('custom-tagging-transcript', 'options'),
         Output('custom-tagging-transcript', 'value'),
         Output('custom-tagging-transcript', 'placeholder')],
        [Input('custom-tagging-gene', 'value'),
         Input('custom-tagging-species', 'value')],
        prevent_initial_call=True
    )
    def update_custom_transcripts(gene_name, species):
        # Look up transcripts from the transcript sequences DB for all species.
        # Mouse returns versioned ENSMUST IDs (looked up via the symbol map);
        # human/xenopus return gene_id strings — both match what the autofill
        # callback expects when querying transcript_data.
        from utils.db import get_assemblies_for_gene_in_transcript_db

        if not gene_name or not species:
            return [], None, 'Select a gene first'

        is_mouse = 'Mus' in species
        assemblies = get_assemblies_for_gene_in_transcript_db(gene_name, species)

        if not assemblies:
            return [], None, f'No transcripts found for {gene_name}'

        if is_mouse:
            # Show human-readable labels (Kdm1a-1, Kdm1a-2 …) but store ENSMUST IDs
            options = [{'label': f'{gene_name}-{i+1}', 'value': a}
                       for i, a in enumerate(assemblies)]
        else:
            options = [{'label': a, 'value': a} for a in assemblies]

        return options, None, 'Select a transcript'

    # === GENE LOOKUP: auto-fill target + context ===
    @app.callback(
        [Output('input-box-tagging-target', 'value', allow_duplicate=True),
         Output('input-box-tagging-context', 'value', allow_duplicate=True),
         Output('custom-tagging-fill-indicator', 'children')],
        [Input('custom-tagging-transcript', 'value')],
        [State('custom-tagging-species', 'value'),
         State('custom-tagging-gene', 'value'),
         State('custom-tagging-transcript', 'options'),
         State('tagging-mode-store', 'data')],
        prevent_initial_call=True
    )
    def autofill_from_transcript(transcript_value, species, gene_name, transcript_options, tagging_mode):
        import sqlite3, os
        from app import TRANSCRIPT_DB_DIR

        if not transcript_value or not species:
            return dash.no_update, dash.no_update, ''

        species_formatted = species.replace(' ', '_')
        db_path = os.path.join(TRANSCRIPT_DB_DIR, f"{species_formatted}_transcript_sequences.db")

        if not os.path.exists(db_path):
            return dash.no_update, dash.no_update, '⚠ Transcript database not found'

        is_mouse = 'Mus' in species

        if tagging_mode == 'first_exon':
            seq_col, ctx_col = 'first_exon_sequence', 'first_exon_sequence_with_context'
            mode_label = "first exon"
        else:
            seq_col, ctx_col = 'last_exon_sequence', 'last_exon_sequence_with_context'
            mode_label = "last exon"

        try:
            conn = get_optimized_connection(db_path)
            cur = conn.cursor()
            # Mouse value = ENSMUST → query by transcript_id
            # Human/Xenopus value = gene_id (e.g. "KDM1A-201") → query by gene_id
            if is_mouse:
                cur.execute(f"SELECT {seq_col}, {ctx_col} FROM transcript_data WHERE transcript_id = ?",
                            (transcript_value,))
            else:
                cur.execute(f"SELECT {seq_col}, {ctx_col} FROM transcript_data WHERE gene_id = ?",
                            (transcript_value,))
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            print(f"autofill error: {e}")
            return dash.no_update, dash.no_update, f'⚠ Error: {e}'

        if not row or not row[0]:
            return dash.no_update, dash.no_update, f'⚠ No {mode_label} sequence found for this transcript'

        # Get the human-readable label for the status message
        label = transcript_value
        if transcript_options:
            match = next((o['label'] for o in transcript_options if o['value'] == transcript_value), None)
            if match:
                label = match

        status = f'✓ {mode_label.capitalize()} sequences loaded for {label}'
        return row[0], row[1], status

    # Callback for eGFP example buttons - populate tag cassette
    @app.callback(
        Output('input-box-tagging-cassette', 'value', allow_duplicate=True),
        [Input('example-egfp-3prime-button', 'n_clicks'),
         Input('example-egfp-5prime-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def populate_egfp_example(threeprime_clicks, fiveprime_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'example-egfp-3prime-button' and threeprime_clicks and threeprime_clicks > 0:
            # SSGSSG-eGFP-STOP sequence for 3' tagging
            egfp_sequence = "ACAAGGATGTTGAGGTATGGTGTAAACTTGAAGACTTCCAGGAGGTGAGCGACCTCAGGTGTCTGAACATATCCTTCTTACACCCCAAAGATTTTACCCCATCTCCTATCGAGAGTGGAGGCGCTACTATGAAGTGTGGGATATAGAGCCAAGCTTCAATGTCTCTTATGCCCTGCATTTGTGGAACCACATGAACCAGGAGGGGCGGGCTGTGATTAGAGGAAGCAACACACTGGTGGAAAATCTCTATCGCAAGCACTGTCCCAGGACTTACAGGGACCTGATTTAAAGGCCCAGAGGGGTCAGTGACTGGGGAGCTGGGTCCAGGTAACAAATCCAGCGGCAGTAGCGGTATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCCATCCTGGTCGAGCTGGACGGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTACGGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACCCTCGTGACCACCCTGACCTACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAGCAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTCTTCAAGGACGACGGCAACTACAAGACCCGCGCCGAGGTGAAGTTCGAGGGCGACACCCTGGTGAACCGCATCGAGCTGAAGGGCATCGACTTCAAGGAGGACGGCAACATCCTGGGGCACAAGCTGGAGTACAACTACAACAGCCACAACGTCTATATCATGGCCGACAAGCAGAAGAACGGCATCAAGGTGAACTTCAAGATCCGCCACAACATCGAGGACGGCAGCGTGCAGCTCGCCGACCACTACCAGCAGAACACCCCCTCGGCGACGGCCCCGTGCTGCTGCCCGACAACCACTACCTGAGCACCCAGTCCGCCCTGAGCAAAGACCCCAACGAGAAGCGCGATCACATGGTCCTGCTGGAGTTCGTGACCGCCGCCGGGATCACTCTCGGCATGGACGAGCTGTACAAGTAA"
            return egfp_sequence
        elif button_id == 'example-egfp-5prime-button' and fiveprime_clicks and fiveprime_clicks > 0:
            # START-eGFP-SSGSSG sequence for 5' tagging
            egfp_5prime_sequence = "ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCCATCCTGGTCGAGCTGGACGGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTACGGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACCCTCGTGACCACCCTGACCTACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAGCAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTCTTCAAGGACGACGGCAACTACAAGACCCGCGCCGAGGTGAAGTTCGAGGGCGACACCCTGGTGAACCGCATCGAGCTGAAGGGCATCGACTTCAAGGAGGACGGCAACATCCTGGGGCACAAGCTGGAGTACAACTACAACAGCCACAACGTCTATATCATGGCCGACAAGCAGAAGAACGGCATCAAGGTGAACTTCAAGATCCGCCACAACATCGAGGACGGCAGCGTGCAGCTCGCCGACCACTACCAGCAGAACACCCCCATCGGCGACGGCCCCGTGCTGCTGCCCGACAACCACTACCTGAGCACCCAGTCCGCCCTGAGCAAAGACCCCAACGAGAAGCGCGATCACATGGTCCTGCTGGAGTTCGTGACCGCCGCCGGGATCACTCTCGGCATGGACGAGCTGTACAAGTCCAGCGGCAGTAGCGGT"
            return egfp_5prime_sequence

        return dash.no_update

    # Main tagging callback - reuses integration logic
    @app.callback(
        [Output('heatmap-tagging-container', 'children'),
         Output('tagging-table-data-store', 'data'),
         Output('tagging-metadata-store', 'data'),
         Output('error-message-tagging', 'children')],
        [Input('submit-button-tagging', 'n_clicks')],
        [State('input-box-tagging-target', 'value'),
         State('input-box-tagging-context', 'value'),
         State('input-box-tagging-cassette', 'value'),
         State('dropdown-menu-tagging', 'value'),
         State('tagging-mode-store', 'data')],
        prevent_initial_call=True
    )
    def update_tagging_heatmap(n_clicks, target_value, context_value, cassette_value, dropdown_value, tagging_mode):
        if n_clicks is not None and n_clicks > 0:
            # Check if all required fields are filled
            if not cassette_value or not context_value or not tagging_mode:
                return html.Div('Please fill in all required fields and select a tagging type', style={'color': 'orange', 'textAlign': 'center', 'margin': '2em'}), None, None, ''

            # Validate all sequence inputs contain only ACTG
            is_valid, error_msg = validate_sequence_chars(context_value, "Genomic context")
            if not is_valid:
                return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

            is_valid, error_msg = validate_sequence_chars(cassette_value, "Tag cassette")
            if not is_valid:
                return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

            # If target is provided, perform validations
            if target_value:
                is_valid, error_msg = validate_sequence_chars(target_value, "Genomic target")
                if not is_valid:
                    return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})
                target_upper = target_value.upper().strip()
                context_upper = context_value.upper().strip()

                # Validation 1: Check start/stop codons
                if tagging_mode == 'first_exon':
                    # 5' tagging - check for ATG start codon
                    if not target_upper.startswith('ATG'):
                        return html.Div('Invalid entry: The first three bases must be the start codon (ATG)',
                                        style={'color': 'red', 'textAlign': 'center', 'margin': '2em', 'fontWeight': '600'}), None, None, ''
                elif tagging_mode == 'last_exon':
                    # 3' tagging - check for stop codon
                    stop_codons = ['TAA', 'TAG', 'TGA']
                    if not any(target_upper.endswith(codon) for codon in stop_codons):
                        return html.Div('Invalid entry: The last three bases must be a stop codon (TAA, TAG, or TGA)',
                                        style={'color': 'red', 'textAlign': 'center', 'margin': '2em', 'fontWeight': '600'}), None, None, ''

                # Validation 2: Check if context matches target (remove 50bp from each end)
                if len(context_upper) >= 100:
                    context_middle = context_upper[50:-50]
                    if context_middle != target_upper:
                        return html.Div([
                            html.P('Invalid entry: The genomic context doesn\'t match the target site', style={'fontWeight': '600', 'marginBottom': '0.5rem'}),
                            html.P('The context should be: 50bp upstream + your target sequence + 50bp downstream', style={'fontSize': '0.9rem', 'marginBottom': '0.5rem'}),
                            html.P('Please check that the middle part of your context (after removing 50bp from each end) matches your target sequence exactly.', style={'fontSize': '0.9rem'})
                        ], style={'color': 'red', 'textAlign': 'center', 'margin': '2em'}), None, None, ''
                else:
                    return html.Div('Invalid entry: context must be at least 100bp (target + 50bp on each side)',
                                    style={'color': 'orange', 'textAlign': 'center', 'margin': '2em'}), None, None, ''

            # Proceed with analysis
            if cassette_value and context_value and tagging_mode:
                try:
                    # Determine which sequence to use as the target
                    # If target_value is provided, use it; otherwise use the full context
                    target_seq = target_value.upper() if target_value else context_value.upper()

                    # Call the same integration function with the appropriate mode
                    max_integration_scores = process_pythia_integration_with_gRNA(
                        target_seq,                 # The exon/target sequence
                        cassette_value.upper(),     # The tag cassette
                        dropdown_value,             # Cell type
                        tagging_mode,               # 'first_exon' or 'last_exon'
                        context_value.upper()       # The full context
                    )

                    # Process and format results (same as integration)
                    max_integration_scores.drop(['integration_score_max', 'integration_score_float', "Revcomp_right_repair_arm", 'Forward_Primer', 'Reverse_Primer'], axis=1, inplace=True)

                    max_integration_scores.rename(columns={
                        'integration_score': 'Pythia Integration Score',
                        'Predicted frequency_left': 'Left junction predicted efficiency',
                        'Amount of trimologies_left': 'Left: Number of Tandem Repeats (-ologies)',
                        'Homol_length_left': 'Left: Length of homology',
                        'context_left': 'Sequence context around gRNA',
                        'Amount of trimologies_right': 'Right: Number of Tandem Repeats (-ologies)',
                        'Homol_length_right': 'Right: Length of homology',
                        'Predicted frequency_right': 'Right junction predicted efficiency',
                        'forward_primer_with_overhang': 'Fw primer with homology overhangs',
                        'reverse_primer_with_overhang': 'Rv primer with homology overhangs'
                    }, inplace=True)

                    max_integration_scores = max_integration_scores[
                        [
                            'Pythia Integration Score',
                            'gRNA',
                            'CRISPRScan score',
                            'strand',
                            'location',
                            'Left: Number of Tandem Repeats (-ologies)',
                            'Left: Length of homology',
                            'Left junction predicted efficiency',
                            'left_repair_arm',
                            'Right: Number of Tandem Repeats (-ologies)',
                            'Right: Length of homology',
                            'Right junction predicted efficiency',
                            'right_repair_arm',
                            'Full repair cassette sequence',
                            'Fw primer with homology overhangs',
                            'Rv primer with homology overhangs',
                            'Forward_Primer_Tm',
                            'Reverse_Primer_Tm'
                        ]
                    ]

                    max_integration_scores.rename(columns={
                        'right_repair_arm': 'Right Repair Arm',
                        'left_repair_arm': 'Left Repair Arm',
                        'Forward_Primer_Tm': 'Forward Primer Tm',
                        'Reverse_Primer_Tm': 'Reverse Primer Tm'
                    }, inplace=True)

                    max_integration_scores['Pythia Integration Score'] = max_integration_scores['Pythia Integration Score'].round(2)
                    max_integration_scores['Left junction predicted efficiency'] = max_integration_scores['Left junction predicted efficiency'].round(2)
                    max_integration_scores['Right junction predicted efficiency'] = max_integration_scores['Right junction predicted efficiency'].round(2)
                    max_integration_scores['Forward Primer Tm'] = max_integration_scores['Forward Primer Tm'].round(2)
                    max_integration_scores['Reverse Primer Tm'] = max_integration_scores['Reverse Primer Tm'].round(2)

                    table_component = dash_table.DataTable(
                        id='tagging-table',
                        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in max_integration_scores.columns],
                        data=max_integration_scores.to_dict('records'),
                        sort_action='native',
                        sort_mode='multi',
                        sort_by=[{'column_id': 'Pythia Integration Score', 'direction': 'desc'}],
                        page_current=0,
                        page_size=10,
                        page_action='native',
                        style_table={
                            'height': '350px',
                            'overflowY': 'auto',
                            'overflowX': 'auto',
                            'maxWidth': '100%'
                        },
                        style_cell={
                            'minWidth': '60px', 'width': 'auto', 'maxWidth': '200px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'textAlign': 'center',
                            'whiteSpace': 'nowrap'
                        },
                        style_header={
                            'backgroundColor': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'center'
                        },
                        css=[{
                            'selector': '.previous-next-container',
                            'rule': 'color: #1f2937 !important; font-weight: 500;'
                        }, {
                            'selector': '.previous-next-container input',
                            'rule': 'color: #1f2937 !important; background-color: #ffffff !important; font-weight: 600; text-align: center;'
                        }]
                    )

                    # Determine title based on tagging mode (avoid backslash in f-string)
                    title_text = "5' (N-terminal) Tagging Results" if tagging_mode == 'first_exon' else "3' (C-terminal) Tagging Results"

                    unified_results = html.Div([
                        html.H2(title_text, className="results-header"),
                        html.P("The table below shows the optimal repair templates and primers for your tagging target, sorted by Pythia Integration Score.",
                               style={'textAlign': 'center', 'marginBottom': '2em', 'color': 'var(--text-secondary)'}),
                        html.Div([
                            html.Div([
                                html.Button(
                                    '📥 Download Table as Excel',
                                    id='download-tagging-button',
                                    n_clicks=0,
                                    style={
                                        'marginBottom': '1em',
                                        'padding': '0.5em 1em',
                                        'backgroundColor': '#10B981',
                                        'color': 'white',
                                        'border': 'none',
                                        'borderRadius': '4px',
                                        'cursor': 'pointer',
                                        'fontWeight': '600',
                                        'fontSize': '14px'
                                    }
                                )
                            ], style={'textAlign': 'right', 'marginBottom': '0.5em'}),
                            table_component
                        ], className="results-table")
                    ], className="unified-results-container")

                    metadata = {
                        'cassette': cassette_value,
                        'context': context_value,
                        'mode': tagging_mode
                    }

                    return unified_results, max_integration_scores.to_dict('records'), metadata, ''

                except ValueError as e:
                    return html.Div(str(e), style={'color': 'orange', 'textAlign': 'center', 'margin': '2em', 'fontWeight': '500'}), None, None, ''
                except Exception as e:
                    print("An exception occurred: ", str(e))
                    return html.Div(f'Error processing: {str(e)}', style={'color': 'red', 'textAlign': 'center', 'margin': '2em'}), None, None, ''
            else:
                return html.Div('Please fill in all required fields and select a tagging type', style={'color': 'orange', 'textAlign': 'center', 'margin': '2em'}), None, None, ''

        return html.Div(), None, None, ''

    # Callback to show/hide modal when download button is clicked
    @app.callback(
        Output('tagging-download-modal', 'is_open'),
        [Input('download-tagging-button', 'n_clicks'),
         Input('tagging-download-confirm-btn', 'n_clicks')],
        [State('tagging-warning-acknowledged', 'data')],
        prevent_initial_call=True
    )
    def handle_tagging_download_modal(download_clicks, confirm_clicks, warning_acknowledged):
        ctx = dash.callback_context
        if not ctx.triggered:
            return False

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'download-tagging-button':
            # Only show modal if button was actually clicked (n_clicks > 0)
            if download_clicks and download_clicks > 0:
                if warning_acknowledged:
                    return False
                else:
                    return True
            return False

        elif trigger_id == 'tagging-download-confirm-btn':
            return False

        return False

    # Callback to mark warning as acknowledged
    @app.callback(
        Output('tagging-warning-acknowledged', 'data'),
        Input('tagging-download-confirm-btn', 'n_clicks'),
        State('tagging-dont-show-again-checkbox', 'value'),
        prevent_initial_call=True
    )
    def mark_tagging_warning_acknowledged(n_clicks, dont_show):
        if n_clicks and 'hide' in (dont_show or []):
            return True
        return dash.no_update

    # Callback to download tagging table as Excel
    @app.callback(
        Output('download-tagging-excel', 'data'),
        [Input('tagging-download-confirm-btn', 'n_clicks'),
         Input('download-tagging-button', 'n_clicks')],
        [State('tagging-table-data-store', 'data'),
         State('tagging-metadata-store', 'data'),
         State('tagging-warning-acknowledged', 'data')],
        prevent_initial_call=True
    )
    def download_tagging_table(confirm_clicks, download_clicks, table_data, metadata, warning_acknowledged):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Only proceed if: (1) confirm button clicked, OR (2) download button clicked AND already acknowledged
        if trigger_id == 'tagging-download-confirm-btn':
            should_download = True
        elif trigger_id == 'download-tagging-button' and warning_acknowledged:
            should_download = True
        else:
            return dash.no_update

        if should_download and table_data and metadata:
            import io

            df = pd.DataFrame(table_data)
            top_result = df.iloc[0]

            grna = top_result['gRNA'] if 'gRNA' in top_result else 'N/A'
            left_tandem = int(top_result['Left: Number of Tandem Repeats (-ologies)'])
            left_homology = int(top_result['Left: Length of homology'])
            left_efficiency = float(top_result['Left junction predicted efficiency'])
            right_tandem = int(top_result['Right: Number of Tandem Repeats (-ologies)'])
            right_homology = int(top_result['Right: Length of homology'])
            right_efficiency = float(top_result['Right junction predicted efficiency'])
            combined_score = float(top_result['Pythia Integration Score'])

            cassette = metadata.get('cassette', 'N/A')
            user_context = metadata.get('context', '')
            tagging_mode = metadata.get('mode', 'integration')

            if 'Left Repair Arm' in top_result and 'Right Repair Arm' in top_result:
                left_arm = top_result['Left Repair Arm']
                right_arm = top_result['Right Repair Arm']
            else:
                left_homology_seq = user_context[-left_homology:] if user_context else ''
                left_arm = left_homology_seq * left_tandem
                right_homology_seq = user_context[:right_homology] if user_context else ''
                right_arm = right_homology_seq * right_tandem

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet('Tagging Results')
                writer.sheets['Tagging Results'] = worksheet

                title_format = workbook.add_format({'bold': True, 'font_size': 14})
                header_format = workbook.add_format({'bold': True, 'font_size': 11})
                normal_format = workbook.add_format({'font_size': 10})

                row = 0
                mode_text = "5' (N-terminal) Tagging" if tagging_mode == 'first_exon' else "3' (C-terminal) Tagging"
                worksheet.write(row, 0, f"{mode_text} Analysis", title_format)
                row += 2

                if grna != 'N/A':
                    worksheet.write(row, 0, f"Your top combination uses gRNA {grna}:", header_format)
                else:
                    worksheet.write(row, 0, "Your top combination is:", header_format)
                row += 2

                worksheet.write(row, 0, f"On the left: {left_tandem} tandem repeats of {left_homology} basepairs, leading to a left efficiency of {left_efficiency}%", normal_format)
                row += 2

                worksheet.write(row, 0, f"On the right: {right_tandem} tandem repeats of {right_homology} basepairs, leading to a right efficiency of {right_efficiency}%", normal_format)
                row += 2

                worksheet.write(row, 0, f"yielding a combined score of {combined_score}.", normal_format)
                row += 2

                worksheet.write(row, 0, f"Your repair cassette is {left_arm} - {cassette} - {right_arm}", normal_format)
                row += 3

                desired_column_order = [
                    'Pythia Integration Score',
                    'gRNA',
                    'CRISPRScan score',
                    'strand',
                    'location',
                    'Left: Number of Tandem Repeats (-ologies)',
                    'Left: Length of homology',
                    'Left junction predicted efficiency',
                    'Left Repair Arm',
                    'Right: Number of Tandem Repeats (-ologies)',
                    'Right: Length of homology',
                    'Right junction predicted efficiency',
                    'Right Repair Arm',
                    'Fw primer with homology overhangs',
                    'Forward Primer Tm',
                    'Rv primer with homology overhangs',
                    'Reverse Primer Tm'
                ]

                existing_columns = [col for col in desired_column_order if col in df.columns]
                remaining_columns = [col for col in df.columns if col not in existing_columns]
                df = df[existing_columns + remaining_columns]

                df.to_excel(writer, sheet_name='Tagging Results', startrow=row, index=False)

                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(idx, idx, min(max_len, 50))

            output.seek(0)

            mode_filename = "5prime" if tagging_mode == 'first_exon' else "3prime"
            return dcc.send_bytes(output.getvalue(), f"pythia_{mode_filename}_tagging_results.xlsx")

        return dash.no_update
