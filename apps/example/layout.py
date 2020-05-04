import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html


def get_layout():

    layout = html.Div(children=[
        html.H1(children='This is the layout of the example app'),
        dcc.Slider(id='slider', min=1, max=2, step=1),
        html.H3(id='slider-output')
    ])
    return layout
