import dash
from dash import Dash, dcc, html
import flask
from data_processing import *
import plotly.express as px

server = flask.Flask(__name__)


@server.route("/")
def home():
    return "Hello, Flask!"

df = read_composte_data() 
fig = px.line(df, x="Countries:text", y=["2004:number", "2020:number"], markers=True)
app = dash.Dash(server=server, routes_pathname_prefix="/dash/")

app.layout = html.Div([
    dcc.Graph(id='graph', figure=fig)
    ])


if __name__ == "__main__":
    app.run_server(debug=True)
