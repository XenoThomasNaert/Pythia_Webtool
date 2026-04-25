import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd

from utils.validation import validate_sequence_chars
from pythia_integration_gRNA_finder import process_pythia_integration_with_gRNA
from utils.tooltips import indelphi_model_tooltip


# ===================================================================
# INTRON TAGGING LAYOUT
# ===================================================================

page_tagging_intron_layout = html.Div([
    html.H1('Pythia Intron Tagging', style={"marginTop": "0.5em", "marginBottom": "0.5em", "paddingBottom": "0.2em", "textAlign": "center"}),
    html.P('Design intron-mediated tagging strategies for last exon replacement with targeted transgene insertion.',
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
                id='dropdown-menu-intron-tagging',
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

    # Step 2: Intron Target Card
    html.Div([
        html.Div([
            html.H3('Step 2: Intron Target', className='step-title'),
            html.P('Provide the intron sequence where you want to target for last exon replacement (the last intron of the gene)', className='step-description')
        ], className='step-header'),
        html.Div([
            html.Label('Intron sequence:', style={'fontWeight': '600', 'marginBottom': '0.5em', 'display': 'block'}),
            html.Div([
                dcc.Input(
                    id='input-box-intron-target',
                    type='text',
                    placeholder='Enter your intron sequence',
                    className='sequence-input',
                    style={'width': '100%'}
                )
            ], className='input-with-examples'),
            html.Label('Intron + 50bp context:', style={'fontWeight': '600', 'marginTop': '1.5rem', 'marginBottom': '0.5em', 'display': 'block'}),
            html.P([
                'Provide 50 bp of flanking sequence on each side (100 bp total around your intron) ',
                html.Span('(Include 50 bp upstream + your intron sequence + 50 bp downstream)',
                          style={'fontStyle': 'italic', 'color': '#6B7280'}),
                ' ',
                html.Span([
                    html.Span('ⓘ', style={'color': '#3B82F6', 'cursor': 'help', 'fontSize': '1rem', 'fontWeight': 'bold'}),
                    html.Span('Why? CRITICAL STEP: The extended flanking context is required for accurate InDelphi predictions and microhomology identification. The deep learning algorithm requires genomic sequence both upstream and downstream of the integration site to properly evaluate microhomology opportunities and predict repair outcomes. The complete sequence in this box should be structured as: [50 bp upstream genomic sequence] - [Your intron sequence (from box above)] - [50 bp downstream genomic sequence]. Without sufficient flanking sequence, the algorithm cannot properly assess repair efficiency and may truncate predictions at the sequence boundaries.',
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
                    id='input-box-intron-context',
                    type='text',
                    placeholder='Enter the intron with additional context',
                    className='sequence-input',
                    style={'width': '100%'}
                )
            ], className='input-with-examples'),
            # Example button for intron
            html.Button(
                'Example: RB1-201 (human)',
                id='example-intron-button',
                n_clicks=0,
                className='submit-button',
                style={'marginTop': '1rem', 'width': 'auto', 'padding': '0.75rem 1.5rem', 'textTransform': 'none'}
            )
        ], className='step-content')
    ], className='step-card'),

    # Step 3: Repair Template Card
    html.Div([
        html.Div([
            html.H3('Step 3: Repair Template', className='step-title'),
            html.P('Design your repair template with splice acceptor, last exon, and tag', className='step-description')
        ], className='step-header'),
        html.Div([
            html.Label('Repair Template Sequence:', style={'fontWeight': '600', 'marginBottom': '0.5em', 'display': 'block'}),
            html.P([
                'The repair template should contain a correct splice acceptor site, followed by the last exon without a stop codon, then your desired tag sequence (e.g., fluorescent protein or epitope tag). For optimal repair template design, refer to ',
                html.A('Naert et al., Nature Biotechnology', href='https://doi.org/10.1038/s41587-021-01108-x', target='_blank', style={'color': '#2E5BFF', 'textDecoration': 'underline'}),
                '.'
            ], style={'fontSize': '0.875rem', 'color': 'var(--text-secondary)', 'marginBottom': '1rem', 'fontStyle': 'italic', 'lineHeight': '1.6'}),
            html.Div([
                dcc.Textarea(
                    id='input-box-intron-repair-template',
                    placeholder='Enter repair template: splice acceptor + last exon without stop + tags + stop codon',
                    className='sequence-input',
                    style={'width': '100%', 'minHeight': '120px', 'resize': 'vertical'}
                )
            ], className='input-with-examples'),
            # Example button for repair template
            html.Button(
                'Example: SA-RB1lastExon-mBaoJin-AlphaTag-FlagTag-SV40polyA',
                id='example-intron-repair-button',
                n_clicks=0,
                className='submit-button',
                style={'marginTop': '1rem', 'width': 'auto', 'padding': '0.75rem 1.5rem', 'textTransform': 'none'}
            )
        ], className='step-content')
    ], className='step-card'),

    # Submit Section
    html.Div([
        html.Button(
            'Run Analysis',
            id='submit-button-intron-tagging',
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
    html.Div(id='error-message-intron-tagging', children=''),
    dcc.Store(id='intron-tagging-table-data-store'),
    dcc.Store(id='intron-tagging-metadata-store'),
    dcc.Download(id='download-intron-tagging-excel'),

    # Off-target warning modal for Intron Tagging downloads
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
                id="intron-tagging-dont-show-again-checkbox",
                options=[{"label": " Don't show this warning again for this session", "value": "hide"}],
                value=[],
                style={'marginRight': 'auto', 'fontSize': '14px'}
            ),
            dbc.Button("I Understand - Proceed with Download", id="intron-tagging-download-confirm-btn", n_clicks=0, style={'backgroundColor': '#10B981', 'borderColor': '#10B981'})
        ], style={'display': 'flex', 'alignItems': 'center'}),
    ], id="intron-tagging-download-modal", is_open=False, size="lg"),

    # Store for download flow
    dcc.Store(id="intron-tagging-warning-acknowledged", storage_type='memory', data=False),

    dcc.Loading(
        id='loading-intron-tagging',
        type='circle',
        children=html.Div(id='heatmap-intron-tagging-container')
    )
], style={'padding': '2em', 'maxWidth': '1000px', 'margin': '0 auto'})


# ===================================================================
# INTRON TAGGING CALLBACKS
# ===================================================================

def register_callbacks(app):

    @app.callback(
        [Output('input-box-intron-target', 'value'),
         Output('input-box-intron-context', 'value'),
         Output('input-box-intron-repair-template', 'value')],
        [Input('example-intron-button', 'n_clicks'),
         Input('example-intron-repair-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def populate_intron_example(intron_clicks, repair_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'example-intron-button' and intron_clicks and intron_clicks > 0:
            # RB1-201 (human) - Example intron sequence (partial for example purposes)
            intron = "TTGCTTGGGGTATGTGTTTTATAATTTGTACATACATACGTATTTTTGTGGTACAGGCTTGGAAAAAAATTTACTCACAGGGATATATGATTTTTAAAGATTTGGAGACCACTGTTTTTTTGGGGGGTGGGGAGG"
            # Intron with 50bp context on each side
            intron_context = "CATCTTTTGGGGTACATAAAGTAGAAGTTCTATTTATCTCATTTTAATGTTTGCTTGGGGTATGTGTTTTATAATTTGTACATACATACGTATTTTTGTGGTACAGGCTTGGAAAAAAATTTACTCACAGGGATATATGATTTTTAAAGATTTGGAGACCACTGTTTTTTTGGGGGGTGGGGAGGGAATTTTTTTTTTAATTGATATATCATAGTTATACATATTTTAGGGGTAC"
            return intron, intron_context, dash.no_update
        elif button_id == 'example-intron-repair-button' and repair_clicks and repair_clicks > 0:
            # Example repair template: SA + Last exon of RB1 (no STOP) + Linker + mBaoJin + Linker + AlphaTag + Linker + FlagTag + SV40polyA
            repair_template = "ATCAATGCTGTTAACAGTTCTTCATCCTTTTTCCAGCTTCTACTCGAACACGAATGCAAAAGCAGAAAATGAATGATAGCATGGATACCTCAAACAAGGAAGAGAAAggatcaggaggatcaggaATGGTCTCAAAGGGAGAGGAGGAAAACATGGCTAGTACACCATTTAAATTTCAACTTAAAGGAACCATCAATGGCAAATCGTTTACCGTTGAAGGCGAAGGTGAAGGGAACTCACATGAAGGTTCTCATAAAGGAAAATATGTTTGTACAAGTGGAAAACTACCGATGTCATGGGCAGCACTTGGGACAACCTTTGGTTATGGAATGAAATATTATACCAAATATCCTAGTGGACTGAAGAACTGGTTTCGTGAAGTAATGCCCGGAGGCTTTACCTACGATCGTCATATTCAATATAAAGGCGATGGGAGTATCCATGCAAAACACCAACACTTTATGAAAAATGGGACTTATCACAACATTGTAGAATTTACCGGTCAGGATTTTAAAGAAAATAGTCCAGTCTTAACTGGAGATATGAATGTCTCATTACCGAATGAAGTCCCACAAATACCCAGAGATGATGGAGTAGAATGCCCAGTGACCTTGCTTTATCCTTTATTATCGGATAAATCAAAATACGTCGAGGCTCACCAATATACAATCTGCAAGCCTCTTCATAATCAACCAGCACCTGATGTCCCATATCACTGGATTCGTAAACAATACACACAAAGCAAAGATGATGCCGAGGAACGCGATCATATCTGTCAATCAGAGACTCTCGAAGCACACTTAAAGGGCATGGACGAGCTGTATAAGggatcaggaTCTCGTCTGGAAGAAGAACTGCGTCGTCGTCTGACCGAAggcagcggcGACTACAAGGACCACGACGGTGACTACAAGGACCACGACATCGACTACAAGGACGACGACGACAAGTGAaacttgtttattgcagcttataatggttacaaataaagcaatagcatcacaaatttcacaaataaagcatttttttcactgcattctagttgtggtttgtccaaactcatcaatgtatcttagtt"
            return dash.no_update, dash.no_update, repair_template

        return dash.no_update, dash.no_update, dash.no_update

    # Main intron tagging callback - uses integration logic
    @app.callback(
        [Output('heatmap-intron-tagging-container', 'children'),
         Output('intron-tagging-table-data-store', 'data'),
         Output('intron-tagging-metadata-store', 'data'),
         Output('error-message-intron-tagging', 'children')],
        [Input('submit-button-intron-tagging', 'n_clicks')],
        [State('input-box-intron-target', 'value'),
         State('input-box-intron-context', 'value'),
         State('input-box-intron-repair-template', 'value'),
         State('dropdown-menu-intron-tagging', 'value')],
        prevent_initial_call=True
    )
    def update_intron_tagging_heatmap(n_clicks, intron_target, intron_context, repair_template, dropdown_value):
        if n_clicks is not None and n_clicks > 0:
            # Check if all required fields are filled
            if not repair_template or not intron_context:
                return html.Div('Please fill in all required fields (intron context and repair template)', style={'color': 'orange', 'textAlign': 'center', 'margin': '2em'}), None, None, ''

            # Validate all sequence inputs contain only ACTG
            is_valid, error_msg = validate_sequence_chars(intron_context, "Intron context")
            if not is_valid:
                return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

            is_valid, error_msg = validate_sequence_chars(repair_template, "Repair template")
            if not is_valid:
                return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})

            # If intron_target is provided, perform context matching validation
            if intron_target:
                is_valid, error_msg = validate_sequence_chars(intron_target, "Intron target")
                if not is_valid:
                    return dash.no_update, dash.no_update, dash.no_update, html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'})
                target_upper = intron_target.upper().strip()
                context_upper = intron_context.upper().strip()

                # Validation: Check if context matches target (remove 50bp from each end)
                if len(context_upper) >= 100:
                    context_middle = context_upper[50:-50]
                    if context_middle != target_upper:
                        return html.Div([
                            html.P('Invalid entry: The intron context doesn\'t match the target site', style={'fontWeight': '600', 'marginBottom': '0.5rem'}),
                            html.P('The context should be: 50bp upstream + your intron sequence + 50bp downstream', style={'fontSize': '0.9rem', 'marginBottom': '0.5rem'}),
                            html.P('Please check that the middle part of your context (after removing 50bp from each end) matches your intron sequence exactly.', style={'fontSize': '0.9rem'})
                        ], style={'color': 'red', 'textAlign': 'center', 'margin': '2em'}), None, None, ''
                else:
                    return html.Div('Invalid entry: context must be at least 100bp (intron + 50bp on each side)',
                                    style={'color': 'orange', 'textAlign': 'center', 'margin': '2em'}), None, None, ''

            # Proceed with analysis
            if repair_template and intron_context:
                try:
                    # Determine which sequence to use as the target
                    # If intron_target is provided, use it; otherwise use the full context
                    target_seq = intron_target.upper() if intron_target else intron_context.upper()

                    # Call integration function with 'integration' mode
                    max_integration_scores = process_pythia_integration_with_gRNA(
                        target_seq,                      # The intron sequence
                        repair_template.upper(),         # The repair template
                        dropdown_value,                  # Cell type
                        'integration',                   # Mode
                        intron_context.upper()          # The full context
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
                        id='intron-tagging-table',
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

                    unified_results = html.Div([
                        html.H2("Intron Tagging Results", className="results-header"),
                        html.P("The table below shows the optimal repair templates and primers for intron-mediated tagging, sorted by Pythia Integration Score.",
                               style={'textAlign': 'center', 'marginBottom': '2em', 'color': 'var(--text-secondary)'}),
                        html.Div([
                            html.Div([
                                html.Button(
                                    '📥 Download Table as Excel',
                                    id='download-intron-tagging-button',
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
                                    }
                                )
                            ], style={'textAlign': 'right', 'marginBottom': '0.5em'}),
                            table_component
                        ], className="results-table")
                    ], className='unified-results-container')

                    # Store metadata
                    metadata = {
                        'intron': intron_target if intron_target else intron_context,
                        'context': intron_context,
                        'repair_template': repair_template
                    }

                    return unified_results, max_integration_scores.to_dict('records'), metadata, ''

                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    print(error_message)
                    import traceback
                    traceback.print_exc()
                    return html.Div(error_message, style={'color': 'red', 'textAlign': 'center', 'margin': '2em'}), None, None, ''

        return html.Div(), None, None, ''

    # Callback to show/hide modal when download button is clicked
    @app.callback(
        Output('intron-tagging-download-modal', 'is_open'),
        [Input('download-intron-tagging-button', 'n_clicks'),
         Input('intron-tagging-download-confirm-btn', 'n_clicks')],
        [State('intron-tagging-warning-acknowledged', 'data')],
        prevent_initial_call=True
    )
    def handle_intron_tagging_download_modal(download_clicks, confirm_clicks, warning_acknowledged):
        ctx = dash.callback_context
        if not ctx.triggered:
            return False

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'download-intron-tagging-button':
            # Only show modal if button was actually clicked (n_clicks > 0)
            if download_clicks and download_clicks > 0:
                if warning_acknowledged:
                    return False
                else:
                    return True
            return False

        elif trigger_id == 'intron-tagging-download-confirm-btn':
            return False

        return False

    # Callback to mark warning as acknowledged
    @app.callback(
        Output('intron-tagging-warning-acknowledged', 'data'),
        Input('intron-tagging-download-confirm-btn', 'n_clicks'),
        State('intron-tagging-dont-show-again-checkbox', 'value'),
        prevent_initial_call=True
    )
    def mark_intron_tagging_warning_acknowledged(n_clicks, dont_show):
        if n_clicks and 'hide' in (dont_show or []):
            return True
        return dash.no_update

    # Download callback for intron tagging
    @app.callback(
        Output('download-intron-tagging-excel', 'data'),
        [Input('intron-tagging-download-confirm-btn', 'n_clicks'),
         Input('download-intron-tagging-button', 'n_clicks')],
        [State('intron-tagging-table-data-store', 'data'),
         State('intron-tagging-metadata-store', 'data'),
         State('intron-tagging-warning-acknowledged', 'data')],
        prevent_initial_call=True
    )
    def download_intron_tagging_table(confirm_clicks, download_clicks, table_data, metadata, warning_acknowledged):
        """Download the intron tagging results table as an Excel file"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Only proceed if: (1) confirm button clicked, OR (2) download button clicked AND already acknowledged
        if trigger_id == 'intron-tagging-download-confirm-btn':
            should_download = True
        elif trigger_id == 'download-intron-tagging-button' and warning_acknowledged:
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

            repair_template = metadata.get('repair_template', 'N/A')
            intron_context = metadata.get('context', '')

            if 'Left Repair Arm' in top_result and 'Right Repair Arm' in top_result:
                left_arm = top_result['Left Repair Arm']
                right_arm = top_result['Right Repair Arm']
            else:
                left_homology_seq = intron_context[-left_homology:] if intron_context else ''
                left_arm = left_homology_seq * left_tandem
                right_homology_seq = intron_context[:right_homology] if intron_context else ''
                right_arm = right_homology_seq * right_tandem

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet('Intron Tagging Results')
                writer.sheets['Intron Tagging Results'] = worksheet

                title_format = workbook.add_format({'bold': True, 'font_size': 14})
                header_format = workbook.add_format({'bold': True, 'font_size': 11})
                normal_format = workbook.add_format({'font_size': 10})

                row = 0
                worksheet.write(row, 0, "Intron Tagging Analysis", title_format)
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

                worksheet.write(row, 0, f"Your optimal repair cassette is {left_arm} - {repair_template} - {right_arm}", normal_format)
                row += 2

                worksheet.write(row, 0, f"Used repair template: {repair_template}", normal_format)
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

                df.to_excel(writer, sheet_name='Intron Tagging Results', startrow=row, index=False)

                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(idx, idx, min(max_len, 50))

            output.seek(0)

            return dcc.send_bytes(output.getvalue(), "pythia_intron_tagging_results.xlsx")

        return dash.no_update
