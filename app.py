from messages import *
from helpers import *
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px

import pandas as pd
import numpy as np

import logging
logging.basicConfig(level=logging.INFO)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = build_dataframe()
assert MY_NAME in df.sender_name.unique().tolist(),\
    f"Name \"{MY_NAME}\" is not a valid sender_name"
contact_counts = count_msg_per_contact(df)
total_sent = len(df.loc[df.sender_name == MY_NAME])
total_received = len(df.loc[df.sender_name != MY_NAME])
first_message_date = df.timestamp.min().strftime('%d-%m-%Y')
last_message_date = df.timestamp.max().strftime('%d-%m-%Y')

pattern = calc_activity_pattern(df)

n, m = connection_matrix(df)

connection_heatmap_fig = px.imshow(m,
                                   labels=dict(
                                       y="Sender", x="Receiver", color="#Messages sent/received"),
                                   y=n,
                                   x=n,
                                   )
connection_heatmap_fig.update_layout(
    autosize=True,
    width=1000,
    height=700,
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    )
)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def generate_table_children(dataframe, max_rows=10):
    return [
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ]


app.layout = html.Div(children=[
    html.H1(children='Facebook Messenger analysis'),

    html.Div(children=f'''
        Exploring {total_sent} messages sent and {total_received} received between {first_message_date} and {last_message_date}
    '''),

    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Global analysis', children=[

            html.H4('#Messages sent/received'),
            html.Label('Select a timeframe'),
            dcc.Dropdown(style={'width': '49%', 'display': 'inline-block'},
                         id='global-timeframe-dropdown',
                         options=[
                {'label': item, 'value': item} for item in ['Hourly', 'Daily', 'Monthly', 'Yearly']
            ],
                value='Monthly'
            ),
            dcc.Graph(id='sent-received-bar-graph'),

            html.H4('Weekly activity'),
            dcc.Graph(
                id='weekly-activity-heatmap',
                figure=px.imshow(pattern.T,
                                 labels=dict(
                                     y="Day of Week", x="Time of Day", color="#Messages sent"),
                                 y=['Monday', 'Tuesday', 'Wednesday',
                                     'Thursday', 'Friday', 'Saturday', 'Sunday'],
                                 x=[str(x)+'h' for x in range(24)]
                                 )
            ),

            html.H4('Contact interactivity'),
            dcc.Graph(
                id='connection-heatmap',
                figure=connection_heatmap_fig,
            ),

            html.H4('#Messages per contact'),
            dcc.Graph(id='contact-count-bar-graph',
                      figure={
                          'data': [
                              {
                                  'x': contact_counts['theirs'][0],
                                  'y': contact_counts['theirs'][1],
                                  'type': 'bar',
                              },
                          ],
                      }
                      ),
        ]),
        dcc.Tab(label='Chat analysis', children=[

            html.Div(children=[
                html.Label('Select a chat', style={
                           'width': '49%', 'display': 'inline-block'}),
                html.Label('Select a timeframe', style={
                           'width': '49%', 'display': 'inline-block'}),
            ]),

            html.Div(children=[

                dcc.Dropdown(style={'width': '49%', 'display': 'inline-block'},
                             id='chat-dropdown',
                             options=[
                    {'label': title, 'value': title} for title in list_chat_titles(df)
                ],
                    value=list_chat_titles(df)[0]
                ),

                dcc.Dropdown(style={'width': '49%', 'display': 'inline-block'},
                             id='timeframe-dropdown',
                             options=[
                    {'label': item, 'value': item} for item in ['Hourly', 'Daily', 'Monthly', 'Yearly']
                ],
                    value='Monthly'
                ),
            ]),

            dcc.Graph(id='msg-count-lines'),

            html.Div(children=[
                dcc.Graph(style={'width': '49%', 'display': 'inline-block'},
                          id='hourly-bars'),

                dcc.Graph(style={'width': '49%', 'display': 'inline-block'},
                          id='weekly-bars'),
            ]),


            html.H4('#Messages per participant'),
            dcc.Graph(id='participants-pie-chart'),

            html.H4('Top words per participant'),
            html.Table(id='top-words-table'),

        ]),
        dcc.Tab(label='Contact analysis', children=[

            html.H4('Stats per contact'),
            html.Label('Select one or more contacts'),
            dcc.Dropdown(id='contact-select-dropdown',
                         options=[
                             {'label': contact, 'value': contact} for contact in sorted(df.sender_name.unique().tolist())],
                         value=sorted(df.sender_name.unique().tolist())[:5],
                         multi=True
                         ),

            html.Table(id='contacts-table'),
        ]),

    ]),

])


@app.callback(
    Output('sent-received-bar-graph', 'figure'),
    [Input('global-timeframe-dropdown', 'value')]
)
def update_global_sent_received(selected_timeframe):
    sent_received = calc_sent_received(df, selected_timeframe)

    fig = px.bar(sent_received, x='timestamp', y='msg_count',
                 color='type', barmode='group', labels={'msg_count': '#messages', 'timestamp': 'Time'})

    return fig


@app.callback(
    [Output('msg-count-lines', 'figure'),
     Output('participants-pie-chart', 'figure'),
     Output('top-words-table', 'children')],
    [Input('chat-dropdown', 'value'),
     Input('timeframe-dropdown', 'value')]
)
def update_figure_and_table(selected_chat_title, selected_timeframe):
    df_chat = filter_chat(df, selected_chat_title)

    most_used_words = {}
    max_vocab_size = 0

    for participant in df_chat.sender_name.unique().tolist():
        wc = wordcount(df_chat.loc[df.sender_name == participant])
        if len(wc) > max_vocab_size:
            max_vocab_size = len(wc)
        most_used_words[participant] = [
            item[0] + f' ({item[1]})' for item in wc]

    equal_size_columns = {}
    for k, v in most_used_words.items():
        col = [np.nan] * max_vocab_size
        col[: len(v)] = v
        equal_size_columns[k] = col

    df_words = pd.DataFrame({k: v for k, v in equal_size_columns.items()})

    aggs = calc_aggregates(df_chat, selected_timeframe)
    figure = px.line(aggs, x="timestamp", y="msg_count", color='sender_name')

    counts = count_msg_per_contact(df_chat)

    pie_chart_data = [
        {
            'labels': counts['theirs'][0] + [MY_NAME],
            'values': counts['theirs'][1] + [counts['mine']],
            'type': 'pie',
        },
    ]

    figure_pie = {
        'data': pie_chart_data,
        'layout': {
            'margin': {
                'l': 80,
                'r': 80,
                'b': 40,
                't': 40
            },
            'legend': {'x': 0, 'y': 1}
        }
    }
    return (figure, figure_pie, generate_table_children(df_words, 10))


@app.callback(
    [Output('hourly-bars', 'figure'),
     Output('weekly-bars', 'figure')],
    [Input('chat-dropdown', 'value')]
)
def update_figures(selected_chat_title):
    df_chat = filter_chat(df, selected_chat_title)

    dist_hourly = calc_distribution(df_chat, 'Hour of Day')
    figure1 = px.bar(dist_hourly, x="timestamp",
                     y="msg_count", color='sender_name')

    dist_weekly = calc_distribution(df_chat, 'Day of Week')
    figure2 = px.bar(dist_weekly, x="timestamp",
                     y="msg_count", color='sender_name')

    return (figure1, figure2)


@app.callback(
    Output('contacts-table', 'children'),
    [Input('contact-select-dropdown', 'value')]
)
def update_contacts_table(selected_contacts):
    return generate_table_children(get_contact_stats(df, selected_contacts))


if __name__ == '__main__':
    app.run_server(debug=True)
