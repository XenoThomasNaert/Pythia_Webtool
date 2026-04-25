from dash import dcc, html
from layouts.common import create_header, create_disclaimer


about_page = html.Div([
    create_header("about"),
    html.Div([
        html.H1("What's Pythia All About?", style={
            "color": "#1F2937",
            "fontSize": "3em",
            "textAlign": "center",
            "marginBottom": "0.5em",
            "marginTop": "1.5em",
            "fontWeight": "700",
            "letterSpacing": "-0.02em",
            "paddingBottom": "0.2em"
        }),
        html.P("Explore accessible research briefings, news coverage, and the actual research paper", style={
            "color": "#6B7280",
            "fontSize": "1.2em",
            "textAlign": "center",
            "marginBottom": "2em",
            "fontWeight": "400"
        }),

        # News Coverage Section
        html.Div([
            html.H2("News Coverage", style={
                "color": "#1F2937",
                "fontSize": "2em",
                "textAlign": "center",
                "marginBottom": "0.5em",
                "fontWeight": "600"
            }),
            html.P("Accessible digests from the scientific community", style={
                "color": "#6B7280",
                "fontSize": "1.1em",
                "textAlign": "center",
                "marginBottom": "2em"
            }),

            # Three news cards
            html.Div([
                # Nature Research Briefing
                html.A([
                    html.Div([
                        html.H3("Nature Biotechnology", style={"color": "#D97706", "fontSize": "1.2em", "marginBottom": "0.25em", "fontWeight": "600"}),
                        html.P("Research Briefing", style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.3", "margin": "0"})
                    ], className="feature-card", style={
                        "padding": "1.5em 1.5em",
                        "backgroundColor": "#F9FAFB",
                        "borderRadius": "12px",
                        "border": "2px solid #E5E7EB",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                        "height": "120px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "flex-start",
                        "textAlign": "center"
                    })
                ], href="https://www.nature.com/articles/s41587-025-02818-2", target="_blank", style={"textDecoration": "none", "flex": "1"}),

                # ETH Zurich News
                html.A([
                    html.Div([
                        html.H3("ETH Zurich News", style={"color": "#D97706", "fontSize": "1.2em", "marginBottom": "0.25em", "fontWeight": "600"}),
                        html.P("AI Meets CRISPR for Precise Gene Editing", style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.3", "margin": "0"})
                    ], className="feature-card", style={
                        "padding": "1.5em 1.5em",
                        "backgroundColor": "#F9FAFB",
                        "borderRadius": "12px",
                        "border": "2px solid #E5E7EB",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                        "height": "120px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "flex-start",
                        "textAlign": "center"
                    })
                ], href="https://hest.ethz.ch/en/news/news-and-events/2025/08/ai-meets-crispr-for-precise-gene-editing.html", target="_blank", style={"textDecoration": "none", "flex": "1"}),

                # UZH News
                html.A([
                    html.Div([
                        html.H3("University of Zurich News", style={"color": "#D97706", "fontSize": "1.2em", "marginBottom": "0.25em", "fontWeight": "600"}),
                        html.P("AI-Powered Genome Editing", style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.3", "margin": "0"})
                    ], className="feature-card", style={
                        "padding": "1.5em 1.5em",
                        "backgroundColor": "#F9FAFB",
                        "borderRadius": "12px",
                        "border": "2px solid #E5E7EB",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                        "height": "120px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "flex-start",
                        "textAlign": "center"
                    })
                ], href="https://www.news.uzh.ch/en/articles/media/2025/AI-genome-editing.html", target="_blank", style={"textDecoration": "none", "flex": "1"}),

            ], style={
                "display": "flex",
                "gap": "1.5em",
                "marginBottom": "8em",
                "flexWrap": "wrap",
                "justifyContent": "center"
            })
        ], style={"maxWidth": "1100px", "margin": "0 auto", "padding": "0 2em"}),

        # Research Paper Section
        html.Div([
            html.H2("The Research Paper", style={
                "color": "#1F2937",
                "fontSize": "2em",
                "textAlign": "center",
                "marginBottom": "0.5em",
                "fontWeight": "600",
                "paddingTop": "2em"
            }),
            html.P("Ready to dive into the nitty-gritty details?", style={
                "color": "#6B7280",
                "fontSize": "1.1em",
                "textAlign": "center",
                "marginBottom": "2em"
            }),

            # Single card for the paper
            html.Div([
                html.A([
                    html.Div([
                        html.H3("Precise, predictable genome integrations by deep-learning-assisted design of microhomology-based templates",
                                style={"color": "#10B981", "fontSize": "1.3em", "marginBottom": "0.75em", "fontWeight": "600", "lineHeight": "1.4"}),
                        html.P("Naert et al., Nature Biotechnology 2025",
                               style={"color": "#4B5563", "fontSize": "1em", "lineHeight": "1.5", "fontWeight": "500"})
                    ], className="feature-card", style={
                        "padding": "2em",
                        "backgroundColor": "#F9FAFB",
                        "borderRadius": "12px",
                        "textAlign": "center",
                        "border": "2px solid #10B981",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                        "minHeight": "90px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "maxWidth": "700px",
                        "margin": "0 auto"
                    })
                ], href="https://www.nature.com/articles/s41587-025-02771-0", target="_blank", style={"textDecoration": "none"}),

            ], style={
                "display": "flex",
                "justifyContent": "center",
                "marginBottom": "2em"
            }),

            # Altmetric badge container
            html.Div(id='altmetric-container', style={
                "display": "flex",
                "justifyContent": "center",
                "marginTop": "4em",
                "marginBottom": "3em",
                "overflowX": "hidden"
            }),

            # Help link below Altmetric
            html.P([
                "Still have questions? Visit our ",
                dcc.Link("Help & Documentation", href="/help", style={"color": "#2E5BFF", "textDecoration": "underline"}),
                " for more information."
            ], style={
                "textAlign": "center",
                "color": "#6B7280",
                "fontSize": "1em",
                "marginTop": "2em",
                "marginBottom": "2em"
            })
        ], style={"maxWidth": "1100px", "margin": "0 auto", "padding": "0 2em"}),

        create_disclaimer()

    ], style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "2em",
        "minHeight": "80vh"
    })
], style={"backgroundColor": "white", "minHeight": "100vh"})
