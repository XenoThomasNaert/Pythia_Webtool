from dash import dcc, html
from layouts.common import create_header, create_disclaimer


# Citation page
citation_page = html.Div([
    create_header("citation"),
    html.Div([
        html.H1("Citation", style={"textAlign": "center", "marginBottom": "2em"}),
        html.Div([
            html.H2("How to Cite Pythia", style={"marginBottom": "1em"}),
            html.P("If you use Pythia in your research, please cite the following publication:",
                   style={"marginBottom": "1.5em", "fontSize": "1.1em"}),

            html.Div([
                html.H3("Published Article:", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.P([
                    html.Strong("Precise, predictable genome integrations by deep-learning-assisted design of microhomology-based templates"),
                    html.Br(), html.Br(),
                    html.Strong("Authors: "), "Thomas Naert, Taiyo Yamamoto, Shuting Han, Melanie Horn, Phillip Bethge, Nikita Vladimirov, Fabian F. Voigt, Joana Figueiro-Silva, Ruxandra Bachmann-Gagescu, Fritjof Helmchen, Soeren S. Lienkamp", html.Br(),
                    html.Strong("Journal: "), "Nature Biotechnology", html.Br(),
                    html.Strong("Published: "), "12 August 2025", html.Br(),
                    html.Strong("DOI: "), html.A("https://doi.org/10.1038/s41587-025-02771-0", href="https://doi.org/10.1038/s41587-025-02771-0", target="_blank", style={"color": "#2E5BFF", "textDecoration": "underline"})
                ], style={
                    "backgroundColor": "var(--background-secondary)",
                    "padding": "1.5em",
                    "borderRadius": "8px",
                    "border": "1px solid var(--border-color)",
                    "fontSize": "0.95em",
                    "lineHeight": "1.8"
                })
            ], style={"marginBottom": "2em"}),

            html.Div([
                html.H3("Citation Details:", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.Ul([
                    html.Li([html.Strong("Received: "), "19 August 2024"]),
                    html.Li([html.Strong("Accepted: "), "10 July 2025"]),
                    html.Li([html.Strong("Published: "), "12 August 2025"]),
                    html.Li([html.Strong("Version of record: "), "12 August 2025"])
                ], style={"lineHeight": "1.8", "fontSize": "0.95em"})
            ], style={"marginBottom": "2em"}),

            html.Div([
                html.H3("BibTeX Format:", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.Pre([
                    "@article{naert2025precise,\n",
                    "  title={Precise, predictable genome integrations by deep-learning-assisted design of microhomology-based templates},\n",
                    "  author={Naert, Thomas and Yamamoto, Taiyo and Han, Shuting and Horn, Melanie and Bethge, Phillip and Vladimirov, Nikita and Voigt, Fabian F and Figueiro-Silva, Joana and Bachmann-Gagescu, Ruxandra and Helmchen, Fritjof and Lienkamp, Soeren S},\n",
                    "  journal={Nature Biotechnology},\n",
                    "  year={2025},\n",
                    "  month={August},\n",
                    "  day={12},\n",
                    "  publisher={Nature Publishing Group},\n",
                    "  doi={10.1038/s41587-025-02771-0},\n",
                    "  url={https://doi.org/10.1038/s41587-025-02771-0}\n",
                    "}"
                ], style={
                    "backgroundColor": "var(--background-secondary)",
                    "padding": "1.5em",
                    "borderRadius": "8px",
                    "border": "1px solid var(--border-color)",
                    "overflow": "auto",
                    "fontSize": "0.9em",
                    "fontFamily": "monospace"
                })
            ], style={"marginBottom": "2em"}),

            html.Div([
                html.H3("Download Citation:", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.P([
                    html.A("Download citation from Nature Biotechnology",
                           href="https://doi.org/10.1038/s41587-025-02771-0",
                           target="_blank",
                           style={"color": "#2E5BFF", "textDecoration": "underline", "fontSize": "1.05em"})
                ])
            ], style={"marginBottom": "2em"}),

            html.Div([
                html.H3("Share this article:", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.P([
                    "Anyone you share the following link with will be able to read this content via Springer Nature SharedIt content-sharing initiative: ",
                    html.A("https://doi.org/10.1038/s41587-025-02771-0",
                           href="https://doi.org/10.1038/s41587-025-02771-0",
                           target="_blank",
                           style={"color": "#2E5BFF", "textDecoration": "underline"})
                ], style={"fontSize": "0.95em", "lineHeight": "1.6"})
            ], style={"marginBottom": "2em"}),

            html.Div([
                html.H3("Acknowledgments:", style={"color": "var(--primary-color)", "marginBottom": "0.5em"}),
                html.P("This work was supported by funding from the institutions shown in the header.",
                       style={"fontSize": "1em", "lineHeight": "1.6"})
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
