from multiprocessing import connection
import sqlite3

import click
from flask import current_app, g
import json


def get_db():
    # Make a connection to the db for this request, if one doesn't already exist
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def queryDbJson(db, query, params=None):
    # db is a sqlite Connection Object. 
    if params is not None:
        data = db.execute(query, params).fetchall()
    else:
        data = db.execute(query).fetchall()
    jdata = [dict(row) for row in data]
    return json.dumps(jdata)

