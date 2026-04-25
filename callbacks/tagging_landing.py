from dash import dcc, html


page_tagging_landing = html.Div([
    html.H1('Pythia Tagging', style={"marginTop": "0.5em", "marginBottom": "2em", "paddingBottom": "0.2em", "textAlign": "center"}),

    html.Div([
        html.Div([
            html.H3([
                'Choose Your Approach ',
                html.Span([
                    html.Span('ⓘ', style={'color': '#3B82F6', 'cursor': 'help', 'fontSize': '1rem', 'fontWeight': 'bold'}),
                    html.Span([
                        html.P('Two complementary strategies are available: direct 3\' exon tagging (which preserves native UTRs but leaves junction scars in coding sequence) and terminal exon replacement via intron targeting (which achieves scarless tagging in a synthetic linker but sacrifices native 3\' UTR elements). The Pythia web tool can evaluate both strategies and assists in selecting the optimal approach based on genomic sequence context, predicted on-target cutting efficiency, and Pythia-predicted integration efficiency.',
                               style={'marginBottom': '1rem', 'lineHeight': '1.5', 'color': '#1F2937'}),
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th('Feature', style={'padding': '8px', 'borderBottom': '2px solid #D1D5DB', 'textAlign': 'left', 'fontWeight': 'bold', 'color': '#1F2937'}),
                                    html.Th('Direct tagging', style={'padding': '8px', 'borderBottom': '2px solid #D1D5DB', 'textAlign': 'left', 'fontWeight': 'bold', 'color': '#1F2937'}),
                                    html.Th('Exon replacement', style={'padding': '8px', 'borderBottom': '2px solid #D1D5DB', 'textAlign': 'left', 'fontWeight': 'bold', 'color': '#1F2937'})
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td('Integration site availability', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('Context-specific', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('Context-specific (often better)', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'})
                                ]),
                                html.Tr([
                                    html.Td('Endogenous 3\' UTR', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('Retained', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('Lost', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'})
                                ]),
                                html.Tr([
                                    html.Td('Endogenous intron', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('Retained', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('Lost', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'})
                                ]),
                                html.Tr([
                                    html.Td('Scarless tagging', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('No (junction scar in coding sequence)', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'}),
                                    html.Td('Yes (scar in intron)', style={'padding': '8px', 'borderBottom': '1px solid #E5E7EB', 'color': '#374151'})
                                ]),
                                html.Tr([
                                    html.Td('Repair template length', style={'padding': '8px', 'color': '#374151'}),
                                    html.Td('Shorter', style={'padding': '8px', 'color': '#374151'}),
                                    html.Td('Longer', style={'padding': '8px', 'color': '#374151'})
                                ])
                            ])
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '0.85rem'})
                    ], style={
                        'visibility': 'hidden',
                        'width': '550px',
                        'backgroundColor': '#FFFFFF',
                        'color': '#1F2937',
                        'textAlign': 'left',
                        'borderRadius': '6px',
                        'padding': '16px',
                        'position': 'absolute',
                        'zIndex': '1000',
                        'marginLeft': '10px',
                        'fontSize': '0.8rem',
                        'lineHeight': '1.4',
                        'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                        'marginTop': '-10px',
                        'border': '1px solid #D1D5DB'
                    }, className='tooltip-text')
                ], style={'position': 'relative', 'display': 'inline-block'}, className='tooltip-container')
            ], className='step-title'),
            html.P('Select how you want to design your tagging strategy', className='step-description')
        ], className='step-header'),

        # Pre-calculated button (top row, centered)
        html.Div([
            dcc.Link(
                html.Div([
                    html.H3('Pre-Calculated Designs', style={'marginBottom': '1rem', 'color': '#2E5BFF'}),
                    html.P('Pre-calculated 3\' tagging strategies', style={'marginBottom': '0.5rem', 'color': '#374151', 'fontWeight': '600'}),
                    html.P('Genome-wide designs available for:', style={'marginBottom': '0.75rem', 'color': '#374151'}),
                    html.P(['• ', html.I('Homo sapiens')], style={'margin': '0.1rem 0', 'color': '#6B7280'}),
                    html.P(['• ', html.I('Mus musculus')], style={'margin': '0.1rem 0', 'color': '#6B7280'}),
                    html.P(['• ', html.I('Xenopus tropicalis')], style={'margin': '0.1rem 0', 'color': '#6B7280'}),
                ], style={
                    'width': '450px',
                    'padding': '2rem',
                    'backgroundColor': '#FFFFFF',
                    'border': '3px solid #2E5BFF',
                    'borderRadius': '0.75rem',
                    'cursor': 'pointer',
                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    'transition': 'all 250ms ease-in-out',
                    'textAlign': 'center',
                    'minHeight': '240px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center'
                }),
                href='/page-tagging-precalculated',
                style={'textDecoration': 'none', 'color': 'inherit'}
            )
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '2rem'}),

        # Custom design buttons (bottom row)
        html.Div([
            # Custom exon tagging button (5' and 3')
            dcc.Link(
                html.Div([
                    html.H3(["Custom Exon", html.Br(), "Tagging"], style={'marginBottom': '1rem', 'color': '#2E5BFF', 'fontSize': '1.5rem'}),
                    html.P('Design custom 5\' or 3\' tagging strategies', style={'marginBottom': '0.5rem', 'color': '#374151'}),
                    html.P('for any genomic target', style={'marginBottom': '0.5rem', 'color': '#374151'}),
                    html.P('(possibly another species)', style={'fontStyle': 'italic', 'color': '#9CA3AF'})
                ], style={
                    'width': '350px',
                    'padding': '2rem',
                    'backgroundColor': '#FFFFFF',
                    'border': '3px solid #2E5BFF',
                    'borderRadius': '0.75rem',
                    'cursor': 'pointer',
                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    'transition': 'all 250ms ease-in-out',
                    'textAlign': 'center',
                    'minHeight': '200px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center'
                }),
                href='/page-tagging-custom',
                style={'textDecoration': 'none', 'color': 'inherit'}
            ),

            # Custom exon replacement button
            dcc.Link(
                html.Div([
                    html.H3('Custom Exon Replacement', style={'marginBottom': '1rem', 'color': '#2E5BFF', 'fontSize': '1.5rem'}),
                    html.P('Design intron-mediated tagging strategies', style={'marginBottom': '0.5rem', 'color': '#374151'}),
                    html.P('for last exon replacement', style={'marginBottom': '0.5rem', 'color': '#374151'}),
                    html.P('(possibly another species)', style={'fontStyle': 'italic', 'color': '#9CA3AF'})
                ], style={
                    'width': '350px',
                    'padding': '2rem',
                    'backgroundColor': '#FFFFFF',
                    'border': '3px solid #2E5BFF',
                    'borderRadius': '0.75rem',
                    'cursor': 'pointer',
                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    'transition': 'all 250ms ease-in-out',
                    'textAlign': 'center',
                    'minHeight': '200px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center'
                }),
                href='/page-tagging-intron',
                style={'textDecoration': 'none', 'color': 'inherit'}
            )
        ], style={'display': 'flex', 'gap': '1.5rem', 'justifyContent': 'center', 'marginTop': '2rem', 'flexWrap': 'wrap'})
    ], className='step-card')
], style={'padding': '2em', 'maxWidth': '1200px', 'margin': '0 auto'})
