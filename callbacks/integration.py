import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import altair as alt

from utils.validation import validate_sequence, validate_sequence_chars
from pythia_integration import process_pythia_integration
from pythia_integration_gRNA_finder import process_pythia_integration_with_gRNA
from utils.tooltips import indelphi_model_tooltip

# ===================================================================
# INTEGRATION TOOL - PAGE 1 LAYOUT
# ===================================================================

page_1_layout = html.Div(
    [
        html.H1('Pythia Integration', style={"marginTop": "0.5em", "marginBottom": "0.5em", "paddingBottom": "0.2em", "textAlign": "center"}),
        html.P('Design gRNAs and microhomology repair templates for targeted transgene insertion at intergenic or intronic landing sites.',
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
                    id='dropdown-menu',
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

        # Step 2: Workflow Selection Card
        html.Div([
            html.Div([
                html.H3('Step 2: Choose Your Workflow', className='step-title'),
                html.P('Select which approach best fits your project', className='step-description')
            ], className='step-header'),
            html.Div([
                html.Div([
                    html.Button(['Pre-validated gRNAs or', html.Br(), 'I already have my gRNA designed'],
                               id='choice-existing-grna',
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
                                   'overflow': 'visible',
                                   'minHeight': '120px',
                                   'display': 'flex',
                                   'alignItems': 'center',
                                   'justifyContent': 'center',
                                   'position': 'relative'
                               }),
                    html.Button('Design gRNA and repair templates for me',
                               id='choice-design-grna',
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
                                   'overflow': 'visible',
                                   'minHeight': '120px',
                                   'display': 'flex',
                                   'alignItems': 'center',
                                   'justifyContent': 'center',
                                   'position': 'relative'
                               })
                ], style={'display': 'flex', 'gap': '1rem', 'marginBottom': '2rem'}),

                # Existing gRNA workflow section (initially hidden)
                html.Div(id='existing-grna-section', children=[
                    html.H4('Genomic Sequence Context', style={'marginBottom': '1rem', 'color': 'var(--primary-color)'}),
                    html.P('Enter genomic sequence context around your gRNA:', style={'marginBottom': '1rem'}),
                    html.Div([
                        html.P('Sequence left of CRISPR/Cas9 DSB (40 bp recommended)', style={'flex': '1', 'fontSize': '0.875rem', 'marginBottom': '0.5em', 'color': 'var(--text-secondary)'}),
                        html.P("DSB", className='dsb-label', style={'flex': '0 0 auto', 'marginBottom': '0.5em'}),
                        html.P('Sequence right of CRISPR/Cas9 DSB (40 bp recommended)', style={'flex': '1', 'textAlign': 'right', 'fontSize': '0.875rem', 'marginBottom': '0.5em', 'color': 'var(--text-secondary)'})
                    ], style={'display': 'flex', 'margin': '0 0 1rem 0'}),
                    html.Div([
                        html.Div([
                            dcc.Input(
                                id='input-box',
                                type='text',
                                placeholder='Enter the genetic sequence left of the DSB',
                                className='sequence-input',
                                style={'width': '49%', 'marginRight': '1%'}
                            ),
                            dcc.Input(
                                id='input-box-2',
                                type='text',
                                placeholder='Enter the genetic sequence right of the DSB',
                                className='sequence-input',
                                style={'width': '49%'}
                            )
                        ], style={'display': 'flex', 'marginBottom': '1rem'}),
                        html.Div([
                            html.Span('Example input:', style={'fontSize': 'var(--text-xs)', 'color': 'var(--gray-500)', 'fontWeight': 'var(--font-medium)', 'marginRight': 'var(--space-3)', 'alignSelf': 'center'}),
                            html.Button(
                                [html.Span("human", style={"marginRight": "0.25em"}), html.Span("AAVS1", style={"fontStyle": "italic"})],
                                id='autofill-button-human-aavs1',
                                n_clicks=0,
                                className='example-button'
                            ),
                            html.Button(
                                [html.Span("X. tropicalis hipp11", style={"fontStyle": "italic", "marginRight": "0.25em"}), "alpha"],
                                id='autofill-button-alpha',
                                n_clicks=0,
                                className='example-button'
                            ),
                            html.Button(
                                [html.Span("X. tropicalis hipp11", style={"fontStyle": "italic", "marginRight": "0.25em"}), "beta"],
                                id='autofill-button-beta',
                                n_clicks=0,
                                className='example-button'
                            ),
                            html.Button(
                                [html.Span("X. tropicalis hipp11", style={"fontStyle": "italic", "marginRight": "0.25em"}), "alpha + beta"],
                                id='autofill-button-alpha-beta',
                                n_clicks=0,
                                className='example-button'
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 'gap': 'var(--space-2)', 'flexWrap': 'wrap'})
                    ])
        ], style={'display': 'none'}),  # Initially hidden

                # Design gRNA workflow section (initially hidden)
                html.Div(id='design-grna-section', children=[
                    html.Div([
                        html.P('Integration does not retain reading frame',
                               style={'fontSize': '0.875rem', 'color': 'var(--text-secondary)',
                                      'marginBottom': '1.5rem', 'fontStyle': 'italic',
                                      'padding': '0.75rem', 'backgroundColor': '#F3F4F6',
                                      'borderRadius': '0.5rem', 'border': '1px solid #E5E7EB'})
                    ]),
                    html.H4('Genomic Target', style={'marginBottom': '1rem', 'color': 'var(--primary-color)'}),
                    html.Label('Genomic target site where you wish to integrate:', style={'fontWeight': '600', 'marginBottom': '0.5em', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='input-box-4',
                            type='text',
                            placeholder='Enter your genomic sequence for integration',
                            className='sequence-input',
                            style={'width': '100%'}
                        )
                    ], className='input-with-examples'),
                    html.Label('Genomic context around the target site:', style={'fontWeight': '600', 'marginBottom': '0.5em', 'display': 'block'}),
                    html.P([
                        'Provide 50 bp of flanking sequence on each side (100 bp total around your target) ',
                        html.Span('(Include 50 bp upstream + your target sequence + 50 bp downstream)', style={'fontStyle': 'italic', 'color': '#6B7280'}),
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
                            id='input-box-context',
                            type='text',
                            placeholder='Enter the genomic context around the target site',
                            className='sequence-input',
                            style={'width': '100%'}
                        ),
                        html.P('Examples:', className='input-examples-label'),
                        html.Div([
                            html.Button(
                                [html.Span("human", style={"marginRight": "0.25em"}), html.Span("AAVS1", style={"fontStyle": "italic"})],
                                id='guide-button-human-aavs1',
                                n_clicks=0,
                                className='example-button'
                            ),
                            html.Button(
                                [html.Span("X. trop. hipp11", style={"fontStyle": "italic"})],
                                id='guide-button-x-tropicalis',
                                n_clicks=0,
                                className='example-button'
                            )
                        ], className='example-grid')
                    ], className='input-with-examples')
                ], style={'display': 'none'})
            ], className='step-content')
        ], className='step-card'),

        # Step 3: Transgene Cassette Card
        html.Div([
            html.Div([
                html.H3('Step 3: Transgene Cassette', className='step-title'),
                html.P('Enter the sequence of your transgene cassette as you intend it to integrate', className='step-description')
            ], className='step-header'),
            html.Div([
                html.Label('Transgene Sequence:', style={'fontWeight': '600', 'marginBottom': '0.5em', 'display': 'block'}),
                html.Div([
                    dcc.Textarea(
                        id='input-box-3',
                        placeholder='Enter the genetic sequence of your transgenic cassette',
                        className='sequence-input',
                        style={'width': '100%', 'minHeight': '100px', 'resize': 'vertical'}
                    ),
                    html.P('Examples:', className='input-examples-label'),
                    html.Div([
                        html.Button(
                            'CMV-eGFP',
                            id='example-button',
                            n_clicks=0,
                            className='example-button'
                        )
                    ], className='example-grid')
                ], className='input-with-examples')
            ], className='step-content')
        ], className='step-card'),
        # Submit Section
        html.Div([
            html.Button(
                'Run Analysis',
                id='submit-button',
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
        dcc.Loading(
            id='loading-integration',
            type='circle',
            children=html.Div([
                html.Div(id='error-message', children=''),
                html.Div(id='heatmap1-container')
            ])
        ),
        dcc.Store(id='integration-table-data-store'),
        dcc.Store(id='integration-metadata-store'),
        dcc.Download(id='download-integration-excel'),

        # Off-target warning modal for Integration downloads
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
                    id="integration-dont-show-again-checkbox",
                    options=[{"label": " Don't show this warning again for this session", "value": "hide"}],
                    value=[],
                    style={'marginRight': 'auto', 'fontSize': '14px'}
                ),
                dbc.Button("I Understand - Proceed with Download", id="integration-download-confirm-btn", n_clicks=0, style={'backgroundColor': '#10B981', 'borderColor': '#10B981'})
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], id="integration-download-modal", is_open=False, size="lg"),

        # Store for download flow
        dcc.Store(id="integration-warning-acknowledged", storage_type='memory', data=False),
        ],
    style={
        "backgroundColor": "var(--background-secondary)",
        "margin": "0",
        "padding": "2rem",
        "minHeight": "100vh"
    }

)

