import os
import requests
import json
import base64
import config

from flask import Flask, current_app as app, render_template, request, redirect, session, make_response
from .functions import db_insert_user, db_insert_track, db_insert_playlist, db_query_playlist, db_get_playlist, get_auth_token, query_tracks, generate_playlist
from datetime import datetime

from . import main

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
SPOTIFY_USERS_URL = "https://api.spotify.com/v1/users/"

#
# Controllers
#

@main.route('/')
def home():
    CLIENT_SIDE_URL = app.config['CLIENT_URL']
    print("CURRENT URL IS", CLIENT_SIDE_URL)

    if request.args.get('ref_code'):
        session.clear() #to wipe the current sesh
        ref_code = base64.b64decode(request.args.get('ref_code'))
        session['ref_code'] = ref_code
        print('Refresh Code ', session['ref_code'])
    return render_template('pages/placeholder.index.html')


@main.route('/go', methods=['GET', 'POST'])
def go():
    session.clear()
    # session['time_range'] = request.args.get('time_range')
    # print(session['time_range'])

    REDIRECT_URI = "{}/callback/q".format(app.config['CLIENT_URL'])
    base_url = 'https://accounts.spotify.com/authorize/?client_id=' + app.config['CLIENT_ID'] + '&response_type=code&redirect_uri=' + REDIRECT_URI + '&scope=user-read-email%20playlist-read-private%20user-follow-read%20user-library-read%20user-top-read%20playlist-modify-private%20playlist-modify-public&state=34fFs29kd09'

    # response = make_response(redirect(base_url,302))
    # response.set_cookie('time_range', request.args.get('time_range'))
    return redirect(base_url)


@main.route('/callback/q')
def callback():
    if request.args.get('error'):
        return request.args.get('error')

    token = get_auth_token(request.args.get('code'))

    # Get profile data
    print('Getting user profile...')
    auth_header = {'Authorization':token}
    user_post = {}
    user_endpoint = "{}/me".format(SPOTIFY_API_URL)

    user_response = requests.get(user_endpoint, headers=auth_header)
    user_data = json.loads(user_response.text)

    user_id = user_data['id'].encode('utf-8')
    user_email = user_data['email'].encode('utf-8')
    user_name = user_data['display_name'].encode('utf-8')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print('\nUser ID: ',user_id, '\nUser Email: ', user_email, '\nTime: ', now)

    if 'ref_code' in session:
        refresh_code = session['ref_code']
    else:
        refresh_code = ''

    pre_key = user_id.decode() + refresh_code
    ref_key = base64.b64encode(pre_key.encode())

    # Add user to db
    try:
        db_insert_user(user_id.decode(), user_email.decode(), user_name.decode(), now, refresh_code, ref_key.decode())
        print("User added")
    except Exception as e:
        print("Error adding user to DB: ", e)
    # time_range = request.cookies.get('time_range')
    # print(time_range + ' from the cookie')

    # Check if user already exists
    # Fix this at some point
    if 'ref_code' in session:
        playlist_id = session['ref_code']
        owner_id = user_id
        playlist = session['ref_code'].split('/')
        print('Playlist split', playlist)
        owner_id = playlist[0]
        playlist_id = playlist[1]
    else:
        print('User not found')

    # So create a new playlist
    title = 'Most Played Tracks'

    # Check for existing playlists first
    playlist_count = db_query_playlist(user_id.decode())
    if playlist_count == 0:
        print('No playlists found')
        playlist_create = generate_playlist(token, user_id, title)

        owner_id = playlist_create[1]
        playlist = playlist_create[2]
        playlist_id = playlist_create[0]

    else:
        print('There exists {} playlist(s)!'.format(playlist_count))
        playlists = db_get_playlist(user_id.decode())

        for r in playlists:
            owner_id = str(r.user_id)
            playlist_id = r.playlist_id

        headers = {'Authorization': token}
        body = {
            'name': title,
            'description':'Created by Soundbite!'
        }
        url = SPOTIFY_USERS_URL + owner_id + '/playlists/' + playlist_id
        response = requests.put(url, headers=headers, data=json.dumps(body))

    pre_pl_key = owner_id + '/' + playlist_id
    p_key = base64.b64encode(pre_pl_key.encode())
    db_insert_playlist(user_id, playlist_id, p_key)

    time_range = 'long_term'
    limit = '50'

    s_df = query_tracks(token, limit, time_range, user_id, owner_id, playlist_id, now)
    pl_url = s_df[1]
    p_id = s_df[2]
    tracks = s_df[3]

    if 'ref_code' in session:
        session.pop('ref_code', None)

    return render_template('pages/placeholder.landing.html', name=user_name.decode(), pl_url=pl_url, user=user_id.decode(), playlist=p_id)
