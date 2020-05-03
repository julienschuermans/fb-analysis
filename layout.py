import plotly.express as px
import logging
import dash_core_components as dcc
import dash_html_components as html

from helpers import *
from network import plot_graph


def get_tab1(weekly_pattern, contact_counts):

    tab1 = [
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
            figure=px.imshow(weekly_pattern.T,
                             labels=dict(
                                 y="Day of Week", x="Time of Day", color="#Messages sent"),
                             y=['Monday', 'Tuesday', 'Wednesday',
                                'Thursday', 'Friday', 'Saturday', 'Sunday'],
                             x=[str(x)+'h' for x in range(24)]
                             )
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
    ]
    return tab1


def get_tab2(df):
    tab2 = [

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

    ]
    return tab2


def get_tab3(contacts):
    tab3 = [

        html.H4('Stats per contact'),
        html.Label('Select one or more contacts'),
        dcc.Dropdown(id='contact-select-dropdown',
                     options=[
                        {'label': contact, 'value': contact} for contact in contacts],
                     value=contacts[:5],
                     multi=True
                     ),

        html.Table(id='contacts-table'),
    ]
    return tab3


def get_tab4(G):
    fig = plot_graph(G)

    tab4 = [
        html.H4('Network Interactions'),
        dcc.Graph(
            id='network graph',
            figure=fig,
        ),
    ]
    return tab4


def get_tab5(df_photos):

    photos_selection = filter_chat(df_photos,  list_chat_titles(df_photos)[0])

    photos_selection = photos_selection.sort_values('timestamp')
    list_of_filenames = photos_selection.photo_uri.tolist()

    tab5 = [
        html.Label('Select a chat'),
        dcc.Dropdown(id='chat-dropdown-media',
                     options=[
                         {'label': title, 'value': title} for title in list_chat_titles(df_photos)
                     ],
                     value=list_chat_titles(df_photos)[0]
                     ),

        html.H4(id='img-count'),

        html.Div(children=[
            dcc.Slider(
                id='my-slider',
                min=0,
                step=1
            ),
        ],
            style={
            'margin-bottom': '80px',
            'margin-right': '20px',
            'margin-left': '20px',
        }
        ),

        html.H4(id='img-details',
                style={
                    'text-align': 'center',
                    'vertical-align': 'middle',
                }),
        html.H5(id='img-date',
                style={
                    'margin-bottom': '20px',
                    'text-align': 'center',
                    'vertical-align': 'middle',
                }),
        html.Div(id='img-container'),
    ]

    return tab5
