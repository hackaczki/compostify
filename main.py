import dash
from dash import dcc, html
import flask
from data_processing import *
import plotly.express as px

server = flask.Flask(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

@server.route("/")
def home():
    return "Welcome to Compostify!"

df = read_composte_data() 
fig = px.line(df, x="Countries:text", y=["2004:number", "2020:number"], markers=True)
mapfig = px.choropleth(locations=df['Countries:code'], color=df['2020:number'], scope="europe")
fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
mapfig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app = dash.Dash(server=server, routes_pathname_prefix="/dash/")

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dash: A web application framework for your data.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(id='graph', figure=fig),
    dcc.Graph(figure=mapfig)
    ])


if __name__ == "__main__":
    app.run_server(debug=True)
