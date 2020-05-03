import time
from helpers import *
from messages import *
from network import build_graph

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps.messages import layout as msg_layout
from apps.messages import callbacks as msg_callbacks


# Dataload Messages
df, df_photos = load_data()
assert MY_NAME in df.sender_name.unique().tolist(),\
    f"Name \"{MY_NAME}\" (in config.py) is not a valid sender_name, is your name \"{df.sender_name.mode().values[0]}\"?"

# Preprocessing Messages
t0 = time.time()
all_contacts = sorted(df.sender_name.unique().tolist())
contact_counts = count_msg_per_contact(df)
total_sent = len(df.loc[df.sender_name == MY_NAME])
total_received = len(df.loc[df.sender_name != MY_NAME])
first_message_date = df.timestamp.min().strftime('%d-%m-%Y')
last_message_date = df.timestamp.max().strftime('%d-%m-%Y')
weekly_pattern = calc_activity_pattern(df)
names, connectivity = connection_matrix(df)
G = build_graph(connectivity, names)
logging.info(f'Preprocessing took {time.time()-t0:.4f} seconds.')

# Page Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(children=[
        html.Div(children=[
            dcc.Link('Home', href='/'),
        ],
            style={'width': '5%', 'display': 'inline-block'}
        ),
        html.Div(children=[
            dcc.Link('Messages', href='/messages'),
        ],
            style={'width': '5%', 'display': 'inline-block'}
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
msg_callbacks.register_callbacks(
    app, df, df_photos, weekly_pattern, contact_counts, all_contacts, G)

# Callbacks that render the page content based on the current path
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div(html.H1('This is the homepage. Nothing to see here.'))
    elif pathname == '/messages':
        return msg_layout.get_layout(total_sent, total_received, first_message_date, last_message_date)
    else:
        return html.Div(html.H1('404'))


if __name__ == '__main__':
    app.run_server(debug=True)
