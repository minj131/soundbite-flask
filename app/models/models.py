from flask import current_app
from flask_sqlalchemy import SQLAlchemy

from app import db

#
# Set classes here
#
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    join_date = db.Column(db.String(120), unique=False)
    ref_code = db.Column(db.String(500), unique=True)
    ref_key = db.Column(db.String(500), unique=True)

    def __init__(self, id, name, email, join_date, ref_code, ref_key):
        self.id = id
        self.username = name
        self.email = email
        self.registered_on = join_date
        self.ref_code = ref_code
        self.ref_key = ref_key

class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False)
    track_id = db.Column(db.Integer, unique=True)
    playlist_id = db.Column(db.String(500), unique=True)
    date = db.Column(db.String(120), unique=False)
    track_key = db.Column(db.String(500), unique=True)

    def __init__(self, id, user_id, track_id, playlist_id, date, track_key):
        self.id = id
        self.user_id = user_id
        self.track_id = track_id
        self.playlist_id = playlist_id
        self.date = date
        self.track_key = track_key

class Playlist(db.Model):
    __tablename__ = 'playlists'
    user_id = db.Column(db.Integer, unique=False)
    playlist_id = db.Column(db.String(500), unique=True)
    p_key = db.Column(db.String(500), primary_key=True, unique=True)

    def __init__(self, user_id, playlist_id, p_key):
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.p_key = p_key
