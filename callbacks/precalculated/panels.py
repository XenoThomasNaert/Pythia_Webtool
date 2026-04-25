import os

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

from Pythia_ExonTagger import reverse_complement
from utils.tag_presets import TAG_PRESETS


def build_readme_panel():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "..", "tagging_info.txt")
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = "No gene data loaded. Please select a database to begin."
    return html.Div(
        [
            html.Div(
                dcc.Markdown(content),
                style={
                    "padding": "2em",
                    "backgroundColor": "var(--bg-primary)",
                    "borderRadius": "10px",
                    "flex": "1 1 100%",
                    "maxWidth": "960px",
                    "boxShadow": "var(--shadow-md)",
                    "transition": "transform 0.15s ease, box-shadow 0.15s ease",
                }
            )
        ],
        style={
            "display": "flex",
            "justifyContent": "center",
            "margin": "2em 0",
            "width": "100%"
        }
    , className="readme-flex")


def build_grna_scatter_plot(df_all, selected_idx, selected_row, mode=None):
    """Build a scatter plot showing all gRNAs with the selected one highlighted."""

    # Prepare data
    x_vals = df_all['integration_score'].tolist()
    y_vals = df_all['CRISPRScan_score'].tolist()
    grna_labels = df_all['gRNA'].tolist()

    # Create the scatter plot
    fig = go.Figure()

    # Add colored background regions - exact logic from user (non-overlapping)
    # RED ZONE: CRISPRScan < 40 OR Integration < 60
    # Split into non-overlapping parts to avoid darker red
    # Part 1: Bottom-left corner (Integration < 60 AND CRISPRScan < 40)
    fig.add_shape(type="rect", x0=0, x1=60, y0=0, y1=40,
                  fillcolor="rgba(255, 182, 193, 0.5)", line_width=0, layer="below")
    # Part 2: Left strip above 40 (Integration < 60 AND CRISPRScan >= 40)
    fig.add_shape(type="rect", x0=0, x1=60, y0=40, y1=120,
                  fillcolor="rgba(255, 182, 193, 0.5)", line_width=0, layer="below")
    # Part 3: Bottom strip right of 60 (Integration >= 60 AND CRISPRScan < 40)
    fig.add_shape(type="rect", x0=60, x1=100, y0=0, y1=40,
                  fillcolor="rgba(255, 182, 193, 0.5)", line_width=0, layer="below")

    # GREEN ZONE: CRISPRScan >= 50 AND Integration >= 75 (best efficiency)
    fig.add_shape(type="rect", x0=75, x1=100, y0=50, y1=120,
                  fillcolor="rgba(144, 238, 144, 0.6)", line_width=0, layer="below")

    # YELLOW ZONE: Everything in between
    # This covers the transition area between red and green
    fig.add_shape(type="rect", x0=60, x1=75, y0=40, y1=120,
                  fillcolor="rgba(255, 255, 153, 0.6)", line_width=0, layer="below")
    # Second yellow zone WITHOUT border (to avoid line in red zone)
    fig.add_shape(type="rect", x0=75, x1=100, y0=40, y1=50,
                  fillcolor="rgba(255, 255, 153, 0.6)", line_width=0, layer="below")

    # Inline legend labels
    # Inline legend labels (vertical, no background)
    legend_y = 117
    fig.add_annotation(
        x=2, y=legend_y,
        text="Low efficiency",
        showarrow=False,
        font=dict(size=12, color="rgba(239, 68, 68, 0.9)"),
        textangle=-90,
        xanchor="center",
        yanchor="top"
    )
    fig.add_annotation(
        x=62, y=legend_y,
        text="Good efficiency",
        showarrow=False,
        font=dict(size=12, color="rgba(234, 179, 8, 0.9)"),
        textangle=-90,
        xanchor="center",
        yanchor="top"
    )
    fig.add_annotation(
        x=77, y=legend_y,
        text="Very good efficiency",
        showarrow=False,
        font=dict(size=12, color="rgba(34, 197, 94, 0.9)"),
        textangle=-90,
        xanchor="center",
        yanchor="top"
    )

    # Add all gRNAs as small blue dots
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers',
        marker=dict(
            size=6,
            color='rgba(59, 130, 246, 0.6)',
            line=dict(width=0)
        ),
        text=grna_labels,
        customdata=list(range(len(df_all))),  # Store index for click handling
        hovertemplate='<b>%{text}</b><br>Pythia: %{x:.1f}<br>CRISPRScan: %{y:.1f}<extra></extra>',
        showlegend=False
    ))


    # Highlight the selected gRNA
    if selected_idx is not None and selected_idx < len(df_all):
        selected_x = selected_row['integration_score']
        selected_y = selected_row['CRISPRScan_score']
        selected_grna = selected_row['gRNA']

        fig.add_trace(go.Scatter(
            x=[selected_x],
            y=[selected_y],
            mode='markers',
            marker=dict(
                size=12,
                color='rgba(239, 68, 68, 0.9)',
                line=dict(width=2, color='white')
            ),
            text=[selected_grna],
            hovertemplate='<b>SELECTED: %{text}</b><br>Pythia: %{x:.1f}<br>CRISPRScan: %{y:.1f}<extra></extra>',
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        xaxis=dict(
            title='Pythia Score',
            range=[0, 100],
            gridcolor='rgba(209, 213, 219, 0.5)',
            showgrid=True,
            zeroline=False,
            fixedrange=True,  # Lock x-axis zoom
            tick0=0,
            tickmode='array',
            tickvals=list(range(0, 101, 10))  # Show labels only at 0, 10, 20, 30...
        ),
        yaxis=dict(
            title='CRISPRScan Score',
            range=[0, 120],
            gridcolor='rgba(209, 213, 219, 0.5)',
            showgrid=True,
            zeroline=False,
            fixedrange=True,  # Lock y-axis zoom
            tick0=0,
            tickmode='array',
            tickvals=list(range(0, 121, 10))  # Show labels only at 0, 10, 20, 30...
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(l=50, r=20, t=20, b=50),  # Reduced margins
        hovermode='closest',
        dragmode=False  # Disable drag to pan
    )

    # Add border around entire plot
    fig.update_xaxes(showline=True, linewidth=2, linecolor='rgba(0, 0, 0, 0.3)', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='rgba(0, 0, 0, 0.3)', mirror=True)

    cutoff_info = html.Div([
        html.Span(
            'CRISPRscan score cutoff explanation',
            style={'fontSize': '0.8rem', 'color': '#9CA3AF', 'marginRight': '6px'}
        ),
        html.Span([
            html.Span('?', style={
                'display': 'inline-block',
                'width': '18px',
                'height': '18px',
                'lineHeight': '18px',
                'textAlign': 'center',
                'borderRadius': '50%',
                'border': '1.5px solid #9CA3AF',
                'color': '#9CA3AF',
                'fontSize': '0.75rem',
                'fontWeight': 'bold',
                'cursor': 'help',
            }),
            html.Span(
                'To save computing power, we limit the number of guides calculated. '
                'Guides are ranked by CRISPRScan score and only the top-scoring ones '
                'are included in the analysis.',
                style={
                    'visibility': 'hidden',
                    'width': '300px',
                    'backgroundColor': '#1F2937',
                    'color': '#fff',
                    'textAlign': 'left',
                    'borderRadius': '6px',
                    'padding': '10px',
                    'position': 'absolute',
                    'zIndex': '1000',
                    'bottom': '125%',
                    'right': '0',
                    'fontSize': '0.82rem',
                    'lineHeight': '1.4',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.15)',
                },
                className='tooltip-text'
            ),
        ], style={'position': 'relative', 'display': 'inline-block'}, className='tooltip-container'),
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'flex-end',
        'marginBottom': '4px',
    }) if mode == 'Intron' else html.Div(style={'marginBottom': '4px'})

    return html.Div([
        cutoff_info,
        dcc.Graph(
            id='grna-scatter-plot',
            figure=fig,
            config={'displayModeBar': False}
        )
    ], style={
        'marginTop': '20px',
        'backgroundColor': 'var(--background-primary)',
        'borderRadius': 'var(--border-radius-lg)',
        'padding': '20px',
        'boxShadow': 'var(--shadow-md)',
        'border': '1px solid var(--border-color)',
        'width': '50%',
        'marginLeft': '0'
    })


def build_custom_sequence_panel(current_sequence: str = '', last_preset_components: list = None):
    """Build a panel for custom sequence input with custom tabs (no Dash dcc.Tabs)"""
    return html.Div([
        html.Div([
            html.Div("Last used for calculation", style={'fontWeight': '600', 'fontSize': '0.8rem', 'color': '#6B7280', 'marginBottom': '6px'}),
            html.Div([
                html.Span(
                    f"{c['type']}: {c['name']} ({c['length']} bp)",
                    style={'backgroundColor': c['color'], 'color': 'white', 'padding': '4px 8px',
                           'borderRadius': '4px', 'marginRight': '8px', 'marginBottom': '6px',
                           'fontSize': '12px', 'fontWeight': '600', 'display': 'inline-block'}
                ) for c in last_preset_components
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '4px'}),
            html.Div(f"{sum(c['length'] for c in last_preset_components)} bp total",
                     style={'fontSize': '0.8rem', 'color': '#6B7280', 'fontStyle': 'italic'})
        ], style={'padding': '10px 12px', 'backgroundColor': '#EFF6FF', 'borderRadius': '6px',
                  'border': '1px solid #BFDBFE'})
        if last_preset_components else html.Div(),
        html.H4([
            "Recalculate Pythia scores for your repair template ",
            html.Span([
                html.Span('ⓘ', style={'color': '#3B82F6', 'cursor': 'help', 'fontSize': '1rem', 'fontWeight': 'bold'}),
                html.Span('Use this to recalculate integration scores with your custom repair template. We precalculated everything with a standard template, but your repair template might differ. In rare cases where your template has microhomology near its edges within the cassette, this can change prediction scores. Recalculation updates your selected gRNA and all download outputs.',
                          style={
                              'visibility': 'hidden',
                              'width': '400px',
                              'backgroundColor': '#1F2937',
                              'color': '#fff',
                              'textAlign': 'left',
                              'borderRadius': '6px',
                              'padding': '10px',
                              'position': 'absolute',
                              'zIndex': '1000',
                              'bottom': '125%',
                              'left': '50%',
                              'marginLeft': '-200px',
                              'fontSize': '0.85rem',
                              'lineHeight': '1.4',
                              'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'
                          },
                          className='tooltip-text')
            ], style={'position': 'relative', 'display': 'inline-block'}, className='tooltip-container')
        ], style={
            'textAlign': 'center',
            'marginTop': '1em',
            'marginBottom': '15px',
            'color': 'var(--primary-color)',
            'fontSize': '1.1rem'
        }),
        # Custom tab buttons
        html.Div([
            html.Button(
                'Presets',
                id='tab-presets-button',
                n_clicks=0,
                style={
                    'flex': '1',
                    'padding': '10px',
                    'backgroundColor': '#3B82F6',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px 0 0 0',
                    'fontWeight': '600',
                    'cursor': 'pointer',
                    'fontSize': '14px'
                }
            ),
            html.Button(
                'Custom Sequence',
                id='tab-custom-button',
                n_clicks=0,
                style={
                    'flex': '1',
                    'padding': '10px',
                    'backgroundColor': '#9CA3AF',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '0 4px 0 0',
                    'fontWeight': '600',
                    'cursor': 'pointer',
                    'fontSize': '14px'
                }
            )
        ], style={'display': 'flex', 'marginBottom': '0'}),

        # Store to track active tab
        dcc.Store(id='active-tab-store', data='presets'),

        # Tab content containers
        html.Div([
            # Custom Sequence Content
            html.Div([
                html.Div([
                            html.Label(
                                "Enter Custom Tag Sequence (ATCG only):",
                                style={
                                    'fontWeight': '600',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'color': 'var(--text-primary)'
                                }
                            ),
                            dcc.Textarea(
                                id='custom-sequence-input',
                                placeholder='Enter sequence containing only A, T, C, G...',
                                style={
                                    'width': '100%',
                                    'height': '100px',
                                    'fontFamily': 'monospace',
                                    'fontSize': '14px',
                                    'padding': '10px',
                                    'borderRadius': '4px',
                                    'border': '1px solid var(--border-color)',
                                    'resize': 'vertical'
                                },
                                value=current_sequence
                            ),
                            html.Div(
                                id='custom-sequence-validation',
                                style={'marginTop': '8px', 'minHeight': '20px'}
                            ),
                            html.Button(
                                'Recalculate with Custom Sequence',
                                id='recalculate-button',
                                n_clicks=0,
                                style={
                                    'marginTop': '15px',
                                    'width': '100%',
                                    'padding': '12px',
                                    'backgroundColor': 'var(--primary-color)',
                                    'color': 'white',
                                    'border': 'none',
                                    'borderRadius': '4px',
                                    'fontWeight': '600',
                                    'cursor': 'pointer',
                                    'fontSize': '14px'
                                }
                            ),
                            html.Button(
                                'Reset to Original',
                                id='reset-sequence-button',
                                n_clicks=0,
                                style={
                                    'marginTop': '10px',
                                    'width': '100%',
                                    'padding': '10px',
                                    'backgroundColor': '#6B7280',
                                    'color': 'white',
                                    'border': 'none',
                                    'borderRadius': '4px',
                                    'fontWeight': '600',
                                    'cursor': 'pointer',
                                    'fontSize': '14px'
                                }
                            )
                        ], style={'padding': '15px'})
            ], id='custom-tab-content', style={'display': 'none'}),

            # Presets Content
            html.Div([
                html.Div([
                            # Linker dropdown
                            html.Div([
                                html.Span("Linker:", style={'fontWeight': '600', 'fontSize': '0.875rem', 'color': 'var(--text-primary)'}),
                                html.Span([
                                    html.Span('ⓘ', style={'color': '#3B82F6', 'cursor': 'help', 'fontSize': '1rem', 'fontWeight': 'bold', 'marginLeft': '6px'}),
                                    html.Span(
                                        'A short flexible peptide sequence (e.g. SSGSSG) that connects the tag to the protein of interest. Including a linker helps prevent steric interference between the tag and the native protein structure.',
                                        className='tooltip-text',
                                        style={'visibility': 'hidden', 'width': '340px', 'backgroundColor': '#1F2937', 'color': '#fff',
                                               'textAlign': 'left', 'borderRadius': '6px', 'padding': '10px', 'position': 'absolute',
                                               'zIndex': '1000', 'marginLeft': '10px', 'fontSize': '0.82rem', 'lineHeight': '1.4',
                                               'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'}
                                    ),
                                ], className='tooltip-container', style={'position': 'relative', 'display': 'inline-block'}),
                            ], style={'marginBottom': '8px', 'display': 'block'}),
                            dcc.Dropdown(
                                id='linker-dropdown',
                                options=[
                                    {'label': f"{l['name']} ({l['description']})", 'value': l['name']}
                                    for l in TAG_PRESETS.get('linkers', [])
                                ],
                                placeholder='Select a linker...',
                                searchable=False,
                                style={'marginBottom': '20px'}
                            ),

                            # Tag dropdown
                            html.Label(
                                "Tag:",
                                style={
                                    'fontWeight': '600',
                                    'fontSize': '0.875rem',
                                    'marginBottom': '8px',
                                    'display': 'block',
                                    'color': 'var(--text-primary)'
                                }
                            ),
                            dcc.Dropdown(
                                id='tag-dropdown',
                                options=[
                                    {'label': f"{t['name']} ({t['description']})", 'value': t['name']}
                                    for t in TAG_PRESETS.get('tags', [])
                                ],
                                placeholder='Select a tag...',
                                searchable=False,
                                style={'marginBottom': '20px'}
                            ),

                            # Additional components container
                            html.Div(id='additional-components-container', children=[], style={'marginBottom': '4px'}),

                            # Add component button
                            html.Button(
                                '+ Add Component',
                                id='add-component-button',
                                n_clicks=0,
                                style={
                                    'marginBottom': '20px',
                                    'padding': '8px 16px',
                                    'backgroundColor': '#4CAF50',
                                    'color': 'white',
                                    'border': 'none',
                                    'borderRadius': '4px',
                                    'cursor': 'pointer',
                                    'fontSize': '14px'
                                }
                            ),

                            # PolyA signal dropdown (intron mode only — shown/hidden by callback)
                            html.Div([
                                html.Div([
                                    html.Span("PolyA Signal:", style={'fontWeight': '600', 'fontSize': '0.875rem', 'color': 'var(--text-primary)'}),
                                    html.Span([
                                        html.Span('ⓘ', style={'color': '#3B82F6', 'cursor': 'help', 'fontSize': '1rem', 'fontWeight': 'bold', 'marginLeft': '6px'}),
                                        html.Span(
                                            'An exogenous polyadenylation signal (e.g. SV40 or bGH) that terminates the transcript at the cassette. In intron-based tagging, the transcript ends here — the endogenous 3\u2032 UTR remains in the genome downstream but is no longer part of the expressed mRNA.',
                                            className='tooltip-text',
                                            style={'visibility': 'hidden', 'width': '340px', 'backgroundColor': '#1F2937', 'color': '#fff',
                                                   'textAlign': 'left', 'borderRadius': '6px', 'padding': '10px', 'position': 'absolute',
                                                   'zIndex': '1000', 'marginLeft': '10px', 'fontSize': '0.82rem', 'lineHeight': '1.4',
                                                   'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'}
                                        ),
                                    ], className='tooltip-container', style={'position': 'relative', 'display': 'inline-block'}),
                                ], style={'marginBottom': '8px', 'display': 'block'}),
                                dcc.Dropdown(
                                    id='polya-dropdown',
                                    options=[
                                        {'label': 'None (not recommended)', 'value': 'none'},
                                        {'label': 'SV40 polyA (135 bp)', 'value': 'SV40 polyA'},
                                        {'label': 'bGH polyA (225 bp)', 'value': 'bGH polyA'},
                                    ],
                                    value=None,
                                    placeholder='Select a polyA signal...',
                                    clearable=False,
                                    searchable=False,
                                    style={'marginBottom': '8px'}
                                ),
                                html.Div(id='polya-warning', style={'marginBottom': '20px'}),
                            ], id='polya-section', style={'display': 'none'}),

                            # Store for tracking component count
                            dcc.Store(id='component-counter', data=0),

                            # Display combined sequence info
                            html.Div(
                                id='preset-sequence-info',
                                style={'marginBottom': '8px', 'minHeight': '40px'}
                            ),


                            # Recalculate button
                            html.Button(
                                'Recalculate with Preset',
                                id='recalculate-preset-button',
                                n_clicks=0,
                                style={
                                    'width': '100%',
                                    'padding': '12px',
                                    'backgroundColor': 'var(--primary-color)',
                                    'color': 'white',
                                    'border': 'none',
                                    'borderRadius': '4px',
                                    'fontWeight': '600',
                                    'cursor': 'pointer',
                                    'fontSize': '14px'
                                }
                            ),
                            # Hidden div that the preset callback outputs to, so
                            # the dcc.Loading on mutation-detail-container shows
                            # a spinner during the computation (same as custom sequence)
                            html.Div(id='preset-loading-output', style={'display': 'none'}),
                        ], style={'padding': '15px'})
            ], id='presets-tab-content', style={'display': 'block'})
        ])
    ], style={
        'marginTop': '20px',
        'backgroundColor': 'var(--background-primary)',
        'borderRadius': 'var(--border-radius-lg)',
        'padding': '20px',
        'boxShadow': 'var(--shadow-md)',
        'border': '1px solid var(--border-color)',
        'width': '50%'
    })


def build_allele_panel(row, gene, tag_length, mode=None):
    """Build the allele frequency table panel"""
    if mode == 'Intron':
        return html.Div(
            className="compact-info-panel info-panel-container allele-panel info-notice",
            style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'minHeight': '100px',
                'padding': '1em'
            },
            children=[
                html.Strong("Note: "),
                " In-frame data is not applicable in Intron mode. Repair templates in this mode are assembled automatically from: (i) the endogenous splice acceptor (last 25 bp of the targeted intron, retrieved from the genome), (ii) the complete last exon with its stop codon removed, (iii) the tag cassette (linker + tag), and (iv) a polyadenylation signal — ensuring proper in-frame splicing when integration is successful."
            ]
        )
    allele_rows = []

    try:
        pcut = int(row['protein_cut_position'])
    except Exception:
        pcut = None

    tag_bp = int(tag_length.replace('bp', ''))
    y = 1 if tag_bp == 3 else 2  # scar AA multiplier

    # ----- Collect allele rows -----
    # Loop to range(6): recalculate_grna now translates x0-x5 proteins, so
    # x5 is properly populated when Amount_of_trimologies_left reaches 5.
    # The genotype fallback keeps the row visible even if translation failed.
    for i in range(6):
        prot = row.get(f'x{i}_protein')
        freq = row.get(f'x{i}_frequency')
        genotype = row.get(f'x{i}_genotype', '')

        has_freq = pd.notna(freq) and float(freq) > 0
        has_protein = pd.notna(prot) and str(prot).strip() != ''
        has_genotype = pd.notna(genotype) and str(genotype).strip() != ''

        if has_freq and (has_protein or has_genotype):
            if has_protein:
                prot = str(prot)
                # ----- NEW: Trim protein to EXACTLY ±15 AA around cut -----
                if pcut is not None and len(prot) > 0:
                    start = max(0, pcut - 15)
                    end = min(len(prot), pcut + 15)
                    prot = prot[start:end]
            else:
                # Translation failed (e.g. CDS missing from DB) — show placeholder
                prot = '—'

            # allele category: None / X AA
            if i == 0:
                category_label = 'None'
            else:
                aa_count = y * i
                category_label = f'{aa_count} AA'

            allele_rows.append({
                'Allele': category_label,
                'Protein sequence': prot,
                'Frequency': float(freq)
            })

    if not allele_rows:
        return html.Div(
            "No allele data available for this gRNA.",
            style={'marginTop': '20px', 'color': 'var(--text-secondary)'}
        )

    allele_df = pd.DataFrame(allele_rows)
    allele_df['Percent'] = allele_df['Frequency']  # keep raw values

    # Sorting logic
    def get_sort_key(allele_label):
        if allele_label == 'None':
            return 0
        else:
            return int(allele_label.split()[0]) // y

    allele_df['sort_key'] = allele_df['Allele'].apply(get_sort_key)
    allele_df = allele_df.sort_values('sort_key', ascending=True).reset_index(drop=True)

    # ----- Colors -----
    def get_color(allele_num):
        if allele_num == 0:
            return "rgb(100,149,237)"        # x0 always blue
        else:
            return "rgb(249,115,22)"        # x1-x4 all orange

    # ----- Build table rows -----
    table_rows = []

    for i, r in allele_df.iterrows():
        allele_label = r['Allele']

        if allele_label == 'None':
            x_num = 0
        else:
            x_num = int(allele_label.split()[0]) // y

        color = get_color(x_num)
        bar_width = r['Percent']
        underline_chars = y * x_num  # still needed for underline

        prot_seq = r['Protein sequence']

        # --- 15/15 PREVIEW (always use 15 AA before and after) ---
        if len(prot_seq) >= 30:
            window_left = 15
            window_right = 15
            left_part = prot_seq[:window_left]
            right_part = prot_seq[window_left:window_left + window_right]

            if underline_chars > 0 and len(right_part) >= underline_chars:
                underlined = right_part[:underline_chars]
                rest = right_part[underline_chars:]
                formatted_seq = html.Span([
                    '...', left_part, ' ',
                    html.U(underlined),
                    rest,
                    '...'
                ])
            else:
                formatted_seq = html.Span([
                    '...', left_part, ' ', right_part, '...'
                ])
        else:
            formatted_seq = prot_seq

        # row format (force consistent 36px height)
        row_height = '36px'
        row_padding = '6px 0'

        table_rows.append(
            html.Div([
                # Protein preview (50%)
                html.Div(formatted_seq, style={
                    'flex': '0 0 50%',
                    'fontFamily': 'Menlo, "Courier New", monospace',
                    'fontSize': '15px',
                    'padding': '0 8px',
                    'userSelect': 'text',
                    'lineHeight': '20px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                }),

                # Percent (8%)
                html.Div(f"{r['Percent']:.1f}", style={
                    'flex': '0 0 8%',
                    'textAlign': 'right',
                    'fontFamily': 'Menlo, "Courier New", monospace',
                    'fontSize': '15px',
                    'padding': '0 4px',
                    'userSelect': 'text',
                    'lineHeight': '20px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'flex-end'
                }),

                # Frequency bar (30%)
                html.Div([
                    html.Div(style={
                        'width': f'{min((bar_width / 60) * 100, 100)}%',
                        'backgroundColor': color,
                        'height': 'var(--allele-bar-height, 12px)',
                        'transition': 'width 0.3s ease',
                        'borderRadius': '2px'
                    }, className="allele-bar")
                ], style={
                    'flex': '0 0 30%',
                    'position': 'relative',
                    'height': 'var(--allele-bar-height, 12px)',
                    'display': 'flex',
                    'alignItems': 'center',
                    'padding': '0 4px'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'backgroundColor': 'white',
                'height': row_height,
            'padding': row_padding,
            'marginBottom': '1.5rem'
        })
    )

    # ----- Remaining percentage row -----
    remaining_percent = max(0.0, 100.0 - allele_df['Percent'].sum())
    if remaining_percent > 0:
        table_rows.append(
            html.Div([
                html.Div(
                    "OUT OF FRAME",
                    style={
                        'flex': '0 0 50%',
                        'fontFamily': 'Menlo, "Courier New", monospace',
                        'fontSize': '15px',
                        'padding': '0 8px',
                        'userSelect': 'text',
                        'lineHeight': '20px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center'
                    }
                ),
                html.Div(f"{remaining_percent:.1f}", style={
                    'flex': '0 0 8%',
                    'textAlign': 'right',
                    'fontFamily': 'Menlo, "Courier New", monospace',
                    'fontSize': '15px',
                    'padding': '0 4px',
                    'userSelect': 'text',
                    'lineHeight': '20px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'flex-end'
                }),
                html.Div([
                    html.Div(style={
                        'width': f'{min(remaining_percent, 60) / 60 * 100}%',
                        'backgroundColor': 'rgb(148,163,184)',
                        'height': 'var(--allele-bar-height, 12px)',
                        'transition': 'width 0.3s ease',
                        'borderRadius': '2px'
                    }, className="allele-bar")
                ], style={
                    'flex': '0 0 30%',
                    'position': 'relative',
                    'height': 'var(--allele-bar-height, 12px)',
                    'display': 'flex',
                    'alignItems': 'center',
                    'padding': '0 4px'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'backgroundColor': 'white',
                'height': row_height,
                'padding': row_padding,
                'marginBottom': '1.5rem'
            })
        )

    allele_table = html.Div(table_rows)

    # ----- OUTER PANEL (70% width) -----
    return html.Div([
        html.Div(
            html.Div(
                "PREDICTED REPAIR INTEGRATION SCAR",
                className="grna-title monospace allele-title-text"
            ),
            className="grna-title-row",
            style={
                'fontWeight': '600', 'marginBottom': '8px',
                'color': '#212529', 'fontSize': '15px'
            }
        ),
        html.Hr(style={
            'borderWidth': '2px 0px 0px',
            'borderStyle': 'solid none none',
            'borderColor': 'rgb(209, 213, 219) currentcolor currentcolor',
            'borderImage': 'none',
            'margin': '8px 0px 12px'
        }),
        allele_table
    ], className="compact-info-panel info-panel-container allele-panel", style={'overflowX': 'hidden', 'height': '335px'})


def build_info_panel(row, gene, tag_length):
    """Sidebar with gRNA properties, compact and consistent."""

    gRNA = row['gRNA']
    loc = row['location']
    strand = '+' if row['strand'] == 'plus' else '-'
    crispr = row['CRISPRScan_score']
    pythia = row['integration_score']

    repair_cassette = row.get('Repair_Cassette', '')
    cassette_length = len(repair_cassette) if isinstance(repair_cassette, str) else 0

    # Apply reverse complement if strand is minus
    repair_cassette_display = repair_cassette
    if strand == '-' and repair_cassette:
        repair_cassette_display = reverse_complement(repair_cassette)

    # Calculate in-frame chance (sum of all x_frequency values, including x5)
    in_frame_chance = 0.0
    for i in range(6):
        freq = row.get(f'x{i}_frequency')
        if pd.notna(freq):
            in_frame_chance += float(freq)

    # Homology metrics
    def _to_int(val):
        try:
            return int(val)
        except Exception:
            return None

    left_trimologies = _to_int(row.get('Amount_of_trimologies_left'))
    right_trimologies = _to_int(row.get('Amount_of_trimologies_right'))
    left_homol = _to_int(row.get('Homol_length_left'))
    right_homol = _to_int(row.get('Homol_length_right'))

    # Title row with copy
    title_row = html.Div(
        [
            html.Div(gRNA, className="grna-title monospace"),
            html.Button(
                "\U0001f4cb",
                id={'type': 'copy-grna-btn', 'gRNA': gRNA},
                n_clicks=0,
                className="compact-clipboard title-copy",
                style={'cursor': 'pointer', 'border': 'none', 'background': 'transparent', 'fontSize': '18px'}
            ),
        ],
        className="grna-title-row"
    )

    # Helper: compact score row
    def info_row(label, value):
        return html.Div(
            [
                html.Span(label, className="info-label"),
                html.Span(f"{value}", className="info-value"),
            ],
            className="info-row"
        )

    def mh_row(label, count, length):
        if count is None or length is None:
            value = "-"
        else:
            value = f"{count} x {length} bp"
        return info_row(label, value)

    def strong_row(label, value):
        return html.Div(
            [
                html.Span(label, className="info-label strong-label"),
                html.Span(f"{value}", className="info-value strong-value"),
            ],
            className="info-row"
        )

    # Efficiency bucket based on Pythia (integration) score and CRISPRScan score
    def efficiency_label(pythia_score, crispr_score):
        if pythia_score >= 75 and crispr_score >= 50:
            return "Very Good"
        if pythia_score >= 60 and crispr_score >= 40:
            return "Good"
        return "Low"

    efficiency = efficiency_label(pythia, crispr)

    return html.Div([
        title_row,
        html.Hr(style={
            'border': '0',
            'borderTop': '2px solid #d1d5db',
            'margin': '8px 0 12px 0'
        }),
        html.Div(
            [
                html.Span("Repair Template", className="info-label strong-label"),
                html.Button(
                    "\U0001f4cb",
                    id={'type': 'copy-cassette-btn', 'gRNA': gRNA},
                    n_clicks=0,
                    className="compact-clipboard",
                    style={'cursor': 'pointer', 'border': 'none', 'background': 'transparent', 'fontSize': '18px'}
                ),
            ],
            className="repair-header"
        ),
        info_row("Length:", f"{cassette_length} bp"),
        mh_row("Left MH:", left_trimologies, left_homol),
        mh_row("Right MH:", right_trimologies, right_homol),
        html.Div(
            [
                html.Span("Download:", className="info-label"),
                html.Span(
                    [
                        html.Span(
                            "FASTA",
                            id={'type': 'download-cassette', 'gRNA': gRNA},
                            n_clicks=0,
                            className="pill-link",
                            style={'cursor': 'pointer'}
                        ),
                        html.Span("|", className="pill-sep"),
                        html.Span(
                            "txt",
                            id={'type': 'download-cassette-txt', 'gRNA': gRNA},
                            n_clicks=0,
                            className="pill-link",
                            style={'cursor': 'pointer'}
                        ),
                    ],
                    className="pill-links"
                ),
            ],
            className="pill-row"
        ),
        html.Hr(style={
            'border': '0',
            'borderTop': '2px solid #d1d5db',
            'margin': '8px 0 10px 0'
        }),
        strong_row("Efficiency", efficiency),
        info_row("Pythia score:", f"{pythia:.1f}"),
        info_row("CRISPRscan score:", f"{crispr:.1f}"),
        info_row("In-frame chance:", f"{in_frame_chance:.1f}%"),
        info_row("Cut location:", f"{loc}"),
        info_row("Strand:", "Plus" if strand == '+' else "Minus"),
    ], className="compact-info-panel info-panel-container", style={'height': '335px'})
