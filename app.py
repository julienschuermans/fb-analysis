import logging
import numpy as np
import pandas as pd

import plotly.express as px
from dash.dash import no_update
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash

from layout import *
from helpers import *
from messages import *
from network import *


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
logging.basicConfig(level=logging.INFO)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True


# general dataload
df, df_photos = load_data()
assert MY_NAME in df.sender_name.unique().tolist(),\
    f"Name \"{MY_NAME}\" (in config.py) is not a valid sender_name, is your name \"{df.sender_name.mode().values[0]}\"?"

# preprocessing
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

# create the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

app.layout = html.Div(children=[
    html.H1(children='Facebook Messenger analysis'),

    html.Div(children=f'''
        Exploring {total_sent} messages sent and {total_received} received between {first_message_date} and {last_message_date}
    '''),

    dcc.Tabs(children=[
        dcc.Tab(label='Personal Stats', value="1"),
        dcc.Tab(label='Chat Analysis', value="2"),
        dcc.Tab(label='Contact Info', value="3"),
        dcc.Tab(label='Network Graph', value="4"),
        dcc.Tab(label='Photo Viewer', value="5"),
    ],
        value="1",
        id='tabs'
    ),
    html.Div(id='tab-output')
])

# tab callbacks


@app.callback(
    Output('tab-output', 'children'),
    [Input('tabs', 'value')])
def show_content(value):

    if value == "1":
        return html.Div(get_tab1(weekly_pattern, contact_counts))
    elif value == "2":
        return html.Div(get_tab2(df))
    elif value == "3":
        return html.Div(get_tab3(all_contacts))
    elif value == "4":
        return html.Div(get_tab4(G))
    elif value == "5":
        return html.Div(get_tab5(df_photos))


# helper functionality
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

# callbacks for content TAB 1


@app.callback(
    Output('sent-received-bar-graph', 'figure'),
    [Input('global-timeframe-dropdown', 'value')]
)
def update_global_sent_received(selected_timeframe):
    sent_received = calc_sent_received(df, selected_timeframe)

    fig = px.bar(sent_received, x='timestamp', y='msg_count',
                 color='type', barmode='group', labels={'msg_count': '#messages', 'timestamp': 'Time'})

    return fig

# callbacks for content TAB 2


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

# callbacks for content TAB 3


@app.callback(
    Output('contacts-table', 'children'),
    [Input('contact-select-dropdown', 'value')]
)
def update_contacts_table(selected_contacts):
    return generate_table_children(get_contact_stats(df, selected_contacts))

# callbacks for content TAB 5


@app.callback(
    [Output('my-slider', 'value'),
     Output('my-slider', 'max'),
     Output('my-slider', 'marks')],
    [Input('chat-dropdown-media', 'value')]
)
def update_slider_options(selected_chat_title):

    photos_selection = filter_chat(df_photos, selected_chat_title)
    photos_selection = photos_selection.sort_values('timestamp')
    list_of_filenames = photos_selection.photo_uri.tolist()

    photos_selection['date'] = pd.to_datetime(photos_selection.timestamp.dt.date).dt.strftime(
        '%d/%m/%Y')

    daily_first = photos_selection.groupby('date').first(
    ).reset_index()
    combined = photos_selection.merge(
        daily_first, on='photo_creation_timestamp', how='left')
    idx_of_first_daily_msg = combined.loc[~combined.sender_name_y.isnull(
    )].index.tolist()
    date_of_first_daily_msg = combined.loc[~combined.sender_name_y.isnull(
    )].date_y.tolist()

    value = 0
    max_value = len(list_of_filenames)-1
    marks = {value:
             {'label': date,
              'style':
              {"transform": "rotate(90deg)", 'float': 'left', 'margin-left': '-35px', 'margin-top': '20px'}}
             #   {'fontSize': 8, 'writing-mode': 'vertical-rl', 'text-orientation': 'mixed', 'margin-left': '-35px', 'margin-bottom': '20px', 'margin-top': '50px'}}
             for value, date in zip(idx_of_first_daily_msg, date_of_first_daily_msg)
             }

    return value, max_value, marks


@app.callback(
    [Output('img-container', 'children'),
     Output('img-details', 'children')],
    [Input('chat-dropdown-media', 'value'),
     Input('my-slider', 'value')]


)
def update_image(selected_chat_title, slider_value):

    photos_selection = filter_chat(df_photos, selected_chat_title)
    photos_selection = photos_selection.sort_values('timestamp')
    list_of_filenames = photos_selection.photo_uri.tolist()

    photos = html.Img(src='data:image/jpg;base64,{}'.format(read_image(list_of_filenames[int(slider_value)]).decode()),
                      style={
        'height': '40%',
        'width': '40%',
        'float': 'left',
        'margin-bottom': '20px'
    }
    )

    text = str(slider_value + 1) + '/' + str(len(list_of_filenames)) + '\n' + photos_selection.iloc[slider_value].sender_name + '  [' + \
        photos_selection.timestamp.dt.strftime(
            '%d-%m-%Y %H:%M').iloc[slider_value] + ']'

    return photos, text


if __name__ == '__main__':
    app.run_server(debug=True)
