from dash import html


def indelphi_model_tooltip():
    """CSS-only hover tooltip for the 'Step 1: Select inDelphi Model' heading.

    Returns a span wrapping the ⓘ icon + hidden tooltip box.
    Shown via CSS :hover — no JS initialization, safe across page navigation.
    """
    content = html.Div([
        html.P(
            html.Strong("Choosing an inDelphi model"),
            style={'marginBottom': '0.5em', 'fontSize': '0.95rem'}
        ),
        html.P(
            "inDelphi was trained on five cell types: mESC, HEK293, U2OS, HCT116, and K562. "
            "Repair outcome preferences are cell-type-specific, and predictive performance can vary "
            "when the model is applied outside its training distribution.",
            style={'marginBottom': '0.6em'}
        ),
        html.Ul([
            html.Li([
                html.Strong("In the training panel: "),
                "select the matching model.",
            ], style={'marginBottom': '0.35em'}),
            html.Li([
                html.Strong("Independently validated: "),
                "use that combination. The mESC model has been validated for early Xenopus and "
                "zebrafish embryos in our hands (Naert et al., Sci Rep 2020). For zebrafish, "
                "Lin et al. (NAR 2025) benchmarked inDelphi, Lindel, and FORECasT in a large-scale "
                "F0 crispant screen — all three useful, with some variation between tools. Note: "
                "these benchmarks address indel-outcome prediction at the DSB, whereas Pythia extends "
                "predictions to the full genome–transgene junction — a related but distinct task, "
                "currently supported only by inDelphi within Pythia.",
            ], style={'marginBottom': '0.35em'}),
            html.Li([
                html.Strong("Other contexts "),
                "(primary cells, iPSCs, cancer lines, non-mammalian systems): MMEJ is broadly "
                "conserved, and Pythia-guided designs transfer reasonably well across mammalian cell "
                "types. Pick the model that most plausibly resembles your system — if unsure, mESC "
                "and HEK293 are sensible defaults. Treat predictions as strong guides rather than "
                "exact forecasts.",
            ]),
        ], style={'marginBottom': '0.6em', 'paddingLeft': '1.1em'}),
        html.P([
            html.Strong("⚠️ Not recommended: "),
            "cells with compromised MMEJ machinery (e.g., POLQ-knockout or Pol θ–deficient "
            "backgrounds). Microhomology-driven repair outcomes are substantially reduced in these "
            "contexts, and predictions are unlikely to be informative.",
        ], style={'marginBottom': '0.4em'}),
        html.P([
            html.Strong("Note on iPSCs: "),
            "hiPSCs have been reported to show higher MMEJ usage than inDelphi predicts "
            "(Grajcarek et al., Nat Commun 2019). Empirical validation is especially advisable here.",
        ]),
    ], style={'fontSize': '0.82rem', 'lineHeight': '1.55', 'textAlign': 'left'})

    return html.Span([
        'ⓘ',
        html.Div(content, className='info-tooltip-box'),
    ], className='info-tooltip-wrapper')
