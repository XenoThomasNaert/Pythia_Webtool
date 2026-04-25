from dash import dcc, html


index_page = html.Div(
    [
        html.Div([
            html.H1(
                "Pythia",
                style={
                    "color": "#1F2937",
                    "fontSize": "3em",
                    "textAlign": "center",
                    "marginBottom": "0.125em",
                    "marginTop": "1.5em",
                    "fontWeight": "700",
                    "letterSpacing": "-0.02em",
                    "paddingLeft": "0.5em",
                    "paddingRight": "0.5em",
                    "paddingBottom": "0.2em",
                    "lineHeight": "1.2",
                    "overflow": "visible"
                }
            ),
            html.P(
                "Deep learning-powered CRISPR design for predictable and precise genome engineering",
                style={
                "color": "#6B7280",
                "fontSize": "1.3em",
                "textAlign": "center",
                "marginBottom": "2em",
                "fontWeight": "400",
                "maxWidth": "900px",
                "margin": "-1em auto 2em auto"
            }),

            # Three feature cards (now clickable!)
            html.Div([
                # Integration card - clickable
                dcc.Link([
                    html.Div([
                        html.Div("🧬", style={"fontSize": "2.5em", "marginBottom": "0.5em"}),
                        html.H3("Integration", style={"color": "#2E5BFF", "fontSize": "1.3em", "marginBottom": "0.5em", "fontWeight": "600"}),
                        html.P("Design transgene cassettes for targeted genomic integration",
                               style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.5"})
                    ], className="feature-card", style={
                        "flex": "1",
                        "padding": "1.5em",
                        "backgroundColor": "#F9FAFB",
                        "borderRadius": "12px",
                        "margin": "0.5em",
                        "textAlign": "center",
                        "border": "1px solid #E5E7EB",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                        "cursor": "pointer"
                    })
                ], href="/page-1", style={"textDecoration": "none", "flex": "1"}),

                # Tagging card - clickable
                dcc.Link([
                    html.Div([
                        html.Div("🏷️", style={"fontSize": "2.5em", "marginBottom": "0.5em"}),
                        html.H3("Tagging", style={"color": "#2E5BFF", "fontSize": "1.3em", "marginBottom": "0.5em", "fontWeight": "600"}),
                        html.P("Label endogenous proteins with fluorescent tags",
                               style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.5"})
                    ], className="feature-card", style={
                        "flex": "1",
                        "padding": "1.5em",
                        "backgroundColor": "#F9FAFB",
                        "borderRadius": "12px",
                        "margin": "0.5em",
                        "textAlign": "center",
                        "border": "1px solid #E5E7EB",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                        "cursor": "pointer"
                    })
                ], href="/page-tagging", style={"textDecoration": "none", "flex": "1"}),

                # Editing card - clickable
                dcc.Link([
                    html.Div([
                        html.Div("✏️", style={"fontSize": "2.5em", "marginBottom": "0.5em"}),
                        html.H3("Editing", style={"color": "#2E5BFF", "fontSize": "1.3em", "marginBottom": "0.5em", "fontWeight": "600"}),
                        html.P("Create scarless single-nucleotide modifications",
                               style={"color": "#4B5563", "fontSize": "0.95em", "lineHeight": "1.5"})
                    ], className="feature-card", style={
                        "flex": "1",
                        "padding": "1.5em",
                        "backgroundColor": "#F9FAFB",
                        "borderRadius": "12px",
                        "margin": "0.5em",
                        "textAlign": "center",
                        "border": "1px solid #E5E7EB",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                        "cursor": "pointer"
                    })
                ], href="/page-2", style={"textDecoration": "none", "flex": "1"})
            ], style={
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "center",
                "maxWidth": "1000px",
                "margin": "0 auto 1.5em auto"
            }),

            # Help message under cards
            html.P(
                [
                    "Not sure which module fits your needs? Check out our ",
                    dcc.Link("Help & Documentation", href="/help", style={"color": "#2E5BFF", "textDecoration": "underline"}),
                    " to learn more!"
                ],
                style={"textAlign": "center", "fontStyle": "italic", "color": "#6B7280", "fontSize": "0.95em", "marginBottom": "1.5em"}
            ),

            # Link to About page
            html.Div([
                dcc.Link([
                    html.H2("What's Pythia All About?", style={
                        "color": "#1F2937",
                        "fontSize": "1.4em",
                        "marginBottom": "0.5em",
                        "fontWeight": "600"
                    }),
                    html.P("Explore accessible research briefings, news coverage, and the actual research paper", style={
                        "color": "#6B7280",
                        "fontSize": "0.95em",
                        "marginBottom": "0"
                    })
                ], href="/about", style={
                    "textDecoration": "none",
                    "display": "block",
                    "padding": "2em",
                    "backgroundColor": "#F9FAFB",
                    "borderRadius": "12px",
                    "border": "2px solid #E5E7EB",
                    "transition": "all 0.2s ease",
                    "cursor": "pointer",
                    "textAlign": "center"
                }, className="about-link-card")
            ], style={
                "maxWidth": "800px",
                "margin": "2em auto 3em auto"
            }),

        ], style={
            "maxWidth": "1200px",
            "margin": "0 auto",
            "padding": "0 2em"
        }),
        # Funding logos (first line)
        html.Div(
            [
            html.Img(src="/assets/Landing/Logo/images.png", style={"maxWidth": "7%", "width": "7%", "height": "7%", "marginTop": "1em", "marginRight": "2.5em"}),
            html.Img(src="/assets/Landing/Logo/ERC.png", style={"maxWidth": "15%", "width": "15%", "height": "15%", "marginTop": "1em", "marginRight": "2.5em"}),
            html.Img(src="/assets/Landing/Logo/swiss.png", style={"maxWidth": "18%", "width": "18%", "height": "19%", "marginTop": "1em", "marginRight": "2.5em"}),
            html.Img(src="/assets/Landing/Logo/fwo.png", style={"maxWidth": "8%", "width": "8%", "height": "8%", "marginTop": "1em", "marginRight": "1.5em"}),
            ],
            style={"display": "flex", "justifyContent": "center", "marginBottom": "1em"}
        ),

        # University logos (second line)
        html.Div(
            [
            html.Img(src="/assets/Landing/Logo/uzh.png", className="university-logo-uzh", style={"maxWidth": "15%", "width": "15%", "height": "15%", "marginTop": "10em", "marginRight": "2.5em"}),
            html.Img(src="/assets/Landing/Logo/eth.png", className="university-logo-eth", style={"maxWidth": "12%", "width": "12%", "height": "12%", "marginTop": "4.5em", "marginRight": "2.5em"}),
            html.Img(src="/assets/Landing/Logo/logo_UGent_EN_RGB_2400_color2.png", className="university-logo-ugent", style={"maxWidth": "8.64%", "width": "8.64%", "height": "8.64%", "marginTop": "1em", "marginBottom": "2em"}),
            ],
            style={"display": "flex", "justifyContent": "center", "alignItems": "flex-start"}
        ),

        html.P(
            [
                "Disclaimer: This tool and its content are provided strictly for academic research purposes only. Any application of the techniques, tools, or information provided here to purposes other than research, including but not limited to commercial use, therapeutic use or other clinical applications, is strictly prohibited. For more information, see our ",
                dcc.Link("Licenses", href="/licenses", style={"color": "#2E5BFF", "textDecoration": "underline"}),
                " page. Since we use pythonanywhere as our hosting provider, our data is transferred to the US by Amazon Web Services, which is certified under the EU-US Privacy Shield Framework. This provides certain safeguards in relation to the handling of your personal data. You can find pythonanywhere's privacy policy under https://www.pythonanywhere.com/privacy_v2/. This website does not implement any user analytics software."
            ],
            style={"color": "black", "fontSize": "0.8em", "textAlign": "center", "marginBottom": "2em"})
    ],
    style={"padding": "2em", "minHeight": "80vh"}
)
