from dash import dcc, html
from layouts.common import create_header, create_disclaimer


# Licenses page
licenses_page = html.Div([
    create_header("licenses"),
    html.Div([
        # Header Section
        html.Div([
            html.H1(
                "License & Terms of Use",
                style={
                    "color": "#1F2937",
                    "fontSize": "2.5em",
                    "fontWeight": "700",
                    "marginBottom": "0.3em",
                    "textAlign": "center"
                }
            ),
            html.P(
                "pythia platform",
                style={
                    "color": "#6B7280",
                    "fontSize": "0.9em",
                    "textTransform": "uppercase",
                    "letterSpacing": "3px",
                    "textAlign": "center",
                    "marginTop": "2.5em",
                    "marginBottom": "2em"
                }
            )
        ]),

        # Warning Box
        html.Div([
            html.Div([
                html.P([
                    html.Strong("IMPORTANT: ", style={"color": "#1F2937"}),
                    "By downloading the code or using the service and/or software application accompanying this license, you are consenting to be bound by all of the terms of this license."
                ], style={"margin": "0", "color": "#1F2937", "fontSize": "1em"})
            ], style={
                "backgroundColor": "rgba(239, 68, 68, 0.1)",
                "borderLeft": "4px solid #EF4444",
                "padding": "1.2em 1.5em",
                "borderRadius": "4px",
                "marginBottom": "2em"
            })
        ], style={"marginBottom": "3em"}),

        # Copyright Notice Section
        html.Div([
            html.H2("Copyright Notice", style={"color": "#2E5BFF", "fontSize": "1.8em", "marginTop": "1em", "marginBottom": "0.8em", "fontWeight": "600"}),
            html.P(
                html.Strong("Copyright © 2024. University of Zurich. All Rights Reserved."),
                style={"fontSize": "1.05em", "marginBottom": "1em", "color": "#1F2937"}
            ),
            html.P(
                "The software is being provided as a service for research, educational, instructional and non-commercial purposes only. By submitting jobs to Pythia, you agree to the terms and conditions herein.",
                style={"fontSize": "1em", "lineHeight": "1.8", "color": "#4B5563"}
            )
        ], style={"marginBottom": "3em"}),

        # Terms and Conditions Section
        html.Div([
            html.H2("Terms and Conditions", style={"color": "#2E5BFF", "fontSize": "1.8em", "marginTop": "1em", "marginBottom": "0.8em", "fontWeight": "600"}),
            html.P("By using Pythia, you confirm and agree to the following:", style={"fontSize": "1em", "marginBottom": "1em", "color": "#4B5563"}),
            html.Ol([
                html.Li("You are an actively enrolled student, post-doctoral researcher, or faculty member at a degree-granting educational institution or government research institution;", style={"marginBottom": "0.8em"}),
                html.Li("You will only use the Pythia Software Application and/or Service for educational, instructional, and/or non-commercial research purposes;", style={"marginBottom": "0.8em"}),
                html.Li("You understand that all results produced using the Code may only be used for non-commercial research and/or academic purposes;", style={"marginBottom": "0.8em"}),
                html.Li("You understand that to obtain any right to use the Code for commercial purposes, or in the context of industrially sponsored research, you must enter into an appropriate, separate and direct license agreement with the Owners;", style={"marginBottom": "0.8em"}),
                html.Li("You will not redistribute unmodified versions of the Code;", style={"marginBottom": "0.8em"}),
                html.Li("You will redistribute modifications, if any, under the same terms as this license and only to non-profits and government research institutions;", style={"marginBottom": "0.8em"}),
                html.Li("You understand that neither the names of the Owners nor the names of the authors may be used to endorse or promote products derived from this software without specific prior written permission.", style={"marginBottom": "0.8em"})
            ], style={"fontSize": "1em", "lineHeight": "1.8", "color": "#4B5563", "paddingLeft": "1.5em"})
        ], style={"marginBottom": "3em"}),

        # Commercial Licensing Section
        html.Div([
            html.H2("Commercial Licensing Inquiries", style={"color": "#2E5BFF", "fontSize": "1.8em", "marginTop": "1em", "marginBottom": "0.8em", "fontWeight": "600"}),

            # Patent Information - Condensed
            html.P([
                html.Strong("Patent: ", style={"color": "#1F2937"}),
                "WO2025040617A1 – \"Microhomology mediated integration of cargo nucleic acid molecules\" – Inventors: Thomas Naert, Soeren Lienkamp – Publication Date: February 27, 2025"
            ], style={"fontSize": "0.95em", "color": "#4B5563", "marginBottom": "1.5em", "lineHeight": "1.6"}),

            html.P(
                "Licensing options are available for commercial entities, for-profit organizations, and industrially sponsored research applications. For inquiries regarding commercial licensing, collaboration opportunities, or technology transfer, please contact:",
                style={"fontSize": "1em", "lineHeight": "1.8", "color": "#4B5563", "marginBottom": "2em"}
            ),

            # Contact Cards Grid
            html.Div([
                # Unitectra Card
                html.Div([
                    html.H4("Unitectra", style={"color": "#2E5BFF", "fontSize": "1.2em", "marginBottom": "0.8em", "fontWeight": "600"}),
                    html.P(html.Strong("Technology Transfer Office"), style={"marginBottom": "0.5em", "color": "#1F2937"}),
                    html.P("Universities of Basel, Bern and Zurich", style={"marginBottom": "0.5em", "color": "#4B5563", "fontSize": "0.95em"}),
                    html.P([
                        "Email: ",
                        html.A("mail@unitectra.ch", href="mailto:mail@unitectra.ch", style={"color": "#2E5BFF", "textDecoration": "none"})
                    ], style={"marginBottom": "1em", "fontSize": "0.95em"}),
                    html.Div([
                        html.P(html.Strong("Zurich Office:"), style={"marginBottom": "0.3em", "color": "#1F2937"}),
                        html.P([
                            "Scheuchzerstrasse 21", html.Br(),
                            "8006 Zürich, Switzerland", html.Br(),
                            "Tel: +41 44 634 44 01"
                        ], style={"fontSize": "0.9em", "lineHeight": "1.6", "color": "#4B5563", "marginBottom": "0"})
                    ], style={"paddingTop": "1em", "borderTop": "1px solid var(--border-color)"})
                ], style={
                    "backgroundColor": "rgba(255, 255, 255, 0.5)",
                    "border": "1px solid var(--border-color)",
                    "borderRadius": "8px",
                    "padding": "1.8em",
                    "transition": "all 0.3s ease",
                    "boxShadow": "var(--shadow-sm)"
                }),

                # Prof. Lienkamp Card
                html.Div([
                    html.H4("Prof. Dr. Soeren Lienkamp", style={"color": "#2E5BFF", "fontSize": "1.2em", "marginBottom": "0.8em", "fontWeight": "600"}),
                    html.P(html.Strong("Principal Investigator"), style={"marginBottom": "0.5em", "color": "#1F2937"}),
                    html.P("Institute of Anatomy", style={"marginBottom": "0.3em", "color": "#4B5563", "fontSize": "0.95em"}),
                    html.P("University of Zurich", style={"marginBottom": "0.8em", "color": "#4B5563", "fontSize": "0.95em"})
                ], style={
                    "backgroundColor": "rgba(255, 255, 255, 0.5)",
                    "border": "1px solid var(--border-color)",
                    "borderRadius": "8px",
                    "padding": "1.8em",
                    "transition": "all 0.3s ease",
                    "boxShadow": "var(--shadow-sm)"
                }),

                # Dr. Naert Card
                html.Div([
                    html.H4("Dr. Thomas Naert", style={"color": "#2E5BFF", "fontSize": "1.2em", "marginBottom": "0.8em", "fontWeight": "600"}),
                    html.P(html.Strong("Lead Inventor"), style={"marginBottom": "0.5em", "color": "#1F2937"}),
                    html.P("Department of Biomedical Molecular Biology", style={"marginBottom": "0.3em", "color": "#4B5563", "fontSize": "0.95em"}),
                    html.P("Ghent University", style={"marginBottom": "0.8em", "color": "#4B5563", "fontSize": "0.95em"})
                ], style={
                    "backgroundColor": "rgba(255, 255, 255, 0.5)",
                    "border": "1px solid var(--border-color)",
                    "borderRadius": "8px",
                    "padding": "1.8em",
                    "transition": "all 0.3s ease",
                    "boxShadow": "var(--shadow-sm)"
                })
            ], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                "gap": "1.5em",
                "marginBottom": "2em"
            }),

            html.P(
                "Unitectra is the technology transfer office of the Universities of Basel, Bern and Zurich, supporting universities and their researchers in the commercial exploitation of research findings through patent protection, licensing negotiations, and technology transfer services.",
                style={"fontSize": "0.95em", "lineHeight": "1.6", "color": "#6B7280", "marginTop": "2em"}
            )
        ], style={"marginBottom": "3em"})
    ], style={
        "maxWidth": "1000px",
        "margin": "0 auto",
        "padding": "2em",
        "backgroundColor": "var(--background-primary)",
        "borderRadius": "12px",
        "boxShadow": "var(--shadow-lg)",
        "border": "1px solid var(--border-color)"
    }),
    create_disclaimer()
], style={"padding": "2em", "minHeight": "80vh", "backgroundColor": "var(--background-secondary)"})
