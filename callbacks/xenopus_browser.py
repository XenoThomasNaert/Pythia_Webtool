import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd

# Initialize df_trops as None
df_trops = None

def load_data_trop():
    global df_trops
    if df_trops is None:
        df_trops = pd.read_csv('assets/Xentro10_Cleaned_df.csv')

page_3_layout = html.Div([
    html.Div([
        dcc.Link('Go back to home', href='/'),
        html.H1('Precomputed guides and inDelphi scores across the Xenopus tropicalis genome'),
        html.P(
            'Enter a gene and receive gRNA sequences with precomputed CRISPRScan scores, and precomputed InDelphi predicted percentage of repair via frameshifting and predicted percentage of repair via microhomology mediated end-joining. This is based on our findings in Naert et al, SciRep 2020 (https://doi.org/10.1038/s41598-020-71412-0). In brief, even with high efficiency levels of genome editing, phenotypes may be obscured by proportional presence of in-frame mutations that still produce functional protein. Here, we allow straightforward selection of guide RNAs with predicted repair outcome signatures enriched towards frameshift mutations, allowing maximization of CRISPR/Cas9 phenotype penetrance in the F0 generation.',
            style={'margin': '1em'}
        ),

        dcc.Input(
            id='input-box-trops',
            type='text',
            placeholder='Enter your gene you wish to CRISPR/Cas9',
            className='modern-input',
            style={'width': '500px', 'marginBottom': '0em', 'color': '#1F2937', 'backgroundColor': '#FFFFFF'}
        ),

        html.Button(
            'Submit',
            id='submit-button-tropsa',
            n_clicks=0,
            style={'marginBottom': '1em'}
        ),

        dcc.Loading(
            id='loading-xenopus',
            type='circle',
            children=html.Div(id='table-container3',
                style={'marginBottom': '1em'})
        )


    ],
    style={'margin-left': '8em', 'margin-right': '8em'})
])


def register_callbacks(app):

    @app.callback(
        Output('table-container3', 'children'),
        [Input('submit-button-tropsa', 'n_clicks')],
        [State('input-box-trops', 'value')]
    )
    def update_output(n_clicks, input_value):
        if n_clicks > 0 and input_value:
            # Load data if not already loaded
            load_data_trop()


            input_value = input_value.lower() if len(input_value) <= 20 else None
            gene_input = df_trops[df_trops['Gene name'].isin([input_value])]
            gene_input = gene_input.sort_values(by='Predicted % repair frameshifting', ascending=False)

            return html.Div(  # Wrap the table within a div
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in gene_input.columns],
                    data=gene_input.to_dict('records'),
                    sort_action='native',  # Enables native sorting
                    sort_mode='multi',  # Allows multiple column sorting
                    style_table={'height': '500px', 'overflowY': 'auto', 'overflowX': 'auto', 'maxWidth': '100%'},  # Responsive table sizing
                    style_cell={
                        'minWidth': '60px', 'width': 'auto', 'maxWidth': '200px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'textAlign': 'center',
                        'whiteSpace': 'nowrap'
                    },
                    style_cell_conditional=[
                        # Key result columns - wider for readability
                        {'if': {'column_id': 'Predicted % repair frameshifting'}, 'maxWidth': '180px'},
                        {'if': {'column_id': 'Predicted % repair via MMEJ'}, 'maxWidth': '180px'},
                        {'if': {'column_id': 'CRISPRScan'}, 'maxWidth': '100px'},
                        # Sequence columns
                        {'if': {'column_id': 'Guide RNA sequence'}, 'maxWidth': '150px'},
                        {'if': {'column_id': 'Gene name'}, 'maxWidth': '120px'}
                    ],
                    style_data_conditional=[  # Add conditional formatting
                        {
                            'if': {
                                'column_id': 'CRISPRScan',  # You can change this to the specific column you want to apply the rule to
                                'filter_query': "{CRISPRScan} > 50"  # Use backticks around the column name
                            },
                            'backgroundColor': 'MediumSpringGreen',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'column_id': 'Predicted % repair frameshifting',  # You can change this to the specific column you want to apply the rule to
                                'filter_query': "{Predicted % repair frameshifting} > 85"  # Use backticks around the column name
                            },
                            'backgroundColor': 'MediumSpringGreen',
                            'color': 'white'
                        }
                    ],
                    fixed_rows={'headers': True}  # This keeps the column headers frozen
                ),
                style={'width': '100%', 'height': '600px'}  # Set the width and height of the wrapping div
            )
        return "Loading data will take a couple of seconds after hitting submit... (input longer then 20 characters is not allowed)"
