import time
import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

from apps.example import layout as example_layout
from apps.example import callbacks as example_callbacks

from apps.messages import layout as msg_layout
from apps.messages import callbacks as msg_callbacks

from modules.dataloader import load_data
from modules.messages import *
from modules.network import build_graph

from config import MY_NAME

# Dataload Messages
t0 = time.time()
df, df_photos = load_data()
logging.info(f'Loading all data took {time.time()-t0:.4f} seconds.')

assert MY_NAME in df.sender_name.unique().tolist(),\
    f"Name \"{MY_NAME}\" (in config.py) is not a valid sender_name, is your name \"{df.sender_name.mode().values[0]}\"?"

# Preprocessing Messages
t0 = time.time()
names, adjacency = get_weighted_adjacency_matrix(df)
G = build_graph(adjacency, names)
logging.info(f'Preprocessing took {time.time()-t0:.4f} seconds.')

# Page Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(children=[
        html.Div(children=[
            dcc.Link('Home', href='/'),
        ],
            style={'width': '15%', 'display': 'inline-block'}
        ),
        html.Div(children=[
            dcc.Link('Messages', href='/messages'),
        ],
            style={'width': '15%', 'display': 'inline-block'}
        ),
        html.Div(children=[
            dcc.Link('Example', href='/example'),
        ],
            style={'width': '15%', 'display': 'inline-block'}
        )
    ],
        style={
            'margin-bottom': '15px',
            'background-color': '#F0F8FF'
    }
    ),
    html.Div(id='page-content')
])

# Register callbacks for separate apps
example_callbacks.register_callbacks(app)
msg_callbacks.register_callbacks(
    app, df, df_photos, G)

# Callbacks that render the page content based on the current path
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div(html.H1('This is the homepage. Nothing to see here.'))
    elif pathname == '/messages':
        return msg_layout.get_layout(df)
    elif pathname == '/example':
        return example_layout.get_layout()
    else:
        return html.Div(html.H1('404'))


if __name__ == '__main__':
    app.run_server(debug=False)
