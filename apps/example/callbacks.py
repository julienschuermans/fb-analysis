import plotly.express as px
from dash.dependencies import Input, Output
import dash_html_components as html


def register_callbacks(app):

    @app.callback(
        Output('slider-output', 'children'),
        [Input('slider', 'value')])
    def example_callback(value):
        """This callback changes the text in some div based on the slider input"""

        if value == 1:
            return 'You selected ONE'
        if value == 2:
            return 'You selected TWO'
