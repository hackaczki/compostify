import dash
from dash import dcc, html
import flask
from flask.templating import render_template
from data_processing import *
import plotly.express as px
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

server = flask.Flask(__name__)

server.secret_key = 'grogjreelfijreijreerjt'
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
UPLOAD_FOLDER = 'static/plants'
ALLOWED_EXTENSIONS = {'jpg'}
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(server)

class Posts(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.Integer, nullable=False)
    Author = db.Column(db.Integer, nullable=False)
    Text = db.Column(db.String(50))
    Date = db.Column(db.String(100), nullable=False)
    Reply_to = db.Column(db.Integer, nullable=True)
    Photo = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"Post('{self.Id}', '{self.Title}', '{self.Author}')"

class Users(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50))
    Password = db.Column(db.String(100))

    def __repr__(self):
        return f"User('{self.Id}', '{self.Username}')"

with server.app_context():
    db.create_all()



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
        children='Compostify!',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Compostify: A web application framework for your ECO trash.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(id='graph', figure=fig),
    dcc.Graph(figure=mapfig)
    ])



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    

@server.route('/forum')
def forum():
    return render_template('index.html')

if __name__ == "__main__":
    app.run_server(debug=True)
