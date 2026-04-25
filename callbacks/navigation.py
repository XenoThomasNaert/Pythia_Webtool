import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

from layouts.common import create_header, create_disclaimer
from layouts.home import index_page
from layouts.about import about_page
from layouts.citation import citation_page
from layouts.licenses import licenses_page
from layouts.team import team_page
from layouts.help import help_page
from callbacks.integration import page_1_layout
from callbacks.editing import page_2_layout
from callbacks.xenopus_browser import page_3_layout
from callbacks.tagging_landing import page_tagging_landing
from callbacks.tagging_custom import page_tagging_custom_layout
from callbacks.tagging_intron import page_tagging_intron_layout
from callbacks.precalculated import page_tagging_precalculated_layout


def register_callbacks(app):

    @app.callback(
        [Output('dev-preview-modal', 'is_open'),
         Output('dev-preview-session-store', 'data')],
        [Input('dev-preview-close', 'n_clicks'),
         Input('url', 'pathname')],
        [State('dev-preview-dont-show', 'value'),
         State('dev-preview-session-store', 'data')],
        prevent_initial_call=False
    )
    def manage_dev_preview_modal(n_clicks, pathname, dont_show_value, store_data):
        """Manage the development preview modal visibility"""
        # Initialize store_data if None
        if store_data is None:
            store_data = {'show_modal': True}

        # If user clicked "I Understand"
        if n_clicks and n_clicks > 0:
            # Check if "don't show again" was checked
            if dont_show_value and 'dont_show' in dont_show_value:
                store_data['show_modal'] = False
                return False, store_data
            else:
                # Just close this time, but show again on next page load
                return False, store_data

        # On any page load, check if we should show the modal
        # Show modal unless user has previously checked "don't show again"
        return store_data.get('show_modal', True), store_data

    @app.callback(
        Output('team-contact-modal', 'is_open'),
        [Input('team-contact-link', 'n_clicks'),
         Input('team-contact-close', 'n_clicks')],
        [State('team-contact-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_team_contact_modal(n_open, n_close, is_open):
        """Toggle the team contact modal"""
        if n_open or n_close:
            return not is_open
        return is_open

    @app.callback(
        Output('help-contact-modal', 'is_open'),
        [Input('help-contact-link', 'n_clicks'),
         Input('help-bug-link', 'n_clicks'),
         Input('help-contact-close', 'n_clicks')],
        [State('help-contact-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_help_contact_modal(n_contact, n_bug, n_close, is_open):
        """Toggle the help contact modal"""
        if n_contact or n_bug or n_close:
            return not is_open
        return is_open

    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/page-1':
            return html.Div([create_header("integration"), page_1_layout, create_disclaimer()])
        elif pathname == '/page-2':
            return html.Div([create_header("editing"), page_2_layout, create_disclaimer()])
        elif pathname == '/page-3':
            return html.Div([create_header("editing"), page_3_layout, create_disclaimer()])
        elif pathname == '/page-tagging':
            return html.Div([create_header("tagging"), page_tagging_landing, create_disclaimer()])
        elif pathname == '/page-tagging-precalculated':
            return html.Div([create_header("tagging"), page_tagging_precalculated_layout, create_disclaimer()])
        elif pathname == '/page-tagging-custom':
            return html.Div([create_header("tagging"), page_tagging_custom_layout, create_disclaimer()])
        elif pathname == '/page-tagging-intron':
            return html.Div([create_header("tagging"), page_tagging_intron_layout, create_disclaimer()])
        elif pathname == '/about':
            return about_page
        elif pathname == '/citation':
            return citation_page
        elif pathname == '/licenses':
            return licenses_page
        elif pathname == '/team':
            return team_page
        elif pathname == '/help':
            return help_page
        else:
            return html.Div([create_header("home"), index_page])

    @app.callback(Output('url', 'pathname'),
                  [Input('page-1-link', 'n_clicks'),
                   Input('page-tagging-link', 'n_clicks'),
                   Input('page-2-link', 'n_clicks')],
                  [State('url', 'pathname')])
    def navigate_to_page(btn1, btn_tagging, btn2, current_path):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        # Only respond to actual button clicks, not initial page loads
        if changed_id and 'page-1-link' in changed_id and btn1:
            return '/page-1'
        elif changed_id and 'page-tagging-link' in changed_id and btn_tagging:
            return '/page-tagging'
        elif changed_id and 'page-2-link' in changed_id and btn2:
            return '/page-2'

        # Don't change the URL if we're not responding to a button click
        return current_path or '/'

    # Altmetric badge callback
    @app.callback(
        Output('altmetric-container', 'children'),
        Input('altmetric-container', 'id')
    )
    def load_altmetric(_):
        return html.Iframe(
            srcDoc="""
            <!DOCTYPE html>
            <html>
            <head>
                <script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script>
            </head>
            <body style='margin:0; padding:20px; display:flex; justify-content:center; align-items:flex-start; background:transparent; transform:scale(1.2); transform-origin:top center;'>
                <div class='altmetric-embed' data-badge-type='donut' data-badge-details='right' data-doi='10.1038/s41587-025-02771-0'></div>
            </body>
            </html>
            """,
            style={
                "border": "0",
                "width": "700px",
                "height": "350px",
                "overflow": "hidden"
            }
        )
