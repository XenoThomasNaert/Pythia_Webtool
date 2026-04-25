from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.common import create_header, create_disclaimer


# Team page
team_page = html.Div([
    create_header("team"),
    html.Div([
        # Header Section
        html.Div([
            html.H1(
                "Core Development Team",
                style={
                    "color": "#1F2937",
                    "fontSize": "2.5em",
                    "textAlign": "center",
                    "marginBottom": "0.5em",
                    "fontWeight": "700"
                }
            ),
            html.P(
                "Meet the scientists behind Pythia",
                style={
                    "color": "#6B7280",
                    "fontSize": "1.2em",
                    "textAlign": "center",
                    "marginBottom": "2em",
                    "fontWeight": "400"
                }
            ),
        ], style={"marginBottom": "2em"}),

        # Introduction Section
        html.Div([
            html.P(
                "Pythia is the result of collaborative research between leading institutions in genome engineering and computational biology. Our interdisciplinary team combines expertise in CRISPR technology, deep learning, and developmental biology to create cutting-edge tools for precise genome editing.",
                style={
                    "color": "#4B5563",
                    "fontSize": "1.05em",
                    "lineHeight": "1.8",
                    "textAlign": "center",
                    "maxWidth": "900px",
                    "margin": "0 auto 3em auto",
                    "padding": "1.5em",
                    "backgroundColor": "#F9FAFB",
                    "borderRadius": "12px",
                    "border": "1px solid #E5E7EB"
                }
            ),
        ]),

        # Institutional Logos
        html.Div([
            html.Img(
                src="/assets/Landing/Logo/uzh.png",
                style={
                    "height": "75px",
                    "margin": "0 2em",
                    "objectFit": "contain"
                }
            ),
            html.Img(
                src="/assets/Landing/Logo/eth.png",
                style={
                    "height": "45px",
                    "margin": "0 2em",
                    "objectFit": "contain"
                }
            ),
            html.Img(
                src="/assets/Landing/Logo/logo_UGent_EN_RGB_2400_color2.png",
                style={
                    "height": "135px",
                    "margin": "0 2em",
                    "objectFit": "contain"
                }
            ),
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "marginBottom": "3em",
            "padding": "2em 0"
        }),

        # Team Members Grid
        html.Div([
            # Dr. Thomas Naert
            html.A([
                html.Div([
                    html.Div([
                        html.Img(src="/assets/pictures/thomas_naert.jpg", style={
                            "width": "150px",
                            "height": "150px",
                            "borderRadius": "12px",
                            "objectFit": "cover",
                            "marginRight": "2em",
                            "border": "2px solid #E5E7EB"
                        }),
                    ], style={"flexShrink": "0"}),
                    html.Div([
                        html.H3("Dr. Thomas Naert", style={"color": "#2E5BFF", "fontSize": "1.4em", "marginBottom": "0.3em", "fontWeight": "600"}),
                        html.P("Lead Developer & Co-Investigator", style={"color": "#6B7280", "fontSize": "0.95em", "marginBottom": "1em", "fontStyle": "italic"}),
                        html.P(
                            "Thomas is a postdoctoral researcher at Ghent University specializing in CRISPR-based genome engineering. He developed the core Pythia algorithms, pioneering an approach that combines deep learning with experimental validation to enable precise, predictable genome modifications. His work bridges computational prediction and practical application in genome editing. His current work focuses on using Pythia technology to get new insights in rare genetic diseases and cancer.",
                            style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.6"}
                        )
                    ], style={"flex": "1"})
                ], className="feature-card", style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "2em",
                    "backgroundColor": "#F9FAFB",
                    "borderRadius": "12px",
                    "border": "1px solid #E5E7EB",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    "marginBottom": "1.5em"
                })
            ], href="https://naertthomas.wordpress.com/", target="_blank", style={"textDecoration": "none", "display": "block"}),

            # Prof. Soeren Lienkamp
            html.A([
                html.Div([
                    html.Div([
                        html.Img(src="/assets/pictures/soeren_lienkamp.jpg", style={
                            "width": "150px",
                            "height": "150px",
                            "borderRadius": "12px",
                            "objectFit": "cover",
                            "marginRight": "2em",
                            "border": "2px solid #E5E7EB"
                        }),
                    ], style={"flexShrink": "0"}),
                    html.Div([
                        html.H3("Prof. Dr. Soeren Lienkamp, MD", style={"color": "#2E5BFF", "fontSize": "1.4em", "marginBottom": "0.3em", "fontWeight": "600"}),
                        html.P("Principal Investigator", style={"color": "#6B7280", "fontSize": "0.95em", "marginBottom": "1em", "fontStyle": "italic"}),
                        html.P(
                            "Professor at the University of Zurich and ETH Zurich with extensive experience in developmental biology and nephrology. Soeren provides scientific oversight for the Pythia project. His laboratory focuses on the mechanisms of kidney development and disease modeling using CRISPR technology, together with pioneering work in reprogramming of kidney cells.",
                            style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.6"}
                        )
                    ], style={"flex": "1"})
                ], className="feature-card", style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "2em",
                    "backgroundColor": "#F9FAFB",
                    "borderRadius": "12px",
                    "border": "1px solid #E5E7EB",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    "marginBottom": "1.5em"
                })
            ], href="https://lienkamplab.org/", target="_blank", style={"textDecoration": "none", "display": "block"}),

            # Taiyo Yamamoto
            html.A([
                html.Div([
                    html.Div([
                        html.Img(src="/assets/pictures/taiyo_yamamoto.jpg", style={
                            "width": "150px",
                            "height": "150px",
                            "borderRadius": "12px",
                            "objectFit": "cover",
                            "marginRight": "2em",
                            "border": "2px solid #E5E7EB"
                        }),
                    ], style={"flexShrink": "0"}),
                    html.Div([
                        html.H3("Taiyo Yamamoto", style={"color": "#2E5BFF", "fontSize": "1.4em", "marginBottom": "0.3em", "fontWeight": "600"}),
                        html.P("In Vivo Tagging Master", style={"color": "#6B7280", "fontSize": "0.95em", "marginBottom": "1em", "fontStyle": "italic"}),
                        html.P([
                            "Taiyo is a PhD candidate in the Molecular Life Sciences program at the Life Science Zurich Graduate School. He made critical contributions to Pythia by providing experimental validation of the technology's ",
                            html.I("in vivo"),
                            " capabilities. His work demonstrated that the Pythia system can successfully tag proteins in living organisms, proving the practical applicability of the computational predictions."
                        ], style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.6"})
                    ], style={"flex": "1"})
                ], className="feature-card", style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "2em",
                    "backgroundColor": "#F9FAFB",
                    "borderRadius": "12px",
                    "border": "1px solid #E5E7EB",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    "marginBottom": "1.5em"
                })
            ], href="https://www.linkedin.com/in/taiyo-yamamoto", target="_blank", style={"textDecoration": "none", "display": "block"}),

            # Dr. Ruth Röck
            html.A([
                html.Div([
                    html.Div([
                        html.Img(src="/assets/pictures/ruth.jpg", style={
                            "width": "150px",
                            "height": "150px",
                            "borderRadius": "12px",
                            "objectFit": "cover",
                            "marginRight": "2em",
                            "border": "2px solid #E5E7EB"
                        }),
                    ], style={"flexShrink": "0"}),
                    html.Div([
                        html.H3("Dr. Ruth Röck", style={"color": "#2E5BFF", "fontSize": "1.4em", "marginBottom": "0.3em", "fontWeight": "600"}),
                        html.P("Biochemistry Wizard", style={"color": "#6B7280", "fontSize": "0.95em", "marginBottom": "1em", "fontStyle": "italic"}),
                        html.P([
                            "Ruth is a postdoctoral researcher at the University of Zurich who led the biochemical validation for the project, providing essential experimental expertise. Her meticulous work includes challenging tasks like isolating specific proteins from minimal biological samples, such as ",
                            html.I("Xenopus"),
                            " embryos, demonstrating the protein-level precision of the Pythia approach."
                        ], style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.6"})
                    ], style={"flex": "1"})
                ], className="feature-card", style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "2em",
                    "backgroundColor": "#F9FAFB",
                    "borderRadius": "12px",
                    "border": "1px solid #E5E7EB",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    "marginBottom": "1.5em"
                })
            ], href="https://www.linkedin.com/in/ruth-r%C3%B6ck-486194275/?originalSubdomain=ch", target="_blank", style={"textDecoration": "none", "display": "block"}),

            # Koen Vromant
            html.Div([
                html.Div([
                    html.Img(src="/assets/pictures/koen.jpg", style={
                        "width": "150px",
                        "height": "150px",
                        "borderRadius": "12px",
                        "objectFit": "cover",
                        "marginRight": "2em",
                        "border": "2px solid #E5E7EB"
                    }),
                ], style={"flexShrink": "0"}),
                html.Div([
                    html.H3("Koen Vromant", style={"color": "#2E5BFF", "fontSize": "1.4em", "marginBottom": "0.3em", "fontWeight": "600"}),
                    html.P("Bioinformatics & Database Wrangler", style={"color": "#6B7280", "fontSize": "0.95em", "marginBottom": "1em", "fontStyle": "italic"}),
                    html.P(
                        "Koen is a second-year Master's student in Biotechnology at Ghent University who developed the critical database infrastructure and genome pipelines that power Pythia's precomputed tagging capabilities. His work on efficient data structures and query optimization enables rapid access to precalculated gRNAs across multiple model organisms.",
                        style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.6"}
                    )
                ], style={"flex": "1"})
            ], className="feature-card", style={
                "display": "flex",
                "alignItems": "center",
                "padding": "2em",
                "backgroundColor": "#F9FAFB",
                "borderRadius": "12px",
                "border": "1px solid #E5E7EB",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                "marginBottom": "1.5em"
            }),

        ], style={
            "maxWidth": "900px",
            "margin": "0 auto",
            "padding": "0 1em"
        }),

        # Contact Section
        html.Div([
            html.H2("Get in Touch", style={"color": "#1F2937", "fontSize": "1.8em", "textAlign": "center", "marginBottom": "1em", "fontWeight": "600"}),
            html.P([
                "Have questions or want to collaborate? Feel free to ",
                html.A("contact us", id="team-contact-link", style={"color": "#2E5BFF", "textDecoration": "underline", "cursor": "pointer"}),
                ". We're always excited to hear from researchers using Pythia!"
            ], style={
                "color": "#4B5563",
                "fontSize": "1.05em",
                "textAlign": "center",
                "lineHeight": "1.6",
                "maxWidth": "700px",
                "margin": "0 auto"
            })
        ], style={"marginTop": "3em", "marginBottom": "2em"}),

        # Contact Modal
        dbc.Modal([
            dbc.ModalHeader("Contact Information"),
            dbc.ModalBody([
                html.Div([
                    html.P([
                        html.Strong("Prof. Dr. Soeren Lienkamp:"),
                        html.Br(),
                        "soeren.lienkamp[AT]uzh.ch"
                    ], style={"marginBottom": "1.5em", "fontSize": "1em", "lineHeight": "1.8"}),
                    html.P([
                        html.Strong("Dr. Thomas Naert:"),
                        html.Br(),
                        "thomas.naert[AT]ugent.be"
                    ], style={"marginBottom": "0", "fontSize": "1em", "lineHeight": "1.8"})
                ])
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="team-contact-close", className="ms-auto", n_clicks=0)
            )
        ], id="team-contact-modal", is_open=False, size="md"),

        create_disclaimer()

    ], style={"padding": "2em", "minHeight": "80vh"})
])
