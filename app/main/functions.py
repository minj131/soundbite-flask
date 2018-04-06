import os, sys
import json
import requests
import base64
import config

from . import main
from .. import db
from ..models import User, Track, Playlist

from flask import Flask, current_app as app, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
SPOTIFY_TOP_TRACKS_URL = "https://api.spotify.com/v1/me/top/tracks?limit="
SPOTIFY_USERS_URL = "https://api.spotify.com/v1/users/"
SPOTIFY_PUBLIC_URL = "https://open.spotify.com/user/"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

#TODO: NEED TO FIX SELECT QUERIES

def db_insert_user(id, name, email, join, ref_code, ref_key):
    user = User(id, name, email, join, ref_code, ref_key)
    db.session.merge(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Rollback: ', e)

def db_insert_track(id, user_id, track_id, playlist_id, date, track_key):
    track = Track(id, user_id, track_id, playlist_id, date, track_key)
    db.session.add(track)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Rollback: ', e)

def db_insert_playlist(user_id, playlist_id, playlist_key):
    playlist = Playlist(user_id.decode(), playlist_id, playlist_key.decode())
    db.session.add(playlist)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Rollback: ', e)

def db_query_playlist(user_id):
    playlist = Playlist.query.filter_by(user_id=user_id).count()
    return playlist

def db_get_playlist(user_id):
    playlist = Playlist.query.filter_by(user_id=user_id).all()
    for p in playlist:
        print(p.user_id, ' - ', p.playlist_id)
    return playlist

def get_auth_token(code):

    REDIRECT_URI = "{}/callback/q".format(app.config['CLIENT_URL'])

    print('Getting access token')
    # print('auth ', authorization)

    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {
        'Authorization': app.config['AUTHORIZATION']
    }

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=body, headers=headers)
    auth_json = json.loads(post_request.text)

    try:
        access_token = 'Bearer ' + auth_json['access_token']
        print(access_token)
        return access_token
    except Exception as e:
        print("Error obtaining access token.\n", e)
        return e

def query_tracks(auth_token, limit, time_range, user_id, owner_id, playlist_id, time):
    user_id = user_id.decode()

    track_headers = {'Authorization': auth_token}
    # THROWING INVALID REQUEST FIX
    track_url = SPOTIFY_TOP_TRACKS_URL + limit + '&time_range=' + time_range
    print(track_url)
    track_response = requests.get(track_url, headers=track_headers)
    track_json = track_response.json()

    # print(track_json)
    track_json = sorted(track_json['items'], key=lambda d: d['popularity'], reverse=True)

    print(track_json)

    print('User top tracks status code: ', track_response.status_code)

    # List to hold relevant track data
    track_list = []
    tracks = []
    index = 0;

    # Get track info for limit range
    print('Adding tracks...')
    try:
        for x in track_json:
            track_name = x['name']
            print(track_name)
            track_id = x['id']
            print(track_id)
            track_uri = x['uri']
            print(track_uri)
            track_score = x['popularity']
            print(track_score)

            track_list.append(track_uri)
            tracks.append(track_name.encode('utf-8'))

            pre_track_key = user_id + track_id
            track_key = base64.b64encode(pre_track_key.encode())

            try:
                db_insert_track(index, user_id, track_id, playlist_id, time, track_key)
                print('On {}: SUCCESS'.format(index))
                print('Inserted: {} for {} into DB'.format(track_id, user_id))
            except Exception as e:
                print('On {}: FAILED'.format(index))
                print('Error Trace: ', e)

            index+=1
    except Exception as e:
            print('Error Trace Track Add: ', e)

    # Add to playlist
    print('Adding playlist {} for {}'.format(playlist_id, user_id))

    playlist_url = SPOTIFY_USERS_URL + user_id + '/playlists/' + playlist_id + '/tracks'
    playlist_public = SPOTIFY_PUBLIC_URL + user_id + '/playlist/' + playlist_id
    headers = {'Authorization':auth_token,'Content-Type':'application/json'}
    body = {'uris':track_list}

    pl_response = requests.put(playlist_url, headers=headers, data=json.dumps(body))
    print(pl_response)
    return pl_response, playlist_public, playlist_id, tracks

def generate_playlist(auth_token, user_id, title):
    user_id = user_id.decode()

    headers = {'Authorization':auth_token, 'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'name': title,
        'description':'Created by Soundbite!'
    }
    playlist_url = SPOTIFY_USERS_URL + user_id + '/playlists'
    pl_response = requests.post(playlist_url, headers=headers, data=json.dumps(body))

    print('User playlist status code (Should be 201): ', pl_response.status_code)

    response_json = pl_response.json()
    playlist_id = response_json['id']
    owner_id = response_json['owner']['id']
    pre_key = playlist_id + '/' + owner_id
    pl = base64.b64encode(pre_key.encode())
    print('Generate Playlist Test: ', playlist_id)

    return playlist_id, owner_id, pl
