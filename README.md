# Soundbite made with Flask

Soundbite is a simple Flask application intended to toy around with the Spotify API. It ranks the user's most popular tracks (by number of plays) and adds them in order to a playlist.

[Deployed on Heroku](https://sound-bite.herokuapp.com/) 

## Quick Start

**1. Clone the repo**

`$ git clone https://github.com/minj131/soundbite-flask.git`

`$ cd soundbite-flask`

**2. Initialize and activate virtualenv**

`$ virtual env --no-site-packages env`

`$ source env/bin/actiavte`

  **If you're on Windows, activate using**
  
`$ \venv\Scripts\activate.bat`

**3. Install the dependencies**

`$ pip install -r requirements.txt`

**4. Create the database**

`$ python run.py recreate_db`

**5. Run the development server**

`$ python run.py runserver`

## Future Work

1. Add time range functionalities
2. Add seed recommendation playlists
