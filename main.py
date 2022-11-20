import dash
from dash import dcc, html, Input, Output, ctx
import flask
from flask.templating import render_template
from data_processing import *
import plotly.express as px
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime
import bcrypt
import datetime 
import plotly.graph_objects as go


##### SERVER FLASK

server = flask.Flask(__name__)

server.secret_key = 'grogjreelfijreijreerjt'
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
UPLOAD_FOLDER = 'static/photos'
ALLOWED_EXTENSIONS = {'jpg'}
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

##### SQL ALCHEMIA 


db = SQLAlchemy(server)

class Posts(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(50), nullable=False)
    Author = db.Column(db.Integer, nullable=False)
    Text = db.Column(db.String(50))
    Date = db.Column(DateTime, default=datetime.datetime.utcnow)
    Reply_to = db.Column(db.Integer, nullable=True)
    Photo = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"Post('{self.Id}', '{self.Title}', '{self.Author}')"

class Users(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50))
    Password = db.Column(db.String(100))

    def __repr__(self):
        return f"Users('{self.Id}', '{self.Username}')"

with server.app_context():
    db.create_all()

##### PLOTS

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

@server.route("/")
def home():
    return "Welcome to Compostify!"

df = read_composte_data() 

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Countries:text"], y=df["2004:number"], name='% Composting 2004',
                         line=dict(color='firebrick', dash='dot', width=6)))
fig.add_trace(go.Scatter(x=df["Countries:text"], y=df["2020:number"], name = '% Composting 2020',
                         line=dict(color='royalblue', width=6)))

mapfig = px.choropleth(locations=df['Countries:code'], color=df['2004:number'], scope="europe", width=800, height=800, title="% of Composting by Country in 2004")

mapfig2 = px.choropleth(locations=df['Countries:code'], color=df['2020:number'], scope="europe", width=800, height=800, title="% of Composting by Country in 2020")

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
mapfig2.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
app = dash.Dash(server=server, routes_pathname_prefix="/dash/")

app.layout = html.Div(style={'backgroundColor': colors['background'], 'font-family': 'Arial'}, children=[
    html.H1(
        children=[html.Br(), 'Compostify!'],
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children=['Compostify: A web application framework for your ECO trash.', 

    html.Div(children=[html.Br(),
                       html.A(href='/composting_tracker', children=html.Button('Track Your Compost', n_clicks=0, style={'padding': '4px 8px 4px 8px', 'text_align':'center','text-transform':'uppercase', 'font-weight':'600', 'font-size':'26px !important', 'margin': '8px'})),
                html.A(href='/forum', children=html.Button('Visit Forum', n_clicks=0, style={'padding': '4px 8px 4px 8px', 'text_align':'center','text-transform':'uppercase', 'font-weight':'600', 'font-size':'26px !important', 'margin': '8px'})),
                html.A(href='/guide', children=html.Button('Look at the Guide', n_clicks=0, style={'padding': '4px 8px 4px 8px', 'text_align':'center','text-transform':'uppercase', 'font-weight':'600', 'font-size':'26px !important', 'margin': '8px'}))
            ])
                       ], style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(id='graph', figure=fig),
    html.Div(children=[
        dcc.Graph(figure=mapfig, style={'display': 'inline-block'}),
        dcc.Graph(figure=mapfig2, style={'display': 'inline-block'})],
        style={'text-align': 'center'})])

##### REST OF FLASK 
def getIdByUsername(userid):
    return Users.query.filter_by(Username=userid).first().Id

def getUsernameById(id):
    return Users.query.filter_by(Id=id).first().Username

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
def hashPassword(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verifyPassword(username, provided_password):
    stored_password = Users.query.filter_by(Username=username).first()
    if not stored_password:
        return False
    return bcrypt.checkpw(provided_password.encode(), stored_password.Password)

def createAccount(username, password):
    if Users.query.filter_by(Username=username).first():
        return False
    password = hashPassword(password)
    user = Users(Username = username, Password = password)
    db.session.add(user)
    db.session.commit()
    return True

def addPost(user,title,text):
    user = Posts(Title = title, Text = text, Author = getIdByUsername(user))
    db.session.add(user)
    db.session.commit()
    return True
##### ROUTES

@server.route('/forum', methods=['GET', 'POST'])
def forum():
    if 'username' not in session:
        return redirect(url_for('register'))
    if request.method == 'POST':
        # Add post to db
        title = request.form['title']
        desc = request.form['description']
        user = session["username"]
        addPost(user,title,desc)
    p = Posts.query.all()
    return render_template('index.html', posts=p, getUsernameById=getUsernameById)

@server.route('/guide')
def guide():
    return render_template('guide.html')

@server.route('/composting_tracker')
def composting_tracker():
    return redirect(url_for('/'))

@server.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('forum'))
    if request.method == 'POST':
        username = request.form['mail']
        password = request.form['password']
        if createAccount(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html')
    return render_template('register.html')


@server.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('forum'))
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        if verifyPassword(username, password):
            session['username'] = username
            return redirect(url_for('forum'))
        else:
        	#bad login or passwd
            return render_template('login.html')
    return render_template('login.html', info = "")

@server.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['username']
    return redirect(url_for('forum'))















if __name__ == "__main__":
    app.run_server(debug=True)
