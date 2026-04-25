from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.common import create_header, create_disclaimer


# Help page
help_page = html.Div([
    create_header("help"),
    html.Div([
        html.H1("Help & Documentation", style={"textAlign": "center", "marginBottom": "2em"}),
        html.Div([
            html.H2("Getting Started", style={"color": "var(--primary-color)", "marginBottom": "1em"}),

            html.Div([
                html.H3("What is Pythia?", style={"marginBottom": "0.5em"}),
                html.P("Pythia is a deep learning-based design tool that leverages predictable DNA repair outcomes to enable precise CRISPR-based genome engineering. It uses inDelphi models to predict and optimize gene integration, protein tagging, and editing outcomes.",
                       style={"marginBottom": "1.5em", "lineHeight": "1.6"})
            ]),

            html.Div([
                html.H3("Available Tools:", style={"marginBottom": "0.5em"}),
                html.Ul([
                    html.Li([html.Strong("Pythia Integration: "), "Design gRNAs and microhomology repair templates for targeted transgene insertion at intergenic or intronic landing sites"]),
                    html.Li([html.Strong("Pythia Tagging: "), "Access precomputed gRNA designs and predictions for endogenous protein fluorescent labeling across several precomputed genomes"]),
                    html.Li([html.Strong("Pythia Custom Tagging: "), "Create N-terminal or C-terminal fluorescent or epitope tags on endogenous proteins with optimized reading frame preservation"]),
                    html.Li([html.Strong("Pythia Intron Tagging: "), "Design intron-mediated tagging strategies for last exon replacement with targeted transgene insertion"]),
                    html.Li([html.Strong("Pythia Editing: "), "Generate repair templates for precise single-nucleotide edits using microhomology-mediated repair"])
                ], style={"marginBottom": "1.5em", "lineHeight": "1.8"})
            ]),

            html.Div([
                html.H3("How to Use:", style={"marginBottom": "0.5em"}),

                html.H4("For Integration Tool:", style={"marginBottom": "0.3em", "fontSize": "1.1em"}),
                html.Ol([
                    html.Li("Select 'Pythia Integration' from the navigation menu"),
                    html.Li("Choose your cell line model (mESC, HEK293, U2OS, HCT116, K562)"),
                    html.Li("Choose your workflow: use existing gRNA or design new gRNA"),
                    html.Li("Enter genomic sequences and transgene cassette"),
                    html.Li("Click 'Run Analysis' to process (processing time: ~1-1.5 minutes for 10 gRNAs)"),
                    html.Li("Review repair template predictions and download results")
                ], style={"marginBottom": "1em", "lineHeight": "1.8"}),

                html.H4("For Precalculated Tagging:", style={"marginBottom": "0.3em", "fontSize": "1.1em"}),
                html.Ol([
                    html.Li("Select 'Pythia Tagging' from the navigation menu"),
                    html.Li("Choose your species from the dropdown menu"),
                    html.Li("Select your cell line/model"),
                    html.Li("Select the gene of interest"),
                    html.Li("Browse precomputed results instantly - no waiting required!"),
                    html.Li("Download results as needed")
                ], style={"marginBottom": "1em", "lineHeight": "1.8"}),

                html.H4("For Custom Tagging:", style={"marginBottom": "0.3em", "fontSize": "1.1em"}),
                html.Ol([
                    html.Li("Select 'Pythia Custom Tagging' from the Tagging submenu"),
                    html.Li("Choose your cell line model"),
                    html.Li("Select tagging mode: 5' tagging (N-terminal) or 3' tagging (C-terminal)"),
                    html.Li([
                        "Enter genomic sequences: ",
                        html.Ul([
                            html.Li("For 5' tagging: First exon starting with ATG (start codon)"),
                            html.Li("For 3' tagging: Last exon ending with stop codon (TAA, TAG, or TGA)")
                        ], style={"marginTop": "0.5em", "marginBottom": "0.5em"})
                    ]),
                    html.Li("Provide genomic context (at least 50 bp flanking on each side)"),
                    html.Li([
                        "Enter tag cassette sequence: ",
                        html.Ul([
                            html.Li("For 5' tagging: START codon + tag (e.g., eGFP) + linker"),
                            html.Li("For 3' tagging: Linker + tag + STOP codon + (optional synthetic polyA)")
                        ], style={"marginTop": "0.5em", "marginBottom": "0.5em"})
                    ]),
                    html.Li("Click 'Run Analysis' to generate optimized repair templates"),
                    html.Li("Review gRNA predictions and tagging efficiency scores")
                ], style={"marginBottom": "1em", "lineHeight": "1.8"}),

                html.H4("For Intron Tagging:", style={"marginBottom": "0.3em", "fontSize": "1.1em"}),
                html.Ol([
                    html.Li("Select 'Pythia Intron Tagging' from the Tagging submenu"),
                    html.Li("Choose your cell line model"),
                    html.Li("Enter the intronic target sequence where you want to insert"),
                    html.Li("Provide genomic context around the target site"),
                    html.Li("Enter repair template: splice acceptor + last exon without stop + tags + stop codon"),
                    html.Li("Click 'Run Analysis' to design optimal integration strategy"),
                    html.Li("Review and download results")
                ], style={"marginBottom": "1em", "lineHeight": "1.8"}),

                html.H4("For Editing Tool:", style={"marginBottom": "0.3em", "fontSize": "1.1em"}),
                html.Ol([
                    html.Li("Select 'Pythia Editing' from the navigation menu"),
                    html.Li("Choose your cell line model"),
                    html.Li("Enter the original sequence and desired edited sequence"),
                    html.Li("Submit to generate optimized ssODN repair templates"),
                    html.Li("Review and download repair template designs")
                ], style={"marginBottom": "1.5em", "lineHeight": "1.8"})
            ]),

            html.Div([
                html.H3("Important Notes:", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.Ul([
                    html.Li("Only use ACTG characters in your sequences (for Integration, Editing, and Custom Tagging tools)"),
                    html.Li("Precalculated Tagging tool provides instant access to precomputed data for common genes across the genome"),
                    html.Li("Custom Tagging and Intron Tagging require proper codon positioning (start/stop codons) for accurate predictions"),
                    html.Li("Processing time for Integration and Custom Tagging: ~1-1.5 minutes for 10 gRNAs (scales linearly)"),
                    html.Li("Example buttons are provided on Custom Tagging and Intron Tagging pages to demonstrate proper input format"),
                    html.Li("Results are provided for academic research purposes only"),
                    html.Li("For optimal Custom Tagging results, ensure genomic context includes at least 50 bp flanking sequence on each side")
                ], style={"marginBottom": "1.5em", "lineHeight": "1.8"})
            ]),

            html.Div([
                html.H3("Need More Help?", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.P([
                    "For additional support or questions about Pythia, please refer to our ",
                    html.A("Nature Biotechnology publication", href="https://www.nature.com/articles/s41587-025-02771-0", target="_blank", style={"color": "#2E5BFF", "textDecoration": "underline"}),
                    " or ",
                    html.A("contact the development team", id="help-contact-link", n_clicks=0, style={"color": "#2E5BFF", "textDecoration": "underline", "cursor": "pointer"}),
                    "."
                ], style={"lineHeight": "1.6", "marginBottom": "1em"}),
                html.P([
                    "Found a bug? Don't panic! We promise our code is more stable than our lab's WiFi. Please ",
                    html.A("let us know", id="help-bug-link", n_clicks=0, style={"color": "#2E5BFF", "textDecoration": "underline", "cursor": "pointer"}),
                    " and we'll be forever grateful (and maybe even send you virtual cookies \U0001f36a)."
                ], style={"lineHeight": "1.6", "fontStyle": "italic", "color": "#6B7280"}),

                # Contact Modal
                dbc.Modal([
                    dbc.ModalHeader("Contact Information"),
                    dbc.ModalBody([
                        html.Div([
                            html.P([
                                html.Strong("Dr. Thomas Naert:"),
                                html.Br(),
                                "thomas.naert[AT]ugent.be"
                            ], style={"marginBottom": "0", "fontSize": "1em", "lineHeight": "1.8"})
                        ])
                    ]),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="help-contact-close", className="ms-auto", n_clicks=0)
                    )
                ], id="help-contact-modal", is_open=False, size="md")
            ])
        ], style={
            "maxWidth": "800px",
            "margin": "0 auto",
            "padding": "2em",
            "backgroundColor": "var(--background-primary)",
            "borderRadius": "12px",
            "boxShadow": "var(--shadow-lg)",
            "border": "1px solid var(--border-color)"
        }),
        create_disclaimer()
    ], style={"padding": "2em", "minHeight": "80vh"})
])