# ===================================================================
# INTEGRATION TOOL - PAGE 1 CALLBACKS
# ===================================================================

def register_callbacks(app):

    # Callback for workflow choice buttons
    @app.callback(
        [Output('choice-existing-grna', 'style'),
         Output('choice-design-grna', 'style'),
         Output('existing-grna-section', 'style'),
         Output('design-grna-section', 'style')],
        [Input('choice-existing-grna', 'n_clicks'),
         Input('choice-design-grna', 'n_clicks')]
    )
    def toggle_workflow_choice(existing_clicks, design_clicks):
        ctx = dash.callback_context

        # Define the base styles using CSS classes
        existing_base_style = {
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
            'whiteSpace': 'nowrap',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'minHeight': '80px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'position': 'relative'
        }

        design_base_style = existing_base_style.copy()

        if not ctx.triggered:
            # No button clicked yet, both sections hidden
            return (existing_base_style, design_base_style, {'display': 'none'}, {'display': 'none'})

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'choice-existing-grna':
            # Existing gRNA workflow selected - make it active with filled style
            existing_active_style = existing_base_style.copy()
            existing_active_style.update({
                'backgroundColor': '#2E5BFF',
                'color': '#FFFFFF',
                'borderColor': '#2E5BFF',
                'boxShadow': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                'transform': 'translateY(-1px)'
            })
            return (existing_active_style, design_base_style, {'display': 'block'}, {'display': 'none'})

        elif button_id == 'choice-design-grna':
            # Design gRNA workflow selected - make it active with filled style
            design_active_style = design_base_style.copy()
            design_active_style.update({
                'backgroundColor': '#2E5BFF',
                'color': '#FFFFFF',
                'borderColor': '#2E5BFF',
                'boxShadow': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                'transform': 'translateY(-1px)'
            })
            return (existing_base_style, design_active_style, {'display': 'none'}, {'display': 'block'})

        # Default case
        return (existing_base_style, design_base_style, {'display': 'none'}, {'display': 'none'})

    @app.callback(
        [Output('input-box', 'value'),
         Output('input-box-2', 'value'),
         Output('input-box-3', 'value'),
         Output('input-box-4', 'value'),
         Output('input-box-context', 'value')],
        [Input('autofill-button-human-aavs1', 'n_clicks'),
         Input('autofill-button-alpha', 'n_clicks'),
         Input('autofill-button-beta', 'n_clicks'),
         Input('autofill-button-alpha-beta', 'n_clicks'),
         Input('example-button', 'n_clicks'),
         Input('guide-button-human-aavs1', 'n_clicks'),
         Input('guide-button-x-tropicalis', 'n_clicks')]
    )
    def autofill_input_boxes(n_clicks_human_aavs1, n_clicks_alpha, n_clicks_beta, n_clicks_alpha_beta, n_clicks_example, n_clicks_guide_human_aavs1, n_clicks_guide_x_tropicalis):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'autofill-button-human-aavs1':
                return 'CTTCCTAGTCTCCTGATATTGGGTCTAACCCCCACCTCCT', 'GTTAGGCAGATTCCTTATCTGGTGACACACCCCCATTTCC', dash.no_update, dash.no_update, dash.no_update  # Example sequences for human AAVS1
            elif button_id == 'autofill-button-alpha':
                return 'TTTTGTTCATAATAATAAATTATTGTTCAAAATAATACCA', 'GTGTGGAGTTCAATTAGTGAGGTCATTCATTTTGTTACAA', dash.no_update, dash.no_update, dash.no_update
            elif button_id == 'autofill-button-beta':
                return 'TTGACGTTATGGAGTGGCCAGCTCAATCCCAGGACCCCAA', 'CTTGTGGGGTGACATCAAAAATGCTGTTTGAGGCAAAACC', dash.no_update, dash.no_update, dash.no_update
            elif button_id == 'autofill-button-alpha-beta':
                return 'TTTTGTTCATAATAATAAATTATTGTTCAAAATAATACCA', 'CTTGTGGGGTGACATCAAAAATGCTGTTTGAGGCAAAACC', dash.no_update, dash.no_update, dash.no_update
            elif button_id == 'example-button':
                return dash.no_update, dash.no_update, 'CTATTGGCTCATGTCCAACATTACCGCCATGTTGACATTGATTATTGACTAGTTATTAATAGTAATCAATTACGGGGTCATTAGTTCATAGCCCATATATGGAGTTCCGCGTTACATAACTTACGGTAAATGGCCCGCCTGGCTGACCGCCCAACGACCCCCGCCCATTGACGTCAATAATGACGTATGTTCCCATAGTAACGCCAATAGGGACTTTCCATTGACGTCAATGGGTGGAGTATTTACGGTAAACTGCCCACTTGGCAGTACATCAAGTGTATCATATGCCAAGTACGCCCCCTATTGACGTCAATGACGGTAAATGGCCCGCCTGGCATTATGCCCAGTACATGACCTTATGGGACTTTCCTACTTGGCAGTACATCTACGTATTAGTCATCGCTATTACCATGGTGATGCGGTTTTGGCAGTACATCAATGGGCGTGGATAGCGGTTTGACTCACGGGGATTTCCAAGTCTCCACCCCATTGACGTCAATGGGAGTTTGTTTTGGCACCAAAATCAACGGGACTTTCCAAAATGTCGTAACAACTCCGCCCCATTGACGCAAATGGGCGGTAGGCGTGTACGGTGGGAGGTCTATATAAGCAGAGCTCGTTTAGTGAACCGTCAGATCGCCTGGAGACGCCATCCACGCTGTTTTGACCTCCATAGAAGACACCGGGACCGATCCAGCCTCCCCTCGAAGCTGATCCTGAGAACTTCAGGGTGAGTCTATGGGACCCTTGATGTTTTCTTTCCCCTTCTTTTCTATGGTTAAGTTCATGTCATAGGAAGGGGAGAAGTAACAGGGTACACATATTGACCAAATCAGGGTAATTTTGCATTTGTAATTTTAAAAAATGCTTTCTTCTTTTAATATACTTTTTTGTTTATCTTATTTCTAATACTTTCCCTAATCTCTTTCTTTCAGGGCAATAATGATACAATGTATCATGCCTCTTTGCACCATTCTAAAGAATAACAGTGATAATTTCTGGGTTAAGGCAATAGCAATATTTCTGCATATAAATATTTCTGCATATAAATTGTAACTGATGTAAGAGGTTTCATATTGCTAATAGCAGCTACAATCCAGCTACCATTCTGCTTTTATTTTATGGTTGGGATAAGGCTGGATTATTCTGAGTCCAAGCTAGGCCCTTTTGCTAATCATGTTCATACCTCTTATCTTCCTCCCACAGCTCCTGGGCAACGTGCTGGTCTGTGTGCTGGCCCATCACTTTGGCAAAGAATTCCGCGGGCCCGGGATCCACCGGTCGCCACCATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCCATCCTGGTCGAGCTGGACGGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTACGGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACCCTCGTGACCACCCTGACCTACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAGCAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTCTTCAAGGACGACGGCAACTACAAGACCCGCGCCGAGGTGAAGTTCGAGGGCGACACCCTGGTGAACCGCATCGAGCTGAAGGGCATCGACTTCAAGGAGGACGGCAACATCCTGGGGCACAAGCTGGAGTACAACTACAACAGCCACAACGTCTATATCATGGCCGACAAGCAGAAGAACGGCATCAAGGTGAACTTCAAGATCCGCCACAACATCGAGGACGGCAGCGTGCAGCTCGCCGACCACTACCAGCAGAACACCCCCATCGGCGACGGCCCCGTGCTGCTGCCCGACAACCACTACCTGAGCACCCAGTCCGCCCTGAGCAAAGACCCCAACGAGAAGCGCGATCACATGGTCCTGCTGGAGTTCGTGACCGCCGCCGGGATCACTCTCGGCATGGACGAGCTGTACAAGTAAAGCGGCCGCTCTAGAGGATCCAAGCTTATCGATACCGTCGACCTCGAGGGCCCAGATCTAATTCACCCCACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAATGCCCTGGCCCACAAGTATCACTAAGCTCGCTTTCTTGCTGTCCAATTTCTATTAAAGGTTCCTTTGTTCCCTAAGTCCAACTACTAAACTGGGGGATATTATGAAGGGCCTTGAGCATCTGGATTCTGCCTAATAAAAAACATTTATTTTCATTGCAATGATGTATTTAAATTATTTCTGAATATTTTACTAAAAAGGGAATGTGGGAGGTCAGTGCATTTAAAACATAAAGAAATGAAGAGCTAGTTCAAACCTTGGGAAAATACACTATATCTTAAACTCCATGAAAGAAGGTGAGGCTGCAAACAGCTAATGCACATTGGCAACAGCCCCTGATGCCTATGCCTTATTCATCCCTCAGAAAAGGATTCAAGTAGAGGCTTGATTTGGAGGTTAAAGTTTTGCTATGCTGTATTTTACATTACTTATTGTTTTAGCTGTCCTCATGAATGTCTTTTCACTACCCATTTGCTTATCCTGCATCTCTCAGCCTTGACTCCACTCAGTTCTCTTGCT', dash.no_update, dash.no_update  # Example sequence for CMV-eGFP
            elif button_id == 'guide-button-human-aavs1':
                return dash.no_update, dash.no_update, dash.no_update, 'CTCCAGGAAATGGGGGTGTGTCACCAGATAAGGAATCTGCCTAACAGGAGGTGGGGGTTAGACCCAATATCAGGAGACTAGG', 'CTGGCTCCATCGTAAGCAAACCTTAGAGGTTCTGGCAAGGAGAGAGATGGCTCCAGGAAATGGGGGTGTGTCACCAGATAAGGAATCTGCCTAACAGGAGGTGGGGGTTAGACCCAATATCAGGAGACTAGGAAGGAGGAGGCCTAAGGATGGGGCTTTTCTGTCACCAATCCTGTCCCTAG'
            elif button_id == 'guide-button-x-tropicalis':
                return dash.no_update, dash.no_update, dash.no_update, 'CAAAATGAATGACCTCACTAATTGAACTCCACACTGGTATTATTTTGAACAATAATTTATTATTATGAACAAAAATCTGTGTAA' , 'TTCTGAATTTCTTTGTTTCCCCCTCTCCATAAATAACATCTGTTTTGTAACAAAATGAATGACCTCACTAATTGAACTCCACACTGGTATTATTTTGAACAATAATTTATTATTATGAACAAAAATCTGTGTAATTGAATCAATTAATGATTCAATGATTCAACAAAGACACTGAATTTTAGGA'
            else:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        [Output('heatmap1-container', 'children'),
         Output('integration-table-data-store', 'data'),
         Output('integration-metadata-store', 'data'),
         Output('error-message', 'children')],
        [Input('submit-button', 'n_clicks')],
        [State('input-box', 'value'),
         State('input-box-2', 'value'),
         State('input-box-3', 'value'),
         State('input-box-4', 'value'),
         State('input-box-context', 'value'),
         State('dropdown-menu', 'value'),
         State('choice-existing-grna', 'n_clicks'),
         State('choice-design-grna', 'n_clicks')]
    )
    def update_heatmap(n_clicks, input_box_value, input_box_2_value, input_box_3_value, input_box_4_value, input_box_context_value, dropdown_value, existing_grna_clicks, design_grna_clicks):    #print("Callback triggered")
        #print(f"n_clicks: {n_clicks}")
        #print(f"input_box_value: {input_box_value}")
        #print(f"input_box_2_value: {input_box_2_value}")
        #print(f"input_box_3_value: {input_box_3_value}")
        #print(f"input_box_4_value: {input_box_4_value}")
        #print(f"dropdown_value: {dropdown_value}")


        if n_clicks is not None and n_clicks > 0:

            # Check the conditions for input boxes
            if input_box_value and input_box_2_value and input_box_3_value and not input_box_4_value:

                # Validate all sequence inputs contain only ACTG
                is_valid, error_msg = validate_sequence_chars(input_box_value, "Left sequence")
                if not is_valid:
                    return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

                is_valid, error_msg = validate_sequence_chars(input_box_2_value, "Right sequence")
                if not is_valid:
                    return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

                is_valid, error_msg = validate_sequence_chars(input_box_3_value, "Transgene cassette")
                if not is_valid:
                    return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

                try:
                    # Process the submitted data using the imported function from pythia_integration.py
                    result = process_pythia_integration(input_box_value.upper(), input_box_2_value.upper(), input_box_3_value.upper(), dropdown_value)
                    # Assuming 'result' is a pandas DataFrame after processing
                    # Create the heatmap using the create_heatmap function
                    df_filtered_left = result.loc[result['side'] == 'left']
                    df_filtered_right = result.loc[result['side'] == 'right']

                    df_combined = pd.merge(df_filtered_left, df_filtered_right, on=['Amount of trimologies', 'Homol_length'], suffixes=('_left', '_right'))
                    df_combined['Predicted frequency'] = (df_combined['Predicted frequency_left']/100) * (df_combined['Predicted frequency_right']/100) * 100

                    left = df_filtered_left.copy()
                    right = df_filtered_right.copy()

                    left.columns = [str(col) + '_left' for col in left.columns]
                    right.columns = [str(col) + '_right' for col in right.columns]

                    combined_df_cart = pd.merge(left.assign(key=1), right.assign(key=1), on='key').drop('key', axis=1)


                    combined_df_cart['Trimology score'] = (combined_df_cart['Predicted frequency_left'] * combined_df_cart['Predicted frequency_right']) / 100
                    combined_df_cart = combined_df_cart.drop(columns=['side_left', 'side_right'])

                    combined_df_cart['Homol_length_left'] = combined_df_cart['Homol_length_left'].astype(int)
                    combined_df_cart['Homol_length_right'] = combined_df_cart['Homol_length_right'].astype(int)
                    combined_df_cart['Amount of trimologies_left'] = combined_df_cart['Amount of trimologies_left'].astype(int)
                    combined_df_cart['Amount of trimologies_right'] = combined_df_cart['Amount of trimologies_right'].astype(int)



                    combined_df_cart.rename(columns={
                        'Amount of trimologies_left': 'Left: Number of Tandem Repeats (-ologies)',
                        'Homol_length_left': 'Left: Length of homology',
                        'Predicted frequency_left': 'Left junction predicted efficiency',
                        'Amount of trimologies_right': 'Right: Number of Tandem Repeats (-ologies)',
                        'Homol_length_right': 'Right: Length of homology',
                        'Predicted frequency_right': 'Right junction predicted efficiency',
                        'Trimology score': 'Pythia Integration Score'
                    }, inplace=True)



                    column_order = [
                        'Pythia Integration Score',
                        'Left: Number of Tandem Repeats (-ologies)',
                        'Left: Length of homology',
                        'Left junction predicted efficiency',
                        'Right: Number of Tandem Repeats (-ologies)',
                        'Right: Length of homology',
                        'Right junction predicted efficiency'
                    ]



                    combined_df_cart = combined_df_cart[column_order]
                    combined_df_cart = combined_df_cart.sort_values('Pythia Integration Score', ascending=False)

                    # Round off to two decimal places for the specified columns
                    combined_df_cart['Pythia Integration Score'] = combined_df_cart['Pythia Integration Score'].round(2)
                    combined_df_cart['Left junction predicted efficiency'] = combined_df_cart['Left junction predicted efficiency'].round(2)
                    combined_df_cart['Right junction predicted efficiency'] = combined_df_cart['Right junction predicted efficiency'].round(2)

                    title_style_left = alt.TitleParams(
                        text='Left junction',
                        fontSize=16,
                        fontWeight='normal',
                        color='black',
                        anchor='start',
                        offset=10,
                        dy=-10
                    )

                    heatmap_left = alt.Chart(df_filtered_left).mark_rect().encode(
                        x=alt.X('Amount of trimologies:O', title='Number of Tandem Repeats (-ologies)'),
                        y=alt.Y('Homol_length:O', title='Length of left homology'),
                        color=alt.Color('Predicted frequency:Q', title='Predicted frequency'),
                        tooltip=['Amount of trimologies', 'Homol_length', 'Predicted frequency']
                    ).properties(
                        width=250,
                        height=250,
                        title=title_style_left
                    )

                    title_style_middle = alt.TitleParams(
                        text='Right junction',
                        fontSize=16,
                        fontWeight='normal',
                        color='black',
                        anchor='start',
                        offset=10,
                        dy=-10
                    )

                    heatmap_right = alt.Chart(df_filtered_right).mark_rect().encode(
                        x=alt.X('Amount of trimologies:O', title='Number of Tandem Repeats (-ologies)'),
                        y=alt.Y('Homol_length:O', title='Length of right homology'),
                        color=alt.Color('Predicted frequency:Q', title='Predicted frequency'),
                        tooltip=['Amount of trimologies', 'Homol_length', 'Predicted frequency']
                    ).properties(
                        width=250,
                        height=250,
                        title=title_style_middle
                    )

                    title_style_right = alt.TitleParams(
                        text='Combined score - Pythia Integration Score',
                        fontSize=16,
                        fontWeight='normal',
                        color='black',
                        anchor='start',
                        offset=10,
                        dy=-10
                    )

                    heatmap_combined = alt.Chart(df_combined).mark_rect().encode(
                        x=alt.X('Amount of trimologies:O', title='Number of Tandem Repeats (-ologies)'),
                        y=alt.Y('Homol_length:O', title='Length of homology (both sides)'),
                        color=alt.Color('Predicted frequency:Q', title='Predicted frequency'),
                        tooltip=['Amount of trimologies', 'Homol_length', 'Predicted frequency']
                    ).properties(
                        width=250,
                        height=250,
                        title=title_style_right
                    )

                    table_component2 = dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in combined_df_cart.columns],
                        data=combined_df_cart.to_dict('records'),
                        sort_action='native',
                        sort_mode='multi',
                        sort_by=[{'column_id': 'Pythia Integration Score', 'direction': 'desc'}],
                        page_current=0,
                        page_size=20,
                        page_action='native',
                        style_table={'overflowX': 'auto', 'maxWidth': '100%'},
                        style_cell={
                            'minWidth': '40px', 'width': 'auto', 'maxWidth': '180px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'textAlign': 'center',
                            'whiteSpace': 'nowrap'
                        },
                        style_header={
                            'backgroundColor': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'lineHeight': '1.2',
                            'paddingTop': '6px',
                            'paddingBottom': '6px',
                        },
                        css=[{
                            'selector': '.previous-next-container',
                            'rule': 'color: #1f2937 !important; font-weight: 500;'
                        }, {
                            'selector': '.previous-next-container input',
                            'rule': 'color: #1f2937 !important; background-color: #ffffff !important; font-weight: 600; text-align: center;'
                        }]
                    )

                    heatmap_top = alt.hconcat(heatmap_left, heatmap_right)
                    heatmap_html2 = heatmap_top.to_html()

                    top_row = combined_df_cart.loc[combined_df_cart['Pythia Integration Score'].idxmax()]

                    left_tandem_repeats = int(top_row['Left: Number of Tandem Repeats (-ologies)'])
                    left_homology_length = int(top_row['Left: Length of homology'])
                    left_efficiency = round(top_row['Left junction predicted efficiency'], 2)
                    right_tandem_repeats = int(top_row['Right: Number of Tandem Repeats (-ologies)'])
                    right_homology_length = int(top_row['Right: Length of homology'])
                    right_efficiency = round(top_row['Right junction predicted efficiency'], 2)
                    trimology_score = round(top_row['Pythia Integration Score'], 2)

                    input_upper = input_box_value.upper()

                    input_2_upper = input_box_2_value.upper()

                    # Slice the last three characters from the first input value
                    last_three_chars = input_upper[-left_homology_length:]

                    # Slice the first three characters from the second input value
                    first_three_chars = input_2_upper[:right_homology_length]

                    # Concatenate the sliced parts
                    result_text = f"Your repair casette is {last_three_chars * left_tandem_repeats} - transgene casette as entered above - {first_three_chars * right_tandem_repeats}"

                    formatted_string_part_1 = "Your top combination is:"
                    formatted_string_part_2 = f"On the left: {left_tandem_repeats} tandem repeats of {left_homology_length} basepairs, leading to a left efficiency of {left_efficiency}%"
                    formatted_string_part_3 = f"On the right: {right_tandem_repeats} tandem repeats of {right_homology_length} basepairs, leading to a right efficiency of {right_efficiency}%"
                    formatted_string_part_4 = f"yielding a combined score of {trimology_score}."

                    # Create a Div with the formatted strings using html.P and html.Br for line breaks

        # Create a Div with the formatted strings using html.P for line breaks
                    top_combination_div = html.Div(
                        [
                            html.P(formatted_string_part_1),
                            html.P(formatted_string_part_2),
                            html.P(formatted_string_part_3),
                            html.P(formatted_string_part_4),
                            html.P(result_text)
                        ],
                        style={'margin': '0.5em 0'}
                    )

                    # Create unified results container for integration
                    unified_results = html.Div([
                        html.H2("Integration Analysis Results", className="results-header"),
                        html.Div([top_combination_div], style={'textAlign': 'center', 'marginBottom': '2em'}),
                        html.Div([
                            html.Iframe(srcDoc=heatmap_html2, style={"width": "100%", "height": "360px", "border": "none"})
                        ], className="results-heatmap"),
                        html.Div([
                            html.Div([
                                html.Button(
                                    '\U0001f4e5 Download Table as Excel',
                                    id='download-integration-button',
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
                            table_component2
                        ], className="results-table")
                    ], className="unified-results-container")

                    # Store metadata for Excel export
                    metadata = {
                        'cassette': input_box_3_value,
                        'left_arm': input_box_value,
                        'right_arm': input_box_2_value
                    }

                    return unified_results, combined_df_cart.to_dict('records'), metadata, ''

                except Exception as e:
                    # If an error is caught, return an error message
                    return html.Div(f'Error processing the heatmap: {str(e)}', style={'color': 'red', 'textAlign': 'center', 'margin': '2em'}), None, None, ''


            elif input_box_3_value and input_box_4_value and not input_box_value and not input_box_2_value:

                # Validate sequences contain only ACTG
                is_valid, error_msg = validate_sequence_chars(input_box_4_value, "Genomic target sequence")
                if not is_valid:
                    return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

                is_valid, error_msg = validate_sequence_chars(input_box_3_value, "Transgene cassette")
                if not is_valid:
                    return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

                if input_box_context_value:
                    is_valid, error_msg = validate_sequence_chars(input_box_context_value, "Genomic context")
                    if not is_valid:
                        return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

                    # Validate that context matches target (remove 50bp from each end)
                    target_upper = input_box_4_value.upper().strip()
                    context_upper = input_box_context_value.upper().strip()

                    if len(context_upper) >= 100:
                        context_middle = context_upper[50:-50]
                        if context_middle != target_upper:
                            return html.Div([
                                html.P('Invalid entry: The genomic context doesn\'t match the target site', style={'fontWeight': '600', 'marginBottom': '0.5rem'}),
                                html.P('The context should be: 50bp upstream + your target sequence + 50bp downstream', style={'fontSize': '0.9rem', 'marginBottom': '0.5rem'}),
                                html.P('Please check that the middle part of your context (after removing 50bp from each end) matches your target sequence exactly.', style={'fontSize': '0.9rem'})
                            ], style={'color': 'red', 'textAlign': 'center', 'margin': '2em'}), None, None, ''
                    else:
                        return html.Div([
                            html.P('Invalid entry: Genomic context is too short', style={'fontWeight': '600', 'marginBottom': '0.5rem'}),
                            html.P('The context must be at least 100bp long (your target sequence + 50bp on each side)', style={'fontSize': '0.9rem', 'marginBottom': '0.5rem'}),
                            html.P('Please provide more flanking sequence around your target site.', style={'fontSize': '0.9rem'})
                        ], style={'color': 'orange', 'textAlign': 'center', 'margin': '2em'}), None, None, ''

                try:
                    max_integration_scores = process_pythia_integration_with_gRNA(input_box_4_value.upper(), input_box_3_value.upper(), dropdown_value, 'integration', input_box_context_value.upper())

                    #max_integration_scores.to_csv("testoutput.csv")

                    max_integration_scores.drop(['integration_score_max', 'integration_score_float', "Revcomp_right_repair_arm", 'Forward_Primer', 'Reverse_Primer'], axis=1, inplace=True)

                    # Rename columns
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

                    table_component3 = dash_table.DataTable(
                        id='integration-table-grna',
                        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in max_integration_scores.columns],
                        data=max_integration_scores.to_dict('records'),
                        sort_action='native',
                        sort_mode='multi',
                        sort_by=[{'column_id': 'Pythia Integration Score', 'direction': 'desc'}],
                        page_current=0,
                        page_size=10,
                        page_action='native',
                        style_table={
                            'height': '350px',  # Fixed height to enable vertical scrolling
                            'overflowY': 'auto',  # Enable vertical scrolling
                            'overflowX': 'auto',  # Enable horizontal scrolling to manage additional columns
                            'maxWidth': '100%'  # Respect parent container width
                        },
                        style_cell={
                            'minWidth': '40px', 'width': 'auto', 'maxWidth': '180px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'textAlign': 'center',
                            'whiteSpace': 'nowrap'
                        },
                        style_cell_conditional=[
                            # Score columns - compact
                            {'if': {'column_id': 'Pythia Integration Score'}, 'maxWidth': '120px'},
                            {'if': {'column_id': 'CRISPRScan score'}, 'maxWidth': '80px'},
                            {'if': {'column_id': 'Left junction predicted efficiency'}, 'maxWidth': '100px'},
                            {'if': {'column_id': 'Right junction predicted efficiency'}, 'maxWidth': '100px'},
                            # Sequence columns - wider for readability
                            {'if': {'column_id': 'left_repair_arm'}, 'maxWidth': '250px'},
                            {'if': {'column_id': 'right_repair_arm'}, 'maxWidth': '250px'},
                            {'if': {'column_id': 'Fw primer with homology overhangs'}, 'maxWidth': '300px'},
                            {'if': {'column_id': 'Rv primer with homology overhangs'}, 'maxWidth': '300px'},
                            # ID columns - medium width
                            {'if': {'column_id': 'gRNA'}, 'maxWidth': '150px'},
                            {'if': {'column_id': 'strand'}, 'maxWidth': '60px'},
                            {'if': {'column_id': 'location'}, 'maxWidth': '80px'}
                        ],
                        style_header={
                            'backgroundColor': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'lineHeight': '1.2',
                            'paddingTop': '6px',
                            'paddingBottom': '6px',
                        },
                        css=[{
                            'selector': '.previous-next-container',
                            'rule': 'color: #1f2937 !important; font-weight: 500;'
                        }, {
                            'selector': '.previous-next-container input',
                            'rule': 'color: #1f2937 !important; background-color: #ffffff !important; font-weight: 600; text-align: center;'
                        }]
                    )


                    # Create unified results container for gRNA integration
                    unified_results = html.Div([
                        html.H2("Integration Analysis Results", className="results-header"),
                        html.P("The table below shows the optimal repair templates and primers for your integration target, sorted by Pythia Integration Score.",
                               style={'textAlign': 'center', 'marginBottom': '2em', 'color': 'var(--text-secondary)'}),
                        html.Div([
                            html.Div([
                                html.Button(
                                    '\U0001f4e5 Download Table as Excel',
                                    id='download-integration-button',
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
                            table_component3
                        ], className="results-table")
                    ], className="unified-results-container")

                    # Store metadata for Excel export
                    metadata = {
                        'cassette': input_box_3_value,
                        'context': input_box_4_value
                    }

                    return unified_results, max_integration_scores.to_dict('records'), metadata, ''

                except Exception as e:
                    return html.Div(f'Error processing: {str(e)}', style={'color': 'red', 'textAlign': 'center', 'margin': '2em'}), None, None, ''




            elif input_box_3_value and input_box_4_value and input_box_value and input_box_2_value:
                return html.Div('Please choose between either Step 2 - left workflow (you already know which gRNA you want to use) or step 2 - right workflow (where gRNAs are designed for you). Only one of both can have data entry.', style={'color': 'orange', 'textAlign': 'center', 'margin': '2em', 'fontSize': '1.1em'}), None, None, ''


        # If n_clicks is 0 or None, return empty components
        return html.Div(), None, None, ''

    # Callback to show/hide modal when download button is clicked
    @app.callback(
        Output('integration-download-modal', 'is_open'),
        [Input('download-integration-button', 'n_clicks'),
         Input('integration-download-confirm-btn', 'n_clicks')],
        [State('integration-warning-acknowledged', 'data')],
        prevent_initial_call=True
    )
    def handle_integration_download_modal(download_clicks, confirm_clicks, warning_acknowledged):
        ctx = dash.callback_context
        if not ctx.triggered:
            return False

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'download-integration-button':
            # Only show modal if button was actually clicked (n_clicks > 0)
            if download_clicks and download_clicks > 0:
                # User clicked download - show modal if not already acknowledged
                if warning_acknowledged:
                    return False
                else:
                    return True
            return False

        elif trigger_id == 'integration-download-confirm-btn':
            # User confirmed - close modal
            return False

        return False

    # Callback to mark warning as acknowledged
    @app.callback(
        Output('integration-warning-acknowledged', 'data'),
        Input('integration-download-confirm-btn', 'n_clicks'),
        State('integration-dont-show-again-checkbox', 'value'),
        prevent_initial_call=True
    )
    def mark_integration_warning_acknowledged(n_clicks, dont_show):
        if n_clicks and 'hide' in (dont_show or []):
            return True
        return dash.no_update

    # Callback to download integration table as Excel
    @app.callback(
        Output('download-integration-excel', 'data'),
        [Input('integration-download-confirm-btn', 'n_clicks'),
         Input('download-integration-button', 'n_clicks')],
        [State('integration-table-data-store', 'data'),
         State('integration-metadata-store', 'data'),
         State('integration-warning-acknowledged', 'data')],
        prevent_initial_call=True
    )
    def download_integration_table(confirm_clicks, download_clicks, table_data, metadata, warning_acknowledged):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Only proceed if: (1) confirm button clicked, OR (2) download button clicked AND already acknowledged
        if trigger_id == 'integration-download-confirm-btn':
            # User just confirmed in modal - proceed
            should_download = True
        elif trigger_id == 'download-integration-button' and warning_acknowledged:
            # User clicked download and already acknowledged - proceed
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
            user_left = metadata.get('left_arm', '')
            user_right = metadata.get('right_arm', '')

            if 'Left Repair Arm' in top_result and 'Right Repair Arm' in top_result:
                left_arm = top_result['Left Repair Arm']
                right_arm = top_result['Right Repair Arm']
            else:
                left_homology_seq = user_left[-left_homology:] if user_left else ''
                left_arm = left_homology_seq * left_tandem
                right_homology_seq = user_right[:right_homology] if user_right else ''
                right_arm = right_homology_seq * right_tandem

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet('Integration Results')
                writer.sheets['Integration Results'] = worksheet

                title_format = workbook.add_format({'bold': True, 'font_size': 14})
                header_format = workbook.add_format({'bold': True, 'font_size': 11})
                normal_format = workbook.add_format({'font_size': 10})

                row = 0

                if user_left and user_right:
                    worksheet.write(row, 0, f"Integration analysis for {user_left} - DSB - {user_right}", title_format)
                else:
                    worksheet.write(row, 0, "Integration analysis", title_format)
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

                df.to_excel(writer, sheet_name='Integration Results', startrow=row, index=False)

                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(idx, idx, min(max_len, 50))

            output.seek(0)
            return dcc.send_bytes(output.getvalue(), "pythia_integration_results.xlsx")

        return dash.no_update
