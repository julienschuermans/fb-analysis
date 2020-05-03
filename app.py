import dash
import logging

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
logging.basicConfig(level=logging.INFO)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True
