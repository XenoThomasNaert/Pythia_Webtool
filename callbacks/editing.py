import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import altair as alt
import pandas as pd
import io
from Pythia_editing_withgrnafinder import process_pythia_editing_withgRNAfinder
from utils.validation import validate_sequence_chars
from utils.tooltips import indelphi_model_tooltip

alt.data_transformers.disable_max_rows()

page_2_layout = html.Div([
    html.H1('Pythia Editing', style={"marginTop": "0.5em", "marginBottom": "0.5em", "paddingBottom": "0.2em", "textAlign": "center"}),
    html.P('Generate repair templates for precise single-nucleotide edits using microhomology-mediated repair.',
           style={"textAlign": "center", "color": "#6B7280", "fontSize": "1.1rem", "marginBottom": "2em", "maxWidth": "800px", "margin": "0 auto 2em auto"}),

    # Step 1: Model Selection Card
    html.Div([
        html.Div([
            html.Div([
                html.H3('Step 1: Select inDelphi Model', className='step-title',
                        style={'display': 'inline', 'margin': 0}),
                indelphi_model_tooltip(),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.P('Choose the appropriate cell type model for your gene editing experiment', className='step-description')
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

    # Step 2: Sequence Input Card
    html.Div([
        html.Div([
            html.H3('Step 2: Enter Sequences', className='step-title'),
            html.P('This module takes an input sequence and a mutated input sequence, then designs gRNAs and corresponding optimal ssODN repair templates to perform base exchanges', className='step-description')
        ], className='step-header'),
        html.Div([
            html.Label('Original Genomic Sequence:', className='form-label'),
            html.P('Provide at least 80 bp of genetic sequence context left and right of your intended mutation site(s)', className='help-text'),
            html.Div([
                dcc.Textarea(
                    id='input-box',
                    placeholder='Enter the original genomic sequence with at least 80 bp of context around mutation sites',
                    className='sequence-input',
                    style={'width': '100%', 'minHeight': '80px', 'resize': 'vertical'}
                ),
                html.P('Example input:', className='input-examples-label'),
                html.Div([
                    html.Button(
                        'eGFP original sequence',
                        id='example-button-original',
                        n_clicks=0,
                        className='example-button'
                    )
                ], className='example-grid')
            ], className='input-with-examples'),

            html.Label('Mutated Genomic Sequence:', className='form-label'),
            html.P('Enter the genomic sequence with the desired base changes', className='help-text'),
            html.Div([
                dcc.Textarea(
                    id='input-box-3',
                    placeholder='Enter the genomic sequence with your desired base changes/mutations',
                    className='sequence-input',
                    style={'width': '100%', 'minHeight': '80px', 'resize': 'vertical'}
                ),
                html.P('Example input:', className='input-examples-label'),
                html.Div([
                    html.Button(
                        'eBFP mutated sequence',
                        id='example-button-mutated',
                        n_clicks=0,
                        className='example-button'
                    )
                ], className='example-grid')
            ], className='input-with-examples')
        ], className='step-content')
    ], className='step-card'),

    # Step 3: Parameters Card
    html.Div([
        html.Div([
            html.H3('Step 3: Configure Parameters', className='step-title'),
            html.P('Set the repair arm lengths and maximum distance for CRISPR targeting', className='step-description')
        ], className='step-header'),
        html.Div([
            html.Label('Repair Arm Lengths:', className='form-label'),
            html.P('Enter the minimal and maximal length of repair arms (5-40 bp)', className='help-text'),
            html.Div([
                html.Div([
                    html.Label('Minimum Length:', style={'fontWeight': '500', 'fontSize': '0.875rem', 'marginBottom': '0.5rem', 'display': 'block'}),
                    dcc.Input(
                        id='input-box-21',
                        type='number',
                        placeholder='Minimal length',
                        value=15,
                        min=5,
                        max=40,
                        style={'width': '100%', 'padding': '0.75rem', 'border': '2px solid #E5E7EB', 'borderRadius': '0.5rem'}
                    )
                ], style={'flex': '1', 'marginRight': '1rem'}),
                html.Div([
                    html.Label('Maximum Length:', style={'fontWeight': '500', 'fontSize': '0.875rem', 'marginBottom': '0.5rem', 'display': 'block'}),
                    dcc.Input(
                        id='input-box-22',
                        type='number',
                        placeholder='Maximal length',
                        value=20,
                        min=5,
                        max=40,
                        style={'width': '100%', 'padding': '0.75rem', 'border': '2px solid #E5E7EB', 'borderRadius': '0.5rem'}
                    )
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'gap': '1rem', 'marginBottom': '1.5rem'}),

            html.Label('Maximum Cut Distance:', className='form-label'),
            html.P('Maximum distance between CRISPR/Cas9 double-stranded break and intended point mutation', className='help-text'),
            dcc.Input(
                id='input-box-419',
                type='number',
                placeholder='Max distance to cut',
                value=20,
                style={'width': '200px', 'padding': '0.75rem', 'border': '2px solid #E5E7EB', 'borderRadius': '0.5rem'}
            )
        ], className='step-content')
    ], className='step-card'),
    # Submit Section
    html.Div([
        html.Button(
            'Run Analysis',
            id='submit-button-page2',
            className='submit-button',
            n_clicks=0
        ),
        html.P('Default sequences are eGFP → eBFP, please expect this to take 3-4 minutes! Computing time scales logarithmically as the difference between maximal and minimal lengths of repair arms increases.',
               className='processing-time')
    ], style={'textAlign': 'center', 'margin': '2rem 0'}),
    dcc.Loading(
        id='loading-editing',
        type='circle',
        children=html.Div([
            html.Div(id='heatmap-editing-output'),
            html.Div(id='error-message2'),
        ])
    ),
    dcc.Store(id='editing-table-data-store'),
    dcc.Download(id='download-editing-excel'),
],
    style={
        "backgroundColor": "var(--background-secondary)",
        "margin": "0",
        "padding": "2rem",
        "minHeight": "100vh"
    }
)


def register_callbacks(app):

    # Callback for example buttons on Editing page
    @app.callback(
        [Output('input-box', 'value', allow_duplicate=True),
         Output('input-box-3', 'value', allow_duplicate=True)],
        [Input('example-button-original', 'n_clicks'),
         Input('example-button-mutated', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_editing_example_sequences(n_clicks_original, n_clicks_mutated):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'example-button-original':
            # eGFP original sequence
            return 'TGGACGGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTACGGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACCCTCGTGACCACCCTGACCTACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAGCAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTCTTCAAGGACGACGGCAACTACAAGACCCGCGC', dash.no_update
        elif button_id == 'example-button-mutated':
            # eBFP mutated sequence (L221H and F223Y mutations for blue fluorescence)
            return dash.no_update, 'TGGACGGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTACGGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACCCTCGTGACCACCCTGAGCCACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAGCAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTCTTCAAGGACGACGGCAACTACAAGACCCGCGC'

        return dash.no_update, dash.no_update

    @app.callback(
        [
            Output('heatmap-editing-output', 'children'),
            Output('error-message2', 'children'),
            Output('editing-table-data-store', 'data'),
        ],
        [Input('submit-button-page2', 'n_clicks')],
        [State('dropdown-menu', 'value'),
         State('input-box', 'value'),
         State('input-box-3', 'value'),
         State('input-box-21', 'value'),
         State('input-box-22', 'value'),
         State('input-box-419', 'value'),]
    )

    def update_output_and_heatmap_editing(n_clicks, dropdown_value, geneticsequence, geneticsequencemut, min_length, max_length, max_distance):
        if n_clicks is None or n_clicks < 1:
            return '', '', None  # No updates if button hasn't been clicked

        # Validate sequence inputs contain only ACTG
        is_valid, error_msg = validate_sequence_chars(geneticsequence, "Original sequence")
        if not is_valid:
            return '', html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'}), None

        is_valid, error_msg = validate_sequence_chars(geneticsequencemut, "Edited sequence")
        if not is_valid:
            return '', html.Div(error_msg, style={'color': 'red', 'padding': '1rem', 'backgroundColor': '#FEE', 'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid red'}), None

        try:
            result_editing_wgrna = process_pythia_editing_withgRNAfinder(dropdown_value, geneticsequence.upper(), geneticsequencemut.upper(), min_length, max_length, max_distance)
        except Exception as e:
            error_div = html.Div([
                html.Strong("Analysis failed"),
                html.P(str(e), style={'marginTop': '0.5rem', 'fontFamily': 'monospace', 'fontSize': '0.85rem'})
            ], style={
                'color': '#7F1D1D', 'padding': '1rem', 'backgroundColor': '#FEE2E2',
                'borderRadius': '0.5rem', 'marginTop': '1rem', 'border': '1px solid #FCA5A5'
            })
            return html.Div(), error_div, None

        # Function to create a heatmap for a given gRNA
        def create_heatmap(df, gRNA):
            chart = alt.Chart(df[df['gRNA'] == gRNA]).mark_rect().encode(
                x=alt.X('Loop index_right:O', title='Length of left repair arm'),
                y=alt.Y('Loop index:O', title='Length of right repair arm', sort="descending"),
                color=alt.Color('Joint probability:Q', title='Predicted frequency'),
                tooltip=["Predicted frequency:Q", "Predicted frequency_right:Q", 'Joint probability:Q']
            ).properties(
                width=200,  # Adjust width as needed to fit all plots
                height=200,  # Adjust height as needed to fit all plots
                title=f'gRNA: {gRNA}'
            )
            return chart

        # Get unique gRNA values
        unique_gRNAs = result_editing_wgrna['gRNA'].unique()

        # Create a list of heatmaps for each gRNA
        heatmaps = [create_heatmap(result_editing_wgrna, gRNA) for gRNA in unique_gRNAs]

        # Function to split list into chunks
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        # Split heatmaps into chunks of 4
        heatmap_chunks = list(chunks(heatmaps, 4))

        # Create horizontal concatenations for each chunk
        hconcat_charts = [alt.hconcat(*chunk) for chunk in heatmap_chunks]

        # Vertically concatenate the horizontal concatenations
        if len(hconcat_charts) > 1:
            final_chart = alt.vconcat(*hconcat_charts).configure_legend(
                titleFontSize=14,
                labelFontSize=12,
                titleFontWeight='normal',
                labelFontWeight='normal'
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14,
                labelFontWeight='normal',
                titleFontWeight='normal'
            )
        elif len(hconcat_charts) == 1:
            final_chart = hconcat_charts[0].configure_legend(
                titleFontSize=14,
                labelFontSize=12,
                titleFontWeight='normal',
                labelFontWeight='normal'
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14,
                labelFontWeight='normal',
                titleFontWeight='normal'
            )
        else:
            # Handle case where no charts are created
            final_chart = alt.Chart().mark_text(text="No data available for visualization")

        # Display the final concatenated chart
        final_chart

            # Rename columns
        result_editing_wgrna = result_editing_wgrna.rename(columns={
                'Joint probability': 'Pythia score',
                'Loop index': 'Length of left repair arm',
                'Loop index_right': 'Length of right repair arm',
                'Predicted frequency': 'Pythia - Left junction',
                'Predicted frequency_right': 'Pythia - right junction',
                'primer_to_order': 'ssODN repair template',
                'gRNA': 'gRNA'
        })

            # Reorder columns
        result_editing_wgrna = result_editing_wgrna[
                [
                    'gRNA',
                    'Pythia score',
                    'CRISPRSCan Score',
                    'Length of left repair arm',
                    'Pythia - Left junction',
                    'Length of right repair arm',
                    'Pythia - right junction',
                    "ssODN repair template"
                ]
            ]

        result_editing_wgrna = result_editing_wgrna.sort_values(by='Pythia score', ascending=False)

        result_editing_wgrna['Pythia score'] = result_editing_wgrna['Pythia score'].round(2)
        result_editing_wgrna['Pythia - Left junction'] = result_editing_wgrna['Pythia - Left junction'].round(2)
        result_editing_wgrna['Pythia - right junction'] = result_editing_wgrna['Pythia - right junction'].round(2)

        table_data = result_editing_wgrna.to_dict('records')

        table_component = dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in result_editing_wgrna.columns],
            data=table_data,
            sort_action='native',
            sort_mode='multi',
            sort_by=[{'column_id': 'Pythia score', 'direction': 'desc'}],
            page_current=0,
            page_size=10,
            page_action='native',
            style_table={'overflowX': 'auto', 'maxWidth': '100%'},
            style_cell={
                'minWidth': '60px', 'width': 'auto',
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
                'lineHeight': '1.3',
            },
            style_cell_conditional=[
                {'if': {'column_id': 'ssODN repair template'}, 'maxWidth': '350px'},
            ],
            css=[{
                'selector': '.previous-next-container',
                'rule': 'color: #1f2937 !important; font-weight: 500;'
            }, {
                'selector': '.previous-next-container input',
                'rule': 'color: #1f2937 !important; background-color: #ffffff !important; font-weight: 600; text-align: center;'
            }]
        )


        heatmap_html = final_chart.to_html()

        # Create unified results container
        unified_results = html.Div([
            html.H2("Analysis Results", className="results-header"),
            html.P("The heatmaps below show predicted repair frequencies for different gRNAs and repair arm lengths. The table contains detailed results sorted by Pythia score.",
                   style={'textAlign': 'center', 'marginBottom': '2em', 'color': 'var(--text-secondary)'}),
            html.Div([
                html.Iframe(srcDoc=heatmap_html, style={"width": "100%", "height": "650px", "border": "none"})
            ], className="results-heatmap"),
            html.Div([
                html.Div([
                    html.Button(
                        '\U0001f4e5 Download Table as Excel',
                        id='download-editing-button',
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
        ], className="unified-results-container")

        return (
            unified_results,  # Unified results component
            html.Div(),       # Error message component (empty on success)
            table_data        # Store table data for Excel download
            )

    @app.callback(
        Output('download-editing-excel', 'data'),
        Input('download-editing-button', 'n_clicks'),
        State('editing-table-data-store', 'data'),
        prevent_initial_call=True
    )
    def download_editing_table(n_clicks, table_data):
        if not n_clicks or not table_data:
            return dash.no_update
        df = pd.DataFrame(table_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Editing Results')
            worksheet = writer.sheets['Editing Results']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, min(max_len, 60))
        output.seek(0)
        return dcc.send_bytes(output.getvalue(), "pythia_editing_results.xlsx")
