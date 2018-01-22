#!/root/.pyenv/versions/app/bin/python
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Response
import os.path
import pygal
import json
from urllib2 import urlopen

app = Flask(__name__)
app.config.from_object('config')


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema1.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
        return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/show',methods=['GET','POST'])
def show_entries():
    cur = g.db.execute('select title, number, year from entries order by id desc')
    entries = [dict(title=row[0], number=row[1], year=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html',entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, number, year) values (?, ?, ?)',
                  [request.form['title'], request.form['number'], request.form['year']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/delete',methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from entries where title=? and number=? and year=?',
                  [request.form['title_delete'], request.form['number_delete'], request.form['year_delete']])
    g.db.commit()
    flash('Data was successfully deleted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Welcome, Simin !')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/grahique', methods=['GET', 'POST'])
def graphique():
    bar_chart = pygal.Bar()
    cur_graphique = g.db.execute('select number, year from entries where title="Finance" order by year asc ')
    list=[]
    label=[]
    for row in cur_graphique.fetchall():
        list.append(row[0])
        label.append(row[1])
    bar_chart.x_labels=label
    bar_chart.add('Finance',list)
    return Response(response=bar_chart.render(), content_type='image/svg+xml')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == "__main__":
    app.run()
